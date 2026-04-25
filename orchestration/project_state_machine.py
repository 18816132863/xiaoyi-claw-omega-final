#!/usr/bin/env python3
"""
项目推进状态机 - V2.8.0

跟踪字段：
- 当前项目名
- 当前阶段
- 当前主目标
- 最近一次完成项
- 下一步建议动作
- 阻塞项
- 风险项
- 待确认项
- 已完成项
- 优先级
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum

from infrastructure.path_resolver import get_project_root

class ProjectStatus(Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class ProjectState:
    """项目状态"""
    id: str
    name: str
    description: str
    status: str
    priority: int
    current_stage: str
    main_goal: str
    last_completed: str
    next_action: str
    blockers: List[str]
    risks: List[str]
    pending_confirmations: List[str]
    completed_items: List[str]
    created_at: str
    updated_at: str
    history: List[Dict]

class ProjectStateMachine:
    """项目推进状态机"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.state_path = self.project_root / 'orchestration' / 'project_state.json'
        
        self.current_project: Optional[ProjectState] = None
        self.projects: Dict[str, ProjectState] = {}
        
        self._load()
    
    def _load(self):
        """加载状态"""
        if self.state_path.exists():
            data = json.loads(self.state_path.read_text(encoding='utf-8'))
            
            current_id = data.get("current_project_id")
            
            for proj_data in data.get("projects", []):
                state = ProjectState(**proj_data)
                self.projects[state.id] = state
                if state.id == current_id:
                    self.current_project = state
    
    def _save(self):
        """保存状态"""
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "current_project_id": self.current_project.id if self.current_project else None,
            "projects": [asdict(p) for p in self.projects.values()],
            "updated": datetime.now().isoformat()
        }
        self.state_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def create_project(self, name: str, description: str = "", 
                       priority: int = 2) -> ProjectState:
        """创建项目"""
        project_id = f"proj_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        state = ProjectState(
            id=project_id,
            name=name,
            description=description,
            status=ProjectStatus.ACTIVE.value,
            priority=priority,
            current_stage="初始化",
            main_goal="",
            last_completed="",
            next_action="",
            blockers=[],
            risks=[],
            pending_confirmations=[],
            completed_items=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            history=[]
        )
        
        self.projects[project_id] = state
        self.current_project = state
        self._save()
        
        return state
    
    def set_current_project(self, project_id: str) -> Optional[ProjectState]:
        """设置当前项目"""
        if project_id in self.projects:
            self.current_project = self.projects[project_id]
            self._save()
            return self.current_project
        return None
    
    def update_stage(self, stage: str):
        """更新当前阶段"""
        if self.current_project:
            old_stage = self.current_project.current_stage
            self.current_project.current_stage = stage
            self.current_project.updated_at = datetime.now().isoformat()
            self.current_project.history.append({
                "action": "stage_change",
                "from": old_stage,
                "to": stage,
                "timestamp": datetime.now().isoformat()
            })
            self._save()
    
    def set_main_goal(self, goal: str):
        """设置主目标"""
        if self.current_project:
            self.current_project.main_goal = goal
            self.current_project.updated_at = datetime.now().isoformat()
            self._save()
    
    def complete_item(self, item: str):
        """完成项目"""
        if self.current_project:
            self.current_project.completed_items.append(item)
            self.current_project.last_completed = item
            self.current_project.updated_at = datetime.now().isoformat()
            self.current_project.history.append({
                "action": "complete",
                "item": item,
                "timestamp": datetime.now().isoformat()
            })
            self._save()
    
    def set_next_action(self, action: str):
        """设置下一步动作"""
        if self.current_project:
            self.current_project.next_action = action
            self.current_project.updated_at = datetime.now().isoformat()
            self._save()
    
    def add_blocker(self, blocker: str, suggestion: str = ""):
        """添加阻塞项"""
        if self.current_project:
            self.current_project.blockers.append(blocker)
            self.current_project.status = ProjectStatus.BLOCKED.value
            self.current_project.updated_at = datetime.now().isoformat()
            self.current_project.history.append({
                "action": "add_blocker",
                "blocker": blocker,
                "suggestion": suggestion,
                "timestamp": datetime.now().isoformat()
            })
            self._save()
    
    def remove_blocker(self, blocker: str):
        """移除阻塞项"""
        if self.current_project and blocker in self.current_project.blockers:
            self.current_project.blockers.remove(blocker)
            if not self.current_project.blockers:
                self.current_project.status = ProjectStatus.ACTIVE.value
            self.current_project.updated_at = datetime.now().isoformat()
            self._save()
    
    def add_risk(self, risk: str):
        """添加风险项"""
        if self.current_project:
            self.current_project.risks.append(risk)
            self.current_project.updated_at = datetime.now().isoformat()
            self._save()
    
    def add_pending_confirmation(self, item: str):
        """添加待确认项"""
        if self.current_project:
            self.current_project.pending_confirmations.append(item)
            self.current_project.updated_at = datetime.now().isoformat()
            self._save()
    
    def confirm(self, item: str):
        """确认项"""
        if self.current_project and item in self.current_project.pending_confirmations:
            self.current_project.pending_confirmations.remove(item)
            self.current_project.updated_at = datetime.now().isoformat()
            self._save()
    
    def is_stuck(self) -> bool:
        """判断项目是否卡住"""
        if not self.current_project:
            return False
        
        # 有阻塞项
        if self.current_project.blockers:
            return True
        
        # 长时间未更新
        updated = datetime.fromisoformat(self.current_project.updated_at)
        if (datetime.now() - updated) > timedelta(days=3):
            return True
        
        # 有待确认项超过3个
        if len(self.current_project.pending_confirmations) > 3:
            return True
        
        return False
    
    def get_unblock_suggestions(self) -> List[str]:
        """获取解除阻塞建议"""
        suggestions = []
        
        if not self.current_project:
            return suggestions
        
        for blocker in self.current_project.blockers:
            if "权限" in blocker:
                suggestions.append(f"申请权限: {blocker}")
            elif "资源" in blocker:
                suggestions.append(f"协调资源: {blocker}")
            elif "依赖" in blocker:
                suggestions.append(f"解决依赖: {blocker}")
            else:
                suggestions.append(f"处理阻塞: {blocker}")
        
        return suggestions
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        if not self.current_project:
            return {"error": "无当前项目"}
        
        return {
            "project_name": self.current_project.name,
            "current_stage": self.current_project.current_stage,
            "main_goal": self.current_project.main_goal,
            "last_completed": self.current_project.last_completed,
            "next_action": self.current_project.next_action,
            "blockers": self.current_project.blockers,
            "risks": self.current_project.risks,
            "pending_confirmations": self.current_project.pending_confirmations,
            "completed_count": len(self.current_project.completed_items),
            "status": self.current_project.status,
            "is_stuck": self.is_stuck(),
            "unblock_suggestions": self.get_unblock_suggestions() if self.is_stuck() else []
        }
    
    def get_report(self) -> str:
        """生成报告"""
        status = self.get_status()
        
        if "error" in status:
            return status["error"]
        
        lines = [
            f"# 项目状态: {status['project_name']}",
            "",
            f"**当前阶段**: {status['current_stage']}",
            f"**主目标**: {status['main_goal'] or '未设置'}",
            f"**状态**: {status['status']}",
            "",
            "## 进度",
            f"- 最近完成: {status['last_completed'] or '无'}",
            f"- 下一步: {status['next_action'] or '待确定'}",
            f"- 已完成项: {status['completed_count']}",
            ""
        ]
        
        if status['blockers']:
            lines.append("## ⚠️ 阻塞项")
            for b in status['blockers']:
                lines.append(f"- {b}")
            lines.append("")
        
        if status['risks']:
            lines.append("## 🔴 风险项")
            for r in status['risks']:
                lines.append(f"- {r}")
            lines.append("")
        
        if status['pending_confirmations']:
            lines.append("## ❓ 待确认")
            for p in status['pending_confirmations']:
                lines.append(f"- {p}")
            lines.append("")
        
        if status['is_stuck']:
            lines.append("## 💡 解除阻塞建议")
            for s in status['unblock_suggestions']:
                lines.append(f"- {s}")
        
        return "\n".join(lines)

# 全局实例
_state_machine = None

def get_project_state_machine() -> ProjectStateMachine:
    global _state_machine
    if _state_machine is None:
        _state_machine = ProjectStateMachine()
    return _state_machine
