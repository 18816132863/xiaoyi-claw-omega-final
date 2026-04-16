"""Skill Permission Policy - 技能权限策略"""

from dataclasses import dataclass
from typing import Dict, List, Set
from enum import Enum


class Permission(Enum):
    """权限类型"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    NETWORK = "network"
    ADMIN = "admin"


@dataclass
class PermissionCheck:
    """权限检查结果"""
    allowed: bool
    granted: List[str]
    denied: List[str]
    reason: str


class SkillPermissionPolicy:
    """技能权限策略"""
    
    # 配置权限映射
    PROFILE_PERMISSIONS = {
        "default": {Permission.READ, Permission.WRITE, Permission.EXECUTE},
        "developer": {Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.NETWORK},
        "operator": {Permission.READ, Permission.EXECUTE},
        "auditor": {Permission.READ},
        "admin": {Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.NETWORK, Permission.ADMIN},
        "restricted": {Permission.READ}
    }
    
    def check(self, manifest, profile: str = "default") -> PermissionCheck:
        """检查技能权限"""
        # 获取配置权限
        profile_perms = self.PROFILE_PERMISSIONS.get(profile, self.PROFILE_PERMISSIONS["default"])
        
        # 获取技能所需权限
        required_perms = set()
        if hasattr(manifest, 'required_permissions'):
            for perm_str in manifest.required_permissions:
                try:
                    required_perms.add(Permission(perm_str))
                except ValueError:
                    pass
        
        # 检查
        granted = []
        denied = []
        
        for perm in required_perms:
            if perm in profile_perms:
                granted.append(perm.value)
            else:
                denied.append(perm.value)
        
        allowed = len(denied) == 0
        reason = "All permissions granted" if allowed else f"Missing permissions: {denied}"
        
        return PermissionCheck(
            allowed=allowed,
            granted=granted,
            denied=denied,
            reason=reason
        )
    
    def is_allowed(self, manifest, profile: str = "default") -> bool:
        """检查是否允许执行"""
        result = self.check(manifest, profile)
        return result.allowed
    
    def get_profile_permissions(self, profile: str) -> List[str]:
        """获取配置的权限"""
        perms = self.PROFILE_PERMISSIONS.get(profile, self.PROFILE_PERMISSIONS["default"])
        return [p.value for p in perms]
