"""
Task Orchestrator - 任务编排器
负责任务的创建、调度和生命周期管理
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import uuid
import logging
import asyncio

logger = logging.getLogger(__name__)


class TaskState:
    """任务状态"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority:
    """任务优先级"""
    LOW = 1
    NORMAL = 5
    HIGH = 10
    URGENT = 20


class Task:
    """任务实体"""
    
    def __init__(
        self,
        task_id: str,
        task_type: str,
        payload: Dict[str, Any],
        priority: int = TaskPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.payload = payload
        self.priority = priority
        self.state = TaskState.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.metadata = metadata or {}
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.retry_count = 0
        self.max_retries = 3
        self.parent_task_id: Optional[str] = None
        self.child_task_ids: List[str] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "payload": self.payload,
            "priority": self.priority,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "parent_task_id": self.parent_task_id,
            "child_task_ids": self.child_task_ids
        }


class TaskOrchestrator:
    """
    任务编排器
    管理任务的完整生命周期
    """
    
    def __init__(self, storage=None, executor=None):
        self.storage = storage
        self.executor = executor
        self._tasks: Dict[str, Task] = {}
        self._handlers: Dict[str, Callable] = {}
        self._hooks: Dict[str, List[Callable]] = {
            "pre_execute": [],
            "post_execute": [],
            "on_error": [],
            "on_retry": []
        }
    
    def register_handler(self, task_type: str, handler: Callable) -> None:
        """注册任务处理器"""
        self._handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")
    
    def add_hook(self, hook_type: str, hook: Callable) -> None:
        """添加钩子函数"""
        if hook_type in self._hooks:
            self._hooks[hook_type].append(hook)
    
    async def create_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        priority: int = TaskPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None
    ) -> Task:
        """
        创建新任务
        
        Args:
            task_type: 任务类型
            payload: 任务负载
            priority: 优先级
            metadata: 元数据
            idempotency_key: 幂等键（防止重复创建）
            
        Returns:
            创建的任务对象
        """
        # 检查幂等性
        if idempotency_key:
            existing = await self._find_by_idempotency_key(idempotency_key)
            if existing:
                logger.info(f"Returning existing task for idempotency key: {idempotency_key}")
                return existing
        
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            task_type=task_type,
            payload=payload,
            priority=priority,
            metadata=metadata
        )
        
        if idempotency_key:
            task.metadata["idempotency_key"] = idempotency_key
        
        self._tasks[task_id] = task
        
        if self.storage:
            await self.storage.save_task(task)
        
        logger.info(f"Created task: {task_id} of type: {task_type}")
        return task
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        if task_id in self._tasks:
            return self._tasks[task_id]
        
        if self.storage:
            task = await self.storage.get_task(task_id)
            if task:
                self._tasks[task_id] = task
            return task
        
        return None
    
    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """执行任务"""
        task = await self.get_task(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        # 检查状态
        if task.state == TaskState.COMPLETED:
            return task.result or {"success": True}
        
        if task.state == TaskState.RUNNING:
            raise ValueError(f"Task already running: {task_id}")
        
        # 更新状态
        task.state = TaskState.RUNNING
        task.started_at = datetime.now()
        task.updated_at = datetime.now()
        
        # 执行前置钩子
        for hook in self._hooks["pre_execute"]:
            await hook(task)
        
        try:
            # 获取处理器
            handler = self._handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"No handler for task type: {task.task_type}")
            
            # 执行任务
            result = await handler(task.payload)
            
            # 更新任务状态
            task.state = TaskState.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            
            # 执行后置钩子
            for hook in self._hooks["post_execute"]:
                await hook(task, result)
            
            logger.info(f"Task completed: {task_id}")
            return result
            
        except Exception as e:
            task.error = str(e)
            task.updated_at = datetime.now()
            
            # 执行错误钩子
            for hook in self._hooks["on_error"]:
                await hook(task, e)
            
            # 判断是否重试
            if task.retry_count < task.max_retries:
                task.state = TaskState.RETRYING
                task.retry_count += 1
                
                for hook in self._hooks["on_retry"]:
                    await hook(task)
                
                logger.warning(f"Task failed, will retry ({task.retry_count}/{task.max_retries}): {task_id}")
            else:
                task.state = TaskState.FAILED
                logger.error(f"Task failed permanently: {task_id}")
            
            raise
    
    async def pause_task(self, task_id: str) -> bool:
        """暂停任务"""
        task = await self.get_task(task_id)
        if not task:
            return False
        
        if task.state not in [TaskState.PENDING, TaskState.QUEUED, TaskState.RUNNING]:
            return False
        
        task.state = TaskState.PAUSED
        task.updated_at = datetime.now()
        
        if self.storage:
            await self.storage.save_task(task)
        
        logger.info(f"Task paused: {task_id}")
        return True
    
    async def resume_task(self, task_id: str) -> bool:
        """恢复任务"""
        task = await self.get_task(task_id)
        if not task:
            return False
        
        if task.state != TaskState.PAUSED:
            return False
        
        task.state = TaskState.PENDING
        task.updated_at = datetime.now()
        
        if self.storage:
            await self.storage.save_task(task)
        
        logger.info(f"Task resumed: {task_id}")
        return True
    
    async def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        task = await self.get_task(task_id)
        if not task:
            return False
        
        if task.state in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]:
            return False
        
        task.state = TaskState.CANCELLED
        task.updated_at = datetime.now()
        
        if self.storage:
            await self.storage.save_task(task)
        
        logger.info(f"Task cancelled: {task_id}")
        return True
    
    async def retry_task(self, task_id: str) -> bool:
        """重试任务"""
        task = await self.get_task(task_id)
        if not task:
            return False
        
        if task.state not in [TaskState.FAILED, TaskState.CANCELLED]:
            return False
        
        task.state = TaskState.PENDING
        task.retry_count += 1
        task.error = None
        task.updated_at = datetime.now()
        
        if self.storage:
            await self.storage.save_task(task)
        
        logger.info(f"Task queued for retry: {task_id}")
        return True
    
    async def list_tasks(
        self,
        state: Optional[str] = None,
        task_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Task]:
        """列出任务"""
        tasks = list(self._tasks.values())
        
        if state:
            tasks = [t for t in tasks if t.state == state]
        
        if task_type:
            tasks = [t for t in tasks if t.task_type == task_type]
        
        # 按创建时间倒序
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        return tasks[:limit]
    
    async def _find_by_idempotency_key(self, key: str) -> Optional[Task]:
        """根据幂等键查找任务"""
        for task in self._tasks.values():
            if task.metadata.get("idempotency_key") == key:
                return task
        return None
