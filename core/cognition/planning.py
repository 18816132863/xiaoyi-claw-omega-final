#!/usr/bin/env python3
"""
规划引擎 - V1.0.0

提供任务分解、计划生成和执行监控能力。
"""

from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import re


class PlanStatus(Enum):
    """计划状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Task:
    """任务"""
    id: str
    name: str
    description: str
    dependencies: Set[str] = field(default_factory=set)
    estimated_duration: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    priority: int = 0
    status: TaskStatus = TaskStatus.PENDING
    assignee: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class Plan:
    """计划"""
    id: str
    name: str
    goal: str
    tasks: List[Task]
    status: PlanStatus = PlanStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None


class PlanningEngine:
    """规划引擎"""
    
    def __init__(self):
        self.plans: Dict[str, Plan] = {}
        self.task_counter = 0
    
    def create_plan(self, goal: str, context: Dict = None) -> Plan:
        """
        根据目标创建计划
        
        Args:
            goal: 目标描述
            context: 上下文信息
        
        Returns:
            生成的计划
        """
        # 分解目标
        sub_goals = self._decompose_goal(goal, context or {})
        
        # 为每个子目标创建任务
        tasks = []
        for i, sub_goal in enumerate(sub_goals):
            task = Task(
                id=f"task_{self.task_counter}",
                name=sub_goal.get("name", f"任务 {i+1}"),
                description=sub_goal.get("description", ""),
                dependencies=set(sub_goal.get("dependencies", [])),
                estimated_duration=timedelta(minutes=sub_goal.get("duration", 30)),
                priority=sub_goal.get("priority", 0)
            )
            tasks.append(task)
            self.task_counter += 1
        
        # 创建计划
        plan = Plan(
            id=f"plan_{len(self.plans)}",
            name=f"计划: {goal[:50]}",
            goal=goal,
            tasks=tasks
        )
        
        self.plans[plan.id] = plan
        return plan
    
    def _decompose_goal(self, goal: str, context: Dict) -> List[Dict]:
        """分解目标为子任务"""
        sub_goals = []
        
        # 识别关键动作
        actions = self._extract_actions(goal)
        
        # 识别约束条件
        constraints = self._extract_constraints(goal)
        
        # 生成子任务
        for i, action in enumerate(actions):
            sub_goal = {
                "name": action,
                "description": f"执行: {action}",
                "dependencies": [],
                "duration": 30,
                "priority": len(actions) - i  # 先执行的任务优先级高
            }
            sub_goals.append(sub_goal)
        
        # 添加依赖关系
        for i in range(1, len(sub_goals)):
            if self._should_depend(sub_goals[i-1], sub_goals[i]):
                sub_goals[i]["dependencies"].append(f"task_{self.task_counter - len(sub_goals) + i - 1}")
        
        return sub_goals
    
    def _extract_actions(self, goal: str) -> List[str]:
        """提取动作"""
        # 识别动词和宾语
        action_patterns = [
            r"(\w+并\w+)",
            r"(\w+后\w+)",
            r"首先(\w+)",
            r"然后(\w+)",
            r"最后(\w+)",
        ]
        
        actions = []
        for pattern in action_patterns:
            matches = re.findall(pattern, goal)
            actions.extend(matches)
        
        # 如果没有识别到，按句子分割
        if not actions:
            sentences = re.split(r'[，。；]', goal)
            actions = [s.strip() for s in sentences if s.strip()]
        
        return actions if actions else [goal]
    
    def _extract_constraints(self, goal: str) -> List[str]:
        """提取约束条件"""
        constraints = []
        
        # 时间约束
        time_patterns = [
            r"在(\w+)之前",
            r"(\w+)分钟内",
            r"(\w+)小时内",
        ]
        for pattern in time_patterns:
            matches = re.findall(pattern, goal)
            constraints.extend(matches)
        
        return constraints
    
    def _should_depend(self, task1: Dict, task2: Dict) -> bool:
        """判断任务2是否依赖任务1"""
        # 简化：顺序任务默认有依赖
        return True
    
    def get_ready_tasks(self, plan_id: str) -> List[Task]:
        """获取可执行的任务"""
        plan = self.plans.get(plan_id)
        if not plan:
            return []
        
        ready = []
        completed_ids = {t.id for t in plan.tasks if t.status == TaskStatus.COMPLETED}
        
        for task in plan.tasks:
            if task.status != TaskStatus.PENDING:
                continue
            
            # 检查依赖是否完成
            if task.dependencies.issubset(completed_ids):
                task.status = TaskStatus.READY
                ready.append(task)
        
        return ready
    
    def execute_task(self, plan_id: str, task_id: str, executor: callable = None) -> Any:
        """执行任务"""
        plan = self.plans.get(plan_id)
        if not plan:
            return None
        
        task = next((t for t in plan.tasks if t.id == task_id), None)
        if not task:
            return None
        
        task.status = TaskStatus.RUNNING
        
        try:
            if executor:
                result = executor(task)
            else:
                result = self._default_executor(task)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            return result
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            return None
    
    def _default_executor(self, task: Task) -> Any:
        """默认执行器"""
        return {"status": "completed", "task": task.name}
    
    def get_progress(self, plan_id: str) -> Dict:
        """获取计划进度"""
        plan = self.plans.get(plan_id)
        if not plan:
            return {}
        
        total = len(plan.tasks)
        completed = sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in plan.tasks if t.status == TaskStatus.FAILED)
        running = sum(1 for t in plan.tasks if t.status == TaskStatus.RUNNING)
        
        return {
            "plan_id": plan_id,
            "total_tasks": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "progress": completed / total if total > 0 else 0,
            "status": plan.status.value
        }
    
    def replan(self, plan_id: str, reason: str) -> Plan:
        """重新规划"""
        old_plan = self.plans.get(plan_id)
        if not old_plan:
            return None
        
        # 保留已完成的任务
        completed_tasks = [t for t in old_plan.tasks if t.status == TaskStatus.COMPLETED]
        
        # 重新分解剩余目标
        remaining_goal = f"继续完成: {old_plan.goal} (原因: {reason})"
        new_plan = self.create_plan(remaining_goal)
        
        # 合并任务
        new_plan.tasks = completed_tasks + new_plan.tasks
        
        return new_plan
    
    def estimate_completion(self, plan_id: str) -> datetime:
        """估算完成时间"""
        plan = self.plans.get(plan_id)
        if not plan:
            return datetime.now()
        
        remaining_duration = timedelta()
        for task in plan.tasks:
            if task.status not in [TaskStatus.COMPLETED]:
                remaining_duration += task.estimated_duration
        
        return datetime.now() + remaining_duration


# 全局规划引擎
_planning_engine: Optional[PlanningEngine] = None


def get_planning_engine() -> PlanningEngine:
    """获取全局规划引擎"""
    global _planning_engine
    if _planning_engine is None:
        _planning_engine = PlanningEngine()
    return _planning_engine
