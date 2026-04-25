#!/usr/bin/env python3
"""
多项目调度器 - V2.8.0

统一管理多项目并行推进，区分：
- 主项目 / 次项目
- 紧急 / 非紧急
- 可立即执行 / 依赖外部信息
- 长期推进 / 一次性任务
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

from infrastructure.path_resolver import get_project_root

class ProjectPriority(Enum):
    PRIMARY = "primary"      # 主项目
    SECONDARY = "secondary"  # 次项目

class Urgency(Enum):
    URGENT = "urgent"        # 紧急
    NORMAL = "normal"        # 正常
    LOW = "low"              # 低优先

class ExecutionState(Enum):
    READY = "ready"          # 可立即执行
    BLOCKED = "blocked"      # 依赖外部信息
    WAITING = "waiting"      # 等待中

class ProjectType(Enum):
    LONG_TERM = "long_term"  # 长期推进
    ONE_TIME = "one_time"    # 一次性任务

@dataclass
class ScheduledProject:
    """调度项目"""
    project_id: str
    name: str
    priority: str
    urgency: str
    execution_state: str
    project_type: str
    current_stage: str
    next_action: str
    blockers: List[str]
    dependencies: List[str]
    last_updated: str
    score: float

class MultiProjectScheduler:
    """多项目调度器"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.schedule_path = self.project_root / 'orchestration' / 'project_schedule.json'
        
        self.projects: Dict[str, ScheduledProject] = {}
        self._load()
    
    def _load(self):
        """加载调度"""
        if self.schedule_path.exists():
            data = json.loads(self.schedule_path.read_text(encoding='utf-8'))
            for proj_data in data.get("projects", []):
                self.projects[proj_data["project_id"]] = ScheduledProject(**proj_data)
    
    def _save(self):
        """保存调度"""
        self.schedule_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "projects": [asdict(p) for p in self.projects.values()],
            "updated": datetime.now().isoformat()
        }
        self.schedule_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def add_project(self, name: str, priority: str = "secondary",
                    urgency: str = "normal", project_type: str = "long_term",
                    dependencies: List[str] = None) -> ScheduledProject:
        """添加项目"""
        project_id = f"proj_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 判断执行状态
        if dependencies:
            execution_state = ExecutionState.WAITING.value
        else:
            execution_state = ExecutionState.READY.value
        
        project = ScheduledProject(
            project_id=project_id,
            name=name,
            priority=priority,
            urgency=urgency,
            execution_state=execution_state,
            project_type=project_type,
            current_stage="初始化",
            next_action="",
            blockers=[],
            dependencies=dependencies or [],
            last_updated=datetime.now().isoformat(),
            score=0.0
        )
        
        self.projects[project_id] = project
        self._recalculate_scores()
        self._save()
        
        return project
    
    def update_project(self, project_id: str, **kwargs):
        """更新项目"""
        if project_id not in self.projects:
            return None
        
        project = self.projects[project_id]
        
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
        
        project.last_updated = datetime.now().isoformat()
        self._recalculate_scores()
        self._save()
        
        return project
    
    def add_blocker(self, project_id: str, blocker: str):
        """添加阻塞"""
        if project_id in self.projects:
            project = self.projects[project_id]
            project.blockers.append(blocker)
            project.execution_state = ExecutionState.BLOCKED.value
            project.last_updated = datetime.now().isoformat()
            self._recalculate_scores()
            self._save()
    
    def remove_blocker(self, project_id: str, blocker: str):
        """移除阻塞"""
        if project_id in self.projects:
            project = self.projects[project_id]
            if blocker in project.blockers:
                project.blockers.remove(blocker)
            
            if not project.blockers:
                project.execution_state = ExecutionState.READY.value
            
            project.last_updated = datetime.now().isoformat()
            self._recalculate_scores()
            self._save()
    
    def _recalculate_scores(self):
        """重新计算调度分数"""
        for project in self.projects.values():
            score = 0.0
            
            # 优先级权重
            if project.priority == ProjectPriority.PRIMARY.value:
                score += 30
            else:
                score += 10
            
            # 紧急程度权重
            if project.urgency == Urgency.URGENT.value:
                score += 30
            elif project.urgency == Urgency.NORMAL.value:
                score += 15
            else:
                score += 5
            
            # 执行状态权重
            if project.execution_state == ExecutionState.READY.value:
                score += 20
            elif project.execution_state == ExecutionState.WAITING.value:
                score += 10
            else:
                score += 0
            
            # 阻塞惩罚
            score -= len(project.blockers) * 5
            
            # 长期项目加分（需要持续关注）
            if project.project_type == ProjectType.LONG_TERM.value:
                score += 10
            
            project.score = max(0, score)
    
    def get_priority_order(self) -> List[ScheduledProject]:
        """获取优先顺序"""
        return sorted(self.projects.values(), key=lambda x: x.score, reverse=True)
    
    def get_current_priority(self) -> Optional[ScheduledProject]:
        """获取当前最优先项目"""
        ready_projects = [
            p for p in self.projects.values()
            if p.execution_state == ExecutionState.READY.value
        ]
        
        if not ready_projects:
            return None
        
        return max(ready_projects, key=lambda x: x.score)
    
    def get_blocked_projects(self) -> List[ScheduledProject]:
        """获取阻塞项目"""
        return [
            p for p in self.projects.values()
            if p.execution_state == ExecutionState.BLOCKED.value
        ]
    
    def get_quick_wins(self) -> List[ScheduledProject]:
        """获取可顺手推进的任务"""
        return [
            p for p in self.projects.values()
            if (p.execution_state == ExecutionState.READY.value and
                p.project_type == ProjectType.ONE_TIME.value and
                not p.blockers)
        ]
    
    def get_next_actions(self, limit: int = 5) -> List[Dict]:
        """获取下一步行动列表"""
        actions = []
        
        for project in self.get_priority_order()[:limit]:
            actions.append({
                "project": project.name,
                "priority": project.priority,
                "urgency": project.urgency,
                "next_action": project.next_action or "待确定",
                "state": project.execution_state,
                "blockers": project.blockers
            })
        
        return actions
    
    def get_report(self) -> str:
        """生成报告"""
        lines = [
            "# 多项目调度报告",
            "",
            "## 当前最优先",
            ""
        ]
        
        current = self.get_current_priority()
        if current:
            lines.append(f"**{current.name}** (分数: {current.score})")
            lines.append(f"- 阶段: {current.current_stage}")
            lines.append(f"- 下一步: {current.next_action or '待确定'}")
        else:
            lines.append("无就绪项目")
        
        lines.extend([
            "",
            "## 优先顺序",
            ""
        ])
        
        for project in self.get_priority_order()[:10]:
            status_emoji = {
                ExecutionState.READY.value: "✅",
                ExecutionState.BLOCKED.value: "❌",
                ExecutionState.WAITING.value: "⏳"
            }.get(project.execution_state, "❓")
            
            lines.append(f"- {status_emoji} {project.name} (分数: {project.score})")
        
        blocked = self.get_blocked_projects()
        if blocked:
            lines.extend([
                "",
                "## 阻塞项目",
                ""
            ])
            for project in blocked:
                lines.append(f"- **{project.name}**: {', '.join(project.blockers)}")
        
        quick_wins = self.get_quick_wins()
        if quick_wins:
            lines.extend([
                "",
                "## 可顺手推进",
                ""
            ])
            for project in quick_wins[:5]:
                lines.append(f"- {project.name}")
        
        return "\n".join(lines)

# 全局实例
_scheduler = None

def get_project_scheduler() -> MultiProjectScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = MultiProjectScheduler()
    return _scheduler
