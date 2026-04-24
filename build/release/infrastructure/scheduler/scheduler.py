"""
任务调度器 V1.0.0

职责：
- 扫描待执行的定时任务
- 将到期任务投递到执行队列
- 支持单次/延迟/Cron/周期调度
"""

import asyncio
import signal
from typing import Optional, Callable, Awaitable
from datetime import datetime, timedelta
from pathlib import Path
import json

from domain.tasks import TaskSpec, TaskStatus, TriggerMode
from infrastructure.storage.repositories import SQLiteTaskRepository


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent.parent


class TaskScheduler:
    """任务调度器"""
    
    def __init__(
        self,
        task_repo: Optional[SQLiteTaskRepository] = None,
        dispatch_callback: Optional[Callable[[str], Awaitable[None]]] = None,
        check_interval: float = 1.0
    ):
        self.task_repo = task_repo or SQLiteTaskRepository()
        self.dispatch_callback = dispatch_callback
        self.check_interval = check_interval
        self.running = False
        self.root = get_project_root()
        
        # 注册信号处理
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        """处理终止信号"""
        print(f"\n[Scheduler] 收到信号 {signum}，正在停止...")
        self.stop()
    
    def start(self):
        """启动调度器"""
        print("=" * 60)
        print("  任务调度器 V1.0.0")
        print("=" * 60)
        print(f"  检查间隔: {self.check_interval} 秒")
        print(f"  启动时间: {datetime.now().isoformat()}")
        print("=" * 60)
        print("  按 Ctrl+C 停止")
        print("=" * 60)
        print()
        
        self.running = True
        asyncio.run(self._run_loop())
    
    def stop(self):
        """停止调度器"""
        self.running = False
    
    async def _run_loop(self):
        """运行循环"""
        while self.running:
            try:
                await self._check_and_dispatch()
            except Exception as e:
                print(f"[Scheduler] 错误: {e}")
            
            await asyncio.sleep(self.check_interval)
        
        print("[Scheduler] 已停止")
    
    async def _check_and_dispatch(self):
        """检查并投递到期任务"""
        now = datetime.now()
        
        # 查询待执行的定时任务
        tasks = await self.task_repo.list_pending_scheduled(now, limit=100)
        
        if not tasks:
            return
        
        for task in tasks:
            try:
                # 获取锁
                locked = await self.task_repo.acquire_lock(task.task_id, lock_ttl=60)
                if not locked:
                    print(f"[Scheduler] 任务 {task.task_id} 已被锁定，跳过")
                    continue
                
                try:
                    # 更新状态为已入队
                    await self.task_repo.update(task.task_id, {
                        "status": TaskStatus.QUEUED.value
                    })
                    
                    print(f"[Scheduler] 投递任务: {task.task_id} ({task.task_type})")
                    
                    # 调用投递回调
                    if self.dispatch_callback:
                        await self.dispatch_callback(task.task_id)
                    else:
                        # 默认：写入队列文件
                        await self._write_to_queue(task)
                
                finally:
                    # 释放锁
                    await self.task_repo.release_lock(task.task_id)
            
            except Exception as e:
                print(f"[Scheduler] 投递任务 {task.task_id} 失败: {e}")
    
    async def _write_to_queue(self, task: TaskSpec):
        """写入执行队列"""
        queue_file = self.root / "data" / "task_queue.jsonl"
        queue_file.parent.mkdir(parents=True, exist_ok=True)
        
        entry = {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "queued_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        with open(queue_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')


class SimpleScheduler:
    """简单调度器（用于测试）"""
    
    def __init__(self, check_interval: float = 1.0):
        self.check_interval = check_interval
        self.running = False
        self.root = get_project_root()
        self.task_repo = SQLiteTaskRepository()
    
    def start(self):
        """启动调度器"""
        print("[SimpleScheduler] 启动...")
        self.running = True
        
        import time
        while self.running:
            try:
                self._check()
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                print(f"[SimpleScheduler] 错误: {e}")
            
            time.sleep(self.check_interval)
        
        print("[SimpleScheduler] 已停止")
    
    def stop(self):
        """停止调度器"""
        self.running = False
    
    def _check(self):
        """检查到期任务"""
        import asyncio
        
        # 使用 asyncio 运行异步方法
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            tasks = loop.run_until_complete(
                self.task_repo.list_pending_scheduled(datetime.now(), limit=10)
            )
            
            for task in tasks:
                print(f"[SimpleScheduler] 发现到期任务: {task.task_id}")
                
                # 更新状态
                loop.run_until_complete(
                    self.task_repo.update(task.task_id, {"status": TaskStatus.QUEUED.value})
                )
                
                # 写入队列
                self._write_to_queue_sync(task)
        
        finally:
            loop.close()
    
    def _write_to_queue_sync(self, task: TaskSpec):
        """同步写入队列"""
        queue_file = self.root / "data" / "task_queue.jsonl"
        queue_file.parent.mkdir(parents=True, exist_ok=True)
        
        entry = {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "queued_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        with open(queue_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        print(f"[SimpleScheduler] 任务已入队: {task.task_id}")


if __name__ == "__main__":
    scheduler = SimpleScheduler(check_interval=1.0)
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.stop()
