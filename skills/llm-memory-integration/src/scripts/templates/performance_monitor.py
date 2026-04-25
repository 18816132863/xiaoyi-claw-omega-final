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
            }
    
    def get_summary(self) -> Dict:
        """获取摘要"""
        with self._lock:
            return {
                "counters": dict(self.counters),
                "query_types": list(self.metrics.keys())
            }

# 全局监控实例
_monitor = PerformanceMonitor()

def get_monitor() -> PerformanceMonitor:
    """获取监控实例"""
    return _monitor
