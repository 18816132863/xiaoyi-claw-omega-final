#!/usr/bin/env python3
"""
异步调用队列
V2.7.0 - 2026-04-10
实现层间异步非阻塞调用
"""

import asyncio
import time
from typing import Any, Callable, Dict, Optional, Coroutine
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
from concurrent.futures import ThreadPoolExecutor

class Priority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3

@dataclass(order=True)
class TaskItem:
    """任务项"""
    priority: int
    task_id: int = field(compare=False)
    coroutine: Coroutine = field(compare=False)
    callback: Optional[Callable] = field(compare=False)
    created_at: float = field(default_factory=time.time, compare=False)

class AsyncCallQueue:
    """异步调用队列"""
    
    def __init__(self, max_workers: int = 4):
        self._queues: Dict[Priority, deque] = {
            Priority.CRITICAL: deque(),
            Priority.HIGH: deque(),
            Priority.NORMAL: deque(),
            Priority.LOW: deque()
        }
        self._results: Dict[int, Any] = {}
        self._task_id = 0
        self._running = False
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    def start(self):
        """启动队列处理"""
        if self._running:
            return
        
        self._running = True
        self._loop = asyncio.new_event_loop()
        
        # 启动处理协程
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._process_queues())
    
    def stop(self):
        """停止队列处理"""
        self._running = False
        if self._loop:
            self._loop.stop()
            self._loop.close()
            self._loop = None
    
    async def _process_queues(self):
        """处理队列"""
        while self._running:
            # 按优先级处理
            for priority in [Priority.CRITICAL, Priority.HIGH, Priority.NORMAL, Priority.LOW]:
                queue = self._queues[priority]
                if queue:
                    item = queue.popleft()
                    try:
                        result = await item.coroutine
                        self._results[item.task_id] = result
                        if item.callback:
                            item.callback(result)
                    except Exception as e:
                        self._results[item.task_id] = {"error": str(e)}
                    break
            else:
                # 所有队列都空，等待
                await asyncio.sleep(0.001)
    
    def submit(self, coroutine: Coroutine, priority: Priority = Priority.NORMAL,
               callback: Optional[Callable] = None) -> int:
        """提交异步任务"""
        self._task_id += 1
        item = TaskItem(
            priority=priority.value,
            task_id=self._task_id,
            coroutine=coroutine,
            callback=callback
        )
        self._queues[priority].append(item)
        return self._task_id
    
    def get_result(self, task_id: int, timeout: float = 5.0) -> Optional[Any]:
        """获取任务结果"""
        start = time.time()
        while time.time() - start < timeout:
            if task_id in self._results:
                return self._results.pop(task_id)
            time.sleep(0.001)
        return None
    
    def get_queue_stats(self) -> Dict:
        """获取队列统计"""
        return {
            priority.name: len(queue)
            for priority, queue in self._queues.items()
        }

# 全局单例
_async_queue: Optional[AsyncCallQueue] = None

def get_async_queue() -> AsyncCallQueue:
    """获取全局异步队列"""
    global _async_queue
    if _async_queue is None:
        _async_queue = AsyncCallQueue()
    return _async_queue

def async_call(coroutine: Coroutine, priority: Priority = Priority.NORMAL) -> int:
    """异步调用（便捷函数）"""
    return get_async_queue().submit(coroutine, priority)
