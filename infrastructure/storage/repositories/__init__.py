# infrastructure/storage/repositories/__init__.py
"""
仓储模块

职责：
- 提供任务持久化接口
- 支持 SQLite / Postgres / Redis 实现
"""

from .interfaces import (
    TaskRepository,
    TaskRunRepository,
    TaskEventRepository,
    CheckpointRepository,
)
from .sqlite_repo import (
    SQLiteTaskRepository,
    SQLiteTaskRunRepository,
    SQLiteTaskStepRepository,
    SQLiteTaskEventRepository,
    SQLiteCheckpointRepository,
)

__all__ = [
    "TaskRepository",
    "TaskRunRepository",
    "TaskEventRepository",
    "CheckpointRepository",
    "SQLiteTaskRepository",
    "SQLiteTaskRunRepository",
    "SQLiteTaskStepRepository",
    "SQLiteTaskEventRepository",
    "SQLiteCheckpointRepository",
]
