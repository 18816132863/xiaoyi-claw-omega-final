"""路由器 - V4.3.1

兼容层：引用 infrastructure/shared/router.py
"""

from infrastructure.shared.router import (
    UnifiedRouter, RouteMode, RouteResult, get_router, route
)

# 兼容旧接口
SkillRouter = UnifiedRouter

__all__ = ['UnifiedRouter', 'RouteMode', 'RouteResult', 'get_router', 'route', 'SkillRouter']
