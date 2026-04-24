"""技能选择器"""

from typing import List, Dict, Any, Optional
from skill_asset_registry import SkillRegistry, SkillAsset


class SkillSelector:
    """技能选择器"""
    
    def __init__(self, registry: Optional[SkillRegistry] = None):
        self.registry = registry or SkillRegistry()
    
    def select_for_goal(self, goal: str, limit: int = 5) -> List[SkillAsset]:
        """为目标选择技能"""
        return self.registry.search(goal, limit)
    
    def select_for_capability(self, capability: str) -> List[SkillAsset]:
        """为能力选择技能"""
        # 从能力名称推断关键词
        keywords = capability.split(".")
        query = " ".join(keywords)
        return self.registry.search(query, limit=3)
    
    def rank_by_success_rate(self, skills: List[SkillAsset]) -> List[SkillAsset]:
        """按成功率排序"""
        return sorted(skills, key=lambda x: x.success_rate, reverse=True)
    
    def get_fallback(self, skill_id: str) -> Optional[SkillAsset]:
        """获取备用技能"""
        skill = self.registry.get(skill_id)
        if skill and skill.fallback_skills:
            for fb_id in skill.fallback_skills:
                fb = self.registry.get(fb_id)
                if fb:
                    return fb
        return None
