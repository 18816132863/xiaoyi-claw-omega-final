"""
Retrieval Trace Store - 检索追踪存储
记录每次检索的完整过程
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
import uuid


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
class RetrievalTrace:
    """检索追踪记录"""
    trace_id: str
    task_id: str
    original_query: str
    rewritten_query: Optional[str] = None
    query_rewrite_reason: Optional[str] = None
    profile: str = "default"
    risk_level: str = "low"
    allowed_sources: List[str] = field(default_factory=list)
    denied_sources: List[str] = field(default_factory=list)
    source_results: List[SourceResult] = field(default_factory=list)
    ranking_result: Dict[str, Any] = field(default_factory=dict)
    injection_plan: Dict[str, Any] = field(default_factory=dict)
    conflict_resolution: Dict[str, Any] = field(default_factory=dict)
    budget_result: Dict[str, Any] = field(default_factory=dict)
    final_result: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "task_id": self.task_id,
            "original_query": self.original_query,
            "rewritten_query": self.rewritten_query,
            "query_rewrite_reason": self.query_rewrite_reason,
            "profile": self.profile,
            "risk_level": self.risk_level,
            "allowed_sources": self.allowed_sources,
            "denied_sources": self.denied_sources,
            "source_results": [sr.to_dict() for sr in self.source_results],
            "ranking_result": self.ranking_result,
            "injection_plan": self.injection_plan,
            "conflict_resolution": self.conflict_resolution,
            "budget_result": self.budget_result,
            "final_result": self.final_result,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms
        }


class RetrievalTraceStore:
    """
    检索追踪存储

    职责：
    - 记录每次检索的完整过程
    - 支持按任务/时间查询
    - 支持统计分析
    """

    def __init__(self, store_dir: str = "memory_context/traces"):
        self.store_dir = store_dir
        self._traces: Dict[str, RetrievalTrace] = {}
        self._task_index: Dict[str, List[str]] = {}
        self._ensure_dir()

    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(self.store_dir, exist_ok=True)

    def create_trace(
        self,
        task_id: str,
        original_query: str,
        profile: str = "default",
        risk_level: str = "low"
    ) -> RetrievalTrace:
        """
        创建追踪记录

        Args:
            task_id: 任务 ID
            original_query: 原始查询
            profile: 执行配置
            risk_level: 风险等级

        Returns:
            RetrievalTrace
        """
        trace_id = f"trace_{uuid.uuid4().hex[:8]}"

        trace = RetrievalTrace(
            trace_id=trace_id,
            task_id=task_id,
            original_query=original_query,
            profile=profile,
            risk_level=risk_level
        )

        self._traces[trace_id] = trace

        # 索引
        if task_id not in self._task_index:
            self._task_index[task_id] = []
        self._task_index[task_id].append(trace_id)

        return trace

    def update_trace(self, trace: RetrievalTrace):
        """更新追踪记录"""
        self._traces[trace.trace_id] = trace
        self._persist(trace)

    def add_source_result(
        self,
        trace_id: str,
        source_result: SourceResult
    ):
        """添加来源结果"""
        trace = self._traces.get(trace_id)
        if trace:
            trace.source_results.append(source_result)

    def finalize_trace(
        self,
        trace_id: str,
        final_result: Dict[str, Any],
        duration_ms: int
    ):
        """完成追踪记录"""
        trace = self._traces.get(trace_id)
        if trace:
            trace.final_result = final_result
            trace.duration_ms = duration_ms
            self._persist(trace)

    def get_trace(self, trace_id: str) -> Optional[RetrievalTrace]:
        """获取追踪记录"""
        if trace_id in self._traces:
            return self._traces[trace_id]
        return self._load_trace(trace_id)

    def get_traces_by_task(self, task_id: str) -> List[RetrievalTrace]:
        """获取任务的所有追踪记录"""
        trace_ids = self._task_index.get(task_id, [])
        traces = []
        for tid in trace_ids:
            trace = self.get_trace(tid)
            if trace:
                traces.append(trace)
        return traces

    def get_recent_traces(self, limit: int = 50) -> List[RetrievalTrace]:
        """获取最近的追踪记录"""
        traces = list(self._traces.values())
        traces.sort(key=lambda t: t.timestamp, reverse=True)
        return traces[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self._traces)
        if total == 0:
            return {"total": 0}

        total_sources = sum(len(t.source_results) for t in self._traces.values())
        total_tokens = sum(
            sum(sr.tokens_used for sr in t.source_results)
            for t in self._traces.values()
        )
        avg_duration = sum(t.duration_ms for t in self._traces.values()) / total

        return {
            "total": total,
            "total_sources_queried": total_sources,
            "total_tokens_used": total_tokens,
            "avg_duration_ms": avg_duration,
            "by_profile": self._count_by_field("profile"),
            "by_risk_level": self._count_by_field("risk_level")
        }

    def _count_by_field(self, field: str) -> Dict[str, int]:
        """按字段统计"""
        counts: Dict[str, int] = {}
        for trace in self._traces.values():
            value = getattr(trace, field, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _persist(self, trace: RetrievalTrace):
        """持久化追踪记录"""
        try:
            path = os.path.join(self.store_dir, f"{trace.trace_id}.json")
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(trace.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _load_trace(self, trace_id: str) -> Optional[RetrievalTrace]:
        """加载追踪记录"""
        path = os.path.join(self.store_dir, f"{trace_id}.json")
        if not os.path.exists(path):
            return None

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            source_results = [
                SourceResult(**sr) for sr in data.get("source_results", [])
            ]

            return RetrievalTrace(
                trace_id=data["trace_id"],
                task_id=data["task_id"],
                original_query=data["original_query"],
                rewritten_query=data.get("rewritten_query"),
                query_rewrite_reason=data.get("query_rewrite_reason"),
                profile=data.get("profile", "default"),
                risk_level=data.get("risk_level", "low"),
                allowed_sources=data.get("allowed_sources", []),
                denied_sources=data.get("denied_sources", []),
                source_results=source_results,
                ranking_result=data.get("ranking_result", {}),
                injection_plan=data.get("injection_plan", {}),
                conflict_resolution=data.get("conflict_resolution", {}),
                budget_result=data.get("budget_result", {}),
                final_result=data.get("final_result", {}),
                timestamp=data.get("timestamp", ""),
                duration_ms=data.get("duration_ms", 0)
            )
        except Exception:
            return None

    def clear_old_traces(self, days: int = 30) -> int:
        """清理旧追踪记录"""
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        to_delete = []

        for trace_id, trace in self._traces.items():
            try:
                ts = datetime.fromisoformat(trace.timestamp)
                if ts < cutoff:
                    to_delete.append(trace_id)
            except Exception:
                pass

        for trace_id in to_delete:
            del self._traces[trace_id]
            path = os.path.join(self.store_dir, f"{trace_id}.json")
            if os.path.exists(path):
                os.remove(path)

        return len(to_delete)


# 全局单例
_retrieval_trace_store = None


def get_retrieval_trace_store() -> RetrievalTraceStore:
    """获取检索追踪存储单例"""
    global _retrieval_trace_store
    if _retrieval_trace_store is None:
        _retrieval_trace_store = RetrievalTraceStore()
    return _retrieval_trace_store
