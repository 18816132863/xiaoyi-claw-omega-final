# domain/__init__.py
"""
领域层

职责：
- 任务定义
- 规格定义
- 状态枚举
- 策略定义
- 验证规则
"""

from .tasks import (
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
]
