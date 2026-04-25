#!/usr/bin/env python3
"""
优先级队列 - V1.0.0

管理任务的优先级和执行顺序。
"""

import heapq
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Priority(Enum):
    """优先级"""
    CRITICAL = 0  # 最高优先级
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    BACKGROUND = 4  # 最低优先级


@dataclass(order=True)
class Task:
    """任务"""
    priority: int
    created_at: datetime = field(compare=True)
    id: str = field(compare=False)
    name: str = field(compare=False)
    action: str = field(compare=False)
    params: Dict = field(compare=False, default_factory=dict)
    deadline: Optional[datetime] = field(compare=False, default=None)
    retries: int = field(compare=False, default=0)
    max_retries: int = field(compare=False, default=3)


class PriorityQueue:
    """优先级队列"""
    
    def __init__(self):
        self._queue: List[Task] = []
        self._task_map: Dict[str, Task] = {}
        self._counter = 0
    
    def push(self, 
             id: str,
             name: str,
             action: str,
             params: Dict = None,
             priority: Priority = Priority.MEDIUM,
             deadline: datetime = None) -> Task:
        """添加任务"""
        task = Task(
            priority=priority.value,
            created_at=datetime.now(),
            id=id,
            name=name,
            action=action,
            params=params or {},
            deadline=deadline
        )
        
        heapq.heappush(self._queue, task)
        self._task_map[id] = task
        return task
    
    def pop(self) -> Optional[Task]:
        """取出最高优先级任务"""
        if not self._queue:
            return None
        
        task = heapq.heappop(self._queue)
        del self._task_map[task.id]
        return task
    
    def peek(self) -> Optional[Task]:
        """查看最高优先级任务"""
        if not self._queue:
            return None
        return self._queue[0]
    
    def remove(self, task_id: str) -> bool:
        """移除任务"""
        if task_id not in self._task_map:
            return False
        
        task = self._task_map[task_id]
        self._queue.remove(task)
        heapq.heapify(self._queue)
        del self._task_map[task_id]
        return True
    
    def update_priority(self, task_id: str, priority: Priority) -> bool:
        """更新任务优先级"""
        if task_id not in self._task_map:
            return False
        
        task = self._task_map[task_id]
        self.remove(task_id)
        task.priority = priority.value
        heapq.heappush(self._queue, task)
        self._task_map[task_id] = task
        return True
    
    def get_by_id(self, task_id: str) -> Optional[Task]:
        """根据ID获取任务"""
        return self._task_map.get(task_id)
    
    def get_all(self) -> List[Task]:
        """获取所有任务"""
        return sorted(self._queue)
    
    def get_by_priority(self, priority: Priority) -> List[Task]:
        """获取指定优先级的任务"""
        return [t for t in self._queue if t.priority == priority.value]
    
    def get_overdue(self) -> List[Task]:
        """获取过期任务"""
        now = datetime.now()
        return [t for t in self._queue if t.deadline and t.deadline < now]
    
    def size(self) -> int:
        """队列大小"""
        return len(self._queue)
    
    def is_empty(self) -> bool:
        """是否为空"""
        return len(self._queue) == 0
    
    def clear(self):
        """清空队列"""
        self._queue.clear()
        self._task_map.clear()


# 全局优先级队列
_priority_queue: Optional[PriorityQueue] = None


def get_priority_queue() -> PriorityQueue:
    """获取全局优先级队列"""
    global _priority_queue
    if _priority_queue is None:
        _priority_queue = PriorityQueue()
    return _priority_queue
