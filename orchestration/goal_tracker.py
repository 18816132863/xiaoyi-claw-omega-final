#!/usr/bin/env python3
"""
用户目标持续追踪 - V2.8.0

追踪：
- 当前项目
- 当前阶段
- 最近动作
- 下一步待办
- 阻塞项
- 已完成项
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

from infrastructure.path_resolver import get_project_root

@dataclass
class Goal:
    """目标"""
    id: str
    name: str
    description: str
    status: str  # active, completed, blocked, paused
    priority: int
    created_at: str
    updated_at: str
    progress: float

@dataclass
class Action:
    """动作"""
    id: str
    goal_id: str
    description: str
    status: str  # pending, in_progress, completed, failed
    timestamp: str

class GoalTracker:
    """目标追踪器"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.tracker_path = self.project_root / 'orchestration' / 'goal_tracker.json'
        
        self.goals: Dict[str, Goal] = {}
        self.actions: List[Action] = []
        self.current_goal_id: Optional[str] = None
        
        self._load()
    
    def _load(self):
        """加载数据"""
        if self.tracker_path.exists():
            data = json.loads(self.tracker_path.read_text(encoding='utf-8'))
            
            for goal_data in data.get("goals", []):
                self.goals[goal_data["id"]] = Goal(**goal_data)
            
            for action_data in data.get("actions", []):
                self.actions.append(Action(**action_data))
            
            self.current_goal_id = data.get("current_goal_id")
    
    def _save(self):
        """保存数据"""
        self.tracker_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "goals": [asdict(g) for g in self.goals.values()],
            "actions": [asdict(a) for a in self.actions],
            "current_goal_id": self.current_goal_id,
            "updated": datetime.now().isoformat()
        }
        self.tracker_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def set_current_project(self, name: str, description: str = "") -> str:
        """设置当前项目"""
        goal_id = f"goal_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        goal = Goal(
            id=goal_id,
            name=name,
            description=description,
            status="active",
            priority=1,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            progress=0.0
        )
        
        self.goals[goal_id] = goal
        self.current_goal_id = goal_id
        self._save()
        
        return goal_id
    
    def update_stage(self, stage: str):
        """更新当前阶段"""
        if self.current_goal_id and self.current_goal_id in self.goals:
            goal = self.goals[self.current_goal_id]
            goal.description = f"{goal.description}\n当前阶段: {stage}"
            goal.updated_at = datetime.now().isoformat()
            self._save()
    
    def add_action(self, description: str, status: str = "completed") -> str:
        """添加动作"""
        action_id = f"act_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        action = Action(
            id=action_id,
            goal_id=self.current_goal_id or "",
            description=description,
            status=status,
            timestamp=datetime.now().isoformat()
        )
        
        self.actions.append(action)
        
        # 限制历史大小
        if len(self.actions) > 100:
            self.actions = self.actions[-100:]
        
        self._save()
        
        return action_id
    
    def add_todo(self, description: str) -> str:
        """添加待办"""
        return self.add_action(description, "pending")
    
    def add_blocker(self, description: str) -> str:
        """添加阻塞项"""
        if self.current_goal_id and self.current_goal_id in self.goals:
            self.goals[self.current_goal_id].status = "blocked"
        return self.add_action(f"[阻塞] {description}", "pending")
    
    def complete_todo(self, action_id: str):
        """完成待办"""
        for action in self.actions:
            if action.id == action_id:
                action.status = "completed"
                action.timestamp = datetime.now().isoformat()
                break
        self._save()
    
    def update_progress(self, progress: float):
        """更新进度"""
        if self.current_goal_id and self.current_goal_id in self.goals:
            self.goals[self.current_goal_id].progress = min(progress, 1.0)
            self.goals[self.current_goal_id].updated_at = datetime.now().isoformat()
            self._save()
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        current_goal = self.goals.get(self.current_goal_id) if self.current_goal_id else None
        
        recent_actions = self.actions[-10:] if self.actions else []
        pending_actions = [a for a in self.actions if a.status == "pending"]
        completed_actions = [a for a in self.actions if a.status == "completed"]
        blockers = [a for a in self.actions if "阻塞" in a.description and a.status == "pending"]
        
        return {
            "current_project": current_goal.name if current_goal else None,
            "current_stage": self._extract_stage(current_goal) if current_goal else None,
            "progress": current_goal.progress if current_goal else 0,
            "recent_actions": [a.description for a in recent_actions],
            "next_todos": [a.description for a in pending_actions[:5]],
            "blockers": [a.description for a in blockers],
            "completed_count": len(completed_actions)
        }
    
    def _extract_stage(self, goal: Goal) -> Optional[str]:
        """提取当前阶段"""
        if "当前阶段:" in goal.description:
            lines = goal.description.split("\n")
            for line in lines:
                if "当前阶段:" in line:
                    return line.split("当前阶段:")[1].strip()
        return None
    
    def get_report(self) -> str:
        """生成报告"""
        status = self.get_status()
        
        lines = [
            "# 目标追踪报告",
            "",
            "## 当前状态",
            "",
            f"- **当前项目**: {status['current_project'] or '无'}",
            f"- **当前阶段**: {status['current_stage'] or '无'}",
            f"- **进度**: {status['progress'] * 100:.0f}%",
            "",
            "## 最近动作",
            ""
        ]
        
        for action in status["recent_actions"][-5:]:
            lines.append(f"- {action}")
        
        if status["next_todos"]:
            lines.extend([
                "",
                "## 待办事项",
                ""
            ])
            for todo in status["next_todos"]:
                lines.append(f"- [ ] {todo}")
        
        if status["blockers"]:
            lines.extend([
                "",
                "## 阻塞项",
                ""
            ])
            for blocker in status["blockers"]:
                lines.append(f"- ⚠️ {blocker}")
        
        lines.extend([
            "",
            f"## 已完成: {status['completed_count']} 项"
        ])
        
        return "\n".join(lines)

# 全局实例
_tracker = None

def get_goal_tracker() -> GoalTracker:
    """获取全局目标追踪器"""
    global _tracker
    if _tracker is None:
        _tracker = GoalTracker()
    return _tracker
