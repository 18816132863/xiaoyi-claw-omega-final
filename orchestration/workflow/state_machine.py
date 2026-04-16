"""State machine for workflow execution."""

from enum import Enum
from typing import Dict, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime


class State(Enum):
    """Workflow states."""
    IDLE = "idle"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Event(Enum):
    """Workflow events."""
    START = "start"
    PLAN_COMPLETE = "plan_complete"
    STEP_COMPLETE = "step_complete"
    STEP_FAIL = "step_fail"
    PAUSE = "pause"
    RESUME = "resume"
    CANCEL = "cancel"
    ALL_COMPLETE = "all_complete"
    FATAL_ERROR = "fatal_error"


@dataclass
class Transition:
    """State transition."""
    from_state: State
    to_state: State
    event: Event
    action: Optional[Callable] = None
    guard: Optional[Callable] = None


@dataclass
class StateHistory:
    """History of state changes."""
    from_state: State
    to_state: State
    event: Event
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


class WorkflowStateMachine:
    """
    State machine for workflow execution.
    
    Manages state transitions and ensures valid workflow lifecycle.
    """
    
    def __init__(self):
        self.current_state = State.IDLE
        self.history: List[StateHistory] = []
        self._transitions: Dict[tuple, Transition] = {}
        self._setup_default_transitions()
    
    def _setup_default_transitions(self):
        """Setup default state transitions."""
        self.add_transition(Transition(State.IDLE, State.PLANNING, Event.START))
        self.add_transition(Transition(State.PLANNING, State.READY, Event.PLAN_COMPLETE))
        self.add_transition(Transition(State.READY, State.RUNNING, Event.START))
        self.add_transition(Transition(State.RUNNING, State.PAUSED, Event.PAUSE))
        self.add_transition(Transition(State.PAUSED, State.RUNNING, Event.RESUME))
        self.add_transition(Transition(State.RUNNING, State.COMPLETED, Event.ALL_COMPLETE))
        self.add_transition(Transition(State.RUNNING, State.FAILED, Event.FATAL_ERROR))
        self.add_transition(Transition(State.RUNNING, State.CANCELLED, Event.CANCEL))
        self.add_transition(Transition(State.PAUSED, State.CANCELLED, Event.CANCEL))
        self.add_transition(Transition(State.FAILED, State.RUNNING, Event.RESUME))  # Retry
    
    def add_transition(self, transition: Transition):
        """Add a transition rule."""
        key = (transition.from_state, transition.event)
        self._transitions[key] = transition
    
    def can_transition(self, event: Event) -> bool:
        """Check if transition is possible."""
        key = (self.current_state, event)
        if key not in self._transitions:
            return False
        
        transition = self._transitions[key]
        if transition.guard:
            return transition.guard()
        
        return True
    
    def transition(self, event: Event, metadata: Dict = None) -> bool:
        """
        Execute a state transition.
        
        Returns:
            True if transition succeeded, False otherwise
        """
        key = (self.current_state, event)
        if key not in self._transitions:
            return False
        
        transition = self._transitions[key]
        
        # Check guard
        if transition.guard and not transition.guard():
            return False
        
        # Record history
        from_state = self.current_state
        self.current_state = transition.to_state
        
        self.history.append(StateHistory(
            from_state=from_state,
            to_state=self.current_state,
            event=event,
            metadata=metadata or {}
        ))
        
        # Execute action
        if transition.action:
            try:
                transition.action()
            except Exception as e:
                # Rollback state
                self.current_state = from_state
                raise e
        
        return True
    
    def get_valid_events(self) -> List[Event]:
        """Get events that can be triggered from current state."""
        valid = []
        for (state, event) in self._transitions.keys():
            if state == self.current_state:
                valid.append(event)
        return valid
    
    def get_history(self, limit: int = None) -> List[StateHistory]:
        """Get state transition history."""
        if limit:
            return self.history[-limit:]
        return self.history
    
    def reset(self):
        """Reset to initial state."""
        self.current_state = State.IDLE
        self.history.clear()
    
    def is_terminal(self) -> bool:
        """Check if current state is terminal."""
        return self.current_state in [State.COMPLETED, State.FAILED, State.CANCELLED]
    
    def is_running(self) -> bool:
        """Check if workflow is running."""
        return self.current_state == State.RUNNING
    
    def is_paused(self) -> bool:
        """Check if workflow is paused."""
        return self.current_state == State.PAUSED
