"""Retrieval Router - 统一检索路由"""

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


@dataclass
class RetrievalResult:
    """检索结果"""
    query: str
    results: List[Dict[str, Any]]
    total_count: int
    source_counts: Dict[str, int]
    engine: str
    latency_ms: float
    retrieved_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "results": self.results,
            "total_count": self.total_count,
            "source_counts": self.source_counts,
            "engine": self.engine,
            "latency_ms": self.latency_ms,
            "retrieved_at": self.retrieved_at.isoformat()
        }


class RetrievalRouter:
    """
    统一检索路由
    
    职责：
    - 决定从哪些源检索
    - 路由到合适的检索引擎
    - 合并和排序结果
    - 应用 Token 预算
    """
    
    def __init__(self):
        self._engines: Dict[str, Any] = {}
        self._source_priorities: Dict[str, int] = {
            "rule": 100,
            "memory": 80,
            "document": 60,
            "session": 40,
            "skill": 30,
            "report": 20
        }
    
    def register_engine(self, name: str, engine):
        """注册检索引擎"""
        self._engines[name] = engine
    
    def set_source_priority(self, source: str, priority: int):
        """设置源优先级"""
        self._source_priorities[source] = priority
    
    def route(self, request: RetrievalRequest) -> RetrievalResult:
        """
        路由检索请求
        
        1. 确定检索源
        2. 调用对应引擎
        3. 合并结果
        4. 排序和裁剪
        """
        start_time = time.time()
        
        # 1. 确定检索源
        sources = self._determine_sources(request)
        
        # 2. 从各源检索
        all_results = []
        source_counts = {}
        
        for source in sources:
            source_results = self._retrieve_from_source(source, request)
            source_counts[source] = len(source_results)
            all_results.extend(source_results)
        
        # 3. 排序
        sorted_results = self._sort_results(all_results)
        
        # 4. 裁剪
        final_results = sorted_results[:request.max_results]
        
        # 5. 应用 Token 预算
        if request.token_budget:
            final_results = self._apply_token_budget(final_results, request.token_budget)
        
        latency = (time.time() - start_time) * 1000
        
        return RetrievalResult(
            query=request.query,
            results=final_results,
            total_count=len(all_results),
            source_counts=source_counts,
            engine="retrieval_router",
            latency_ms=latency
        )
    
    def _determine_sources(self, request: RetrievalRequest) -> List[str]:
        """确定检索源"""
        # 如果请求指定了源，使用请求的
        if request.sources:
            return request.sources
        
        # 否则根据 profile 决定
        profile_sources = {
            "developer": ["memory", "document", "skill"],
            "operator": ["memory", "document", "report"],
            "auditor": ["rule", "report", "document"],
            "admin": ["memory", "document", "rule", "skill", "report"],
            "default": ["memory", "document"]
        }
        
        return profile_sources.get(request.profile, profile_sources["default"])
    
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
