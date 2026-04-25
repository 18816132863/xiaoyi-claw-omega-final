# application/task_service/scheduler.py
"""
调度服务 V1.0.0

职责：
- 扫描到期任务
- 投递任务到队列
- 管理调度状态
"""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from domain.tasks import TaskStatus, TriggerMode
from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository


class SchedulerService:
    """调度服务"""
    
    def __init__(self, task_repo: Optional[SQLiteTaskRepository] = None):
        self.task_repo = task_repo or SQLiteTaskRepository()
        self.root = Path(__file__).resolve().parent.parent.parent
    
    async def scan_and_dispatch(self) -> Dict[str, Any]:
        """扫描到期任务并投递"""
        now = datetime.now()
        
        # 查询待执行的定时任务
        tasks = await self.task_repo.list_pending_scheduled(now, limit=100)
        
        dispatched = 0
        errors = []
        
        for task in tasks:
            try:
                # 获取锁
                locked = await self.task_repo.acquire_lock(task.task_id, lock_ttl=60)
                if not locked:
                    continue
                
                try:
                    # 更新状态为已入队
                    await self.task_repo.update(task.task_id, {
                        "status": TaskStatus.QUEUED.value
                    })
                    
                    # 写入执行队列
                    await self._write_to_queue(task.task_id)
                    
                    dispatched += 1
                
                finally:
                    await self.task_repo.release_lock(task.task_id)
            
            except Exception as e:
                errors.append({
                    "task_id": task.task_id,
                    "error": str(e)
                })
        
        return {
            "scanned": len(tasks),
            "dispatched": dispatched,
            "errors": errors
        }
    
    async def _write_to_queue(self, task_id: str):
        """写入执行队列"""
        import json
        
        queue_file = self.root / "data" / "task_queue.jsonl"
        queue_file.parent.mkdir(parents=True, exist_ok=True)
        
        entry = {
            "task_id": task_id,
            "queued_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        with open(queue_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    async def get_pending_count(self) -> int:
        """获取待执行任务数量"""
        queue_file = self.root / "data" / "task_queue.jsonl"
        
        if not queue_file.exists():
            return 0
        
        import json
        count = 0
        with open(queue_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("status") == "pending":
                        count += 1
                except:
                    pass
        
        return count
