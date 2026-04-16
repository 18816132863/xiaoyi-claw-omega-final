"""
Permission Engine - 权限引擎
检查 profile 对能力的访问权限
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Set
from enum import Enum


@dataclass
class PermissionResult:
    """权限检查结果"""
    allowed: List[str]
    blocked: List[str]
    reasons: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "blocked": self.blocked,
            "reasons": self.reasons
        }


class PermissionEngine:
    """
    权限引擎
    
    检查 profile 对能力的访问权限
    """
    
    # Profile 权限配置
    PROFILE_PERMISSIONS = {
        "development": {
            "allowed_categories": ["skill", "workflow", "memory", "report", "external", "system", "high_risk"],
            "blocked_capabilities": [],
            "max_risk_weight": 5.0
        },
        "performance": {
            "allowed_categories": ["skill", "workflow", "memory", "report", "external", "system"],
            "blocked_capabilities": ["high_risk.*"],
            "max_risk_weight": 4.0
        },
        "default": {
            "allowed_categories": ["skill", "workflow", "memory", "report", "external"],
            "blocked_capabilities": ["high_risk.*", "system.*"],
            "max_risk_weight": 3.0
        },
        "production": {
            "allowed_categories": ["skill", "workflow", "memory", "report"],
            "blocked_capabilities": ["high_risk.*", "system.*", "external.api"],
            "max_risk_weight": 2.5
        },
        "safe": {
            "allowed_categories": ["skill", "memory", "report"],
            "blocked_capabilities": ["high_risk.*", "system.*", "external.*", "skill.install", "skill.remove"],
            "max_risk_weight": 2.0
        },
        "restricted": {
            "allowed_categories": ["memory", "report"],
            "blocked_capabilities": ["high_risk.*", "system.*", "external.*", "skill.*", "workflow.*"],
            "max_risk_weight": 1.0
        }
    }
    
    def __init__(self):
        self._custom_permissions: Dict[str, Dict[str, Any]] = {}
    
    def check(
        self,
        profile: str,
        capabilities: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        检查权限
        
        Args:
            profile: 配置文件名
            capabilities: 能力列表
            context: 上下文
            
        Returns:
            {"allowed": [...], "blocked": [...]}
        """
        allowed = []
        blocked = []
        reasons = []
        
        permissions = self._get_permissions(profile)
        allowed_categories = permissions.get("allowed_categories", [])
        blocked_capabilities = permissions.get("blocked_capabilities", [])
        
        for cap in capabilities:
            # 提取分类
            category = cap.split(".")[0] if "." in cap else "unknown"
            
            # 检查分类
            if category not in allowed_categories:
                blocked.append(cap)
                reasons.append(f"Category '{category}' not allowed for profile '{profile}'")
                continue
            
            # 检查阻止列表
            is_blocked = False
            for pattern in blocked_capabilities:
                if self._match_capability(cap, pattern):
                    blocked.append(cap)
                    reasons.append(f"Capability '{cap}' blocked by pattern '{pattern}'")
                    is_blocked = True
                    break
            
            if not is_blocked:
                allowed.append(cap)
        
        return {"allowed": allowed, "blocked": blocked}
    
    def is_allowed(
        self,
        profile: str,
        capability: str
    ) -> bool:
        """
        检查单个能力是否允许
        
        Args:
            profile: 配置文件名
            capability: 能力名称
            
        Returns:
            是否允许
        """
        result = self.check(profile, [capability])
        return capability in result["allowed"]
    
    def set_profile_permissions(
        self,
        profile: str,
        permissions: Dict[str, Any]
    ):
        """
        设置 profile 权限
        
        Args:
            profile: 配置文件名
            permissions: 权限配置
        """
        self._custom_permissions[profile] = permissions
    
    def get_profile_permissions(self, profile: str) -> Dict[str, Any]:
        """
        获取 profile 权限
        
        Args:
            profile: 配置文件名
            
        Returns:
            权限配置
        """
        return self._get_permissions(profile)
    
    def reload(self) -> Dict[str, Any]:
        """
        重新加载
        
        Returns:
            重载结果
        """
        return {
            "status": "reloaded",
            "builtin_profiles": len(self.PROFILE_PERMISSIONS),
            "custom_profiles": len(self._custom_permissions)
        }
    
    def _get_permissions(self, profile: str) -> Dict[str, Any]:
        """
        获取权限配置
        
        Args:
            profile: 配置文件名
            
        Returns:
            权限配置
        """
        if profile in self._custom_permissions:
            return self._custom_permissions[profile]
        return self.PROFILE_PERMISSIONS.get(profile, self.PROFILE_PERMISSIONS["default"])
    
    def _match_capability(self, capability: str, pattern: str) -> bool:
        """
        匹配能力
        
        Args:
            capability: 能力名称
            pattern: 模式
            
        Returns:
            是否匹配
        """
        if pattern == "*":
            return True
        
        if "*" not in pattern:
            return capability == pattern
        
        # 前缀匹配
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return capability.startswith(prefix)
        
        return False


# 全局单例
_permission_engine = None

def get_permission_engine() -> PermissionEngine:
    """获取权限引擎单例"""
    global _permission_engine
    if _permission_engine is None:
        _permission_engine = PermissionEngine()
    return _permission_engine
