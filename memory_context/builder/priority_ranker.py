"""Priority ranker for context sources."""

from typing import List, Dict
from enum import Enum


class SourcePriority(Enum):
    """Priority levels for source types."""
    CRITICAL = 100
    HIGH = 75
    MEDIUM = 50
    LOW = 25


class PriorityRanker:
    """Ranks sources by priority for context construction."""
    
    def __init__(self):
        # Default priority by source type
        self.type_priority = {
            "rule": SourcePriority.CRITICAL.value,
            "decision_log": SourcePriority.HIGH.value,
            "document": SourcePriority.MEDIUM.value,
            "memory": SourcePriority.MEDIUM.value,
            "session": SourcePriority.LOW.value,
            "report": SourcePriority.LOW.value,
            "skill": SourcePriority.MEDIUM.value,
            "additional": SourcePriority.HIGH.value
        }
        
        # Importance multipliers
        self.importance_multipliers = {
            "critical": 1.5,
            "high": 1.2,
            "medium": 1.0,
            "low": 0.8
        }
    
    def rank(self, sources: List[Dict]) -> List[str]:
        """
        Rank sources and return ordered source IDs.
        
        Returns:
            List of source_ids in priority order
        """
        scored = []
        
        for source in sources:
            score = self._calculate_score(source)
            source_id = source.get("source_id", str(len(scored)))
            scored.append((source_id, score))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [s[0] for s in scored]
    
    def _calculate_score(self, source: Dict) -> float:
        """Calculate priority score for a source."""
        # Base score from type
        source_type = source.get("type", "document")
        base_score = self.type_priority.get(source_type, SourcePriority.MEDIUM.value)
        
        # Relevance score
        relevance = source.get("relevance", 0.5)
        
        # Importance multiplier
        importance = source.get("metadata", {}).get("importance", "medium")
        multiplier = self.importance_multipliers.get(importance, 1.0)
        
        # Recency bonus (if available)
        recency_bonus = self._get_recency_bonus(source)
        
        # Final score
        final_score = (base_score * relevance * multiplier) + recency_bonus
        
        return final_score
    
    def _get_recency_bonus(self, source: Dict) -> float:
        """Calculate recency bonus."""
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
    
    def set_type_priority(self, source_type: str, priority: int):
        """Set custom priority for a source type."""
        self.type_priority[source_type] = priority
    
    def get_top_sources(self, sources: List[Dict], n: int = 5) -> List[Dict]:
        """Get top N sources by priority."""
        ranked_ids = self.rank(sources)
        id_set = set(ranked_ids[:n])
        return [s for s in sources if s.get("source_id") in id_set]
