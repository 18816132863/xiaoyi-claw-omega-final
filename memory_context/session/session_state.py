"""Session state management for short-term context."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import json


@dataclass
class SessionState:
    """Current session state container."""
    session_id: str
    task_id: Optional[str] = None
    status: str = "idle"  # idle, running, paused, completed, failed
    current_step: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Context
    file_context: list = field(default_factory=list)
    command_chain: list = field(default_factory=list)
    variables: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "task_id": self.task_id,
            "status": self.status,
            "current_step": self.current_step,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "file_context": self.file_context,
            "command_chain": self.command_chain,
            "variables": self.variables
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SessionState":
        return cls(
            session_id=data["session_id"],
            task_id=data.get("task_id"),
            status=data.get("status", "idle"),
            current_step=data.get("current_step"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            file_context=data.get("file_context", []),
            command_chain=data.get("command_chain", []),
            variables=data.get("variables", {})
        )


class SessionStateStore:
    """Manages session state persistence."""
    
    def __init__(self, store_path: str = "memory_context/data/sessions.json"):
        self.store_path = store_path
        self._cache: dict[str, SessionState] = {}
    
    def get(self, session_id: str) -> Optional[SessionState]:
        if session_id in self._cache:
            return self._cache[session_id]
        # TODO: Load from persistent store
        return None
    
    def save(self, state: SessionState) -> None:
        state.updated_at = datetime.now()
        self._cache[state.session_id] = state
        # TODO: Persist to store
    
    def create(self, session_id: str) -> SessionState:
        state = SessionState(session_id=session_id)
        self.save(state)
        return state
    
    def update(self, session_id: str, **kwargs) -> Optional[SessionState]:
        state = self.get(session_id)
        if state:
            for key, value in kwargs.items():
                if hasattr(state, key):
                    setattr(state, key, value)
            self.save(state)
        return state
