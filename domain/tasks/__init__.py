# domain/tasks/__init__.py
"""
任务领域模块
"""

from .specs import (
    TaskStatus,
    StepStatus,
    TriggerMode,
    ScheduleType,
    EventType,
    TaskType,
    RetryPolicy,
    TimeoutPolicy,
    ScheduleSpec,
    StepSpec,
    TaskSpec,
)
from .state_machine import (
    can_transition,
    get_valid_transitions,
    is_terminal_status,
    STATE_TRANSITIONS,
)

__all__ = [
    "TaskStatus",
    "StepStatus",
    "TriggerMode",
    "ScheduleType",
    "EventType",
    "TaskType",
    "RetryPolicy",
    "TimeoutPolicy",
    "ScheduleSpec",
    "StepSpec",
    "TaskSpec",
    "can_transition",
    "get_valid_transitions",
    "is_terminal_status",
    "STATE_TRANSITIONS",
]
