"""
FastAPI-based Agent API
Provides REST endpoints for job submission and management
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import os
import sys
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from observability.logging.logger import setup_logging
from observability.tracing.tracer import setup_tracing

# Setup logging and tracing
setup_logging()
setup_tracing("agent-api")

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Enterprise Agent API",
    description="Deep Research Agent with Long-Running Task Support",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class JobConstraints(BaseModel):
    """Job execution constraints"""
    budget_tokens: Optional[int] = Field(default=100000, ge=1000, le=1000000)
    time_limit_min: Optional[int] = Field(default=60, ge=1, le=480)
    max_parallel_tasks: Optional[int] = Field(default=4, ge=1, le=10)


class JobPolicy(BaseModel):
    """Job policy settings"""
    require_human_approval: bool = Field(default=False)
    require_citations: bool = Field(default=True)
    allowed_domains: Optional[List[str]] = None


class JobRequest(BaseModel):
    """Job submission request"""
    task: str = Field(..., min_length=10, max_length=5000)
    constraints: Optional[JobConstraints] = Field(default_factory=JobConstraints)
    policy: Optional[JobPolicy] = Field(default_factory=JobPolicy)
    metadata: Optional[Dict[str, Any]] = None


class JobStatus(BaseModel):
    """Job status response"""
    job_id: str
    status: str  # queued, running, completed, failed, cancelled
    task: str
    created_at: datetime
    updated_at: datetime
    progress: Optional[float] = None  # 0.0 to 1.0
    current_step: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class JobResponse(BaseModel):
    """Job submission response"""
    job_id: str
    status: str
    message: str
    created_at: datetime


# In-memory job store (in production, use database or Service Bus)
jobs_store: Dict[str, JobStatus] = {}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Enterprise Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from datetime import timezone
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(request: JobRequest):
    """
    Submit a new research job
    """
    try:
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        
        # Create job status
        job_status = JobStatus(
            job_id=job_id,
            status="queued",
            task=request.task,
            created_at=created_at,
            updated_at=created_at,
            progress=0.0
        )
        
        # Store job
        jobs_store[job_id] = job_status
        
        logger.info(f"Job created: {job_id}", extra={
            "job_id": job_id,
            "task_length": len(request.task),
            "constraints": request.constraints.dict() if request.constraints else None
        })
        
        # In production, enqueue to Service Bus
        # await enqueue_job(job_id, request)
        
        return JobResponse(
            job_id=job_id,
            status="queued",
            message="Job successfully queued for processing",
            created_at=created_at
        )
        
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )


@app.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get job status and results
    """
    if job_id not in jobs_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}"
        )
    
    return jobs_store[job_id]


@app.get("/jobs", response_model=List[JobStatus])
async def list_jobs(
    status_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    List all jobs with optional filtering
    """
    jobs = list(jobs_store.values())
    
    if status_filter:
        jobs = [j for j in jobs if j.status == status_filter]
    
    # Sort by creation time (newest first)
    jobs.sort(key=lambda x: x.created_at, reverse=True)
    
    # Pagination
    jobs = jobs[offset:offset + limit]
    
    return jobs


@app.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a running job
    """
    if job_id not in jobs_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}"
        )
    
    job = jobs_store[job_id]
    
    if job.status in ["completed", "failed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is already in terminal state: {job.status}"
        )
    
    job.status = "cancelled"
    job.updated_at = datetime.now(timezone.utc)
    
    logger.info(f"Job cancelled: {job_id}")
    
    return {"message": f"Job {job_id} cancelled successfully"}


@app.post("/jobs/{job_id}/approve")
async def approve_job_step(job_id: str, approval: Dict[str, Any]):
    """
    Approve a pending job step (Human-in-the-loop)
    """
    if job_id not in jobs_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}"
        )
    
    # In production, this would interact with the approval system
    logger.info(f"Approval received for job: {job_id}", extra={"approval": approval})
    
    return {"message": "Approval recorded", "job_id": job_id}


@app.get("/metrics")
async def get_metrics():
    """
    Get API metrics
    """
    total_jobs = len(jobs_store)
    status_counts = {}
    
    for job in jobs_store.values():
        status_counts[job.status] = status_counts.get(job.status, 0) + 1
    
    return {
        "total_jobs": total_jobs,
        "status_counts": status_counts,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("API_PORT", "8080"))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
