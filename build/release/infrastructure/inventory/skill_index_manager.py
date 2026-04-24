"""技能索引管理器 - V1.0.0"""

from typing import Dict, List, Set
from pathlib import Path
from infrastructure.path_resolver import get_project_root
import json

class SkillIndexManager:
    """技能索引管理器"""
    
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path or get_project_root())
        self.index_path = self.workspace / "infrastructure/inventory/skill_inverted_index.json"
        self.hot_cache_path = self.workspace / "infrastructure/optimization/HOT_CACHE.json"
        
        self.trigger_index: Dict[str, List[str]] = {}
        self.category_index: Dict[str, List[str]] = {}
        self.hot_skills: List[str] = []
        
        self._load_indexes()
    
    def _load_indexes(self):
        """加载索引"""
        # 加载倒排索引
        if self.index_path.exists():
            with open(self.index_path) as f:
                data = json.load(f)
            self.trigger_index = data.get("by_trigger", {})
            self.category_index = data.get("by_category", {})
        
        # 加载热点缓存
        if self.hot_cache_path.exists():
            with open(self.hot_cache_path) as f:
                data = json.load(f)
            self.hot_skills = data.get("top_skills", [])
    
    def find_by_trigger(self, trigger: str) -> List[str]:
        """根据触发词查找技能"""
        # 精确匹配
        if trigger in self.trigger_index:
            return self.trigger_index[trigger]
        
        # 模糊匹配
        results = []
        trigger_lower = trigger.lower()
        for key, skills in self.trigger_index.items():
            if trigger_lower in key.lower() or key.lower() in trigger_lower:
                results.extend(skills)
        
        return list(set(results))
    
    def find_by_category(self, category: str) -> List[str]:
        """根据分类查找技能"""
        return self.category_index.get(category, [])
    
    def is_hot(self, skill_id: str) -> bool:
        """检查是否为热点技能"""
        return skill_id in self.hot_skills
    
    def get_hot_skills(self) -> List[str]:
        """获取热点技能列表"""
        return self.hot_skills
    
    def get_stats(self) -> Dict:
        """获取索引统计"""
        return {
            "trigger_count": len(self.trigger_index),
            "category_count": len(self.category_index),
            "hot_skill_count": len(self.hot_skills),
            "total_indexed_skills": len(set(
                sum(self.trigger_index.values(), []) + 
                sum(self.category_index.values(), [])
            ))
        }
