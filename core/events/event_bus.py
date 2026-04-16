"""Event bus - unified event system."""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import asyncio
from collections import defaultdict


class EventType(Enum):
    # Task events
    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    
    # Context events
    CONTEXT_BUILT = "context_built"
    CONTEXT_CLEARED = "context_cleared"
    
    # Workflow events
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    
    # Step events
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    RETRY_TRIGGERED = "retry_triggered"
    FALLBACK_TRIGGERED = "fallback_triggered"
    
    # Skill events
    SKILL_SELECTED = "skill_selected"
    SKILL_EXECUTED = "skill_executed"
    SKILL_FAILED = "skill_failed"
    
    # Policy events
    POLICY_APPLIED = "policy_applied"
    POLICY_DENIED = "policy_denied"
    
    # Degradation events
    DEGRADATION_TRIGGERED = "degradation_triggered"
    DEGRADATION_RECOVERED = "degradation_recovered"
    KILL_SWITCH_ACTIVATED = "kill_switch_activated"
    
    # Memory events
    MEMORY_STORED = "memory_stored"
    MEMORY_RETRIEVED = "memory_retrieved"
    
    # Budget events
    BUDGET_EXCEEDED = "budget_exceeded"
    BUDGET_WARNING = "budget_warning"


@dataclass
class Event:
    """A system event."""
    event_type: EventType
    source: str
    data: Dict
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = ""
    correlation_id: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.event_id:
            self.event_id = f"{self.event_type.value}_{self.timestamp.strftime('%Y%m%d%H%M%S%f')}"
    
    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "source": self.source,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "metadata": self.metadata
        }


class EventBus:
    """
    Unified event bus for the entire system.
    
    Features:
    - Pub/sub pattern
    - Synchronous and async handlers
    - Event correlation
    - Event history
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self._handlers: Dict[EventType, List[Callable]] = defaultdict(list)
        self._async_handlers: Dict[EventType, List[Callable]] = defaultdict(list)
        self._global_handlers: List[Callable] = []
        self._history: List[Event] = []
        self._correlation_map: Dict[str, List[str]] = defaultdict(list)
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe to an event type."""
        self._handlers[event_type].append(handler)
    
    def subscribe_async(self, event_type: EventType, handler: Callable):
        """Subscribe an async handler to an event type."""
        self._async_handlers[event_type].append(handler)
    
    def subscribe_global(self, handler: Callable):
        """Subscribe to all events."""
        self._global_handlers.append(handler)
    
    def unsubscribe(self, event_type: EventType, handler: Callable):
        """Unsubscribe from an event type."""
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
        if handler in self._async_handlers[event_type]:
            self._async_handlers[event_type].remove(handler)
    
    def publish(self, event: Event):
        """Publish an event."""
        # Add to history
        self._history.append(event)
        if len(self._history) > self.max_history:
            self._history.pop(0)
        
        # Track correlation
        if event.correlation_id:
            self._correlation_map[event.correlation_id].append(event.event_id)
        
        # Call sync handlers
        for handler in self._handlers[event.event_type]:
            try:
                handler(event)
            except Exception as e:
                print(f"Warning: Event handler failed: {e}")
        
        # Call global handlers
        for handler in self._global_handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"Warning: Global handler failed: {e}")
    
    async def publish_async(self, event: Event):
        """Publish an event with async handlers."""
        self.publish(event)
        
        # Call async handlers
        for handler in self._async_handlers[event.event_type]:
            try:
                await handler(event)
            except Exception as e:
                print(f"Warning: Async handler failed: {e}")
    
    def emit(
        self,
        event_type: EventType,
        source: str,
        data: Dict,
        correlation_id: str = None
    ) -> Event:
        """Convenience method to create and publish an event."""
        event = Event(
            event_type=event_type,
            source=source,
            data=data,
            correlation_id=correlation_id or ""
        )
        self.publish(event)
        return event
    
    def get_history(
        self,
        event_type: EventType = None,
        source: str = None,
        limit: int = 100
    ) -> List[Event]:
        """Get event history."""
        events = self._history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if source:
            events = [e for e in events if e.source == source]
        
        return events[-limit:]
    
    def get_correlated_events(self, correlation_id: str) -> List[Event]:
        """Get all events with a correlation ID."""
        event_ids = self._correlation_map.get(correlation_id, [])
        return [e for e in self._history if e.event_id in event_ids]
    
    def clear_history(self):
        """Clear event history."""
        self._history.clear()
        self._correlation_map.clear()


# Global event bus instance
_global_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus."""
    global _global_bus
    if _global_bus is None:
        _global_bus = EventBus()
    return _global_bus


def emit_event(
    event_type: EventType,
    source: str,
    data: Dict,
    correlation_id: str = None
) -> Event:
    """Emit an event to the global bus."""
    return get_event_bus().emit(event_type, source, data, correlation_id)
