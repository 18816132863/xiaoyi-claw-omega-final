"""
Profile Degradation Strategy - 配置降级策略
根据风险等级和资源状况降级配置
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class DegradationReason(Enum):
    """降级原因"""
    HIGH_RISK = "high_risk"
    TOKEN_EXHAUSTED = "token_exhausted"
    COST_EXHAUSTED = "cost_exhausted"
    MANUAL = "manual"
    SYSTEM = "system"


@dataclass
class DegradationRule:
    """降级规则"""
    from_profile: str
    to_profile: str
    trigger_risk_levels: List[str]
    trigger_token_threshold: int
    trigger_cost_threshold: float
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_profile": self.from_profile,
            "to_profile": self.to_profile,
            "trigger_risk_levels": self.trigger_risk_levels,
            "trigger_token_threshold": self.trigger_token_threshold,
            "trigger_cost_threshold": self.trigger_cost_threshold,
            "enabled": self.enabled
        }


class ProfileDegradationStrategy:
    """
    配置降级策略
    
    根据风险等级和资源状况降级配置：
    - 高风险 -> 降级到更安全的配置
    - 资源不足 -> 降级到更低消耗的配置
    """
    
    # 默认降级规则
    DEFAULT_RULES = [
        DegradationRule(
            from_profile="performance",
            to_profile="default",
            trigger_risk_levels=["high"],
            trigger_token_threshold=50000,
            trigger_cost_threshold=10.0
        ),
        DegradationRule(
            from_profile="performance",
            to_profile="safe",
            trigger_risk_levels=["critical"],
            trigger_token_threshold=20000,
            trigger_cost_threshold=5.0
        ),
        DegradationRule(
            from_profile="development",
            to_profile="default",
            trigger_risk_levels=["high"],
            trigger_token_threshold=100000,
            trigger_cost_threshold=20.0
        ),
        DegradationRule(
            from_profile="development",
            to_profile="safe",
            trigger_risk_levels=["critical"],
            trigger_token_threshold=50000,
            trigger_cost_threshold=10.0
        ),
        DegradationRule(
            from_profile="default",
            to_profile="safe",
            trigger_risk_levels=["high", "critical"],
            trigger_token_threshold=30000,
            trigger_cost_threshold=5.0
        ),
        DegradationRule(
            from_profile="safe",
            to_profile="restricted",
            trigger_risk_levels=["critical"],
            trigger_token_threshold=10000,
            trigger_cost_threshold=2.0
        ),
    ]
    
    # 降级链
    DEGRADATION_CHAIN = {
        "development": ["default", "safe", "restricted"],
        "performance": ["default", "safe", "restricted"],
        "production": ["safe", "restricted"],
        "default": ["safe", "restricted"],
        "safe": ["restricted"],
        "restricted": []
    }
    
    def __init__(self):
        self._rules: List[DegradationRule] = list(self.DEFAULT_RULES)
        self._custom_rules: List[DegradationRule] = []
        
        # 风险等级到降级配置的映射
        self._risk_profile_map = {
            "low": None,  # 不降级
            "medium": None,  # 不降级
            "high": "safe",
            "critical": "restricted"
        }
    
    def get_degraded_profile(
        self,
        current_profile: str,
        risk_level: Any,
        token_available: bool = True,
        cost_available: bool = True
    ) -> str:
        """
        获取降级后的配置
        
        Args:
            current_profile: 当前配置
            risk_level: 风险等级
            token_available: token 是否可用
            cost_available: 成本是否可用
            
        Returns:
            降级后的配置名
        """
        risk_str = risk_level.value if hasattr(risk_level, 'value') else str(risk_level)
        
        # 1. 检查风险等级触发
        target_by_risk = self._risk_profile_map.get(risk_str)
        if target_by_risk:
            # 检查是否在降级链中
            chain = self.DEGRADATION_CHAIN.get(current_profile, [])
            if target_by_risk in chain:
                return target_by_risk
        
        # 2. 检查规则触发
        for rule in self._rules:
            if not rule.enabled:
                continue
            
            if rule.from_profile != current_profile:
                continue
            
            # 检查风险等级
            if risk_str in rule.trigger_risk_levels:
                return rule.to_profile
            
            # 检查资源
            if not token_available or not cost_available:
                return rule.to_profile
        
        # 3. 资源不足时降一级
        if not token_available or not cost_available:
            chain = self.DEGRADATION_CHAIN.get(current_profile, [])
            if chain:
                return chain[0]
        
        return current_profile
    
    def get_degradation_chain(self, profile: str) -> List[str]:
        """
        获取降级链
        
        Args:
            profile: 配置名
            
        Returns:
            降级链
        """
        chain = [profile] + self.DEGRADATION_CHAIN.get(profile, [])
        return chain
    
    def add_rule(self, rule: DegradationRule) -> bool:
        """
        添加降级规则
        
        Args:
            rule: 降级规则
            
        Returns:
            是否添加成功
        """
        self._rules.append(rule)
        self._custom_rules.append(rule)
        return True
    
    def remove_rule(self, from_profile: str, to_profile: str) -> bool:
        """
        移除降级规则
        
        Args:
            from_profile: 源配置
            to_profile: 目标配置
            
        Returns:
            是否移除成功
        """
        for i, rule in enumerate(self._rules):
            if rule.from_profile == from_profile and rule.to_profile == to_profile:
                # 检查是否是默认规则
                if rule in self.DEFAULT_RULES:
                    rule.enabled = False
                else:
                    self._rules.pop(i)
                    if rule in self._custom_rules:
                        self._custom_rules.remove(rule)
                return True
        return False
    
    def set_risk_profile_map(self, risk_level: str, target_profile: Optional[str]):
        """
        设置风险等级到配置的映射
        
        Args:
            risk_level: 风险等级
            target_profile: 目标配置（None 表示不降级）
        """
        self._risk_profile_map[risk_level] = target_profile
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """
        获取所有规则
        
        Returns:
            规则列表
        """
        return [rule.to_dict() for rule in self._rules]
    
    def reload(self) -> Dict[str, Any]:
        """
        重新加载策略
        
        Returns:
            重载结果
        """
        self._rules = list(self.DEFAULT_RULES) + self._custom_rules
        
        return {
            "status": "reloaded",
            "total_rules": len(self._rules),
            "enabled_rules": sum(1 for r in self._rules if r.enabled),
            "degradation_chains": len(self.DEGRADATION_CHAIN)
        }
    
    def export(self) -> str:
        """
        导出策略
        
        Returns:
            JSON 字符串
        """
        data = {
            "rules": [rule.to_dict() for rule in self._rules],
            "degradation_chains": self.DEGRADATION_CHAIN,
            "risk_profile_map": self._risk_profile_map
        }
        return json.dumps(data, indent=2, ensure_ascii=False)


# 全局单例
_profile_degradation_strategy = None

def get_profile_degradation_strategy() -> ProfileDegradationStrategy:
    """获取配置降级策略单例"""
    global _profile_degradation_strategy
    if _profile_degradation_strategy is None:
        _profile_degradation_strategy = ProfileDegradationStrategy()
    return _profile_degradation_strategy
