"""
指标收集模块 V1.0.0

收集和暴露关键业务指标。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from collections import defaultdict
import threading


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, metrics_dir: Optional[Path] = None):
        self.metrics_dir = metrics_dir
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()
        
        if metrics_dir:
            metrics_dir.mkdir(parents=True, exist_ok=True)
    
    def increment(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """增加计数器"""
        with self._lock:
            key = self._make_key(name, labels)
            self._counters[key] += value
    
    def gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """设置仪表值"""
        with self._lock:
            key = self._make_key(name, labels)
            self._gauges[key] = value
    
    def histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """记录直方图值"""
        with self._lock:
            key = self._make_key(name, labels)
            self._histograms[key].append(value)
    
    def _make_key(self, name: str, labels: Optional[Dict[str, str]] = None) -> str:
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有指标"""
        with self._lock:
            result = {
                "timestamp": datetime.now().isoformat(),
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {}
            }
            
            for key, values in self._histograms.items():
                if values:
                    result["histograms"][key] = {
                        "count": len(values),
                        "sum": sum(values),
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values)
                    }
            
            return result
    
    def export(self) -> str:
        """导出为 JSON"""
        return json.dumps(self.get_all(), indent=2, ensure_ascii=False)
    
    def save(self, filename: str = "metrics.json"):
        """保存到文件"""
        if self.metrics_dir:
            path = self.metrics_dir / filename
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.export())


# 全局 metrics 实例
_metrics: Optional[MetricsCollector] = None


def get_metrics(metrics_dir: Optional[Path] = None) -> MetricsCollector:
    """获取全局 metrics 实例"""
    global _metrics
    if _metrics is None:
        _metrics = MetricsCollector(metrics_dir=metrics_dir)
    return _metrics
