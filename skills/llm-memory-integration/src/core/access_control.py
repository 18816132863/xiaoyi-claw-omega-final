#!/usr/bin/env python3
"""
访问控制模块 (v5.0)
RBAC 权限、用户管理、角色管理、审计日志
"""

import json
import time
import hashlib
import secrets
from typing import Dict, List, Optional, Set
from pathlib import Path
from enum import Enum


class Permission(Enum):
    """权限枚举"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    SEARCH = "search"
    EXPORT = "export"
    IMPORT = "import"


class Role:
    """
    角色定义
    """
    
    # 预定义角色
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    
    # 角色权限映射
    ROLE_PERMISSIONS = {
        ADMIN: {p.value for p in Permission},
        USER: {Permission.READ.value, Permission.WRITE.value, Permission.SEARCH.value, Permission.EXPORT.value},
        GUEST: {Permission.READ.value, Permission.SEARCH.value}
    }
    
    def __init__(self, name: str, permissions: Optional[Set[str]] = None):
        """
        初始化角色
        
        Args:
            name: 角色名称
            permissions: 权限集合
        """
        self.name = name
        self.permissions = permissions or set()
    
    def has_permission(self, permission: str) -> bool:
        """
        检查是否有权限
        
        Args:
            permission: 权限名称
        
        Returns:
            bool: 是否有权限
        """
        return permission in self.permissions
    
    def add_permission(self, permission: str):
        """添加权限"""
        self.permissions.add(permission)
    
    def remove_permission(self, permission: str):
        """移除权限"""
        self.permissions.discard(permission)


class User:
    """
    用户定义
    """
    
    def __init__(
        self,
        user_id: str,
        username: str,
        roles: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ):
        """
        初始化用户
        
        Args:
            user_id: 用户 ID
            username: 用户名
            roles: 角色列表
            metadata: 元数据
        """
        self.user_id = user_id
        self.username = username
        self.roles = roles or [Role.USER]
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.last_login = None
    
    def get_permissions(self) -> Set[str]:
        """
        获取所有权限
        
        Returns:
            Set[str]: 权限集合
        """
        permissions = set()
        for role in self.roles:
            permissions.update(Role.ROLE_PERMISSIONS.get(role, set()))
        return permissions
    
    def has_permission(self, permission: str) -> bool:
        """
        检查是否有权限
        
        Args:
            permission: 权限名称
        
        Returns:
            bool: 是否有权限
        """
        return permission in self.get_permissions()


class AccessControlManager:
    """
    访问控制管理器
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化访问控制管理器
        
        Args:
            config_path: 配置路径
        """
        self.config_path = Path(config_path) if config_path else None
        
        # 用户存储
        self.users: Dict[str, User] = {}
        
        # 角色存储
        self.roles: Dict[str, Role] = {}
        
        # 审计日志
        self.audit_log: List[Dict] = []
        
        # 初始化默认角色
        self._init_default_roles()
        
        print("访问控制管理器初始化完成")
    
    def _init_default_roles(self):
        """初始化默认角色"""
        for role_name, permissions in Role.ROLE_PERMISSIONS.items():
            self.roles[role_name] = Role(role_name, permissions)
    
    def create_user(
        self,
        username: str,
        password: str,
        roles: Optional[List[str]] = None
    ) -> User:
        """
        创建用户
        
        Args:
            username: 用户名
            password: 密码
            roles: 角色列表
        
        Returns:
            User: 用户对象
        """
        user_id = f"user_{secrets.token_hex(8)}"
        
        # 哈希密码
        password_hash = self._hash_password(password)
        
        user = User(
            user_id=user_id,
            username=username,
            roles=roles or [Role.USER],
            metadata={'password_hash': password_hash}
        )
        
        self.users[user_id] = user
        
        # 审计日志
        self._log_audit('user_created', user_id, {'username': username})
        
        print(f"✅ 用户已创建: {username}")
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        认证用户
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            Optional[User]: 用户对象
        """
        for user in self.users.values():
            if user.username == username:
                stored_hash = user.metadata.get('password_hash', '')
                if self._verify_password(password, stored_hash):
                    user.last_login = time.time()
                    self._log_audit('login', user.user_id, {'username': username})
                    return user
        
        return None
    
    def check_permission(self, user_id: str, permission: str) -> bool:
        """
        检查权限
        
        Args:
            user_id: 用户 ID
            permission: 权限名称
        
        Returns:
            bool: 是否有权限
        """
        user = self.users.get(user_id)
        if not user:
            return False
        
        has_perm = user.has_permission(permission)
        
        # 审计日志
        self._log_audit('permission_check', user_id, {
            'permission': permission,
            'result': has_perm
        })
        
        return has_perm
    
    def add_role_to_user(self, user_id: str, role_name: str) -> bool:
        """
        给用户添加角色
        
        Args:
            user_id: 用户 ID
            role_name: 角色名称
        
        Returns:
            bool: 是否成功
        """
        user = self.users.get(user_id)
        if not user:
            return False
        
        if role_name not in self.roles:
            return False
        
        if role_name not in user.roles:
            user.roles.append(role_name)
            self._log_audit('role_added', user_id, {'role': role_name})
        
        return True
    
    def remove_role_from_user(self, user_id: str, role_name: str) -> bool:
        """
        移除用户角色
        
        Args:
            user_id: 用户 ID
            role_name: 角色名称
        
        Returns:
            bool: 是否成功
        """
        user = self.users.get(user_id)
        if not user:
            return False
        
        if role_name in user.roles:
            user.roles.remove(role_name)
            self._log_audit('role_removed', user_id, {'role': role_name})
        
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户 ID
        
        Returns:
            bool: 是否成功
        """
        if user_id in self.users:
            username = self.users[user_id].username
            del self.users[user_id]
            self._log_audit('user_deleted', user_id, {'username': username})
            return True
        return False
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """
        获取审计日志
        
        Args:
            limit: 返回数量
        
        Returns:
            List[Dict]: 审计日志
        """
        return self.audit_log[-limit:]
    
    def _hash_password(self, password: str) -> str:
        """
        哈希密码
        
        Args:
            password: 密码
        
        Returns:
            str: 哈希值
        """
        salt = secrets.token_hex(16)
        hash_value = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{hash_value}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """
        验证密码
        
        Args:
            password: 密码
            stored_hash: 存储的哈希值
        
        Returns:
            bool: 是否匹配
        """
        try:
            salt, hash_value = stored_hash.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == hash_value
        except Exception:
            return False
    
    def _log_audit(self, action: str, user_id: str, details: Dict):
        """
        记录审计日志
        
        Args:
            action: 操作
            user_id: 用户 ID
            details: 详情
        """
        self.audit_log.append({
            'timestamp': time.time(),
            'action': action,
            'user_id': user_id,
            'details': details
        })
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            'total_users': len(self.users),
            'total_roles': len(self.roles),
            'audit_log_size': len(self.audit_log)
        }


if __name__ == "__main__":
    # 测试
    print("=== 访问控制测试 ===")
    
    acm = AccessControlManager()
    
    # 创建用户
    admin = acm.create_user("admin", "admin123", [Role.ADMIN])
    user = acm.create_user("test_user", "password123", [Role.USER])
    guest = acm.create_user("guest", "guest123", [Role.GUEST])
    
    # 认证测试
    authenticated = acm.authenticate("admin", "admin123")
    print(f"认证: {'✅' if authenticated else '❌'}")
    
    # 权限检查
    print(f"Admin 有 admin 权限: {acm.check_permission(admin.user_id, 'admin')}")
    print(f"User 有 admin 权限: {acm.check_permission(user.user_id, 'admin')}")
    print(f"Guest 有 read 权限: {acm.check_permission(guest.user_id, 'read')}")
    
    # 审计日志
    print(f"\n审计日志: {len(acm.get_audit_log())} 条")
    
    # 统计
    stats = acm.get_stats()
    print(f"统计: {stats}")
