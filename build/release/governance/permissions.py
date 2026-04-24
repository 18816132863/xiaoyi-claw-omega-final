#!/usr/bin/env python3
"""
权限管理模块 - V1.0.0

管理用户和系统的操作权限。
"""

from enum import Enum
from typing import Dict, List, Set, Optional
from dataclasses import dataclass


class Permission(Enum):
    """权限枚举"""
    # 文件权限
    FILE_READ = "file:read"
    FILE_WRITE = "file:write"
    FILE_DELETE = "file:delete"
    
    # 技能权限
    SKILL_EXECUTE = "skill:execute"
    SKILL_INSTALL = "skill:install"
    SKILL_UNINSTALL = "skill:uninstall"
    
    # 系统权限
    SYSTEM_CONFIG = "system:config"
    SYSTEM_RESTART = "system:restart"
    
    # 网络权限
    NETWORK_REQUEST = "network:request"
    
    # 通讯权限
    MESSAGE_SEND = "message:send"
    PHONE_CALL = "phone:call"


@dataclass
class Role:
    """角色定义"""
    name: str
    permissions: Set[Permission]
    inherits: Optional[str] = None


# 预定义角色
ROLES: Dict[str, Role] = {
    "guest": Role(
        name="guest",
        permissions={
            Permission.FILE_READ,
            Permission.SKILL_EXECUTE,
        }
    ),
    "user": Role(
        name="user",
        permissions={
            Permission.FILE_READ,
            Permission.FILE_WRITE,
            Permission.SKILL_EXECUTE,
            Permission.NETWORK_REQUEST,
        },
        inherits="guest"
    ),
    "admin": Role(
        name="admin",
        permissions={
            Permission.FILE_READ,
            Permission.FILE_WRITE,
            Permission.FILE_DELETE,
            Permission.SKILL_EXECUTE,
            Permission.SKILL_INSTALL,
            Permission.SKILL_UNINSTALL,
            Permission.SYSTEM_CONFIG,
            Permission.NETWORK_REQUEST,
            Permission.MESSAGE_SEND,
            Permission.PHONE_CALL,
        },
        inherits="user"
    ),
    "superadmin": Role(
        name="superadmin",
        permissions=set(Permission),  # 所有权限
        inherits="admin"
    ),
}


class PermissionManager:
    """权限管理器"""
    
    def __init__(self):
        self.user_roles: Dict[str, str] = {}
    
    def get_role(self, role_name: str) -> Optional[Role]:
        """获取角色"""
        return ROLES.get(role_name)
    
    def get_permissions(self, role_name: str) -> Set[Permission]:
        """获取角色的所有权限（包括继承）"""
        role = self.get_role(role_name)
        if not role:
            return set()
        
        permissions = set(role.permissions)
        
        # 递归获取继承的权限
        if role.inherits:
            inherited = self.get_permissions(role.inherits)
            permissions.update(inherited)
        
        return permissions
    
    def has_permission(self, role_name: str, permission: Permission) -> bool:
        """检查角色是否有指定权限"""
        permissions = self.get_permissions(role_name)
        return permission in permissions
    
    def check_action(self, role_name: str, action: str) -> bool:
        """检查是否允许执行操作"""
        try:
            permission = Permission(action)
            return self.has_permission(role_name, permission)
        except ValueError:
            return False
    
    def assign_role(self, user_id: str, role_name: str):
        """为用户分配角色"""
        if role_name in ROLES:
            self.user_roles[user_id] = role_name
    
    def get_user_role(self, user_id: str) -> str:
        """获取用户角色"""
        return self.user_roles.get(user_id, "user")


# 全局权限管理器
_permission_manager: Optional[PermissionManager] = None


def get_permission_manager() -> PermissionManager:
    """获取全局权限管理器"""
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = PermissionManager()
    return _permission_manager
