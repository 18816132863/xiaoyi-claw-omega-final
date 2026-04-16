"""Priority Ranker - 上下文优先级排序"""

from typing import List, Dict, Any
from enum import Enum


class SourcePriority(Enum):
    """源优先级"""
    RULE = 100
    DECISION_LOG = 90
    MEMORY = 80
    DOCUMENT = 70
    SKILL = 60
    SESSION = 50
    REPORT = 40


class PriorityRanker:
    """
    上下文优先级排序器
    
    考虑因素：
    - 源类型权重
    - 相关性分数
    - 重要性等级
    - 时间新鲜度
    """
    
    def __init__(self):
        self.source_weights = {
            "rule": 1.0,
            "decision_log": 0.9,
            "memory": 0.8,
            "document": 0.7,
            "skill": 0.6,
            "session": 0.5,
            "report": 0.4,
            "additional": 0.3
        }
        
        self.importance_multipliers = {
            "critical": 1.5,
            "high": 1.2,
            "medium": 1.0,
            "low": 0.8
        }
    
    def rank(self, sources: List[Dict[str, Any]]) -> List[str]:
        """
        排序并返回 source_id 列表
        
        Args:
            sources: 源列表，每个源包含 type, relevance, importance 等
        
        Returns:
            排序后的 source_id 列表
        """
        scored = []
        
        for source in sources:
            score = self._calculate_score(source)
            source_id = source.get("source_id", str(len(scored)))
            scored.append((source_id, score))
        
        # 按分数降序排序
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [s[0] for s in scored]
    
    def _calculate_score(self, source: Dict[str, Any]) -> float:
        """计算优先级分数"""
        # 基础分数（源类型权重）
        source_type = source.get("type", "document")
        base_score = self.source_weights.get(source_type, 0.5) * 100
        
        # 相关性分数
        relevance = source.get("relevance", 0.5)
        
        # 重要性乘数
        importance = source.get("importance", "medium")
        if isinstance(importance, str):
            multiplier = self.importance_multipliers.get(importance, 1.0)
        else:
            multiplier = 1.0
        
        # 时间新鲜度加成
        recency_bonus = self._get_recency_bonus(source)
        
        # 最终分数
        final_score = (base_score * relevance * multiplier) + recency_bonus
        
        return final_score
    
    def _get_recency_bonus(self, source: Dict[str, Any]) -> float:
        """计算时间新鲜度加成"""
        from datetime import datetime, timedelta
        
        created_at = source.get("created_at")
        if not created_at:
            return 0
        
        try:
            if isinstance(created_at, str):
                created = datetime.fromisoformat(created_at)
            else:
                created = created_at
            
            age = datetime.now() - created
            
            if age < timedelta(hours=1):
                return 20
            elif age < timedelta(days=1):
                return 10
            elif age < timedelta(days=7):
                return 5
            else:
                return 0
        except:
            return 0
    
    def get_top_sources(
        self,
        sources: List[Dict[str, Any]],
        n: int = 5
    ) -> List[Dict[str, Any]]:
        """获取 Top-N 源"""
        ranked_ids = set(self.rank(sources)[:n])
        return [s for s in sources if s.get("source_id") in ranked_ids]
    
    def set_source_weight(self, source_type: str, weight: float):
        """设置源类型权重"""
        self.source_weights[source_type] = weight
    
    def set_importance_multiplier(self, importance: str, multiplier: float):
        """设置重要性乘数"""
        self.importance_multipliers[importance] = multiplier
