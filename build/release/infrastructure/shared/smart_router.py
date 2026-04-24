#!/usr/bin/env python3
"""
smart_router - V4.3.2 融合版

融合自:
- infrastructure/performance/smart_router.py
- infrastructure/optimization/smart_router.py

此模块为统一实现，其他位置通过兼容层引用
"""

from infrastructure.shared.router import (
    UnifiedRouter, RouteMode, RouteResult, get_router, route
)

SmartRouter = UnifiedRouter

__all__ = ['UnifiedRouter', 'RouteMode', 'RouteResult', 'get_router', 'route', 'SmartRouter']