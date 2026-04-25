#!/usr/bin/env python3
"""
资源与组合调度中心 - V2.8.1

能力：
- 项目优先级模型
- 资源占用模型
- 预算约束模型
- 时间窗口约束
- 机会成本评估
- 风险收益比评估
- 推进顺序建议
- 暂停/延后/加速建议
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

from infrastructure.path_resolver import get_project_root

class Priority(Enum):
    P0 = "p0"  # 关键
    P1 = "p1"  # 高
    P2 = "p2"  # 中
    P3 = "p3"  # 低

class ResourceType(Enum):
    HUMAN = "human"           # 人力资源
    COMPUTE = "compute"       # 计算资源
    STORAGE = "storage"       # 存储资源
    BUDGET = "budget"         # 预算资源
    TIME = "time"             # 时间资源

class ScheduleAction(Enum):
    START = "start"           # 启动
    ACCELERATE = "accelerate" # 加速
    MAINTAIN = "maintain"     # 维持
    DELAY = "delay"           # 延后
    PAUSE = "pause"           # 暂停
    CANCEL = "cancel"         # 取消

@dataclass
class Resource:
    """资源"""
    resource_id: str
    name: str
    resource_type: str
    total_capacity: float
    used_capacity: float
    available_capacity: float
    cost_per_unit: float
    constraints: Dict

@dataclass
class ProjectPortfolio:
    """项目组合"""
    project_id: str
    name: str
    priority: str
    status: str
    start_date: str
    end_date: str
    estimated_effort: float       # 预估工作量
    actual_effort: float          # 实际工作量
    progress: float               # 进度
    required_resources: Dict[str, float]  # 所需资源
    allocated_resources: Dict[str, float]  # 已分配资源
    budget: float                 # 预算
    spent: float                  # 已花费
    risk_level: str               # 风险等级
    expected_value: float         # 预期价值
    dependencies: List[str]       # 依赖项目
    goal_id: str                  # 关联目标

@dataclass
class ScheduleDecision:
    """调度决策"""
    decision_id: str
    project_id: str
    action: str
    reason: str
    impact: Dict
    confidence: float
    created_at: str

class PortfolioResourceScheduler:
    """资源与组合调度中心"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.portfolio_path = self.project_root / 'portfolio'
        self.config_path = self.portfolio_path / 'portfolio_config.json'
        
        # 资源
        self.resources: Dict[str, Resource] = {}
        
        # 项目组合
        self.projects: Dict[str, ProjectPortfolio] = {}
        
        # 调度决策
        self.decisions: List[ScheduleDecision] = []
        
        self._init_default_resources()
        self._load()
    
    def _init_default_resources(self):
        """初始化默认资源"""
        default_resources = [
            Resource("res_human_01", "人力资源", ResourceType.HUMAN.value, 100.0, 0.0, 100.0, 100.0, {}),
            Resource("res_compute_01", "计算资源", ResourceType.COMPUTE.value, 1000.0, 0.0, 1000.0, 1.0, {}),
            Resource("res_storage_01", "存储资源", ResourceType.STORAGE.value, 10000.0, 0.0, 10000.0, 0.1, {}),
            Resource("res_budget_01", "预算资源", ResourceType.BUDGET.value, 100000.0, 0.0, 100000.0, 1.0, {}),
        ]
        
        for res in default_resources:
            self.resources[res.resource_id] = res
    
    def _load(self):
        """加载配置"""
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text(encoding='utf-8'))
            
            for rid, res in data.get("resources", {}).items():
                self.resources[rid] = Resource(**res)
            
            for pid, proj in data.get("projects", {}).items():
                self.projects[pid] = ProjectPortfolio(**proj)
            
            self.decisions = [ScheduleDecision(**d) for d in data.get("decisions", [])]
    
    def _save(self):
        """保存配置"""
        self.portfolio_path.mkdir(parents=True, exist_ok=True)
        data = {
            "resources": {rid: asdict(r) for rid, r in self.resources.items()},
            "projects": {pid: asdict(p) for pid, p in self.projects.items()},
            "decisions": [asdict(d) for d in self.decisions],
            "updated": datetime.now().isoformat()
        }
        self.config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    # === 资源管理 ===
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """获取资源"""
        return self.resources.get(resource_id)
    
    def allocate_resource(self, resource_id: str, project_id: str,
                          amount: float) -> Dict:
        """分配资源"""
        if resource_id not in self.resources:
            return {"error": "资源不存在"}
        
        resource = self.resources[resource_id]
        
        if amount > resource.available_capacity:
            return {"error": f"资源不足: 需要 {amount}, 可用 {resource.available_capacity}"}
        
        resource.used_capacity += amount
        resource.available_capacity -= amount
        
        if project_id in self.projects:
            project = self.projects[project_id]
            project.allocated_resources[resource_id] = project.allocated_resources.get(resource_id, 0) + amount
        
        self._save()
        
        return {"status": "allocated", "resource_id": resource_id, "amount": amount}
    
    def release_resource(self, resource_id: str, project_id: str,
                         amount: float) -> Dict:
        """释放资源"""
        if resource_id not in self.resources:
            return {"error": "资源不存在"}
        
        resource = self.resources[resource_id]
        resource.used_capacity -= amount
        resource.available_capacity += amount
        
        if project_id in self.projects:
            project = self.projects[project_id]
            if resource_id in project.allocated_resources:
                project.allocated_resources[resource_id] -= amount
        
        self._save()
        
        return {"status": "released", "resource_id": resource_id, "amount": amount}
    
    # === 项目管理 ===
    def add_project(self, name: str, priority: str, start_date: str,
                    end_date: str, estimated_effort: float,
                    required_resources: Dict, budget: float,
                    risk_level: str, expected_value: float,
                    goal_id: str = "") -> ProjectPortfolio:
        """添加项目"""
        project_id = f"proj_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        project = ProjectPortfolio(
            project_id=project_id,
            name=name,
            priority=priority,
            status="planned",
            start_date=start_date,
            end_date=end_date,
            estimated_effort=estimated_effort,
            actual_effort=0.0,
            progress=0.0,
            required_resources=required_resources,
            allocated_resources={},
            budget=budget,
            spent=0.0,
            risk_level=risk_level,
            expected_value=expected_value,
            dependencies=[],
            goal_id=goal_id
        )
        
        self.projects[project_id] = project
        self._save()
        
        return project
    
    def get_project(self, project_id: str) -> Optional[ProjectPortfolio]:
        """获取项目"""
        return self.projects.get(project_id)
    
    def list_projects(self, priority: str = None, status: str = None) -> List[ProjectPortfolio]:
        """列出项目"""
        projects = list(self.projects.values())
        
        if priority:
            projects = [p for p in projects if p.priority == priority]
        if status:
            projects = [p for p in projects if p.status == status]
        
        return projects
    
    # === 优先级计算 ===
    def calculate_priority_score(self, project_id: str) -> float:
        """计算优先级分数"""
        project = self.get_project(project_id)
        if not project:
            return 0.0
        
        score = 0.0
        
        # 优先级权重 (40%)
        priority_weights = {"p0": 40, "p1": 30, "p2": 20, "p3": 10}
        score += priority_weights.get(project.priority, 10)
        
        # 预期价值权重 (30%)
        max_value = max((p.expected_value for p in self.projects.values()), default=1)
        value_score = (project.expected_value / max_value) * 30 if max_value > 0 else 0
        score += value_score
        
        # 风险调整 (15%)
        risk_weights = {"low": 15, "medium": 10, "high": 5, "critical": 0}
        score += risk_weights.get(project.risk_level, 10)
        
        # 紧急程度 (15%)
        if project.end_date:
            end = datetime.fromisoformat(project.end_date)
            days_remaining = (end - datetime.now()).days
            if days_remaining < 7:
                score += 15
            elif days_remaining < 30:
                score += 10
            else:
                score += 5
        
        return score
    
    # === 调度建议 ===
    def generate_schedule_recommendations(self) -> List[Dict]:
        """生成调度建议"""
        recommendations = []
        
        # 计算所有项目的优先级分数
        project_scores = []
        for project in self.projects.values():
            score = self.calculate_priority_score(project.project_id)
            project_scores.append((project, score))
        
        # 按分数排序
        project_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 检查资源约束
        for project, score in project_scores:
            # 检查资源是否足够
            resource_gap = self._check_resource_gap(project)
            
            if resource_gap:
                # 资源不足，建议延后
                recommendations.append({
                    "project_id": project.project_id,
                    "name": project.name,
                    "action": ScheduleAction.DELAY.value,
                    "reason": f"资源不足: {resource_gap}",
                    "priority_score": score
                })
            elif project.status == "planned":
                # 可以启动
                recommendations.append({
                    "project_id": project.project_id,
                    "name": project.name,
                    "action": ScheduleAction.START.value,
                    "reason": "资源充足，建议启动",
                    "priority_score": score
                })
            elif project.progress < 0.5 and score > 70:
                # 高优先级但进度慢，建议加速
                recommendations.append({
                    "project_id": project.project_id,
                    "name": project.name,
                    "action": ScheduleAction.ACCELERATE.value,
                    "reason": "高优先级项目，建议加速",
                    "priority_score": score
                })
        
        return recommendations
    
    def _check_resource_gap(self, project: ProjectPortfolio) -> Optional[str]:
        """检查资源缺口"""
        for res_id, required in project.required_resources.items():
            if res_id in self.resources:
                available = self.resources[res_id].available_capacity
                if required > available:
                    return f"{res_id}: 需要 {required}, 可用 {available}"
        return None
    
    # === 机会成本评估 ===
    def evaluate_opportunity_cost(self, project_id: str) -> Dict:
        """评估机会成本"""
        project = self.get_project(project_id)
        if not project:
            return {"error": "项目不存在"}
        
        # 计算如果选择此项目，其他项目的机会成本
        other_projects = [p for p in self.projects.values() if p.project_id != project_id]
        
        # 按优先级排序
        other_projects.sort(key=lambda p: self.calculate_priority_score(p.project_id), reverse=True)
        
        # 计算资源占用导致的其他项目延迟
        delayed_value = 0.0
        for other in other_projects[:3]:  # 考虑前3个受影响的项目
            delayed_value += other.expected_value * 0.1  # 假设延迟10%
        
        return {
            "project_id": project_id,
            "project_value": project.expected_value,
            "opportunity_cost": delayed_value,
            "net_value": project.expected_value - delayed_value,
            "affected_projects": [p.project_id for p in other_projects[:3]]
        }
    
    # === 风险收益评估 ===
    def evaluate_risk_return(self, project_id: str) -> Dict:
        """评估风险收益比"""
        project = self.get_project(project_id)
        if not project:
            return {"error": "项目不存在"}
        
        risk_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        risk_score = risk_scores.get(project.risk_level, 2)
        
        # 风险收益比 = 预期价值 / (风险分数 * 预算)
        if project.budget > 0:
            ratio = project.expected_value / (risk_score * project.budget)
        else:
            ratio = project.expected_value / risk_score
        
        return {
            "project_id": project_id,
            "expected_value": project.expected_value,
            "risk_level": project.risk_level,
            "risk_score": risk_score,
            "budget": project.budget,
            "risk_return_ratio": ratio,
            "recommendation": "favorable" if ratio > 1 else "unfavorable"
        }
    
    # === 报告 ===
    def get_report(self) -> str:
        """生成报告"""
        lines = [
            "# 资源与组合调度报告",
            f"\n生成时间: {datetime.now().isoformat()}",
            "",
            "## 资源概览",
            ""
        ]
        
        for res in self.resources.values():
            usage = (res.used_capacity / res.total_capacity * 100) if res.total_capacity > 0 else 0
            lines.append(f"- **{res.name}**: {usage:.1f}% ({res.used_capacity}/{res.total_capacity})")
        
        lines.extend([
            "",
            "## 项目组合",
            ""
        ])
        
        for project in sorted(self.projects.values(), key=lambda p: p.priority):
            lines.append(f"- [{project.priority}] **{project.name}**: {project.progress*100:.0f}%")
        
        lines.extend([
            "",
            "## 调度建议",
            ""
        ])
        
        recommendations = self.generate_schedule_recommendations()
        for rec in recommendations[:5]:
            lines.append(f"- [{rec['action']}] {rec['name']}: {rec['reason']}")
        
        return "\n".join(lines)

# 全局实例
_resource_scheduler = None

def get_resource_scheduler() -> PortfolioResourceScheduler:
    global _resource_scheduler
    if _resource_scheduler is None:
        _resource_scheduler = PortfolioResourceScheduler()
    return _resource_scheduler
