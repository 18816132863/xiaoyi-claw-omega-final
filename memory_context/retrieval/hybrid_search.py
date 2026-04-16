"""Hybrid search combining vector and keyword search."""

import time
from typing import Optional
from .retrieval_router import RetrievalRequest, RetrievalResult


class HybridSearch:
    """Combines vector and keyword search for better results."""
    
    def __init__(self, vector_engine=None, keyword_engine=None, weights: dict = None):
        self.vector_engine = vector_engine
        self.keyword_engine = keyword_engine
        self.weights = weights or {"vector": 0.7, "keyword": 0.3}
    
    def search(self, request: RetrievalRequest) -> RetrievalResult:
        """Perform hybrid search."""
        start_time = time.time()
        
        vector_results = []
        keyword_results = []
        
        if self.vector_engine:
            vector_results = self.vector_engine.search(request.query, request.max_results * 2)
        
        if self.keyword_engine:
            keyword_results = self.keyword_engine.search(request.query, request.max_results * 2)
        
        # Merge and re-rank
        merged = self._merge_results(vector_results, keyword_results)
        
        # Apply score filter
        filtered = [r for r in merged if r.get("score", 0) >= request.min_score]
        
        # Limit results
        final_results = filtered[:request.max_results]
        
        latency = (time.time() - start_time) * 1000
        
        return RetrievalResult(
            query=request.query,
            results=final_results,
            total_count=len(filtered),
            engine="hybrid",
            latency_ms=latency
        )
    
    def _merge_results(self, vector_results: list, keyword_results: list) -> list:
        """Merge and deduplicate results."""
        merged = {}
        
        for result in vector_results:
            rid = result.get("id")
            if rid:
                merged[rid] = result.copy()
                merged[rid]["score"] = result.get("score", 0) * self.weights["vector"]
        
        for result in keyword_results:
            rid = result.get("id")
            if rid:
                if rid in merged:
                    # Combine scores
                    merged[rid]["score"] += result.get("score", 0) * self.weights["keyword"]
                else:
                    merged[rid] = result.copy()
                    merged[rid]["score"] = result.get("score", 0) * self.weights["keyword"]
        
        # Sort by score
        return sorted(merged.values(), key=lambda x: x.get("score", 0), reverse=True)
