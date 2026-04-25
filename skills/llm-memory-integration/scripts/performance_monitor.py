#!/usr/bin/env python3
"""
监控指标模块
运行时性能监控
"""

import time
import threading
from typing import Dict, List
from collections import defaultdict
from datetime import datetime

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self._lock = threading.Lock()
    
    def record_query(self, query_type: str, latency_ms: float, cache_hit: bool = False):
        """记录查询"""
        with self._lock:
            self.metrics[query_type].append({
                "timestamp": time.time(),
                "latency_ms": latency_ms,
                "cache_hit": cache_hit
            })
            self.counters[f"{query_type}_total"] += 1
            if cache_hit:
                self.counters[f"{query_type}_cache_hits"] += 1
    
    def record_error(self, error_type: str):
        """记录错误"""
        with self._lock:
            self.counters[f"errors_{error_type}"] += 1
    
    def get_stats(self, query_type: str) -> Dict:
        """获取统计"""
        with self._lock:
            records = self.metrics.get(query_type, [])
            
            if not records:
                return {}
            
            latencies = [r["latency_ms"] for r in records]
            cache_hits = sum(1 for r in records if r["cache_hit"])
            
            return {
                "total_queries": len(records),
                "cache_hits": cache_hits,
                "cache_hit_rate": cache_hits / len(records) if records else 0,
                "avg_latency_ms": sum(latencies) / len(latencies),
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies),
                "p50_latency_ms": sorted(latencies)[len(latencies) // 2],
                "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 20 else max(latencies),
                "p99_latency_ms": sorted(latencies)[int(len(latencies) * 0.99)] if len(latencies) > 100 else max(latencies)
            }
    
    def get_summary(self) -> Dict:
        """获取摘要"""
        with self._lock:
            return {
                "counters": dict(self.counters),
                "query_types": list(self.metrics.keys())
            }
    
    def reset(self):
        """重置"""
        with self._lock:
            self.metrics.clear()
            self.counters.clear()

# 全局监控实例
_monitor = PerformanceMonitor()

def get_monitor() -> PerformanceMonitor:
    """获取监控实例"""
    return _monitor
