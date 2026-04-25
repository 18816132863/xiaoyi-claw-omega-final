#!/usr/bin/env python3
"""
战略目标引擎 - V2.8.1

能力：
- 年度目标、阶段目标、项目目标、任务目标的分层定义
- 目标之间的依赖关系与映射关系
- 目标与工作流、项目、资源、产物之间的绑定
- 目标偏离检测机制
- 目标变更后的影响分析机制
- 目标完成度与推进状态追踪
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from infrastructure.path_resolver import get_project_root

class GoalLevel(Enum):
    ANNUAL = "annual"           # 年度目标
    PHASE = "phase"             # 阶段目标
    PROJECT = "project"         # 项目目标
    TASK = "task"               # 任务目标

class GoalStatus(Enum):
    DRAFT = "draft"             # 草稿
    ACTIVE = "active"           # 激活
    IN_PROGRESS = "in_progress" # 进行中
    AT_RISK = "at_risk"         # 风险中
    BLOCKED = "blocked"         # 阻塞
    COMPLETED = "completed"     # 已完成
    CANCELLED = "cancelled"     # 已取消

class GoalPriority(Enum):
    CRITICAL = "critical"       # 关键
    HIGH = "high"               # 高
    MEDIUM = "medium"           # 中
    LOW = "low"                 # 低

@dataclass
class Goal:
    """目标"""
    goal_id: str
    name: str
    level: str
    status: str
    priority: str
    description: str
    parent_goal_id: Optional[str]   # 父目标
    child_goal_ids: List[str]       # 子目标
    dependencies: List[str]         # 依赖目标
    bound_workflows: List[str]      # 绑定工作流
    bound_projects: List[str]       # 绑定项目
    bound_resources: List[str]      # 绑定资源
    bound_products: List[str]       # 绑定产物
    metrics: Dict[str, Any]         # 衡量指标
    target_value: float             # 目标值
    current_value: float            # 当前值
    completion_rate: float          # 完成率
    start_date: str
    end_date: str
    owner: str
    created_at: str
    updated_at: str
    deviation_alerts: List[str]     # 偏离告警
    change_history: List[Dict]      # 变更历史

@dataclass
class GoalRelation:
    """目标关系"""
    source_goal_id: str
    target_goal_id: str
    relation_type: str              # depends_on / contributes_to / conflicts_with
    weight: float                   # 权重

class StrategicGoalEngine:
    """战略目标引擎"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.strategy_path = self.project_root / 'strategy'
        self.config_path = self.strategy_path / 'goals.json'
        
        # 目标
        self.goals: Dict[str, Goal] = {}
        
        # 目标关系
        self.relations: List[GoalRelation] = []
        
        self._load()
    
    def _load(self):
        """加载目标"""
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text(encoding='utf-8'))
            
            for gid, goal in data.get("goals", {}).items():
                self.goals[gid] = Goal(**goal)
            
            self.relations = [GoalRelation(**r) for r in data.get("relations", [])]
    
    def _save(self):
        """保存目标"""
        self.strategy_path.mkdir(parents=True, exist_ok=True)
        data = {
            "goals": {gid: asdict(g) for gid, g in self.goals.items()},
            "relations": [asdict(r) for r in self.relations],
            "updated": datetime.now().isoformat()
        }
        self.config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def _generate_goal_id(self, level: str) -> str:
        """生成目标ID"""
        prefix = {
            GoalLevel.ANNUAL.value: "goal_annual",
            GoalLevel.PHASE.value: "goal_phase",
            GoalLevel.PROJECT.value: "goal_proj",
            GoalLevel.TASK.value: "goal_task"
        }
        return f"{prefix.get(level, 'goal')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # === 目标管理 ===
    def create_goal(self, name: str, level: str, description: str,
                    priority: str = "medium", parent_goal_id: str = None,
                    target_value: float = 100.0, start_date: str = None,
                    end_date: str = None, owner: str = "") -> Goal:
        """创建目标"""
        goal_id = self._generate_goal_id(level)
        
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        
        goal = Goal(
            goal_id=goal_id,
            name=name,
            level=level,
            status=GoalStatus.DRAFT.value,
            priority=priority,
            description=description,
            parent_goal_id=parent_goal_id,
            child_goal_ids=[],
            dependencies=[],
            bound_workflows=[],
            bound_projects=[],
            bound_resources=[],
            bound_products=[],
            metrics={},
            target_value=target_value,
            current_value=0.0,
            completion_rate=0.0,
            start_date=start_date,
            end_date=end_date,
            owner=owner,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            deviation_alerts=[],
            change_history=[]
        )
        
        self.goals[goal_id] = goal
        
        # 更新父目标的子目标列表
        if parent_goal_id and parent_goal_id in self.goals:
            self.goals[parent_goal_id].child_goal_ids.append(goal_id)
        
        self._save()
        
        return goal
    
    def activate_goal(self, goal_id: str) -> Dict:
        """激活目标"""
        if goal_id not in self.goals:
            return {"error": "目标不存在"}
        
        goal = self.goals[goal_id]
        goal.status = GoalStatus.ACTIVE.value
        goal.updated_at = datetime.now().isoformat()
        self._save()
        
        return {"status": "activated", "goal_id": goal_id}
    
    def update_progress(self, goal_id: str, current_value: float) -> Dict:
        """更新进度"""
        if goal_id not in self.goals:
            return {"error": "目标不存在"}
        
        goal = self.goals[goal_id]
        old_value = goal.current_value
        goal.current_value = current_value
        
        # 计算完成率
        if goal.target_value > 0:
            goal.completion_rate = min(100.0, (current_value / goal.target_value) * 100)
        
        # 更新状态
        if goal.completion_rate >= 100:
            goal.status = GoalStatus.COMPLETED.value
        elif goal.completion_rate >= 50:
            goal.status = GoalStatus.IN_PROGRESS.value
        
        # 记录变更
        goal.change_history.append({
            "type": "progress_update",
            "old_value": old_value,
            "new_value": current_value,
            "timestamp": datetime.now().isoformat()
        })
        
        goal.updated_at = datetime.now().isoformat()
        self._save()
        
        # 检查偏离
        self._check_deviation(goal_id)
        
        # 向上汇总
        self._aggregate_to_parent(goal_id)
        
        return {
            "goal_id": goal_id,
            "completion_rate": goal.completion_rate,
            "status": goal.status
        }
    
    def _check_deviation(self, goal_id: str):
        """检查目标偏离"""
        goal = self.goals.get(goal_id)
        if not goal:
            return
        
        # 计算预期进度
        start = datetime.fromisoformat(goal.start_date)
        end = datetime.fromisoformat(goal.end_date)
        now = datetime.now()
        
        total_days = (end - start).days
        elapsed_days = (now - start).days
        
        if total_days > 0:
            expected_rate = min(100.0, (elapsed_days / total_days) * 100)
            actual_rate = goal.completion_rate
            
            # 偏离超过 20%
            deviation = expected_rate - actual_rate
            if deviation > 20:
                alert = f"目标偏离: 预期 {expected_rate:.1f}%, 实际 {actual_rate:.1f}%, 偏离 {deviation:.1f}%"
                if alert not in goal.deviation_alerts:
                    goal.deviation_alerts.append(alert)
                    goal.status = GoalStatus.AT_RISK.value
            elif deviation > 10:
                goal.status = GoalStatus.IN_PROGRESS.value
        
        self._save()
    
    def _aggregate_to_parent(self, goal_id: str):
        """向上汇总到父目标"""
        goal = self.goals.get(goal_id)
        if not goal or not goal.parent_goal_id:
            return
        
        parent = self.goals.get(goal.parent_goal_id)
        if not parent:
            return
        
        # 计算所有子目标的平均完成率
        child_rates = []
        for child_id in parent.child_goal_ids:
            if child_id in self.goals:
                child_rates.append(self.goals[child_id].completion_rate)
        
        if child_rates:
            parent.completion_rate = sum(child_rates) / len(child_rates)
            parent.current_value = (parent.completion_rate / 100) * parent.target_value
        
        self._save()
    
    # === 目标绑定 ===
    def bind_workflow(self, goal_id: str, workflow_id: str):
        """绑定工作流"""
        if goal_id in self.goals:
            if workflow_id not in self.goals[goal_id].bound_workflows:
                self.goals[goal_id].bound_workflows.append(workflow_id)
                self._save()
    
    def bind_project(self, goal_id: str, project_id: str):
        """绑定项目"""
        if goal_id in self.goals:
            if project_id not in self.goals[goal_id].bound_projects:
                self.goals[goal_id].bound_projects.append(project_id)
                self._save()
    
    def bind_resource(self, goal_id: str, resource_id: str):
        """绑定资源"""
        if goal_id in self.goals:
            if resource_id not in self.goals[goal_id].bound_resources:
                self.goals[goal_id].bound_resources.append(resource_id)
                self._save()
    
    # === 目标关系 ===
    def add_dependency(self, source_goal_id: str, target_goal_id: str, weight: float = 1.0):
        """添加依赖关系"""
        relation = GoalRelation(
            source_goal_id=source_goal_id,
            target_goal_id=target_goal_id,
            relation_type="depends_on",
            weight=weight
        )
        self.relations.append(relation)
        
        if source_goal_id in self.goals:
            self.goals[source_goal_id].dependencies.append(target_goal_id)
        
        self._save()
    
    # === 影响分析 ===
    def analyze_change_impact(self, goal_id: str) -> Dict:
        """分析目标变更影响"""
        if goal_id not in self.goals:
            return {"error": "目标不存在"}
        
        goal = self.goals[goal_id]
        
        # 找出所有受影响的目标
        affected = []
        
        # 子目标
        for child_id in goal.child_goal_ids:
            if child_id in self.goals:
                affected.append({
                    "goal_id": child_id,
                    "relation": "child",
                    "impact": "high"
                })
        
        # 依赖此目标的其他目标
        for relation in self.relations:
            if relation.target_goal_id == goal_id:
                affected.append({
                    "goal_id": relation.source_goal_id,
                    "relation": "depends_on",
                    "impact": "medium"
                })
        
        # 绑定的工作流和项目
        for wf_id in goal.bound_workflows:
            affected.append({
                "resource_id": wf_id,
                "type": "workflow",
                "impact": "medium"
            })
        
        for proj_id in goal.bound_projects:
            affected.append({
                "resource_id": proj_id,
                "type": "project",
                "impact": "high"
            })
        
        return {
            "goal_id": goal_id,
            "affected_count": len(affected),
            "affected_items": affected
        }
    
    # === 查询 ===
    def get_goal(self, goal_id: str) -> Optional[Goal]:
        """获取目标"""
        return self.goals.get(goal_id)
    
    def list_goals(self, level: str = None, status: str = None,
                   owner: str = None) -> List[Goal]:
        """列出目标"""
        goals = list(self.goals.values())
        
        if level:
            goals = [g for g in goals if g.level == level]
        if status:
            goals = [g for g in goals if g.status == status]
        if owner:
            goals = [g for g in goals if g.owner == owner]
        
        return goals
    
    def get_goal_tree(self, goal_id: str = None) -> Dict:
        """获取目标树"""
        if goal_id:
            root = self.goals.get(goal_id)
            if not root:
                return {}
            roots = [root]
        else:
            # 获取所有顶级目标
            roots = [g for g in self.goals.values() if not g.parent_goal_id]
        
        def build_tree(goal: Goal) -> Dict:
            node = {
                "goal_id": goal.goal_id,
                "name": goal.name,
                "level": goal.level,
                "status": goal.status,
                "completion_rate": goal.completion_rate,
                "children": []
            }
            
            for child_id in goal.child_goal_ids:
                if child_id in self.goals:
                    node["children"].append(build_tree(self.goals[child_id]))
            
            return node
        
        return {
            "tree": [build_tree(r) for r in roots]
        }
    
    def get_report(self) -> str:
        """生成报告"""
        lines = [
            "# 战略目标报告",
            f"\n生成时间: {datetime.now().isoformat()}",
            ""
        ]
        
        # 按层级统计
        for level in GoalLevel:
            goals = [g for g in self.goals.values() if g.level == level.value]
            if goals:
                lines.append(f"## {level.value.upper()} 目标 ({len(goals)})")
                for goal in goals:
                    status = "✅" if goal.status == GoalStatus.COMPLETED.value else "⚠️" if goal.status == GoalStatus.AT_RISK.value else "📝"
                    lines.append(f"- {status} **{goal.name}**: {goal.completion_rate:.1f}%")
                lines.append("")
        
        # 偏离告警
        alerts = []
        for goal in self.goals.values():
            alerts.extend(goal.deviation_alerts)
        
        if alerts:
            lines.extend([
                "## 偏离告警",
                ""
            ])
            for alert in alerts:
                lines.append(f"- ⚠️ {alert}")
        
        return "\n".join(lines)

# 全局实例
_goal_engine = None

def get_goal_engine() -> StrategicGoalEngine:
    global _goal_engine
    if _goal_engine is None:
        _goal_engine = StrategicGoalEngine()
    return _goal_engine
