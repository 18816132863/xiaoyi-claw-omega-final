"""Memory Retrieval Benchmark - 记忆检索基准测试"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os


@dataclass
class RetrievalResult:
    """检索结果记录"""
    query: str
    hit: bool
    token_usage: int
    source_count: int
    latency_ms: int
    timestamp: str = ""


@dataclass
class MemoryMetrics:
    """记忆指标"""
    total_queries: int
    hits: int
    misses: int
    hit_rate: float
    avg_token_usage: float
    avg_source_count: float
    avg_latency_ms: float
    timestamp: str
    details: Dict[str, Any] = field(default_factory=dict)


class MemoryRetrievalBench:
    """
    记忆检索基准测试
    
    职责：
    - 统计检索命中率
    - 计算 token 使用量
    - 生成指标报告
    """
    
    def __init__(self, metrics_dir: str = "reports/metrics"):
        self.metrics_dir = metrics_dir
        self._results: List[RetrievalResult] = []
        self._ensure_dir()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(self.metrics_dir, exist_ok=True)
    
    def record(
        self,
        query: str,
        hit: bool,
        token_usage: int,
        source_count: int,
        latency_ms: int = 0
    ):
        """
        记录检索结果
        
        Args:
            query: 查询
            hit: 是否命中
            token_usage: token 使用量
            source_count: 源数量
            latency_ms: 耗时（毫秒）
        """
        result = RetrievalResult(
            query=query,
            hit=hit,
            token_usage=token_usage,
            source_count=source_count,
            latency_ms=latency_ms,
            timestamp=datetime.now().isoformat()
        )
        self._results.append(result)
    
    def compute(self) -> MemoryMetrics:
        """
        计算指标
        
        Returns:
            MemoryMetrics
        """
        total = len(self._results)
        hits = sum(1 for r in self._results if r.hit)
        misses = total - hits
        hit_rate = hits / total if total > 0 else 0.0
        
        token_usages = [r.token_usage for r in self._results]
        avg_token = sum(token_usages) / len(token_usages) if token_usages else 0.0
        
        source_counts = [r.source_count for r in self._results]
        avg_sources = sum(source_counts) / len(source_counts) if source_counts else 0.0
        
        latencies = [r.latency_ms for r in self._results]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        
        # 按源数量分布
        source_distribution = {}
        for r in self._results:
            bucket = f"{r.source_count}_sources"
            source_distribution[bucket] = source_distribution.get(bucket, 0) + 1
        
        metrics = MemoryMetrics(
            total_queries=total,
            hits=hits,
            misses=misses,
            hit_rate=hit_rate,
            avg_token_usage=avg_token,
            avg_source_count=avg_sources,
            avg_latency_ms=avg_latency,
            timestamp=datetime.now().isoformat(),
            details={
                "source_distribution": source_distribution,
                "min_token_usage": min(token_usages) if token_usages else 0,
                "max_token_usage": max(token_usages) if token_usages else 0,
                "min_source_count": min(source_counts) if source_counts else 0,
                "max_source_count": max(source_counts) if source_counts else 0
            }
        )
        
        return metrics
    
    def save(self, metrics: MemoryMetrics = None) -> str:
        """
        保存指标
        
        Args:
            metrics: 指标对象
        
        Returns:
            文件路径
        """
        if metrics is None:
            metrics = self.compute()
        
        path = os.path.join(self.metrics_dir, "memory_metrics.json")
        data = {
            "total_queries": metrics.total_queries,
            "hits": metrics.hits,
            "misses": metrics.misses,
            "hit_rate": metrics.hit_rate,
            "avg_token_usage": metrics.avg_token_usage,
            "avg_source_count": metrics.avg_source_count,
            "avg_latency_ms": metrics.avg_latency_ms,
            "timestamp": metrics.timestamp,
            "details": metrics.details
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return path
    
    def run_benchmark(self, test_queries: List[Dict[str, Any]]) -> MemoryMetrics:
        """
        运行基准测试
        
        Args:
            test_queries: 测试查询列表
        
        Returns:
            MemoryMetrics
        """
        for query in test_queries:
            self.record(
                query=query.get("query", ""),
                hit=query.get("hit", False),
                token_usage=query.get("token_usage", 0),
                source_count=query.get("source_count", 0),
                latency_ms=query.get("latency_ms", 0)
            )
        
        metrics = self.compute()
        self.save(metrics)
        
        return metrics
    
    def load(self) -> Optional[Dict[str, Any]]:
        """加载已保存的指标"""
        path = os.path.join(self.metrics_dir, "memory_metrics.json")
        if not os.path.exists(path):
            return None
        
        with open(path, 'r') as f:
            return json.load(f)
    
    def clear(self):
        """清空结果"""
        self._results.clear()
