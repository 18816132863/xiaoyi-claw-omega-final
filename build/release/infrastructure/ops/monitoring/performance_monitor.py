#!/usr/bin/env python3
"""
performance_monitor - V4.3.2 融合版

融合自:
- infrastructure/performance/performance_monitor.py
- infrastructure/monitoring/performance_monitor.py

此模块为统一实现，其他位置通过兼容层引用
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import threading

@dataclass
class Metric:
    """指标"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)

class PerformanceMonitor:
    """性能监控器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._metrics: Dict[str, List[Metric]] = {}
                    cls._instance._timers: Dict[str, float] = {}
        return cls._instance
    
    def record(self, name: str, value: float, tags: Dict[str, str] = None):
        """记录指标"""
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(Metric(name, value, tags=tags or {}))
    
    def start_timer(self, name: str):
        """开始计时"""
        self._timers[name] = time.time()
    
    def stop_timer(self, name: str) -> float:
        """停止计时并返回耗时（毫秒）"""
        if name not in self._timers:
            return 0.0
        elapsed = (time.time() - self._timers[name]) * 1000
        self.record(f"{name}_duration_ms", elapsed)
        del self._timers[name]
        return elapsed
    
    def get_metrics(self, name: str = None) -> List[Metric]:
        """获取指标"""
        if name:
            return self._metrics.get(name, [])
        all_metrics = []
        for metrics in self._metrics.values():
            all_metrics.extend(metrics)
        return all_metrics

# 全局实例
_monitor: Optional[PerformanceMonitor] = None

def get_monitor() -> PerformanceMonitor:
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor

def record_metric(name: str, value: float, tags: Dict[str, str] = None):
    get_monitor().record(name, value, tags)
