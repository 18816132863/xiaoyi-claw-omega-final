"""Context builder - unified entry point for context construction."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, List, Dict
import json


@dataclass
class ContextBundle:
    """Final context bundle for task execution."""
    task_id: str
    profile: str
    intent: str
    sources: List[Dict]
    token_count: int
    token_budget: int
    conflicts_resolved: List[Dict]
    priority_order: List[str]
    built_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "profile": self.profile,
            "intent": self.intent,
            "sources": self.sources,
            "token_count": self.token_count,
            "token_budget": self.token_budget,
            "conflicts_resolved": self.conflicts_resolved,
            "priority_order": self.priority_order,
            "built_at": self.built_at.isoformat()
        }
    
    def to_prompt_context(self) -> str:
        """Convert to string for LLM prompt."""
        lines = []
        for source in self.sources:
            source_type = source.get("type", "unknown")
            content = source.get("content", "")
            relevance = source.get("relevance", 0)
            lines.append(f"[{source_type}] (relevance: {relevance:.2f})\n{content}\n")
        return "\n".join(lines)


class ContextBuilder:
    """
    Unified entry point for context construction.
    
    Any upper layer that needs context must go through this interface.
    """
    
    def __init__(
        self,
        retrieval_router=None,
        reranker=None,
        budgeter=None,
        conflict_resolver=None,
        priority_ranker=None
    ):
        self.retrieval_router = retrieval_router
        self.reranker = reranker
        self.budgeter = budgeter
        self.conflict_resolver = conflict_resolver
        self.priority_ranker = priority_ranker
    
    def build_context(
        self,
        task_id: str,
        profile: str,
        intent: str,
        sources: List[str] = None,
        token_budget: int = 8000,
        additional_context: Dict = None
    ) -> ContextBundle:
        """
        Build context bundle for task execution.
        
        Args:
            task_id: Unique task identifier
            profile: User/system profile
            intent: Task intent description
            sources: Explicit source types to query
            token_budget: Maximum tokens for context
            additional_context: Extra context to include
        
        Returns:
            ContextBundle ready for task execution
        """
        # 1. Retrieve relevant information
        raw_sources = self._retrieve(intent, sources, token_budget)
        
        # 2. Rerank by relevance
        ranked_sources = self._rerank(raw_sources, intent)
        
        # 3. Resolve conflicts
        resolved_sources, conflicts = self._resolve_conflicts(ranked_sources)
        
        # 4. Apply token budget
        budgeted_sources, actual_tokens = self._apply_budget(
            resolved_sources, token_budget
        )
        
        # 5. Prioritize
        priority_order = self._prioritize(budgeted_sources)
        
        # 6. Add additional context if provided
        if additional_context:
            for key, value in additional_context.items():
                budgeted_sources.append({
                    "type": "additional",
                    "content": f"{key}: {value}",
                    "relevance": 1.0,
                    "source_id": f"additional_{key}"
                })
        
        return ContextBundle(
            task_id=task_id,
            profile=profile,
            intent=intent,
            sources=budgeted_sources,
            token_count=actual_tokens,
            token_budget=token_budget,
            conflicts_resolved=conflicts,
            priority_order=priority_order
        )
    
    def _retrieve(
        self,
        intent: str,
        sources: List[str],
        token_budget: int
    ) -> List[Dict]:
        """Retrieve from all relevant sources."""
        if not self.retrieval_router:
            return []
        
        from .retrieval.retrieval_router import RetrievalRequest
        
        request = RetrievalRequest(
            query=intent,
            sources=sources or ["memory", "document", "rule"],
            max_results=20,
            token_budget=token_budget
        )
        
        result = self.retrieval_router.route(request)
        return result.results
    
    def _rerank(self, sources: List[Dict], intent: str) -> List[Dict]:
        """Rerank sources by relevance."""
        if not self.reranker:
            return sources
        return self.reranker.rerank(sources, intent)
    
    def _resolve_conflicts(self, sources: List[Dict]) -> tuple[List[Dict], List[Dict]]:
        """Resolve conflicts between sources."""
        if not self.conflict_resolver:
            return sources, []
        return self.conflict_resolver.resolve(sources)
    
    def _apply_budget(
        self,
        sources: List[Dict],
        token_budget: int
    ) -> tuple[List[Dict], int]:
        """Apply token budget constraint."""
        if not self.budgeter:
            # Simple estimation
            budgeted = []
            total = 0
            for source in sources:
                content = source.get("content", "")
                estimated = len(content) // 4  # Rough token estimate
                if total + estimated <= token_budget:
                    budgeted.append(source)
                    total += estimated
            return budgeted, total
        
        return self.budgeter.apply(sources, token_budget)
    
    def _prioritize(self, sources: List[Dict]) -> List[str]:
        """Generate priority order."""
        if not self.priority_ranker:
            return [s.get("source_id", str(i)) for i, s in enumerate(sources)]
        return self.priority_ranker.rank(sources)


# Convenience function for direct use
def build_context(
    task_id: str,
    profile: str,
    intent: str,
    sources: List[str] = None,
    token_budget: int = 8000
) -> ContextBundle:
    """
    Convenience function to build context.
    
    Usage:
        bundle = build_context(
            task_id="task_123",
            profile="developer",
            intent="Find architecture documentation",
            token_budget=4000
        )
        prompt_context = bundle.to_prompt_context()
    """
    builder = ContextBuilder()
    return builder.build_context(
        task_id=task_id,
        profile=profile,
        intent=intent,
        sources=sources,
        token_budget=token_budget
    )
