"""
Permission - 权限模块
"""

from .permission_engine import (
    PermissionEngine,
    PermissionResult,
    get_permission_engine
)

__all__ = [
    "PermissionEngine",
    "PermissionResult",
    "get_permission_engine"
]
