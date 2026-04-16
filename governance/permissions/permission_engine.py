"""Permission Engine - 权限引擎"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
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


@dataclass
class ProfilePermissions:
    """配置权限"""
    profile: str
    permissions: Set[Permission]
    allowed_categories: List[str]
    denied_skills: List[str]
    max_token_budget: int
    max_cost_budget: float


class PermissionEngine:
    """
    权限引擎
    
    职责：
    - 按 profile 管理权限
    - 检查能力是否允许
    - 管理技能访问控制
    """
    
    def __init__(self):
        # 配置权限定义
        self._profile_permissions: Dict[str, ProfilePermissions] = {
            "admin": ProfilePermissions(
                profile="admin",
                permissions={Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.NETWORK, Permission.ADMIN},
                allowed_categories=["*"],
                denied_skills=[],
                max_token_budget=32000,
                max_cost_budget=100.0
            ),
            "developer": ProfilePermissions(
                profile="developer",
                permissions={Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.NETWORK},
                allowed_categories=["code", "git", "docker", "utility", "search", "document"],
                denied_skills=[],
                max_token_budget=16000,
                max_cost_budget=50.0
            ),
            "default": ProfilePermissions(
                profile="default",
                permissions={Permission.READ, Permission.WRITE, Permission.EXECUTE},
                allowed_categories=["utility", "search", "document"],
                denied_skills=[],
                max_token_budget=8000,
                max_cost_budget=20.0
            ),
            "operator": ProfilePermissions(
                profile="operator",
                permissions={Permission.READ, Permission.EXECUTE},
                allowed_categories=["search", "document", "data"],
                denied_skills=[],
                max_token_budget=4000,
                max_cost_budget=10.0
            ),
            "auditor": ProfilePermissions(
                profile="auditor",
                permissions={Permission.READ},
                allowed_categories=["search", "document"],
                denied_skills=[],
                max_token_budget=2000,
                max_cost_budget=5.0
            ),
            "restricted": ProfilePermissions(
                profile="restricted",
                permissions={Permission.READ},
                allowed_categories=["utility"],
                denied_skills=[],
                max_token_budget=1000,
                max_cost_budget=1.0
            )
        }
    
    def check_permissions(
        self,
        profile: str,
        requested_permissions: List[str],
        requested_capabilities: List[str] = None
    ) -> PermissionCheck:
        """
        检查权限
        
        Args:
            profile: 执行配置
            requested_permissions: 请求的权限
            requested_capabilities: 请求的能力
        
        Returns:
            PermissionCheck
        """
        profile_perms = self._profile_permissions.get(
            profile,
            self._profile_permissions["default"]
        )
        
        granted = []
        denied = []
        
        # 检查权限
        for perm_str in requested_permissions:
            try:
                perm = Permission(perm_str)
                if perm in profile_perms.permissions:
                    granted.append(perm_str)
                else:
                    denied.append(perm_str)
            except ValueError:
                denied.append(perm_str)
        
        # 检查能力
        if requested_capabilities:
            for cap in requested_capabilities:
                if cap in profile_perms.denied_skills:
                    denied.append(cap)
        
        allowed = len(denied) == 0
        reason = "All permissions granted" if allowed else f"Missing permissions: {denied}"
        
        return PermissionCheck(
            allowed=allowed,
            granted=granted,
            denied=denied,
            reason=reason
        )
    
    def check_skill_allowed(
        self,
        profile: str,
        skill_category: str,
        skill_id: str
    ) -> tuple[bool, str]:
        """检查技能是否允许"""
        profile_perms = self._profile_permissions.get(
            profile,
            self._profile_permissions["default"]
        )
        
        # 检查拒绝列表
        if skill_id in profile_perms.denied_skills:
            return False, f"Skill {skill_id} is denied for profile {profile}"
        
        # 检查分类
        if "*" in profile_perms.allowed_categories:
            return True, "All categories allowed"
        
        if skill_category in profile_perms.allowed_categories:
            return True, f"Category {skill_category} allowed"
        
        return False, f"Category {skill_category} not allowed for profile {profile}"
    
    def get_allowed_capabilities(self, profile: str) -> List[str]:
        """获取允许的能力"""
        profile_perms = self._profile_permissions.get(
            profile,
            self._profile_permissions["default"]
        )
        
        capabilities = [p.value for p in profile_perms.permissions]
        
        if "*" in profile_perms.allowed_categories:
            capabilities.append("all_categories")
        else:
            capabilities.extend([f"category:{cat}" for cat in profile_perms.allowed_categories])
        
        return capabilities
    
    def get_blocked_capabilities(self, profile: str) -> List[str]:
        """获取禁止的能力"""
        profile_perms = self._profile_permissions.get(
            profile,
            self._profile_permissions["default"]
        )
        
        all_perms = set(p.value for p in Permission)
        blocked_perms = all_perms - set(p.value for p in profile_perms.permissions)
        
        return list(blocked_perms)
    
    def get_profile_budgets(self, profile: str) -> Dict[str, Any]:
        """获取配置预算"""
        profile_perms = self._profile_permissions.get(
            profile,
            self._profile_permissions["default"]
        )
        
        return {
            "max_token_budget": profile_perms.max_token_budget,
            "max_cost_budget": profile_perms.max_cost_budget
        }
    
    def add_profile(self, profile: str, permissions: ProfilePermissions):
        """添加配置"""
        self._profile_permissions[profile] = permissions
    
    def deny_skill(self, profile: str, skill_id: str):
        """禁止技能"""
        if profile in self._profile_permissions:
            self._profile_permissions[profile].denied_skills.append(skill_id)
