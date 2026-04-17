"""
Retrieval Router - 正式检索路由主链
Phase3 Group4 核心模块
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import time


class SourceType(Enum):
    """检索源类型"""
    SESSION = "session"
    MEMORY = "memory"
    DOCUMENT = "document"
    SKILL = "skill"
    RULE = "rule"
    REPORT = "report"
    SESSION_HISTORY = "session_history"
    LONG_TERM_MEMORY = "long_term_memory"
    REPORT_MEMORY = "report_memory"
    WORKFLOW_HISTORY = "workflow_history"
    SKILL_HISTORY = "skill_history"
    USER_PREFERENCE = "user_preference"
    COMPANY_KNOWLEDGE = "company_knowledge"
    EXTERNAL_KNOWLEDGE = "external_knowledge"


@dataclass
class RetrievalRequest:
    """检索请求"""
    query: str
    sources: List[str] = field(default_factory=lambda: ["memory", "document"])
    max_results: int = 10
    min_score: float = 0.0
    profile: str = "default"
    token_budget: Optional[int] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    risk_level: str = "low"
    capabilities: List[str] = field(default_factory=list)
    trace_id: Optional[str] = None  # 支持传入 trace_id
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SourceResult:
    """来源检索结果"""
    source_id: str
    source_type: str
    query_used: str
    hits_count: int = 0
    filtered_count: int = 0
    returned_count: int = 0
    tokens_used: int = 0
    latency_ms: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type,
            "query_used": self.query_used,
            "hits_count": self.hits_count,
            "filtered_count": self.filtered_count,
            "returned_count": self.returned_count,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "error": self.error
        }


@dataclass
class RetrievalResult:
    """检索结果"""
    query: str
    results: List[Dict[str, Any]]
    total_count: int
    source_counts: Dict[str, int]
    engine: str
    latency_ms: float
    source_results: List[SourceResult] = field(default_factory=list)
    allowed_sources: List[str] = field(default_factory=list)
    denied_sources: List[str] = field(default_factory=list)
    retrieved_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "results": self.results,
            "total_count": self.total_count,
            "source_counts": self.source_counts,
            "engine": self.engine,
            "latency_ms": self.latency_ms,
            "source_results": [sr.to_dict() for sr in self.source_results],
            "allowed_sources": self.allowed_sources,
            "denied_sources": self.denied_sources,
            "retrieved_at": self.retrieved_at.isoformat()
        }


class RetrievalRouter:
    """
    正式检索路由主链
    
    主链流程：
    1. 接收 RetrievalRequest
    2. 调 SourcePolicyRouter 决定允许查哪些 source
    3. 从各源检索
    4. 合并结果
    5. 排序和裁剪
    6. 生成 SourceResult 记录
    7. 返回 RetrievalResult（含 source_results 供 trace 使用）
    """
    
    def __init__(
        self,
        source_policy_router=None,
        retrieval_trace_store=None
    ):
        self._engines: Dict[str, Any] = {}
        self._source_priorities: Dict[str, int] = {
            "rule": 100,
            "memory": 80,
            "document": 60,
            "session": 40,
            "skill": 30,
            "report": 20,
            "session_history": 100,
            "user_preference": 95,
            "long_term_memory": 80,
            "workflow_history": 70,
            "skill_history": 60,
            "report_memory": 50,
            "company_knowledge": 40,
            "external_knowledge": 30
        }
        
        # Group4 新模块
        self._source_policy_router = source_policy_router
        self._retrieval_trace_store = retrieval_trace_store
    
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
    
    def register_engine(self, name: str, engine):
        """注册检索引擎"""
        self._engines[name] = engine
    
    def set_source_priority(self, source: str, priority: int):
        """设置源优先级"""
        self._source_priorities[source] = priority
    
    def route(self, request: RetrievalRequest) -> RetrievalResult:
        """
        路由检索请求
        
        主链流程：
        1. 接收 RetrievalRequest
        2. 调 SourcePolicyRouter 决定允许查哪些 source
        3. 从各源检索
        4. 合并结果
        5. 排序和裁剪
        6. 生成 SourceResult 记录
        7. 返回 RetrievalResult
        """
        start_time = time.time()
        
        # ========== 第一步：调 SourcePolicyRouter 决定允许查哪些 source ==========
        from memory_context.retrieval.source_policy_router import RiskLevel
        
        risk_level_enum = {
            "low": RiskLevel.LOW,
            "medium": RiskLevel.MEDIUM,
            "high": RiskLevel.HIGH,
            "critical": RiskLevel.CRITICAL
        }.get(request.risk_level, RiskLevel.LOW)
        
        routing_result = self.source_policy_router.route(
            profile=request.profile,
            risk_level=risk_level_enum,
            capabilities=request.capabilities
        )
        
        allowed_sources = [s.value for s in routing_result.allowed_sources]
        denied_sources = [s.value for s in routing_result.denied_sources]
        
        # ========== 第二步：确定实际检索源（取请求和允许的交集）==========
        if request.sources:
            # 过滤掉不允许的源
            sources = [s for s in request.sources if s in allowed_sources]
        else:
            sources = allowed_sources
        
        # ========== 第三步：从各源检索 ==========
        all_results = []
        source_counts = {}
        source_results = []
        
        for source in sources:
            source_start = time.time()
            source_result = self._retrieve_from_source(source, request)
            source_latency = int((time.time() - source_start) * 1000)
            
            source_counts[source] = len(source_result)
            all_results.extend(source_result)
            
            # 生成 SourceResult 记录
            sr = SourceResult(
                source_id=f"src_{source}",
                source_type=source,
                query_used=request.query,
                hits_count=len(source_result),
                filtered_count=0,
                returned_count=len(source_result),
                tokens_used=sum(len(r.get("content", "")) // 4 for r in source_result),
                latency_ms=source_latency
            )
            source_results.append(sr)
        
        # ========== 第四步：排序 ==========
        sorted_results = self._sort_results(all_results)
        
        # ========== 第五步：裁剪 ==========
        final_results = sorted_results[:request.max_results]
        
        # ========== 第六步：应用 Token 预算 ==========
        if request.token_budget:
            final_results = self._apply_token_budget(final_results, request.token_budget)
        
        latency = (time.time() - start_time) * 1000
        
        # ========== 第七步：如果存在 trace_id，保存到 retrieval_trace_store ==========
        if request.trace_id:
            from memory_context.retrieval.retrieval_trace_store import SourceResult
            
            # 更新或创建 trace
            existing_trace = self.retrieval_trace_store.get_trace(request.trace_id)
            
            if existing_trace:
                # 更新现有 trace
                existing_trace.allowed_sources = allowed_sources
                existing_trace.denied_sources = denied_sources
                existing_trace.source_results = source_results
                existing_trace.ranking_result = {
                    "total_items": len(all_results),
                    "ranked_items": len(final_results)
                }
                existing_trace.budget_result = {
                    "budget_tokens": request.token_budget or 0,
                    "used_tokens": sum(len(r.get("content", "")) // 4 for r in final_results)
                }
                existing_trace.final_result = {
                    "total_results": len(final_results),
                    "source_counts": source_counts,
                    "latency_ms": latency
                }
                self.retrieval_trace_store.update_trace(existing_trace)
            else:
                # 创建新 trace
                new_trace = self.retrieval_trace_store.create_trace(
                    task_id=request.metadata.get("task_id", "unknown"),
                    original_query=request.query,
                    profile=request.profile,
                    risk_level=request.risk_level
                )
                new_trace.allowed_sources = allowed_sources
                new_trace.denied_sources = denied_sources
                new_trace.source_results = source_results
                new_trace.final_result = {
                    "total_results": len(final_results),
                    "source_counts": source_counts,
                    "latency_ms": latency
                }
                self.retrieval_trace_store.update_trace(new_trace)
        
        return RetrievalResult(
            query=request.query,
            results=final_results,
            total_count=len(all_results),
            source_counts=source_counts,
            engine="retrieval_router",
            latency_ms=latency,
            source_results=source_results,
            allowed_sources=allowed_sources,
            denied_sources=denied_sources
        )
    
    def _retrieve_from_source(
        self,
        source: str,
        request: RetrievalRequest
    ) -> List[Dict[str, Any]]:
        """从单个源检索"""
        # 检查是否有注册的引擎
        if source in self._engines:
            engine = self._engines[source]
            return engine.search(request.query, request.max_results)
        
        # 否则返回空（后续可接入真实引擎）
        return []
    
    def _sort_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """排序结果"""
        def get_score(result: Dict) -> float:
            # 综合分数 = 相关性分数 * 源优先级权重
            relevance = result.get("score", 0.5)
            source = result.get("source_type", "document")
            priority = self._source_priorities.get(source, 50) / 100
            return relevance * priority
        
        return sorted(results, key=get_score, reverse=True)
    
    def _apply_token_budget(
        self,
        results: List[Dict[str, Any]],
        budget: int
    ) -> List[Dict[str, Any]]:
        """应用 Token 预算"""
        budgeted = []
        current_tokens = 0
        
        for result in results:
            content = result.get("content", "")
            estimated_tokens = len(content) // 4
            
            if current_tokens + estimated_tokens <= budget:
                budgeted.append(result)
                current_tokens += estimated_tokens
            else:
                break
        
        return budgeted
    
    def search(
        self,
        query: str,
        sources: List[str] = None,
        max_results: int = 10,
        **kwargs
    ) -> RetrievalResult:
        """便捷搜索方法"""
        request = RetrievalRequest(
            query=query,
            sources=sources,
            max_results=max_results,
            **kwargs
        )
        return self.route(request)


# 全局单例
_retrieval_router = None


def get_retrieval_router() -> RetrievalRouter:
    """获取检索路由器单例"""
    global _retrieval_router
    if _retrieval_router is None:
        _retrieval_router = RetrievalRouter()
    return _retrieval_router
