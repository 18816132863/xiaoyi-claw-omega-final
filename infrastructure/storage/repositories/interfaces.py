"""
任务仓储接口 V1.0.0

职责：
- 定义任务持久化接口
- 支持任务 CRUD
- 支持查询和过滤
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from domain.tasks import TaskSpec, TaskStatus, ScheduleType


class TaskRepository(ABC):
    """任务仓储接口"""
    
    @abstractmethod
    async def create(self, task: TaskSpec) -> str:
        """创建任务，返回任务 ID"""
        pass
    
    @abstractmethod
    async def get(self, task_id: str) -> Optional[TaskSpec]:
        """获取任务"""
        pass
    
    @abstractmethod
    async def update(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """更新任务"""
        pass
    
    @abstractmethod
    async def delete(self, task_id: str) -> bool:
        """删除任务"""
        pass
    
    @abstractmethod
    async def list_by_user(
        self,
        user_id: str,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TaskSpec]:
        """列出用户的任务"""
        pass
    
    @abstractmethod
    async def list_pending_scheduled(
        self,
        before: datetime,
        limit: int = 100
    ) -> List[TaskSpec]:
        """列出待执行的定时任务"""
        pass
    
    @abstractmethod
    async def acquire_lock(self, task_id: str, lock_ttl: int = 60) -> bool:
        """获取任务锁"""
        pass
    
    @abstractmethod
    async def release_lock(self, task_id: str) -> bool:
        """释放任务锁"""
        pass


class TaskRunRepository(ABC):
    """任务运行仓储接口"""
    
    @abstractmethod
    async def create_run(self, task_id: str, run_no: int) -> str:
        """创建运行记录"""
        pass
    
    @abstractmethod
    async def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """获取运行记录"""
        pass
    
    @abstractmethod
    async def update_run(self, run_id: str, updates: Dict[str, Any]) -> bool:
        """更新运行记录"""
        pass
    
    @abstractmethod
    async def list_runs(self, task_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """列出任务的运行记录"""
        pass


class TaskEventRepository(ABC):
    """任务事件仓储接口"""
    
    @abstractmethod
    async def record_event(
        self,
        task_id: str,
        event_type: str,
        event_payload: Dict[str, Any],
        run_id: Optional[str] = None
    ) -> str:
        """记录事件"""
        pass
    
    @abstractmethod
    async def list_events(
        self,
        task_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """列出任务事件"""
        pass


class CheckpointRepository(ABC):
    """检查点仓储接口"""
    
    @abstractmethod
    async def save_checkpoint(
        self,
        task_id: str,
        run_id: str,
        thread_id: str,
        checkpoint_id: str,
        snapshot: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """保存检查点"""
        pass
    
    @abstractmethod
    async def get_latest_checkpoint(
        self,
        thread_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取最新检查点"""
        pass
    
    @abstractmethod
    async def list_checkpoints(
        self,
        task_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """列出检查点"""
        pass
