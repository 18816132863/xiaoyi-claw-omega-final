"""并行处理器 - V1.0.0"""

from typing import Dict, List, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class ParallelProcessor:
    """并行处理器 - 多任务并行执行"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_stats = {"total": 0, "success": 0, "failed": 0}
    
    def execute_parallel(self, tasks: List[Dict[str, Any]]) -> List[Any]:
        """并行执行任务"""
        futures = []
        results = []
        
        for task in tasks:
            func = task.get("func")
            args = task.get("args", ())
            kwargs = task.get("kwargs", {})
            
            future = self.executor.submit(func, *args, **kwargs)
            futures.append((future, task.get("name", "unknown")))
        
        for future, name in futures:
            self.task_stats["total"] += 1
            try:
                result = future.result(timeout=30)
                results.append({"name": name, "result": result, "status": "success"})
                self.task_stats["success"] += 1
            except Exception as e:
                results.append({"name": name, "error": str(e), "status": "failed"})
                self.task_stats["failed"] += 1
        
        return results
    
    def map_parallel(self, func: Callable, items: List[Any]) -> List[Any]:
        """并行映射"""
        return list(self.executor.map(func, items))
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "max_workers": self.max_workers,
            **self.task_stats,
            "success_rate": self.task_stats["success"] / max(1, self.task_stats["total"])
        }
    
    def shutdown(self):
        """关闭执行器"""
        self.executor.shutdown(wait=True)
