#!/usr/bin/env python3
"""兼容层 - 引用 infrastructure/performance_integration.py"""

from infrastructure.performance_integration import (
    PerformanceMonitor, get_monitor, record_metric
)

__all__ = ['PerformanceMonitor', 'get_monitor', 'record_metric']
