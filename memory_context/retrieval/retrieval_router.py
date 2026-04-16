"""Retrieval system for memory context."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class RetrievalRequest:
    """Request for memory retrieval."""
    query: str
    sources: list[str]  # session, memory, document, skill, rule, report
    max_results: int = 10
    min_score: float = 0.0
    profile: Optional[str] = None
    token_budget: Optional[int] = None


@dataclass
class RetrievalResult:
    """Result from retrieval."""
    query: str
    results: list[dict]
    total_count: int
    engine: str
    latency_ms: float


class RetrievalRouter:
    """Routes retrieval requests to appropriate engines."""
    
    def __init__(self):
        self.engines = {}
    
    def register_engine(self, name: str, engine):
        self.engines[name] = engine
    
    def route(self, request: RetrievalRequest) -> RetrievalResult:
        """Route to best engine based on request."""
        # Default to hybrid if available
        if "hybrid" in self.engines:
            return self.engines["hybrid"].search(request)
        elif "vector" in self.engines:
            return self.engines["vector"].search(request)
        elif "tfidf" in self.engines:
            return self.engines["tfidf"].search(request)
        else:
            raise RuntimeError("No retrieval engine available")
    
    def search(self, query: str, sources: list[str] = None, **kwargs) -> RetrievalResult:
        """Convenience method for simple searches."""
        request = RetrievalRequest(
            query=query,
            sources=sources or ["memory", "document"],
            **kwargs
        )
        return self.route(request)
