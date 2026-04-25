"""任务优先级队列 - V1.0.0"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import heapq

@dataclass(order=True)
class Task:
    """任务"""
    priority: int
    task_id: str = field(compare=False)
    task_type: str = field(compare=False)
    payload: Any = field(compare=False)
    created_at: datetime = field(default_factory=datetime.now, compare=False)

class PriorityQueue:
    """任务优先级队列"""
    
    PRIORITY_MAP = {
        "urgent": 0,
        "high": 1,
        "normal": 2,
        "low": 3,
        "background": 4
    }
    
    def __init__(self):
        self.queue: List[Task] = []
        self.task_count = 0
        self.completed_count = 0
    
    def add(self, task_id: str, task_type: str, payload: Any, priority: str = "normal") -> str:
        """添加任务"""
        priority_value = self.PRIORITY_MAP.get(priority, 2)
        task = Task(
            priority=priority_value,
            task_id=task_id,
            task_type=task_type,
            payload=payload
        )
        heapq.heappush(self.queue, task)
        self.task_count += 1
        return task_id
    
    def get_next(self) -> Optional[Task]:
        """获取下一个任务"""
        if not self.queue:
            return None
        task = heapq.heappop(self.queue)
        self.completed_count += 1
        return task
    
    def peek(self) -> Optional[Task]:
        """查看下一个任务"""
        if not self.queue:
            return None
        return self.queue[0]
    
    def get_by_type(self, task_type: str) -> List[Task]:
        """按类型获取任务"""
        return [t for t in self.queue if t.task_type == task_type]
    
    def clear(self):
        """清空队列"""
        self.queue.clear()
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "queue_size": len(self.queue),
            "total_tasks": self.task_count,
            "completed_tasks": self.completed_count,
            "pending_by_priority": {
                priority: len([t for t in self.queue if t.priority == value])
                for priority, value in self.PRIORITY_MAP.items()
            }
        }
