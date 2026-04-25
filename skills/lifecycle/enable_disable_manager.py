"""
启用/禁用管理器

管理技能的启用和禁用状态
"""

from datetime import datetime
from typing import Dict, List, Optional, Set
from pathlib import Path
import json


class EnableDisableManager:
    """启用/禁用管理器"""
    
    def __init__(self, state_file: Path = None):
        self.state_file = state_file or Path("data/skill_states.json")
        self.disabled_skills: Set[str] = set()
        self.enabled_skills: Set[str] = set()
        self._load_state()
    
    def _load_state(self):
        """加载状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.disabled_skills = set(data.get("disabled", []))
            self.enabled_skills = set(data.get("enabled", []))
    
    def _save_state(self):
        """保存状态"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump({
                "disabled": list(self.disabled_skills),
                "enabled": list(self.enabled_skills),
                "updated": datetime.now().isoformat(),
            }, f, ensure_ascii=False, indent=2)
    
    def enable(self, skill_id: str) -> bool:
        """启用技能"""
        self.disabled_skills.discard(skill_id)
        self.enabled_skills.add(skill_id)
        self._save_state()
        return True
    
    def disable(self, skill_id: str, reason: str = "") -> bool:
        """禁用技能"""
        self.enabled_skills.discard(skill_id)
        self.disabled_skills.add(skill_id)
        self._save_state()
        return True
    
    def is_enabled(self, skill_id: str) -> bool:
        """检查技能是否启用"""
        return skill_id not in self.disabled_skills
    
    def is_disabled(self, skill_id: str) -> bool:
        """检查技能是否禁用"""
        return skill_id in self.disabled_skills
    
    def get_enabled_skills(self) -> List[str]:
        """获取启用的技能列表"""
        return list(self.enabled_skills)
    
    def get_disabled_skills(self) -> List[str]:
        """获取禁用的技能列表"""
        return list(self.disabled_skills)
    
    def toggle(self, skill_id: str) -> bool:
        """切换技能状态"""
        if self.is_disabled(skill_id):
            return self.enable(skill_id)
        else:
            return self.disable(skill_id)


__all__ = ["EnableDisableManager"]
