"""
Profile Switcher - 配置文件切换器
管理不同运行模式的配置切换
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class ProfileType(Enum):
    """配置文件类型"""
    DEFAULT = "default"
    SAFE = "safe"
    PERFORMANCE = "performance"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    RESTRICTED = "restricted"


@dataclass
class ProfileConfig:
    """配置文件"""
    name: str
    profile_type: ProfileType
    description: str
    token_budget: int
    cost_budget: float
    allowed_categories: List[str]
    max_risk_level: str
    degradation_order: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "profile_type": self.profile_type.value,
            "description": self.description,
            "token_budget": self.token_budget,
            "cost_budget": self.cost_budget,
            "allowed_categories": self.allowed_categories,
            "max_risk_level": self.max_risk_level,
            "degradation_order": self.degradation_order
        }


class ProfileSwitcher:
    """
    配置文件切换器
    
    管理不同运行模式的配置：
    - default: 默认配置
    - safe: 安全模式，限制高风险操作
    - performance: 性能模式，放宽限制
    - development: 开发模式，宽松配置
    - production: 生产模式，严格配置
    - restricted: 受限模式，最小权限
    """
    
    # 预定义配置
    BUILTIN_PROFILES = {
        "default": ProfileConfig(
            name="default",
            profile_type=ProfileType.DEFAULT,
            description="默认配置，平衡安全与性能",
            token_budget=100000,
            cost_budget=10.0,
            allowed_categories=["skill", "workflow", "memory", "report", "external"],
            max_risk_level="medium",
            degradation_order=["safe", "restricted"]
        ),
        "safe": ProfileConfig(
            name="safe",
            profile_type=ProfileType.SAFE,
            description="安全模式，限制高风险操作",
            token_budget=50000,
            cost_budget=5.0,
            allowed_categories=["skill", "memory", "report"],
            max_risk_level="low",
            degradation_order=["restricted"]
        ),
        "performance": ProfileConfig(
            name="performance",
            profile_type=ProfileType.PERFORMANCE,
            description="性能模式，放宽限制",
            token_budget=200000,
            cost_budget=20.0,
            allowed_categories=["skill", "workflow", "memory", "report", "external", "system"],
            max_risk_level="high",
            degradation_order=["default", "safe", "restricted"]
        ),
        "development": ProfileConfig(
            name="development",
            profile_type=ProfileType.DEVELOPMENT,
            description="开发模式，宽松配置",
            token_budget=500000,
            cost_budget=50.0,
            allowed_categories=["skill", "workflow", "memory", "report", "external", "system", "high_risk"],
            max_risk_level="critical",
            degradation_order=["default", "safe", "restricted"]
        ),
        "production": ProfileConfig(
            name="production",
            profile_type=ProfileType.PRODUCTION,
            description="生产模式，严格配置",
            token_budget=80000,
            cost_budget=8.0,
            allowed_categories=["skill", "workflow", "memory", "report"],
            max_risk_level="medium",
            degradation_order=["safe", "restricted"]
        ),
        "restricted": ProfileConfig(
            name="restricted",
            profile_type=ProfileType.RESTRICTED,
            description="受限模式，最小权限",
            token_budget=10000,
            cost_budget=1.0,
            allowed_categories=["memory", "report"],
            max_risk_level="low",
            degradation_order=[]
        ),
    }
    
    def __init__(self):
        self._profiles: Dict[str, ProfileConfig] = dict(self.BUILTIN_PROFILES)
        self._current_profile = "default"
        self._custom_profiles: Dict[str, ProfileConfig] = {}
    
    def get(self, name: str) -> Optional[ProfileConfig]:
        """
        获取配置文件
        
        Args:
            name: 配置文件名
            
        Returns:
            配置文件，不存在返回 None
        """
        return self._profiles.get(name)
    
    def get_current(self) -> ProfileConfig:
        """
        获取当前配置文件
        
        Returns:
            当前配置文件
        """
        return self._profiles.get(self._current_profile, self.BUILTIN_PROFILES["default"])
    
    def switch(self, name: str) -> bool:
        """
        切换配置文件
        
        Args:
            name: 配置文件名
            
        Returns:
            是否切换成功
        """
        if name not in self._profiles:
            return False
        
        self._current_profile = name
        return True
    
    def register(self, profile: ProfileConfig) -> bool:
        """
        注册自定义配置文件
        
        Args:
            profile: 配置文件
            
        Returns:
            是否注册成功
        """
        if profile.name in self.BUILTIN_PROFILES:
            return False
        
        self._profiles[profile.name] = profile
        self._custom_profiles[profile.name] = profile
        return True
    
    def unregister(self, name: str) -> bool:
        """
        注销自定义配置文件
        
        Args:
            name: 配置文件名
            
        Returns:
            是否注销成功
        """
        if name in self.BUILTIN_PROFILES:
            return False
        
        if name not in self._profiles:
            return False
        
        del self._profiles[name]
        if name in self._custom_profiles:
            del self._custom_profiles[name]
        return True
    
    def list_profiles(self) -> List[str]:
        """
        列出所有配置文件
        
        Returns:
            配置文件名列表
        """
        return list(self._profiles.keys())
    
    def get_degradation_chain(self, name: str) -> List[str]:
        """
        获取降级链
        
        Args:
            name: 配置文件名
            
        Returns:
            降级链
        """
        profile = self.get(name)
        if not profile:
            return ["restricted"]
        
        chain = [name] + profile.degradation_order
        if "restricted" not in chain:
            chain.append("restricted")
        return chain
    
    def get_next_degraded_profile(self, name: str) -> Optional[str]:
        """
        获取下一个降级配置
        
        Args:
            name: 当前配置文件名
            
        Returns:
            下一个降级配置名，无则返回 None
        """
        chain = self.get_degradation_chain(name)
        try:
            current_index = chain.index(name)
            if current_index + 1 < len(chain):
                return chain[current_index + 1]
        except ValueError:
            pass
        return None
    
    def is_capability_allowed(self, profile_name: str, category: str) -> bool:
        """
        检查能力分类是否允许
        
        Args:
            profile_name: 配置文件名
            category: 能力分类
            
        Returns:
            是否允许
        """
        profile = self.get(profile_name)
        if not profile:
            return False
        
        return category in profile.allowed_categories
    
    def get_token_budget(self, name: str) -> int:
        """
        获取 token 预算
        
        Args:
            name: 配置文件名
            
        Returns:
            token 预算
        """
        profile = self.get(name)
        return profile.token_budget if profile else 0
    
    def get_cost_budget(self, name: str) -> float:
        """
        获取成本预算
        
        Args:
            name: 配置文件名
            
        Returns:
            成本预算
        """
        profile = self.get(name)
        return profile.cost_budget if profile else 0.0
    
    def get_max_risk_level(self, name: str) -> str:
        """
        获取最大风险等级
        
        Args:
            name: 配置文件名
            
        Returns:
            最大风险等级
        """
        profile = self.get(name)
        return profile.max_risk_level if profile else "low"
    
    def reload(self) -> Dict[str, Any]:
        """
        重新加载配置
        
        Returns:
            重载结果
        """
        self._profiles = dict(self.BUILTIN_PROFILES)
        self._profiles.update(self._custom_profiles)
        
        return {
            "status": "reloaded",
            "total_profiles": len(self._profiles),
            "builtin": len(self.BUILTIN_PROFILES),
            "custom": len(self._custom_profiles),
            "current": self._current_profile
        }
    
    def export_profiles(self) -> str:
        """
        导出配置为 JSON
        
        Returns:
            JSON 字符串
        """
        data = {
            name: profile.to_dict()
            for name, profile in self._profiles.items()
        }
        return json.dumps(data, indent=2, ensure_ascii=False)


# 全局单例
_profile_switcher = None

def get_profile_switcher() -> ProfileSwitcher:
    """获取配置切换器单例"""
    global _profile_switcher
    if _profile_switcher is None:
        _profile_switcher = ProfileSwitcher()
    return _profile_switcher
