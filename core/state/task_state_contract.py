"""Task state contract - task lifecycle state management."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import uuid


class TaskStatus(Enum):
    """Task lifecycle states."""
    CREATED = "created"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskState:
    """
    Task state contract.
    
    Represents the complete state of a task.
    """
    task_id: str
    status: TaskStatus = TaskStatus.CREATED
    profile: str = "default"
    intent: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    current_step: Optional[str] = None
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "profile": self.profile,
            "intent": self.intent,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "current_step": self.current_step,
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TaskState":
        return cls(
            task_id=data["task_id"],
            status=TaskStatus(data.get("status", "created")),
            profile=data.get("profile", "default"),
            intent=data.get("intent", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            current_step=data.get("current_step"),
            completed_steps=data.get("completed_steps", []),
            failed_steps=data.get("failed_steps", []),
            result=data.get("result", {}),
            error=data.get("error"),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def create(cls, intent: str, profile: str = "default") -> "TaskState":
        """Create a new task state."""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        return cls(
            task_id=task_id,
            intent=intent,
            profile=profile
        )


class TaskStateContract:
    """
    Contract for task state management.
    
    All task state operations must go through this contract.
    """
    
    def __init__(self):
        self._tasks: Dict[str, TaskState] = {}
    
    def create_task(self, intent: str, profile: str = "default") -> TaskState:
        """Create a new task."""
        task = TaskState.create(intent=intent, profile=profile)
        self._tasks[task.task_id] = task
        return task
    
    def get_task(self, task_id: str) -> Optional[TaskState]:
        """Get task by ID."""
        return self._tasks.get(task_id)
    
    def update_task(self, task_id: str, **kwargs) -> Optional[TaskState]:
        """Update task state."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        return task
    
    def start_task(self, task_id: str) -> Optional[TaskState]:
        """Mark task as started."""
        return self.update_task(
            task_id,
            status=TaskStatus.RUNNING,
            started_at=datetime.now()
        )
    
    def complete_task(self, task_id: str, result: Dict = None) -> Optional[TaskState]:
        """Mark task as completed."""
        return self.update_task(
            task_id,
            status=TaskStatus.COMPLETED,
            completed_at=datetime.now(),
            result=result or {}
        )
    
    def fail_task(self, task_id: str, error: str) -> Optional[TaskState]:
        """Mark task as failed."""
        return self.update_task(
            task_id,
            status=TaskStatus.FAILED,
            completed_at=datetime.now(),
            error=error
        )
    
    def get_active_tasks(self) -> List[TaskState]:
        """Get all active tasks."""
        return [
            t for t in self._tasks.values()
            if t.status in [TaskStatus.CREATED, TaskStatus.PLANNING, TaskStatus.RUNNING]
        ]
    
    def get_recent_tasks(self, limit: int = 10) -> List[TaskState]:
        """Get recent tasks."""
        tasks = sorted(
            self._tasks.values(),
            key=lambda t: t.created_at,
            reverse=True
        )
        return tasks[:limit]


# Global accessor
_task_state_contract: Optional[TaskStateContract] = None


def get_task_state_contract() -> TaskStateContract:
    """Get the task state contract instance."""
    global _task_state_contract
    if _task_state_contract is None:
        _task_state_contract = TaskStateContract()
    return _task_state_contract
