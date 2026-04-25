"""自适应学习器 - V1.0.0"""

from typing import Dict, List, Any, Tuple
from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path
from infrastructure.path_resolver import get_project_root

class AdaptiveLearner:
    """自适应学习器 - 从用户交互中学习"""
    
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path or get_project_root())
        self.learning_file = self.workspace / ".cache" / "adaptive_learning.json"
        self.learning_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 学习数据
        self.query_patterns: Dict[str, int] = defaultdict(int)
        self.skill_usage: Dict[str, int] = defaultdict(int)
        self.error_patterns: Dict[str, int] = defaultdict(int)
        self.success_patterns: Dict[str, List[str]] = defaultdict(list)
        
        self._load_learning()
    
    def _load_learning(self):
        """加载学习数据"""
        if self.learning_file.exists():
            with open(self.learning_file) as f:
                data = json.load(f)
            self.query_patterns = defaultdict(int, data.get("query_patterns", {}))
            self.skill_usage = defaultdict(int, data.get("skill_usage", {}))
            self.error_patterns = defaultdict(int, data.get("error_patterns", {}))
    
    def _save_learning(self):
        """保存学习数据"""
        data = {
            "query_patterns": dict(self.query_patterns),
            "skill_usage": dict(self.skill_usage),
            "error_patterns": dict(self.error_patterns),
            "updated": datetime.now().isoformat()
        }
        with open(self.learning_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def record_query(self, query: str):
        """记录查询"""
        # 提取模式
        pattern = self._extract_pattern(query)
        self.query_patterns[pattern] += 1
        self._save_learning()
    
    def record_skill_usage(self, skill_id: str, success: bool):
        """记录技能使用"""
        self.skill_usage[skill_id] += 1
        if not success:
            self.error_patterns[skill_id] += 1
        self._save_learning()
    
    def _extract_pattern(self, query: str) -> str:
        """提取查询模式"""
        # 简化查询为模式
        import re
        pattern = query.lower()
        pattern = re.sub(r'\d+', '{NUM}', pattern)
        pattern = re.sub(r'https?://\S+', '{URL}', pattern)
        return pattern[:50]
    
    def get_hot_queries(self, top_k: int = 10) -> List[Tuple[str, int]]:
        """获取热门查询"""
        sorted_queries = sorted(self.query_patterns.items(), key=lambda x: x[1], reverse=True)
        return sorted_queries[:top_k]
    
    def get_hot_skills(self, top_k: int = 10) -> List[Tuple[str, int]]:
        """获取热门技能"""
        sorted_skills = sorted(self.skill_usage.items(), key=lambda x: x[1], reverse=True)
        return sorted_skills[:top_k]
    
    def get_error_rate(self, skill_id: str) -> float:
        """获取技能错误率"""
        total = self.skill_usage.get(skill_id, 0)
        if total == 0:
            return 0.0
        return self.error_patterns.get(skill_id, 0) / total
    
    def suggest_skill(self, query: str) -> List[str]:
        """根据查询建议技能"""
        pattern = self._extract_pattern(query)
        
        # 基于历史推荐
        suggestions = []
        for skill, count in self.skill_usage.items():
            if count > 5 and self.get_error_rate(skill) < 0.1:
                suggestions.append(skill)
        
        return suggestions[:5]
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "unique_queries": len(self.query_patterns),
            "total_queries": sum(self.query_patterns.values()),
            "unique_skills": len(self.skill_usage),
            "total_skill_uses": sum(self.skill_usage.values()),
            "error_patterns": len(self.error_patterns)
        }
