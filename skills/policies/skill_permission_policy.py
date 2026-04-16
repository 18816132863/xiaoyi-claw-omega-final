"""Skill Permission Policy - 技能权限策略"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import Enum

from skills.registry.skill_registry import SkillManifest, SkillCategory


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
    """
    技能权限策略
    
    职责：
    - 按 profile 管理技能访问权限
    - 检查技能是否允许执行
    - 管理分类访问控制
    """
    
    def __init__(self):
        # 配置权限映射
        self._profile_permissions: Dict[str, Set[Permission]] = {
            "admin": {Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.NETWORK, Permission.ADMIN},
            "developer": {Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.NETWORK},
            "default": {Permission.READ, Permission.WRITE, Permission.EXECUTE},
            "operator": {Permission.READ, Permission.EXECUTE},
            "auditor": {Permission.READ},
            "restricted": {Permission.READ}
        }
        
        # 分类访问控制
        self._profile_categories: Dict[str, List[str]] = {
            "admin": ["*"],
            "developer": ["code", "git", "docker", "utility", "search", "document", "data"],
            "default": ["utility", "search", "document"],
            "operator": ["search", "document", "data"],
            "auditor": ["search", "document"],
            "restricted": ["utility"]
        }
        
        # 禁止的技能
        self._denied_skills: Dict[str, List[str]] = {
            "restricted": ["*"]  # restricted 配置禁止所有技能
        }
    
    def check(
        self,
        manifest: SkillManifest,
        profile: str
    ) -> PermissionCheck:
        """
        检查技能权限
        
        Args:
            manifest: 技能清单
            profile: 执行配置
        
        Returns:
            PermissionCheck
        """
        granted = []
        denied = []
        
        # 获取配置权限
        profile_perms = self._profile_permissions.get(
            profile,
            self._profile_permissions["default"]
        )
        
        # 检查技能是否在禁止列表
        denied_list = self._denied_skills.get(profile, [])
        if "*" in denied_list or manifest.skill_id in denied_list:
            return PermissionCheck(
                allowed=False,
                granted=[],
                denied=[manifest.skill_id],
                reason=f"Skill {manifest.skill_id} is denied for profile {profile}"
            )
        
        # 检查分类
        allowed_categories = self._profile_categories.get(profile, [])
        if "*" not in allowed_categories:
            if manifest.category.value not in allowed_categories:
                return PermissionCheck(
                    allowed=False,
                    granted=[],
                    denied=[manifest.category.value],
                    reason=f"Category {manifest.category.value} not allowed for profile {profile}"
                )
        
        # 检查权限
        for perm_str in manifest.required_permissions:
            try:
                perm = Permission(perm_str)
                if perm in profile_perms:
                    granted.append(perm_str)
                else:
                    denied.append(perm_str)
            except ValueError:
                denied.append(perm_str)
        
        allowed = len(denied) == 0
        reason = "All permissions granted" if allowed else f"Missing permissions: {denied}"
        
        return PermissionCheck(
            allowed=allowed,
            granted=granted,
            denied=denied,
            reason=reason
        )
    
    def is_allowed(
        self,
        manifest: SkillManifest,
        profile: str
    ) -> bool:
        """检查是否允许"""
        result = self.check(manifest, profile)
        return result.allowed
    
    def get_allowed_categories(self, profile: str) -> List[str]:
        """获取允许的分类"""
        return self._profile_categories.get(profile, [])
    
    def get_allowed_permissions(self, profile: str) -> List[str]:
        """获取允许的权限"""
        perms = self._profile_permissions.get(
            profile,
            self._profile_permissions["default"]
        )
        return [p.value for p in perms]
    
    def deny_skill(self, profile: str, skill_id: str):
        """禁止技能"""
        if profile not in self._denied_skills:
            self._denied_skills[profile] = []
        if skill_id not in self._denied_skills[profile]:
            self._denied_skills[profile].append(skill_id)
    
    def allow_skill(self, profile: str, skill_id: str):
        """允许技能"""
        if profile in self._denied_skills:
            if skill_id in self._denied_skills[profile]:
                self._denied_skills[profile].remove(skill_id)
    
    def set_profile_categories(self, profile: str, categories: List[str]):
        """设置配置分类"""
        self._profile_categories[profile] = categories
    
    def set_profile_permissions(self, profile: str, permissions: List[str]):
        """设置配置权限"""
        perms = set()
        for perm_str in permissions:
            try:
                perms.add(Permission(perm_str))
            except ValueError:
                pass
        self._profile_permissions[profile] = perms
