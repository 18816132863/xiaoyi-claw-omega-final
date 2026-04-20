# domain/tasks/__init__.py
"""
任务领域模块

职责：
- 任务规格定义
- 任务状态机
- 任务仓储接口
- 任务事件
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
