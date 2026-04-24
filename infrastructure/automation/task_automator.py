#!/usr/bin/env python3
"""
任务自动化器 - V1.0.0

自动执行重复性任务和批处理操作。
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import threading
import queue


class AutomatorTaskStatus(Enum):
    """自动化器任务状态（与 domain.tasks.specs.TaskStatus 不同）"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    BACKGROUND = 4


@dataclass
class AutomatedTask:
    """自动化任务"""
    id: str
    name: str
    action: Callable
    params: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.MEDIUM
    status: AutomatorTaskStatus = AutomatorTaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    dependencies: List[str] = field(default_factory=list)


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    duration_ms: int = 0


class TaskAutomator:
    """任务自动化器"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.tasks: Dict[str, AutomatedTask] = {}
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.results: Dict[str, TaskResult] = {}
        self.workers: List[threading.Thread] = []
        self.running = False
        self.task_counter = 0
        self._lock = threading.Lock()
    
    def start(self):
        """启动自动化器"""
        if self.running:
            return
        
        self.running = True
        
        # 启动工作线程
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """停止自动化器"""
        self.running = False
    
    def _worker(self):
        """工作线程"""
        while self.running:
            try:
                # 获取任务
                priority, task_id = self.task_queue.get(timeout=1)
                task = self.tasks.get(task_id)
                
                if not task or task.status == AutomatorTaskStatus.CANCELLED:
                    continue
                
                # 执行任务
                self._execute_task(task)
                
            except queue.Empty:
                continue
            except Exception as e:
                continue
    
    def _execute_task(self, task: AutomatedTask):
        """执行任务"""
        task.status = AutomatorTaskStatus.RUNNING
        task.started_at = datetime.now()
        
        start_time = datetime.now()
        
        try:
            # 执行动作
            result = task.action(**task.params)
            
            task.result = result
            task.status = AutomatorTaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            # 记录结果
            duration = (task.completed_at - start_time).total_seconds() * 1000
            self.results[task.id] = TaskResult(
                task_id=task.id,
                success=True,
                result=result,
                duration_ms=int(duration)
            )
            
        except Exception as e:
            task.error = str(e)
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                # 重试
                task.status = AutomatorTaskStatus.PENDING
                self.task_queue.put((task.priority.value, task.id))
            else:
                # 失败
                task.status = AutomatorTaskStatus.FAILED
                task.completed_at = datetime.now()
                
                self.results[task.id] = TaskResult(
                    task_id=task.id,
                    success=False,
                    result=None,
                    error=str(e)
                )
    
    def submit(self,
               name: str,
               action: Callable,
               params: Dict = None,
               priority: TaskPriority = TaskPriority.MEDIUM,
               dependencies: List[str] = None) -> str:
        """
        提交任务
        
        Args:
            name: 任务名称
            action: 执行函数
            params: 参数
            priority: 优先级
            dependencies: 依赖任务ID
        
        Returns:
            任务ID
        """
        with self._lock:
            task_id = f"task_{self.task_counter}"
            self.task_counter += 1
        
        task = AutomatedTask(
            id=task_id,
            name=name,
            action=action,
            params=params or {},
            priority=priority,
            dependencies=dependencies or []
        )
        
        self.tasks[task_id] = task
        
        # 检查依赖
        if self._check_dependencies(task):
            task.status = AutomatorTaskStatus.QUEUED
            self.task_queue.put((priority.value, task_id))
        
        return task_id
    
    def _check_dependencies(self, task: AutomatedTask) -> bool:
        """检查依赖是否完成"""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != AutomatorTaskStatus.COMPLETED:
                return False
        return True
    
    def cancel(self, task_id: str) -> bool:
        """取消任务"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task.status in [AutomatorTaskStatus.PENDING, AutomatorTaskStatus.QUEUED]:
            task.status = AutomatorTaskStatus.CANCELLED
            return True
        
        return False
    
    def get_status(self, task_id: str) -> Optional[AutomatorTaskStatus]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        return task.status if task else None
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """获取任务结果"""
        return self.results.get(task_id)
    
    def batch_submit(self, tasks: List[Dict]) -> List[str]:
        """批量提交任务"""
        task_ids = []
        
        for t in tasks:
            task_id = self.submit(
                name=t.get("name", "unnamed"),
                action=t.get("action", lambda: None),
                params=t.get("params", {}),
                priority=t.get("priority", TaskPriority.MEDIUM),
                dependencies=t.get("dependencies", [])
            )
            task_ids.append(task_id)
        
        return task_ids
    
    def wait_for_completion(self, task_ids: List[str], timeout: float = None) -> Dict[str, TaskResult]:
        """等待任务完成"""
        results = {}
        start_time = datetime.now()
        
        while True:
            all_done = True
            
            for task_id in task_ids:
                if task_id in self.results:
                    results[task_id] = self.results[task_id]
                else:
                    task = self.tasks.get(task_id)
                    if task and task.status not in [AutomatorTaskStatus.COMPLETED, AutomatorTaskStatus.FAILED, AutomatorTaskStatus.CANCELLED]:
                        all_done = False
            
            if all_done:
                break
            
            if timeout:
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed >= timeout:
                    break
            
            import time
            time.sleep(0.1)
        
        return results
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = sum(
                1 for t in self.tasks.values() if t.status == status
            )
        
        return {
            "total_tasks": len(self.tasks),
            "queue_size": self.task_queue.qsize(),
            "completed": status_counts.get("completed", 0),
            "failed": status_counts.get("failed", 0),
            "running": status_counts.get("running", 0),
            "pending": status_counts.get("pending", 0),
            "success_rate": (
                status_counts.get("completed", 0) / len(self.tasks)
                if self.tasks else 0
            )
        }


# 全局任务自动化器
_task_automator: Optional[TaskAutomator] = None


def get_task_automator() -> TaskAutomator:
    """获取全局任务自动化器"""
    global _task_automator
    if _task_automator is None:
        _task_automator = TaskAutomator()
        _task_automator.start()
    return _task_automator
