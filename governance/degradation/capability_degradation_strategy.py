"""
Capability Degradation Strategy - 能力降级策略
根据风险等级和资源状况限制能力
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import Enum
import json


class DegradationMode(Enum):
    """降级模式"""
    NONE = "none"
    SAFE = "safe"
    RESTRICTED = "restricted"
    MINIMAL = "minimal"


@dataclass
class CapabilityDegradationRule:
    """能力降级规则"""
    mode: DegradationMode
    blocked_categories: List[str]
    blocked_capabilities: List[str]
    max_risk_weight: float
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "blocked_categories": self.blocked_categories,
            "blocked_capabilities": self.blocked_capabilities,
            "max_risk_weight": self.max_risk_weight,
            "description": self.description
        }


class CapabilityDegradationStrategy:
    """
    能力降级策略
    
    根据风险等级和资源状况限制能力：
    1. 限制高风险 capability
    2. 切换低成本 profile
    3. 强制 safe mode
    """
    
    # 降级模式配置
    DEGRADATION_MODES = {
        DegradationMode.NONE: CapabilityDegradationRule(
            mode=DegradationMode.NONE,
            blocked_categories=[],
            blocked_capabilities=[],
            max_risk_weight=5.0,
            description="无限制"
        ),
        DegradationMode.SAFE: CapabilityDegradationRule(
            mode=DegradationMode.SAFE,
            blocked_categories=["high_risk", "system"],
            blocked_capabilities=[
                "high_risk.write",
                "high_risk.delete",
                "high_risk.execute",
                "system.restart"
            ],
            max_risk_weight=3.0,
            description="安全模式，限制高风险操作"
        ),
        DegradationMode.RESTRICTED: CapabilityDegradationRule(
            mode=DegradationMode.RESTRICTED,
            blocked_categories=["high_risk", "system", "external"],
            blocked_capabilities=[
                "high_risk.*",
                "system.*",
                "external.api",
                "external.network",
                "skill.install",
                "skill.remove"
            ],
            max_risk_weight=2.0,
            description="受限模式，仅允许基础操作"
        ),
        DegradationMode.MINIMAL: CapabilityDegradationRule(
            mode=DegradationMode.MINIMAL,
            blocked_categories=["high_risk", "system", "external", "workflow"],
            blocked_capabilities=[
                "high_risk.*",
                "system.*",
                "external.*",
                "workflow.create",
                "workflow.modify",
                "skill.*"
            ],
            max_risk_weight=1.0,
            description="最小模式，仅允许读取操作"
        ),
    }
    
    # 风险等级到降级模式的映射
    RISK_MODE_MAP = {
        "low": DegradationMode.NONE,
        "medium": DegradationMode.NONE,
        "high": DegradationMode.SAFE,
        "critical": DegradationMode.RESTRICTED
    }
    
    def __init__(self):
        self._custom_modes: Dict[DegradationMode, CapabilityDegradationRule] = {}
        self._current_mode = DegradationMode.NONE
    
    def get_degradation_mode(
        self,
        risk_level: Any,
        token_available: bool = True,
        cost_available: bool = True
    ) -> str:
        """
        获取降级模式
        
        Args:
            risk_level: 风险等级
            token_available: token 是否可用
            cost_available: 成本是否可用
            
        Returns:
            降级模式名
        """
        risk_str = risk_level.value if hasattr(risk_level, 'value') else str(risk_level)
        
        # 1. 根据风险等级确定模式
        mode = self.RISK_MODE_MAP.get(risk_str, DegradationMode.SAFE)
        
        # 2. 资源不足时升级降级级别
        if not token_available or not cost_available:
            if mode == DegradationMode.NONE:
                mode = DegradationMode.SAFE
            elif mode == DegradationMode.SAFE:
                mode = DegradationMode.RESTRICTED
            elif mode == DegradationMode.RESTRICTED:
                mode = DegradationMode.MINIMAL
        
        return mode.value
    
    def get_blocked_capabilities(
        self,
        mode: DegradationMode
    ) -> List[str]:
        """
        获取被阻止的能力列表
        
        Args:
            mode: 降级模式
            
        Returns:
            被阻止的能力列表
        """
        rule = self._get_rule(mode)
        return rule.blocked_capabilities if rule else []
    
    def get_blocked_categories(
        self,
        mode: DegradationMode
    ) -> List[str]:
        """
        获取被阻止的能力分类列表
        
        Args:
            mode: 降级模式
            
        Returns:
            被阻止的分类列表
        """
        rule = self._get_rule(mode)
        return rule.blocked_categories if rule else []
    
    def is_capability_allowed(
        self,
        capability: str,
        category: str,
        mode: DegradationMode
    ) -> bool:
        """
        检查能力是否允许
        
        Args:
            capability: 能力名称
            category: 能力分类
            mode: 降级模式
            
        Returns:
            是否允许
        """
        rule = self._get_rule(mode)
        if not rule:
            return True
        
        # 检查分类
        if category in rule.blocked_categories:
            return False
        
        # 检查能力
        for blocked in rule.blocked_capabilities:
            if self._match_capability(capability, blocked):
                return False
        
        return True
    
    def filter_capabilities(
        self,
        capabilities: List[str],
        categories: Dict[str, str],
        mode: DegradationMode
    ) -> Dict[str, List[str]]:
        """
        过滤能力
        
        Args:
            capabilities: 能力列表
            categories: 能力到分类的映射
            mode: 降级模式
            
        Returns:
            {"allowed": [...], "blocked": [...]}
        """
        allowed = []
        blocked = []
        
        for cap in capabilities:
            category = categories.get(cap, "unknown")
            if self.is_capability_allowed(cap, category, mode):
                allowed.append(cap)
            else:
                blocked.append(cap)
        
        return {"allowed": allowed, "blocked": blocked}
    
    def set_mode(self, mode: DegradationMode):
        """
        设置当前降级模式
        
        Args:
            mode: 降级模式
        """
        self._current_mode = mode
    
    def get_current_mode(self) -> DegradationMode:
        """
        获取当前降级模式
        
        Returns:
            当前降级模式
        """
        return self._current_mode
    
    def add_custom_mode(self, rule: CapabilityDegradationRule):
        """
        添加自定义降级模式
        
        Args:
            rule: 降级规则
        """
        self._custom_modes[rule.mode] = rule
    
    def remove_custom_mode(self, mode: DegradationMode) -> bool:
        """
        移除自定义降级模式
        
        Args:
            mode: 降级模式
            
        Returns:
            是否移除成功
        """
        if mode in self._custom_modes:
            del self._custom_modes[mode]
            return True
        return False
    
    def get_modes(self) -> List[Dict[str, Any]]:
        """
        获取所有降级模式
        
        Returns:
            降级模式列表
        """
        modes = dict(self.DEGRADATION_MODES)
        modes.update(self._custom_modes)
        return [rule.to_dict() for rule in modes.values()]
    
    def reload(self) -> Dict[str, Any]:
        """
        重新加载策略
        
        Returns:
            重载结果
        """
        return {
            "status": "reloaded",
            "builtin_modes": len(self.DEGRADATION_MODES),
            "custom_modes": len(self._custom_modes),
            "current_mode": self._current_mode.value
        }
    
    def _get_rule(self, mode: DegradationMode) -> Optional[CapabilityDegradationRule]:
        """
        获取降级规则
        
        Args:
            mode: 降级模式
            
        Returns:
            降级规则
        """
        if mode in self._custom_modes:
            return self._custom_modes[mode]
        return self.DEGRADATION_MODES.get(mode)
    
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
    
    def export(self) -> str:
        """
        导出策略
        
        Returns:
            JSON 字符串
        """
        modes = dict(self.DEGRADATION_MODES)
        modes.update(self._custom_modes)
        
        data = {
            "modes": {mode.value: rule.to_dict() for mode, rule in modes.items()},
            "risk_mode_map": {k: v.value for k, v in self.RISK_MODE_MAP.items()},
            "current_mode": self._current_mode.value
        }
        return json.dumps(data, indent=2, ensure_ascii=False)


# 全局单例
_capability_degradation_strategy = None

def get_capability_degradation_strategy() -> CapabilityDegradationStrategy:
    """获取能力降级策略单例"""
    global _capability_degradation_strategy
    if _capability_degradation_strategy is None:
        _capability_degradation_strategy = CapabilityDegradationStrategy()
    return _capability_degradation_strategy
