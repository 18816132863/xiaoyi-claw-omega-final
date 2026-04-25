"""
任务服务 V1.0.0

职责：
- 创建任务
- 校验任务
- 持久化任务
- 查询任务
- 取消/暂停/恢复任务
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from domain.tasks import (
    TaskSpec,
    TaskStatus,
    TriggerMode,
    EventType,
)
from infrastructure.storage.repositories import (
    SQLiteTaskRepository,
    SQLiteTaskEventRepository,
)


class TaskService:
    """任务服务"""
    
    def __init__(
        self,
        task_repo: Optional[SQLiteTaskRepository] = None,
        event_repo: Optional[SQLiteTaskEventRepository] = None
    ):
        self.task_repo = task_repo or SQLiteTaskRepository()
        self.event_repo = event_repo or SQLiteTaskEventRepository()
    
    async def create_task(self, spec: TaskSpec) -> Dict[str, Any]:
        """
        创建任务
        
        流程：
        1. 校验规格
        2. 生成幂等键
        3. 持久化
        4. 记录事件
        """
        # 1. 校验
        errors = spec.validate_spec()
        if errors:
            return {
                "success": False,
                "errors": errors,
                "task_id": None
            }
        
        # 2. 生成幂等键
        if not spec.idempotency_key:
            spec.idempotency_key = spec.generate_idempotency_key()
        
        # 3. 检查幂等
        existing = await self._check_idempotency(spec.idempotency_key)
        if existing:
            return {
                "success": True,
                "task_id": existing,
                "message": "任务已存在（幂等）",
                "idempotent": True
            }
        
        # 4. 设置初始状态
        spec.status = TaskStatus.VALIDATED
        
        # 5. 计算下次运行时间
        if spec.trigger_mode == TriggerMode.SCHEDULED and spec.schedule:
            next_run = spec.schedule.get_next_run_at()
            if next_run:
                # 更新 schedule 的 next_run_at
                spec.schedule.next_run_at = next_run.isoformat()
        
        # 6. 持久化
        task_id = await self.task_repo.create(spec)
        
        # 7. 更新状态
        await self.task_repo.update(task_id, {"status": TaskStatus.PERSISTED.value})
        
        # 8. 记录事件
        await self.event_repo.record_event(
            task_id=task_id,
            event_type=EventType.CREATED.value,
            event_payload={
                "task_type": spec.task_type,
                "goal": spec.goal,
                "trigger_mode": spec.trigger_mode.value
            }
        )
        
        await self.event_repo.record_event(
            task_id=task_id,
            event_type=EventType.VALIDATED.value,
            event_payload={"errors": []}
        )
        
        await self.event_repo.record_event(
            task_id=task_id,
            event_type=EventType.PERSISTED.value,
            event_payload={}
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "status": TaskStatus.PERSISTED.value,
            "idempotent": False
        }
    
    async def get_task(self, task_id: str) -> Optional[TaskSpec]:
        """获取任务"""
        return await self.task_repo.get(task_id)
    
    async def list_tasks(
        self,
        user_id: str,
        status: Optional[TaskStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[TaskSpec]:
        """列出任务"""
        return await self.task_repo.list_by_user(user_id, status, limit, offset)
    
    async def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """取消任务"""
        task = await self.task_repo.get(task_id)
        if not task:
            return {"success": False, "error": "任务不存在"}
        
        # 检查是否可取消
        if task.status in (TaskStatus.SUCCEEDED, TaskStatus.FAILED, TaskStatus.CANCELLED):
            return {"success": False, "error": f"任务状态 {task.status.value} 不可取消"}
        
        # 更新状态
        await self.task_repo.update(task_id, {"status": TaskStatus.CANCELLED.value})
        
        # 记录事件
        await self.event_repo.record_event(
            task_id=task_id,
            event_type=EventType.CANCELLED.value,
            event_payload={"previous_status": task.status.value}
        )
        
        return {"success": True, "task_id": task_id, "status": TaskStatus.CANCELLED.value}
    
    async def pause_task(self, task_id: str) -> Dict[str, Any]:
        """暂停任务"""
        task = await self.task_repo.get(task_id)
        if not task:
            return {"success": False, "error": "任务不存在"}
        
        # 扩展可暂停状态：PERSISTED, QUEUED, RUNNING, WAITING_RETRY
        if task.status not in (TaskStatus.PERSISTED, TaskStatus.QUEUED, TaskStatus.RUNNING, TaskStatus.WAITING_RETRY):
            return {"success": False, "error": f"任务状态 {task.status.value} 不可暂停"}
        
        previous_status = task.status.value
        await self.task_repo.update(task_id, {"status": TaskStatus.PAUSED.value})
        
        await self.event_repo.record_event(
            task_id=task_id,
            event_type=EventType.PAUSED.value,
            event_payload={"previous_status": previous_status}
        )
        
        return {"success": True, "task_id": task_id, "status": TaskStatus.PAUSED.value, "previous_status": previous_status}
    
    async def resume_task(self, task_id: str) -> Dict[str, Any]:
        """恢复任务"""
        task = await self.task_repo.get(task_id)
        if not task:
            return {"success": False, "error": "任务不存在"}
        
        if task.status != TaskStatus.PAUSED:
            return {"success": False, "error": f"任务状态 {task.status.value} 不可恢复"}
        
        # 从最近一次 PAUSED 事件获取 previous_status
        events = await self.event_repo.list_events(task_id, limit=100)
        previous_status = TaskStatus.QUEUED.value  # 默认恢复到 QUEUED
        
        for event in reversed(events):
            if event.get("event_type") == EventType.PAUSED.value:
                payload = event.get("event_payload", {})
                if isinstance(payload, str):
                    import json
                    payload = json.loads(payload)
                previous_status = payload.get("previous_status", TaskStatus.QUEUED.value)
                break
        
        # 根据之前状态决定恢复目标
        if previous_status == TaskStatus.PERSISTED.value:
            target_status = TaskStatus.PERSISTED.value
        else:
            target_status = TaskStatus.QUEUED.value
        
        await self.task_repo.update(task_id, {"status": TaskStatus.RESUMED.value})
        
        await self.event_repo.record_event(
            task_id=task_id,
            event_type=EventType.RESUMED.value,
            event_payload={"previous_status": previous_status, "target_status": target_status}
        )
        
        # 恢复到目标状态
        await self.task_repo.update(task_id, {"status": target_status})
        
        return {"success": True, "task_id": task_id, "status": target_status, "previous_status": previous_status}
    
    async def get_task_events(self, task_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取任务事件"""
        return await self.event_repo.list_events(task_id, limit)
    
    async def _check_idempotency(self, idempotency_key: str) -> Optional[str]:
        """检查幂等键"""
        # 简化实现：查询数据库
        # 实际应该用专门的索引查询
        return None
