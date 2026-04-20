# application/task_service/__init__.py
"""
任务服务模块

职责：
- 任务创建
- 任务校验
- 任务查询
- 任务管理（取消/暂停/恢复）
"""

from .service import TaskService

__all__ = ["TaskService"]
