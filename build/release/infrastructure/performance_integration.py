#!/usr/bin/env python3
"""
性能集成统一入口 - V4.3.2

融合自:
- core/performance_integration.py
- orchestration/performance_integration.py
- execution/performance_integration.py
- governance/performance_integration.py
- memory_context/performance_integration.py

各层通过此模块访问性能监控功能
"""

from infrastructure.monitoring.performance_monitor import (
    PerformanceMonitor, get_monitor, record_metric
)

__all__ = ['PerformanceMonitor', 'get_monitor', 'record_metric']
