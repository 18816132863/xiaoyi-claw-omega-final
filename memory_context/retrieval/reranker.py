"""Reranker for retrieval results."""

from typing import List, Dict, Optional
import re


class Reranker:
    """Reranks retrieval results based on various signals."""
    
    def __init__(self):
        self.boost_factors = {
            "exact_match": 0.2,
            "recency": 0.1,
            "importance": 0.15,
            "source_quality": 0.1
        }
    
    def rerank(
        self,
        results: List[Dict],
        query: str,
        context: Dict = None
    ) -> List[Dict]:
        """Rerank results with additional signals."""
        reranked = []
        
        for result in results:
            score = result.get("score", 0)
            
            # Exact match boost
            if self._has_exact_match(result.get("content", ""), query):
                score += self.boost_factors["exact_match"]
            
            # Recency boost
            recency = self._get_recency_score(result)
            score += recency * self.boost_factors["recency"]
            
            # Importance boost
            importance = result.get("metadata", {}).get("importance", "medium")
            importance_scores = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.1}
            score += importance_scores.get(importance, 0.4) * self.boost_factors["importance"]
            
            # Source quality boost
            source_type = result.get("source_type", "")
            source_scores = {"rule": 1.0, "decision_log": 0.9, "document": 0.7, "session": 0.5}
            score += source_scores.get(source_type, 0.5) * self.boost_factors["source_quality"]
            
            result["reranked_score"] = min(score, 1.0)
            reranked.append(result)
        
        return sorted(reranked, key=lambda x: x.get("reranked_score", 0), reverse=True)
    
    def _has_exact_match(self, content: str, query: str) -> bool:
        """Check for exact phrase match."""
        return query.lower() in content.lower()
    
    def _get_recency_score(self, result: Dict) -> float:
        """Calculate recency score (0-1)."""
        from datetime import datetime, timedelta
        
        created_at = result.get("created_at")
        if not created_at:
            return 0.5
        
        try:
            if isinstance(created_at, str):
                created = datetime.fromisoformat(created_at)
            else:
                created = created_at
            
            age = datetime.now() - created
            
            if age < timedelta(days=1):
                return 1.0
            elif age < timedelta(days=7):
                return 0.8
            elif age < timedelta(days=30):
                return 0.6
            elif age < timedelta(days=90):
                return 0.4
            else:
                return 0.2
        except:
            return 0.5


class CrossEncoderReranker(Reranker):
    """Uses cross-encoder model for reranking."""
    
    def __init__(self, model_name: str = None):
        super().__init__()
        self.model_name = model_name
        self._model = None
    
    def _load_model(self):
        if self._model is None:
            # TODO: Load cross-encoder model
            pass
        return self._model
    
    def rerank(
        self,
        results: List[Dict],
        query: str,
        context: Dict = None
    ) -> List[Dict]:
        """Rerank using cross-encoder."""
        # Fall back to base reranker if no model
        if self._model is None:
            return super().rerank(results, query, context)
        
        # TODO: Use cross-encoder for reranking
        return super().rerank(results, query, context)
