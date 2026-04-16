from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional


class LifecycleState(str, Enum):
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


@dataclass
class LifecycleEvent:
    skill_id: str
    from_state: Optional[LifecycleState]
    to_state: LifecycleState
    timestamp: datetime = field(default_factory=datetime.now)
    reason: str = ""


class LifecycleManager:
    def __init__(self):
        self._states: Dict[str, LifecycleState] = {}
        self._events: List[LifecycleEvent] = []

    def initialize_skill(self, skill_id: str) -> LifecycleState:
        self._states[skill_id] = LifecycleState.INSTALLED
        self._events.append(
            LifecycleEvent(skill_id=skill_id, from_state=None, to_state=LifecycleState.INSTALLED, reason="initialize")
        )
        return self._states[skill_id]

    def transition(self, skill_id: str, to_state: LifecycleState, reason: str = "") -> LifecycleState:
        from_state = self._states.get(skill_id)
        self._states[skill_id] = to_state
        self._events.append(
            LifecycleEvent(skill_id=skill_id, from_state=from_state, to_state=to_state, reason=reason)
        )
        return to_state

    def get_state(self, skill_id: str) -> Optional[LifecycleState]:
        return self._states.get(skill_id)

    def get_events(self, skill_id: Optional[str] = None) -> List[LifecycleEvent]:
        if skill_id is None:
            return list(self._events)
        return [e for e in self._events if e.skill_id == skill_id]
