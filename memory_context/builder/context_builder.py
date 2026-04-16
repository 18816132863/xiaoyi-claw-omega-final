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
        priority_ranker=None,
        session_history=None
    ):
        self.retrieval_router = retrieval_router
        self.reranker = reranker
        self.budgeter = budgeter
        self.conflict_resolver = conflict_resolver
        self.priority_ranker = priority_ranker
        self.session_history = session_history
    
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
        all_sources = []
        
        # 1. 始终添加任务意图作为核心上下文
        all_sources.append({
            "type": "intent",
            "content": f"任务意图: {intent}",
            "relevance": 1.0,
            "source_id": "task_intent"
        })
        
        # 2. 添加配置信息
        all_sources.append({
            "type": "profile",
            "content": f"执行配置: {profile}",
            "relevance": 0.9,
            "source_id": "profile_info"
        })
        
        # 3. 添加任务ID
        all_sources.append({
            "type": "task",
            "content": f"任务ID: {task_id}",
            "relevance": 0.8,
            "source_id": "task_id"
        })
        
        # 4. 如果有会话历史，添加最近的上下文
        if self.session_history:
            history_context = self.session_history.to_context_string(max_tokens=1000)
            if history_context:
                all_sources.append({
                    "type": "session",
                    "content": f"会话历史:\n{history_context}",
                    "relevance": 0.7,
                    "source_id": "session_history"
                })
        
        # 5. 尝试从检索系统获取更多上下文
        retrieved_sources = self._retrieve(intent, sources, token_budget)
        all_sources.extend(retrieved_sources)
        
        # 6. 添加额外上下文
        if additional_context:
            for key, value in additional_context.items():
                all_sources.append({
                    "type": "additional",
                    "content": f"{key}: {value}",
                    "relevance": 0.6,
                    "source_id": f"additional_{key}"
                })
        
        # 7. 重排序
        ranked_sources = self._rerank(all_sources, intent)
        
        # 8. 解决冲突
        resolved_sources, conflicts = self._resolve_conflicts(ranked_sources)
        
        # 9. 应用 token 预算
        budgeted_sources, actual_tokens = self._apply_budget(
            resolved_sources, token_budget
        )
        
        # 10. 确保至少有基本上下文
        if not budgeted_sources:
            budgeted_sources = [
                {
                    "type": "fallback",
                    "content": f"任务: {intent} (配置: {profile})",
                    "relevance": 1.0,
                    "source_id": "fallback_context"
                }
            ]
            actual_tokens = len(intent) // 4 + 10
        
        # 11. 生成优先级顺序
        priority_order = self._prioritize(budgeted_sources)
        
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
        
        # 正确导入
        try:
            from memory_context.retrieval.retrieval_router import RetrievalRequest
            
            request = RetrievalRequest(
                query=intent,
                sources=sources or ["memory", "document", "rule"],
                max_results=20,
                token_budget=token_budget
            )
            
            result = self.retrieval_router.route(request)
            return result.results
        except ImportError:
            return []
    
    def _rerank(self, sources: List[Dict], intent: str) -> List[Dict]:
        """Rerank sources by relevance."""
        if not self.reranker:
            # 简单排序：按 relevance 降序
            return sorted(sources, key=lambda s: s.get("relevance", 0), reverse=True)
        return self.reranker.rerank(sources, intent)
    
    def _resolve_conflicts(self, sources: List[Dict]) -> tuple:
        """Resolve conflicts between sources."""
        if not self.conflict_resolver:
            return sources, []
        return self.conflict_resolver.resolve(sources)
    
    def _apply_budget(
        self,
        sources: List[Dict],
        token_budget: int
    ) -> tuple:
        """Apply token budget constraint."""
        budgeted = []
        total = 0
        
        for source in sources:
            content = source.get("content", "")
            # 估算 token 数量（约 4 字符 = 1 token）
            estimated = max(len(content) // 4, 1)
            
            if total + estimated <= token_budget:
                budgeted.append(source)
                total += estimated
            else:
                # 如果预算不够，至少保留高相关性的源
                if source.get("relevance", 0) >= 0.8 and total < token_budget * 0.5:
                    budgeted.append(source)
                    total += estimated
        
        return budgeted, total
    
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
