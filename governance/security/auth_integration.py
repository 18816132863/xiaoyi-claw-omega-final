#!/usr/bin/env python3
"""
权限与架构集成
V2.7.0 - 2026-04-10

将实时权限控制融合到六层架构
"""

import os
import sys
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from functools import wraps

# 使用 path_resolver 获取项目根目录
try:
    from infrastructure.path_resolver import get_project_root
    WORKSPACE = get_project_root()
except ImportError:
    # 回退
    WORKSPACE = Path(__file__).parent.parent.parent

if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))

from governance.security.realtime_auth import (
    RealtimeAuthManager, get_auth_manager
)

class AuthMiddleware:
    """权限中间件 - 融合到 L5 治理层"""
    
    def __init__(self):
        self.auth_manager = get_auth_manager()
        self.audit_log: list = []
    
    def check_exec_permission(self, command: str) -> tuple:
        """检查执行权限 (L6 基建层)"""
        allowed, reason = self.auth_manager.check_command(command)
        self._audit("exec", command, allowed, reason)
        return allowed, reason
    
    def check_write_permission(self, path: str) -> tuple:
        """检查写入权限 (L5 数据层)"""
        allowed, reason = self.auth_manager.check_path(path, "write")
        self._audit("write", path, allowed, reason)
        return allowed, reason
    
    def check_read_permission(self, path: str) -> tuple:
        """检查读取权限"""
        allowed, reason = self.auth_manager.check_path(path, "read")
        self._audit("read", path, allowed, reason)
        return allowed, reason
    
    def _audit(self, operation: str, target: str, allowed: bool, reason: str):
        """审计记录"""
        import time
        self.audit_log.append({
            "timestamp": time.time(),
            "operation": operation,
            "target": target,
            "allowed": allowed,
            "reason": reason
        })
        
        # 限制日志大小
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    def require_auth(self, operation_type: str = "exec"):
        """装饰器 - 需要授权"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 根据操作类型检查权限
                if operation_type == "exec":
                    # 从参数中提取命令
                    command = kwargs.get("command", args[0] if args else "")
                    allowed, reason = self.check_exec_permission(command)
                elif operation_type == "write":
                    path = kwargs.get("path", args[1] if len(args) > 1 else "")
                    allowed, reason = self.check_write_permission(path)
                else:
                    allowed, reason = True, "无需授权"
                
                if not allowed:
                    raise PermissionError(f"操作被拒绝: {reason}")
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def grant_temp_auth(self, operations: list = None, paths: list = None,
                        timeout: int = 300) -> str:
        """授予临时授权"""
        return self.auth_manager.grant_auth(
            operations=operations,
            paths=paths,
            timeout=timeout
        )
    
    def revoke_auth(self):
        """撤销授权"""
        self.auth_manager.revoke_auth()
    
    def get_status(self) -> dict:
        """获取授权状态"""
        return self.auth_manager.get_auth_status()
    
    def get_audit_log(self, limit: int = 50) -> list:
        """获取审计日志"""
        return self.audit_log[-limit:]

# 全局实例
_middleware: Optional[AuthMiddleware] = None

def get_auth_middleware() -> AuthMiddleware:
    """获取全局权限中间件"""
    global _middleware
    if _middleware is None:
        _middleware = AuthMiddleware()
    return _middleware

def require_exec_auth(func: Callable) -> Callable:
    """执行权限装饰器"""
    return get_auth_middleware().require_auth("exec")(func)

def require_write_auth(func: Callable) -> Callable:
    """写入权限装饰器"""
    return get_auth_middleware().require_auth("write")(func)
