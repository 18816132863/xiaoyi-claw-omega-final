"""
Batch Orchestrator - 批量编排器
负责批量任务的并行执行和管理
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import uuid
import logging
import asyncio
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class BatchState(Enum):
    """批量任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchItem:
    """批量任务项"""
    item_id: str
    payload: Dict[str, Any]
    state: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class BatchJob:
    """批量任务"""
    batch_id: str
    name: str
    items: List[BatchItem] = field(default_factory=list)
    state: BatchState = BatchState.PENDING
    concurrency: int = 5
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "name": self.name,
            "state": self.state.value,
            "concurrency": self.concurrency,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
            "summary": self.get_summary(),
            "items": [
                {
                    "item_id": item.item_id,
                    "state": item.state,
                    "result": item.result,
                    "error": item.error
                }
                for item in self.items
            ]
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        total = len(self.items)
        completed = sum(1 for i in self.items if i.state == "completed")
        failed = sum(1 for i in self.items if i.state == "failed")
        pending = sum(1 for i in self.items if i.state == "pending")
        running = sum(1 for i in self.items if i.state == "running")
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "running": running,
            "success_rate": (completed / total * 100) if total > 0 else 0
        }


class BatchOrchestrator:
    """
    批量编排器
    管理批量任务的并行执行
    """
    
    def __init__(self, storage=None, task_orchestrator=None):
        self.storage = storage
        self.task_orchestrator = task_orchestrator
        self._batches: Dict[str, BatchJob] = {}
        self._handlers: Dict[str, Callable] = {}
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
    
    def register_handler(self, item_type: str, handler: Callable) -> None:
        """注册批量项处理器"""
        self._handlers[item_type] = handler
        logger.info(f"Registered batch handler for type: {item_type}")
    
    async def create_batch(
        self,
        name: str,
        items: List[Dict[str, Any]],
        concurrency: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> BatchJob:
        """
        创建批量任务
        
        Args:
            name: 批量任务名称
            items: 批量项列表
            concurrency: 并发数
            metadata: 元数据
            
        Returns:
            创建的批量任务对象
        """
        batch_id = str(uuid.uuid4())
        
        batch_items = [
            BatchItem(
                item_id=f"{batch_id}_{i}",
                payload=item
            )
            for i, item in enumerate(items)
        ]
        
        batch = BatchJob(
            batch_id=batch_id,
            name=name,
            items=batch_items,
            concurrency=concurrency,
            metadata=metadata or {}
        )
        
        self._batches[batch_id] = batch
        self._semaphores[batch_id] = asyncio.Semaphore(concurrency)
        
        if self.storage:
            await self.storage.save_batch(batch)
        
        logger.info(f"Created batch: {batch_id} with {len(items)} items")
        return batch
    
    async def get_batch(self, batch_id: str) -> Optional[BatchJob]:
        """获取批量任务"""
        if batch_id in self._batches:
            return self._batches[batch_id]
        
        if self.storage:
            batch = await self.storage.get_batch(batch_id)
            if batch:
                self._batches[batch_id] = batch
            return batch
        
        return None
    
    async def execute_batch(
        self,
        batch_id: str,
        handler: Optional[Callable] = None,
        stop_on_failure: bool = False
    ) -> Dict[str, Any]:
        """
        执行批量任务
        
        Args:
            batch_id: 批量任务ID
            handler: 处理函数（可选，覆盖注册的处理器）
            stop_on_failure: 是否在第一个失败时停止
            
        Returns:
            执行结果
        """
        batch = await self.get_batch(batch_id)
        if not batch:
            raise ValueError(f"Batch not found: {batch_id}")
        
        if batch.state == BatchState.RUNNING:
            raise ValueError(f"Batch already running: {batch_id}")
        
        batch.state = BatchState.RUNNING
        batch.started_at = datetime.now()
        
        semaphore = self._semaphores.get(batch_id, asyncio.Semaphore(batch.concurrency))
        
        logger.info(f"Starting batch execution: {batch_id}")
        
        async def execute_item(item: BatchItem) -> None:
            """执行单个项"""
            async with semaphore:
                item.state = "running"
                item.started_at = datetime.now()
                
                try:
                    # 获取处理器
                    item_handler = handler
                    if not item_handler:
                        item_type = item.payload.get("_type", "default")
                        item_handler = self._handlers.get(item_type)
                    
                    if not item_handler:
                        raise ValueError(f"No handler for item type: {item.payload.get('_type', 'default')}")
                    
                    result = await item_handler(item.payload)
                    item.result = result
                    item.state = "completed"
                    item.completed_at = datetime.now()
                    
                except Exception as e:
                    item.error = str(e)
                    item.state = "failed"
                    item.completed_at = datetime.now()
                    logger.error(f"Batch item failed: {item.item_id} - {e}")
                    
                    if stop_on_failure:
                        raise
        
        # 并行执行所有项
        try:
            tasks = [execute_item(item) for item in batch.items]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # 更新批量状态
            summary = batch.get_summary()
            
            if summary["failed"] == 0:
                batch.state = BatchState.COMPLETED
            elif summary["completed"] > 0:
                batch.state = BatchState.PARTIALLY_COMPLETED
            else:
                batch.state = BatchState.FAILED
            
            batch.completed_at = datetime.now()
            
            if self.storage:
                await self.storage.save_batch(batch)
            
            logger.info(f"Batch completed: {batch_id} - {batch.state.value}")
            
            return {
                "batch_id": batch_id,
                "state": batch.state.value,
                "summary": summary
            }
            
        except Exception as e:
            batch.state = BatchState.FAILED
            batch.completed_at = datetime.now()
            
            if self.storage:
                await self.storage.save_batch(batch)
            
            logger.error(f"Batch failed: {batch_id} - {e}")
            raise
    
    async def cancel_batch(self, batch_id: str) -> bool:
        """取消批量任务"""
        batch = await self.get_batch(batch_id)
        if not batch:
            return False
        
        if batch.state not in [BatchState.PENDING, BatchState.RUNNING]:
            return False
        
        batch.state = BatchState.CANCELLED
        batch.completed_at = datetime.now()
        
        if self.storage:
            await self.storage.save_batch(batch)
        
        logger.info(f"Batch cancelled: {batch_id}")
        return True
    
    async def retry_failed_items(
        self,
        batch_id: str,
        handler: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """重试失败的项"""
        batch = await self.get_batch(batch_id)
        if not batch:
            raise ValueError(f"Batch not found: {batch_id}")
        
        failed_items = [item for item in batch.items if item.state == "failed"]
        
        if not failed_items:
            return {
                "batch_id": batch_id,
                "retried": 0,
                "message": "No failed items to retry"
            }
        
        # 重置失败项状态
        for item in failed_items:
            item.state = "pending"
            item.error = None
            item.result = None
        
        # 重新执行
        batch.state = BatchState.RUNNING
        result = await self.execute_batch(batch_id, handler)
        
        return {
            "batch_id": batch_id,
            "retried": len(failed_items),
            "result": result
        }
    
    async def get_batch_progress(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """获取批量任务进度"""
        batch = await self.get_batch(batch_id)
        if not batch:
            return None
        
        summary = batch.get_summary()
        
        elapsed = None
        if batch.started_at:
            end_time = batch.completed_at or datetime.now()
            elapsed = (end_time - batch.started_at).total_seconds()
        
        eta = None
        if summary["running"] > 0 and elapsed and summary["completed"] > 0:
            avg_time = elapsed / summary["completed"]
            remaining = summary["pending"] + summary["running"]
            eta = remaining * avg_time
        
        return {
            "batch_id": batch_id,
            "name": batch.name,
            "state": batch.state.value,
            "summary": summary,
            "elapsed_seconds": elapsed,
            "eta_seconds": eta
        }
    
    async def list_batches(
        self,
        state: Optional[BatchState] = None,
        limit: int = 100
    ) -> List[BatchJob]:
        """列出批量任务"""
        batches = list(self._batches.values())
        
        if state:
            batches = [b for b in batches if b.state == state]
        
        batches.sort(key=lambda b: b.created_at, reverse=True)
        
        return batches[:limit]
