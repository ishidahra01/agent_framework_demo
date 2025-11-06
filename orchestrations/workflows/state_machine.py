"""
Workflow State Machine for Long-Running Jobs
Handles checkpointing, resumption, and state transitions
"""
from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, UTC, timezone
import json
import logging

logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    """Workflow states"""
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING_APPROVAL = "waiting_approval"
    REFLECTING = "reflecting"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Checkpoint:
    """Checkpoint for workflow state"""
    checkpoint_id: str
    workflow_id: str
    state: WorkflowState
    step_index: int
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowStep:
    """Individual workflow step"""
    step_id: str
    name: str
    state: WorkflowState
    dependencies: List[str] = field(default_factory=list)
    retries: int = 0
    max_retries: int = 3
    result: Optional[Any] = None
    error: Optional[str] = None


class WorkflowStateMachine:
    """
    State machine for managing workflow execution
    """
    
    # Valid state transitions
    TRANSITIONS = {
        WorkflowState.PENDING: [WorkflowState.PLANNING, WorkflowState.CANCELLED],
        WorkflowState.PLANNING: [WorkflowState.EXECUTING, WorkflowState.FAILED, WorkflowState.CANCELLED],
        WorkflowState.EXECUTING: [WorkflowState.WAITING_APPROVAL, WorkflowState.REFLECTING, 
                                  WorkflowState.FAILED, WorkflowState.CANCELLED],
        WorkflowState.WAITING_APPROVAL: [WorkflowState.EXECUTING, WorkflowState.CANCELLED],
        WorkflowState.REFLECTING: [WorkflowState.REPORTING, WorkflowState.EXECUTING, 
                                   WorkflowState.FAILED, WorkflowState.CANCELLED],
        WorkflowState.REPORTING: [WorkflowState.COMPLETED, WorkflowState.FAILED, WorkflowState.CANCELLED],
        WorkflowState.COMPLETED: [],
        WorkflowState.FAILED: [],
        WorkflowState.CANCELLED: []
    }
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.current_state = WorkflowState.PENDING
        self.steps: List[WorkflowStep] = []
        self.checkpoints: List[Checkpoint] = []
        self.context: Dict[str, Any] = {}
        
    def can_transition(self, new_state: WorkflowState) -> bool:
        """Check if transition is valid"""
        allowed_states = self.TRANSITIONS.get(self.current_state, [])
        return new_state in allowed_states
    
    def transition(self, new_state: WorkflowState, context: Optional[Dict[str, Any]] = None) -> bool:
        """Transition to new state"""
        if not self.can_transition(new_state):
            logger.error(f"Invalid transition: {self.current_state} -> {new_state}")
            return False
        
        logger.info(f"Workflow {self.workflow_id}: {self.current_state} -> {new_state}")
        
        self.current_state = new_state
        
        if context:
            self.context.update(context)
        
        # Create checkpoint
        self._create_checkpoint()
        
        return True
    
    def _create_checkpoint(self) -> Checkpoint:
        """Create checkpoint of current state"""
        checkpoint = Checkpoint(
            checkpoint_id=f"cp_{len(self.checkpoints)}",
            workflow_id=self.workflow_id,
            state=self.current_state,
            step_index=len(self.steps),
            data=self.context.copy()
        )
        
        self.checkpoints.append(checkpoint)
        logger.debug(f"Checkpoint created: {checkpoint.checkpoint_id}")
        
        return checkpoint
    
    def restore_from_checkpoint(self, checkpoint: Checkpoint):
        """Restore workflow from checkpoint"""
        logger.info(f"Restoring workflow {self.workflow_id} from checkpoint {checkpoint.checkpoint_id}")
        
        self.current_state = checkpoint.state
        self.context = checkpoint.data.copy()
        
        # Restore steps up to checkpoint
        if checkpoint.step_index < len(self.steps):
            self.steps = self.steps[:checkpoint.step_index]
    
    def add_step(self, step: WorkflowStep):
        """Add step to workflow"""
        self.steps.append(step)
        logger.debug(f"Step added: {step.step_id}")
    
    def get_current_step(self) -> Optional[WorkflowStep]:
        """Get current executing step"""
        for step in self.steps:
            if step.state in [WorkflowState.PLANNING, WorkflowState.EXECUTING]:
                return step
        return None
    
    def mark_step_completed(self, step_id: str, result: Any):
        """Mark step as completed"""
        for step in self.steps:
            if step.step_id == step_id:
                step.state = WorkflowState.COMPLETED
                step.result = result
                logger.info(f"Step completed: {step_id}")
                return True
        return False
    
    def mark_step_failed(self, step_id: str, error: str):
        """Mark step as failed"""
        for step in self.steps:
            if step.step_id == step_id:
                step.error = error
                step.retries += 1
                
                if step.retries >= step.max_retries:
                    step.state = WorkflowState.FAILED
                    logger.error(f"Step failed after {step.retries} retries: {step_id}")
                else:
                    logger.warning(f"Step failed (retry {step.retries}/{step.max_retries}): {step_id}")
                
                return True
        return False
    
    def can_retry_step(self, step_id: str) -> bool:
        """Check if step can be retried"""
        for step in self.steps:
            if step.step_id == step_id:
                return step.retries < step.max_retries
        return False
    
    def serialize(self) -> str:
        """Serialize workflow state to JSON"""
        data = {
            "workflow_id": self.workflow_id,
            "current_state": self.current_state.value,
            "steps": [
                {
                    "step_id": s.step_id,
                    "name": s.name,
                    "state": s.state.value,
                    "dependencies": s.dependencies,
                    "retries": s.retries,
                    "max_retries": s.max_retries,
                    "error": s.error
                }
                for s in self.steps
            ],
            "context": self.context
        }
        return json.dumps(data)
    
    @classmethod
    def deserialize(cls, data: str) -> 'WorkflowStateMachine':
        """Deserialize workflow from JSON"""
        obj = json.loads(data)
        
        workflow = cls(obj["workflow_id"])
        workflow.current_state = WorkflowState(obj["current_state"])
        workflow.context = obj["context"]
        
        for step_data in obj["steps"]:
            step = WorkflowStep(
                step_id=step_data["step_id"],
                name=step_data["name"],
                state=WorkflowState(step_data["state"]),
                dependencies=step_data["dependencies"],
                retries=step_data["retries"],
                max_retries=step_data["max_retries"],
                error=step_data.get("error")
            )
            workflow.steps.append(step)
        
        return workflow
    
    def get_progress(self) -> float:
        """Calculate workflow progress (0.0 to 1.0)"""
        if not self.steps:
            return 0.0
        
        completed = sum(1 for s in self.steps if s.state == WorkflowState.COMPLETED)
        return completed / len(self.steps)
