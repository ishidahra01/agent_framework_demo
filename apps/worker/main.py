"""
Worker service for processing long-running agent jobs
"""
import asyncio
import logging
import os
import sys
from typing import Dict, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.deep_research.agent import DeepResearchAgent
from agents.tools.base import ToolRegistry
from agents.memory.manager import MemoryManager
from agents.policies.manager import PolicyManager
from observability.logging.logger import setup_logging
from observability.tracing.tracer import setup_tracing

# Setup logging and tracing
setup_logging()
setup_tracing("agent-worker")

logger = logging.getLogger(__name__)


class JobWorker:
    """
    Worker for processing agent jobs
    """
    
    def __init__(self):
        self.running = False
        self.agent = None
        self.tool_registry = None
        self.memory_manager = None
        self.policy_manager = None
        
    async def initialize(self):
        """Initialize worker components"""
        logger.info("Initializing worker...")
        
        # Create tool registry
        tool_config = {
            "web_search": {
                "api_key": os.getenv("BING_SEARCH_API_KEY"),
                "endpoint": os.getenv("BING_SEARCH_ENDPOINT")
            },
            "browser": {
                "allowed_domains": os.getenv("DOMAIN_ALLOWLIST", "").split(",")
            }
        }
        self.tool_registry = ToolRegistry.create_default_registry(tool_config)
        
        # Create memory manager
        memory_config = {
            "short_term_ttl": int(os.getenv("SHORT_TERM_MEMORY_TTL_SECONDS", "3600")),
            "long_term_enabled": os.getenv("LONG_TERM_MEMORY_ENABLED", "false").lower() == "true",
            "ai_search_endpoint": os.getenv("AI_SEARCH_ENDPOINT", ""),
            "ai_search_key": os.getenv("AI_SEARCH_API_KEY", ""),
            "ai_search_index": os.getenv("AI_SEARCH_INDEX_NAME", "agent-mem-long")
        }
        self.memory_manager = MemoryManager.create_default(memory_config)
        
        # Create policy manager
        policy_config = {
            "domain_allowlist": os.getenv("DOMAIN_ALLOWLIST", "").split(","),
            "require_citations": os.getenv("REQUIRE_CITATIONS", "true").lower() == "true",
            "rate_limit_requests_per_minute": int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60")),
            "rate_limit_tokens_per_minute": int(os.getenv("RATE_LIMIT_TOKENS_PER_MINUTE", "150000")),
            "human_approval_steps": ["external_data_export", "suspicious_domain"]
        }
        self.policy_manager = PolicyManager(policy_config)
        
        # Create agent
        self.agent = DeepResearchAgent()
        
        # Register tools with agent
        for tool_name in self.tool_registry.list_tools():
            tool = self.tool_registry.get(tool_name)
            self.agent.register_tool(tool_name, tool)
        
        # Set memory and policy managers
        self.agent.set_memory(self.memory_manager)
        self.agent.set_policy_manager(self.policy_manager)
        
        logger.info("Worker initialized successfully")
    
    async def process_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single job
        """
        job_id = job.get("job_id")
        task = job.get("task")
        constraints = job.get("constraints", {})
        
        logger.info(f"Processing job: {job_id}", extra={"job_id": job_id})
        
        try:
            # Run agent
            result = await self.agent.run(task, constraints)
            
            logger.info(f"Job completed: {job_id}", extra={
                "job_id": job_id,
                "status": result.get("status")
            })
            
            return {
                "job_id": job_id,
                "status": "completed",
                "result": result,
                "completed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Job failed: {job_id}", extra={
                "job_id": job_id,
                "error": str(e)
            }, exc_info=True)
            
            return {
                "job_id": job_id,
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
    
    async def poll_queue(self):
        """
        Poll job queue for new jobs
        In production, this would connect to Azure Service Bus
        """
        logger.info("Starting queue polling...")
        
        while self.running:
            try:
                # Mock: In production, receive from Service Bus
                # job = await receive_from_service_bus()
                
                # For now, just sleep
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error polling queue: {str(e)}", exc_info=True)
                await asyncio.sleep(10)
    
    async def start(self):
        """Start the worker"""
        self.running = True
        
        await self.initialize()
        
        logger.info("Worker started")
        
        # Start polling
        await self.poll_queue()
    
    async def stop(self):
        """Stop the worker"""
        logger.info("Stopping worker...")
        self.running = False


async def main():
    """Main entry point"""
    worker = JobWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        await worker.stop()
    except Exception as e:
        logger.error(f"Worker error: {str(e)}", exc_info=True)
        await worker.stop()
        raise


if __name__ == "__main__":
    asyncio.run(main())
