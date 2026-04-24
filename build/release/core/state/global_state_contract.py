"""Global state contract - unified state management."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class SystemState(Enum):
    """System-level states."""
    INITIALIZING = "initializing"
    READY = "ready"
    BUSY = "busy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    ERROR = "error"


@dataclass
class GlobalState:
    """
    Global system state contract.
    
    Single source of truth for system-wide state.
    """
    state: SystemState = SystemState.READY
    active_tasks: int = 0
    active_sessions: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "state": self.state.value,
            "active_tasks": self.active_tasks,
            "active_sessions": self.active_sessions,
            "last_updated": self.last_updated.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "GlobalState":
        return cls(
            state=SystemState(data.get("state", "ready")),
            active_tasks=data.get("active_tasks", 0),
            active_sessions=data.get("active_sessions", 0),
            last_updated=datetime.fromisoformat(data["last_updated"]) if data.get("last_updated") else datetime.now(),
            metadata=data.get("metadata", {})
        )


class GlobalStateContract:
    """
    Contract for global state access.
    
    All state access must go through this contract.
    """
    
    _instance: Optional["GlobalStateContract"] = None
    _state: GlobalState = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._state = GlobalState()
        return cls._instance
    
    def get_state(self) -> GlobalState:
        """Get current global state."""
        return self._state
    
    def set_state(self, state: SystemState) -> None:
        """Set system state."""
        self._state.state = state
        self._state.last_updated = datetime.now()
    
    def increment_tasks(self) -> int:
        """Increment active task count."""
        self._state.active_tasks += 1
        self._state.last_updated = datetime.now()
        return self._state.active_tasks
    
    def decrement_tasks(self) -> int:
        """Decrement active task count."""
        if self._state.active_tasks > 0:
            self._state.active_tasks -= 1
        self._state.last_updated = datetime.now()
        return self._state.active_tasks
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        self._state.metadata[key] = value
        self._state.last_updated = datetime.now()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self._state.metadata.get(key, default)


# Global accessor
def get_global_state() -> GlobalStateContract:
    """Get the global state contract instance."""
    return GlobalStateContract()
