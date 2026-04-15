#!/usr/bin/env python3
"""
执行器池 - V1.0.0

管理并发执行任务。
"""

import concurrent.futures
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import threading


class ExecutorStatus(Enum):
    """执行器状态"""
    IDLE = "idle"
    BUSY = "busy"
    FULL = "full"


@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    result: Any
    error: Optional[str] = None
    duration_ms: int = 0


class ExecutorPool:
    """执行器池"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self._futures: Dict[str, concurrent.futures.Future] = {}
        self._lock = threading.Lock()
        self._active_count = 0
    
    @property
    def status(self) -> ExecutorStatus:
        """获取执行器状态"""
        with self._lock:
            if self._active_count == 0:
                return ExecutorStatus.IDLE
            elif self._active_count < self.max_workers:
                return ExecutorStatus.BUSY
            else:
                return ExecutorStatus.FULL
    
    @property
    def available_slots(self) -> int:
        """获取可用槽位"""
        with self._lock:
            return self.max_workers - self._active_count
    
    def submit(self, 
               task_id: str,
               func: Callable,
               *args,
               **kwargs) -> str:
        """提交任务"""
        with self._lock:
            if self._active_count >= self.max_workers:
                raise RuntimeError("执行器池已满")
            
            def wrapper():
                self._active_count += 1
                try:
                    return func(*args, **kwargs)
                finally:
                    with self._lock:
                        self._active_count -= 1
            
            future = self._executor.submit(wrapper)
            self._futures[task_id] = future
            return task_id
    
    def get_result(self, task_id: str, timeout: float = None) -> Optional[ExecutionResult]:
        """获取任务结果"""
        future = self._futures.get(task_id)
        if not future:
            return None
        
        try:
            result = future.result(timeout=timeout)
            return ExecutionResult(success=True, result=result)
        except Exception as e:
            return ExecutionResult(success=False, result=None, error=str(e))
        finally:
            del self._futures[task_id]
    
    def cancel(self, task_id: str) -> bool:
        """取消任务"""
        future = self._futures.get(task_id)
        if future:
            cancelled = future.cancel()
            if cancelled:
                del self._futures[task_id]
            return cancelled
        return False
    
    def wait_all(self, timeout: float = None) -> Dict[str, ExecutionResult]:
        """等待所有任务完成"""
        results = {}
        for task_id, future in list(self._futures.items()):
            try:
                result = future.result(timeout=timeout)
                results[task_id] = ExecutionResult(success=True, result=result)
            except Exception as e:
                results[task_id] = ExecutionResult(success=False, result=None, error=str(e))
        
        self._futures.clear()
        return results
    
    def shutdown(self, wait: bool = True):
        """关闭执行器"""
        self._executor.shutdown(wait=wait)
        self._futures.clear()


# 全局执行器池
_executor_pool: Optional[ExecutorPool] = None


def get_executor_pool() -> ExecutorPool:
    """获取全局执行器池"""
    global _executor_pool
    if _executor_pool is None:
        _executor_pool = ExecutorPool()
    return _executor_pool
