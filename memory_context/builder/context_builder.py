"""
Context Builder - 正式上下文构建主链
Phase3 Group4 核心模块
"""

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
    trace_id: Optional[str] = None
    injection_plan: Optional[Dict] = None
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
            "trace_id": self.trace_id,
            "injection_plan": self.injection_plan,
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
    正式上下文构建主链
    
    主链流程：
    1. 接收 task_id / profile / intent / sources / token_budget
    2. 调 QueryRewriter 重写 query
    3. 调 SourcePolicyRouter 决定允许查哪些 source
    4. 调 RetrievalRouter 检索
    5. 调 SourceConfidenceRanker 排可信度
    6. 调 ContextInjectionPlanner 规划注入
    7. 调 ConflictResolver 做冲突消解
    8. 调 ContextBudgeter 做 token 裁剪
    9. 调 ContextSummaryCompactor 做总结压缩
    10. 生成 ContextBundle
    11. 生成并保存 retrieval trace
    """
    
    def __init__(
        self,
        retrieval_router=None,
        reranker=None,
        budgeter=None,
        conflict_resolver=None,
        priority_ranker=None,
        session_history=None,
        # Group4 新模块
        query_rewriter=None,
        source_policy_router=None,
        retrieval_trace_store=None,
        context_injection_planner=None,
        context_summary_compactor=None,
        source_confidence_ranker=None
    ):
        self.retrieval_router = retrieval_router
        self.reranker = reranker
        self.budgeter = budgeter
        self.conflict_resolver = conflict_resolver
        self.priority_ranker = priority_ranker
        self.session_history = session_history
        
        # Group4 新模块
        self._query_rewriter = query_rewriter
        self._source_policy_router = source_policy_router
        self._retrieval_trace_store = retrieval_trace_store
        self._context_injection_planner = context_injection_planner
        self._context_summary_compactor = context_summary_compactor
        self._source_confidence_ranker = source_confidence_ranker
    
    @property
    def query_rewriter(self):
        """延迟加载 query_rewriter"""
        if self._query_rewriter is None:
            from memory_context.retrieval.query_rewriter import get_query_rewriter
            self._query_rewriter = get_query_rewriter()
        return self._query_rewriter
    
    @property
    def source_policy_router(self):
        """延迟加载 source_policy_router"""
        if self._source_policy_router is None:
            from memory_context.retrieval.source_policy_router import get_source_policy_router, RiskLevel
            self._source_policy_router = get_source_policy_router()
        return self._source_policy_router
    
    @property
    def retrieval_trace_store(self):
        """延迟加载 retrieval_trace_store"""
        if self._retrieval_trace_store is None:
            from memory_context.retrieval.retrieval_trace_store import get_retrieval_trace_store
            self._retrieval_trace_store = get_retrieval_trace_store()
        return self._retrieval_trace_store
    
    @property
    def context_injection_planner(self):
        """延迟加载 context_injection_planner"""
        if self._context_injection_planner is None:
            from memory_context.builder.context_injection_planner import get_context_injection_planner
            self._context_injection_planner = get_context_injection_planner()
        return self._context_injection_planner
    
    @property
    def context_summary_compactor(self):
        """延迟加载 context_summary_compactor"""
        if self._context_summary_compactor is None:
            from memory_context.builder.context_summary_compactor import get_context_summary_compactor
            self._context_summary_compactor = get_context_summary_compactor()
        return self._context_summary_compactor
    
    @property
    def source_confidence_ranker(self):
        """延迟加载 source_confidence_ranker"""
        if self._source_confidence_ranker is None:
            from memory_context.builder.source_confidence_ranker import get_source_confidence_ranker
            self._source_confidence_ranker = get_source_confidence_ranker()
        return self._source_confidence_ranker
    
    def build_context(
        self,
        task_id: str,
        profile: str,
        intent: str,
        sources: List[str] = None,
        token_budget: int = 8000,
        additional_context: Dict = None,
        risk_level: str = "low",
        capabilities: List[str] = None
    ) -> ContextBundle:
        """
        Build context bundle for task execution.
        
        主链流程：
        1. 接收 task_id / profile / intent / sources / token_budget
        2. 调 QueryRewriter 重写 query
        3. 调 SourcePolicyRouter 决定允许查哪些 source
        4. 调 RetrievalRouter 检索
        5. 调 SourceConfidenceRanker 排可信度
        6. 调 ContextInjectionPlanner 规划注入
        7. 调 ConflictResolver 做冲突消解
        8. 调 ContextBudgeter 做 token 裁剪
        9. 调 ContextSummaryCompactor 做总结压缩
        10. 生成 ContextBundle
        11. 生成并保存 retrieval trace
        
        Args:
            task_id: Unique task identifier
            profile: User/system profile
            intent: Task intent description
            sources: Explicit source types to query
            token_budget: Maximum tokens for context
            additional_context: Extra context to include
            risk_level: Risk level for source policy
            capabilities: Granted capabilities
        
        Returns:
            ContextBundle ready for task execution
        """
        import time
        start_time = time.time()
        capabilities = capabilities or []
        
        # ========== 第一步：创建 retrieval trace ==========
        trace = self.retrieval_trace_store.create_trace(
            task_id=task_id,
            original_query=intent,
            profile=profile,
            risk_level=risk_level
        )
        
        # ========== 第二步：调 QueryRewriter 重写 query ==========
        rewrite_result = self.query_rewriter.rewrite(
            query=intent,
            context={"profile": profile, "task_id": task_id},
            profile=profile
        )
        
        trace.rewritten_query = rewrite_result.rewritten_query
        trace.query_rewrite_reason = rewrite_result.reason
        
        # ========== 第三步：调 SourcePolicyRouter 决定允许查哪些 source ==========
        from memory_context.retrieval.source_policy_router import RiskLevel
        
        risk_level_enum = {
            "low": RiskLevel.LOW,
            "medium": RiskLevel.MEDIUM,
            "high": RiskLevel.HIGH,
            "critical": RiskLevel.CRITICAL
        }.get(risk_level, RiskLevel.LOW)
        
        routing_result = self.source_policy_router.route(
            profile=profile,
            risk_level=risk_level_enum,
            capabilities=capabilities
        )
        
        trace.allowed_sources = [s.value for s in routing_result.allowed_sources]
        trace.denied_sources = [s.value for s in routing_result.denied_sources]
        
        # ========== 第四步：调 RetrievalRouter 检索 ==========
        all_sources = []
        
        # 4.1 始终添加任务意图作为核心上下文
        all_sources.append({
            "type": "intent",
            "content": f"任务意图: {intent}",
            "relevance": 1.0,
            "source_id": "task_intent",
            "source_type": "session_history",
            "tokens": len(intent) // 4 + 5
        })
        
        # 4.2 添加配置信息
        all_sources.append({
            "type": "profile",
            "content": f"执行配置: {profile}",
            "relevance": 0.9,
            "source_id": "profile_info",
            "source_type": "session_history",
            "tokens": 10
        })
        
        # 4.3 添加任务ID
        all_sources.append({
            "type": "task",
            "content": f"任务ID: {task_id}",
            "relevance": 0.8,
            "source_id": "task_id",
            "source_type": "session_history",
            "tokens": 5
        })
        
        # 4.4 如果有会话历史，添加最近的上下文
        if self.session_history:
            history_context = self.session_history.to_context_string(max_tokens=1000)
            if history_context:
                all_sources.append({
                    "type": "session",
                    "content": f"会话历史:\n{history_context}",
                    "relevance": 0.7,
                    "source_id": "session_history",
                    "source_type": "session_history",
                    "tokens": len(history_context) // 4
                })
        
        # 4.5 从检索系统获取更多上下文（只查允许的 source）
        allowed_source_types = [s.value for s in routing_result.allowed_sources]
        retrieved_sources = self._retrieve(
            rewrite_result.rewritten_query,
            allowed_source_types,
            token_budget,
            trace
        )
        all_sources.extend(retrieved_sources)
        
        # 4.6 添加额外上下文
        if additional_context:
            for key, value in additional_context.items():
                all_sources.append({
                    "type": "additional",
                    "content": f"{key}: {value}",
                    "relevance": 0.6,
                    "source_id": f"additional_{key}",
                    "source_type": "session_history",
                    "tokens": len(str(value)) // 4
                })
        
        # ========== 第五步：调 SourceConfidenceRanker 排可信度 ==========
        ranking_result = self.source_confidence_ranker.rank(
            sources=all_sources,
            query=rewrite_result.rewritten_query,
            context={"profile": profile}
        )
        
        trace.ranking_result = ranking_result.to_dict()
        
        # 获取可信度分数
        confidence_scores = {
            score.source_id: score.score
            for score in ranking_result.ranked_items
        }
        
        # ========== 第六步：调 ContextInjectionPlanner 规划注入 ==========
        injection_plan = self.context_injection_planner.plan(
            task_id=task_id,
            sources=all_sources,
            token_budget=token_budget,
            confidence_scores=confidence_scores
        )
        
        trace.injection_plan = injection_plan.to_dict()
        
        # ========== 第七步：根据 injection plan 过滤来源 ==========
        # 只保留 required 和 optional（未被 suppressed 的）
        allowed_source_ids = set(injection_plan.final_injection_order)
        suppressed_ids = {s.source_id for s in injection_plan.suppressed_sources}
        
        filtered_sources = [
            s for s in all_sources
            if s.get("source_id") in allowed_source_ids and s.get("source_id") not in suppressed_ids
        ]
        
        # 按 injection order 排序
        source_order_map = {
            s.source_id: s.injection_order
            for s in injection_plan.required_sources + injection_plan.optional_sources
        }
        filtered_sources.sort(
            key=lambda s: source_order_map.get(s.get("source_id", ""), 999)
        )
        
        # ========== 第八步：调 ConflictResolver 做冲突消解 ==========
        resolved_sources, conflicts = self._resolve_conflicts(filtered_sources)
        
        trace.conflict_resolution = {
            "conflicts_found": len(conflicts),
            "resolutions": conflicts
        }
        
        # ========== 第九步：调 ContextBudgeter 做 token 裁剪 ==========
        budgeted_sources, actual_tokens, trimmed = self._apply_budget(
            resolved_sources, token_budget
        )
        
        trace.budget_result = {
            "budget_tokens": token_budget,
            "used_tokens": actual_tokens,
            "trimmed_tokens": sum(s.get("tokens", 0) for s in trimmed),
            "trimmed_items": [{"source_id": s.get("source_id")} for s in trimmed]
        }
        
        # ========== 第十步：调 ContextSummaryCompactor 做总结压缩 ==========
        if actual_tokens > token_budget * 0.9:
            compaction_result = self.context_summary_compactor.compact(
                content=budgeted_sources,
                target_tokens=int(token_budget * 0.8),
                strategy="moderate"
            )
            budgeted_sources = compaction_result.preserved_items
            actual_tokens = compaction_result.compacted_tokens
        
        # ========== 第十一步：确保至少有基本上下文 ==========
        if not budgeted_sources:
            budgeted_sources = [
                {
                    "type": "fallback",
                    "content": f"任务: {intent} (配置: {profile})",
                    "relevance": 1.0,
                    "source_id": "fallback_context",
                    "source_type": "session_history",
                    "tokens": len(intent) // 4 + 10
                }
            ]
            actual_tokens = len(intent) // 4 + 10
        
        # ========== 第十二步：生成优先级顺序 ==========
        priority_order = [s.get("source_id", str(i)) for i, s in enumerate(budgeted_sources)]
        
        # ========== 第十三步：完成 trace 并保存 ==========
        duration_ms = int((time.time() - start_time) * 1000)
        
        trace.final_result = {
            "injected_sources": [s.get("source_id") for s in budgeted_sources],
            "total_items": len(budgeted_sources),
            "total_tokens": actual_tokens,
            "compression_ratio": actual_tokens / token_budget if token_budget > 0 else 1.0
        }
        
        self.retrieval_trace_store.finalize_trace(
            trace.trace_id,
            trace.final_result,
            duration_ms
        )
        
        # ========== 第十四步：生成 ContextBundle ==========
        return ContextBundle(
            task_id=task_id,
            profile=profile,
            intent=intent,
            sources=budgeted_sources,
            token_count=actual_tokens,
            token_budget=token_budget,
            conflicts_resolved=conflicts,
            priority_order=priority_order,
            trace_id=trace.trace_id,
            injection_plan=injection_plan.to_dict()
        )
    
    def _retrieve(
        self,
        intent: str,
        allowed_sources: List[str],
        token_budget: int,
        trace
    ) -> List[Dict]:
        """Retrieve from all relevant sources."""
        if not self.retrieval_router:
            return []
        
        # 正确导入
        try:
            from memory_context.retrieval.retrieval_router import RetrievalRequest
            from memory_context.retrieval.retrieval_trace_store import SourceResult
            
            request = RetrievalRequest(
                query=intent,
                sources=allowed_sources,
                max_results=20,
                token_budget=token_budget
            )
            
            result = self.retrieval_router.route(request)
            
            # 记录到 trace
            if hasattr(result, 'source_results'):
                for sr in result.source_results:
                    self.retrieval_trace_store.add_source_result(trace.trace_id, sr)
            
            return result.results
        except ImportError:
            return []
    
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
        trimmed = []
        total = 0
        
        for source in sources:
            content = source.get("content", "")
            estimated = source.get("tokens", len(content) // 4)
            
            if total + estimated <= token_budget:
                budgeted.append(source)
                total += estimated
            else:
                # 如果预算不够，至少保留高相关性的源
                if source.get("relevance", 0) >= 0.8 and total < token_budget * 0.5:
                    budgeted.append(source)
                    total += estimated
                else:
                    trimmed.append(source)
        
        return budgeted, total, trimmed


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
