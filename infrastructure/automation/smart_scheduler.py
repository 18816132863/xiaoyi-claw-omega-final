#!/usr/bin/env python3
"""
智能调度器 - V1.0.0

智能调度任务执行，支持优先级、依赖和资源管理。
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import heapq


class ScheduleType(Enum):
    """调度类型"""
    ONCE = "once"           # 一次性
    RECURRING = "recurring"  # 周期性
    CRON = "cron"           # Cron表达式
    DEPENDENT = "dependent"  # 依赖触发


class ScheduleStatus(Enum):
    """调度状态"""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class ScheduledTask:
    """调度任务"""
    id: str
    name: str
    action: Callable
    schedule_type: ScheduleType
    next_run: datetime
    interval: Optional[timedelta] = None
    cron_expr: Optional[str] = None
    priority: int = 0
    status: ScheduleStatus = ScheduleStatus.SCHEDULED
    dependencies: List[str] = field(default_factory=list)
    resource_requirements: Dict[str, float] = field(default_factory=dict)
    last_run: Optional[datetime] = None
    last_result: Optional[Any] = None
    run_count: int = 0
    error_count: int = 0
    max_errors: int = 3


@dataclass
class Resource:
    """资源"""
    name: str
    capacity: float
    used: float = 0
    
    @property
    def available(self) -> float:
        return self.capacity - self.used


class SmartScheduler:
    """智能调度器"""
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.resources: Dict[str, Resource] = {}
        self.schedule_queue: List[tuple] = []  # (next_run, priority, task_id)
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.task_counter = 0
        self._lock = threading.Lock()
        
        # 初始化默认资源
        self._init_default_resources()
    
    def _init_default_resources(self):
        """初始化默认资源"""
        self.resources["cpu"] = Resource(name="cpu", capacity=100)
        self.resources["memory"] = Resource(name="memory", capacity=100)
        self.resources["io"] = Resource(name="io", capacity=100)
    
    def start(self):
        """启动调度器"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
    
    def _scheduler_loop(self):
        """调度循环"""
        while self.running:
            try:
                self._check_and_execute()
                import time
                time.sleep(1)
            except Exception as e:
                continue
    
    def _check_and_execute(self):
        """检查并执行到期任务"""
        now = datetime.now()
        
        with self._lock:
            # 检查队列
            while self.schedule_queue and self.schedule_queue[0][0] <= now:
                _, _, task_id = heapq.heappop(self.schedule_queue)
                task = self.tasks.get(task_id)
                
                if not task or task.status != ScheduleStatus.SCHEDULED:
                    continue
                
                # 检查依赖
                if not self._check_dependencies(task):
                    # 重新入队
                    task.next_run = now + timedelta(seconds=5)
                    heapq.heappush(self.schedule_queue, (task.next_run, task.priority, task_id))
                    continue
                
                # 检查资源
                if not self._check_resources(task):
                    # 重新入队
                    task.next_run = now + timedelta(seconds=10)
                    heapq.heappush(self.schedule_queue, (task.next_run, task.priority, task_id))
                    continue
                
                # 执行任务
                self._execute_task(task)
    
    def _check_dependencies(self, task: ScheduledTask) -> bool:
        """检查依赖"""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != ScheduleStatus.COMPLETED:
                return False
        return True
    
    def _check_resources(self, task: ScheduledTask) -> bool:
        """检查资源"""
        for resource_name, required in task.resource_requirements.items():
            resource = self.resources.get(resource_name)
            if not resource or resource.available < required:
                return False
        return True
    
    def _allocate_resources(self, task: ScheduledTask):
        """分配资源"""
        for resource_name, required in task.resource_requirements.items():
            resource = self.resources.get(resource_name)
            if resource:
                resource.used += required
    
    def _release_resources(self, task: ScheduledTask):
        """释放资源"""
        for resource_name, required in task.resource_requirements.items():
            resource = self.resources.get(resource_name)
            if resource:
                resource.used = max(0, resource.used - required)
    
    def _execute_task(self, task: ScheduledTask):
        """执行任务"""
        task.status = ScheduleStatus.RUNNING
        task.last_run = datetime.now()
        
        self._allocate_resources(task)
        
        try:
            result = task.action()
            task.last_result = result
            task.status = ScheduleStatus.COMPLETED
            task.run_count += 1
            
        except Exception as e:
            task.last_result = str(e)
            task.error_count += 1
            
            if task.error_count >= task.max_errors:
                task.status = ScheduleStatus.FAILED
            else:
                task.status = ScheduleStatus.SCHEDULED
        
        finally:
            self._release_resources(task)
        
        # 如果是周期性任务，重新调度
        if task.schedule_type == ScheduleType.RECURRING and task.interval:
            if task.status == ScheduleStatus.COMPLETED:
                task.status = ScheduleStatus.SCHEDULED
                task.next_run = datetime.now() + task.interval
                heapq.heappush(self.schedule_queue, (task.next_run, task.priority, task.id))
    
    def schedule(self,
                 name: str,
                 action: Callable,
                 schedule_type: ScheduleType = ScheduleType.ONCE,
                 start_time: datetime = None,
                 interval: timedelta = None,
                 cron_expr: str = None,
                 priority: int = 0,
                 dependencies: List[str] = None,
                 resources: Dict[str, float] = None) -> str:
        """
        调度任务
        
        Args:
            name: 任务名称
            action: 执行函数
            schedule_type: 调度类型
            start_time: 开始时间
            interval: 间隔（周期性任务）
            cron_expr: Cron表达式
            priority: 优先级
            dependencies: 依赖任务
            resources: 资源需求
        
        Returns:
            任务ID
        """
        with self._lock:
            task_id = f"sched_{self.task_counter}"
            self.task_counter += 1
        
        next_run = start_time or datetime.now()
        
        task = ScheduledTask(
            id=task_id,
            name=name,
            action=action,
            schedule_type=schedule_type,
            next_run=next_run,
            interval=interval,
            cron_expr=cron_expr,
            priority=priority,
            dependencies=dependencies or [],
            resource_requirements=resources or {}
        )
        
        self.tasks[task_id] = task
        heapq.heappush(self.schedule_queue, (next_run, priority, task_id))
        
        return task_id
    
    def cancel(self, task_id: str) -> bool:
        """取消任务"""
        task = self.tasks.get(task_id)
        if task and task.status == ScheduleStatus.SCHEDULED:
            task.status = ScheduleStatus.CANCELLED
            return True
        return False
    
    def pause(self, task_id: str) -> bool:
        """暂停任务"""
        task = self.tasks.get(task_id)
        if task:
            task.status = ScheduleStatus.PAUSED
            return True
        return False
    
    def resume(self, task_id: str) -> bool:
        """恢复任务"""
        task = self.tasks.get(task_id)
        if task and task.status == ScheduleStatus.PAUSED:
            task.status = ScheduleStatus.SCHEDULED
            heapq.heappush(self.schedule_queue, (task.next_run, task.priority, task_id))
            return True
        return False
    
    def get_upcoming(self, limit: int = 10) -> List[ScheduledTask]:
        """获取即将执行的任务"""
        now = datetime.now()
        upcoming = [
            t for t in self.tasks.values()
            if t.status == ScheduleStatus.SCHEDULED and t.next_run >= now
        ]
        upcoming.sort(key=lambda t: t.next_run)
        return upcoming[:limit]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        status_counts = {}
        for status in ScheduleStatus:
            status_counts[status.value] = sum(
                1 for t in self.tasks.values() if t.status == status
            )
        
        return {
            "total_tasks": len(self.tasks),
            "scheduled": status_counts.get("scheduled", 0),
            "running": status_counts.get("running", 0),
            "completed": status_counts.get("completed", 0),
            "failed": status_counts.get("failed", 0),
            "total_runs": sum(t.run_count for t in self.tasks.values()),
            "resource_usage": {
                name: {"used": r.used, "available": r.available}
                for name, r in self.resources.items()
            }
        }


# 全局智能调度器
_smart_scheduler: Optional[SmartScheduler] = None


def get_smart_scheduler() -> SmartScheduler:
    """获取全局智能调度器"""
    global _smart_scheduler
    if _smart_scheduler is None:
        _smart_scheduler = SmartScheduler()
        _smart_scheduler.start()
    return _smart_scheduler
