"""技能注册表"""

from typing import Dict, List, Optional, Any
from .schemas import SkillAsset
from .scanner import SkillScanner
import json
from pathlib import Path


class SkillRegistry:
    """技能注册表"""
    
    def __init__(self, storage_path: str = "data/skill_assets.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._skills: Dict[str, SkillAsset] = {}
        self._load()
    
    def _load(self):
        """加载技能"""
        if self.storage_path.exists():
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                for skill_data in data.get("skills", []):
                    skill = SkillAsset(**skill_data)
                    self._skills[skill.skill_id] = skill
        else:
            # 首次加载，扫描技能
            scanner = SkillScanner()
            for skill in scanner.scan_all():
                self._skills[skill.skill_id] = skill
            self._save()
    
    def _save(self):
        """保存技能"""
        with open(self.storage_path, "w") as f:
            json.dump({
                "skills": [s.__dict__ for s in self._skills.values()],
            }, f, ensure_ascii=False, indent=2)
    
    def get(self, skill_id: str) -> Optional[SkillAsset]:
        """获取技能"""
        return self._skills.get(skill_id)
    
    def search(self, query: str, limit: int = 10) -> List[SkillAsset]:
        """搜索技能"""
        query_lower = query.lower()
        results = []
        
        for skill in self._skills.values():
            score = 0
            if query_lower in skill.name.lower():
                score += 10
            if query_lower in skill.description.lower():
                score += 5
            if query_lower in skill.category.lower():
                score += 3
            for tag in skill.tags:
                if query_lower in tag.lower():
                    score += 2
            
            if score > 0:
                results.append((score, skill))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in results[:limit]]
    
    def list_by_category(self, category: str) -> List[SkillAsset]:
        """按分类列出"""
        return [s for s in self._skills.values() if s.category == category]
    
    def list_all(self) -> List[SkillAsset]:
        """列出所有"""
        return list(self._skills.values())
    
    def update_usage(self, skill_id: str, success: bool):
        """更新使用统计"""
        skill = self._skills.get(skill_id)
        if skill:
            skill.last_used_at = str(datetime.now())
            if success:
                skill.success_rate = min(1.0, skill.success_rate + 0.01)
            else:
                skill.success_rate = max(0.0, skill.success_rate - 0.01)
            self._save()
    
    def get_top_skills(self, limit: int = 10) -> List[SkillAsset]:
        """获取热门技能"""
        sorted_skills = sorted(
            self._skills.values(),
            key=lambda x: x.success_rate,
            reverse=True
        )
        return sorted_skills[:limit]


# 添加缺失的导入
from datetime import datetime
