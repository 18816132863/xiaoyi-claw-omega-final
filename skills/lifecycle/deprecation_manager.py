"""
弃用管理器

管理技能的弃用状态和迁移
"""

from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json


class DeprecationManager:
    """弃用管理器"""
    
    def __init__(self, deprecation_file: Path = None):
        self.deprecation_file = deprecation_file or Path("data/skill_deprecations.json")
        self.deprecations: Dict[str, Dict] = {}
        self._load()
    
    def _load(self):
        """加载弃用信息"""
        if self.deprecation_file.exists():
            with open(self.deprecation_file, 'r', encoding='utf-8') as f:
                self.deprecations = json.load(f)
    
    def _save(self):
        """保存弃用信息"""
        self.deprecation_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.deprecation_file, 'w', encoding='utf-8') as f:
            json.dump(self.deprecations, f, ensure_ascii=False, indent=2)
    
    def deprecate(self, skill_id: str, reason: str, replacement: str = None, 
                  sunset_date: str = None) -> bool:
        """标记技能为弃用"""
        self.deprecations[skill_id] = {
            "deprecated_at": datetime.now().isoformat(),
            "reason": reason,
            "replacement": replacement,
            "sunset_date": sunset_date,
            "status": "deprecated",
        }
        self._save()
        return True
    
    def undeprecate(self, skill_id: str) -> bool:
        """取消弃用标记"""
        if skill_id in self.deprecations:
            del self.deprecations[skill_id]
            self._save()
            return True
        return False
    
    def is_deprecated(self, skill_id: str) -> bool:
        """检查技能是否已弃用"""
        return skill_id in self.deprecations
    
    def get_deprecation_info(self, skill_id: str) -> Optional[Dict]:
        """获取弃用信息"""
        return self.deprecations.get(skill_id)
    
    def get_deprecated_skills(self) -> List[str]:
        """获取所有弃用技能"""
        return list(self.deprecations.keys())
    
    def check_sunset(self) -> List[str]:
        """检查已到达日落日期的技能"""
        now = datetime.now()
        sunset_skills = []
        
        for skill_id, info in self.deprecations.items():
            sunset_date = info.get("sunset_date")
            if sunset_date:
                try:
                    sunset_dt = datetime.fromisoformat(sunset_date)
                    if now >= sunset_dt:
                        sunset_skills.append(skill_id)
                except:
                    pass
        
        return sunset_skills
    
    def migrate(self, old_skill_id: str, new_skill_id: str) -> bool:
        """迁移到新技能"""
        if old_skill_id in self.deprecations:
            self.deprecations[old_skill_id]["migrated_to"] = new_skill_id
            self.deprecations[old_skill_id]["migrated_at"] = datetime.now().isoformat()
            self._save()
            return True
        return False


__all__ = ["DeprecationManager"]
