"""
Review Policy - 审查策略
判断什么风险等级或能力需要进入 review
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from enum import Enum
import json


class ReviewTrigger(Enum):
    """审查触发条件"""
    RISK_LEVEL = "risk_level"
    CAPABILITY = "capability"
    PROFILE = "profile"
    CUSTOM = "custom"


@dataclass
class ReviewRule:
    """审查规则"""
    name: str
    trigger: ReviewTrigger
    condition: str
    enabled: bool = True
    priority: int = 1
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "trigger": self.trigger.value,
            "condition": self.condition,
            "enabled": self.enabled,
            "priority": self.priority,
            "description": self.description
        }


class ReviewPolicy:
    """
    审查策略
    
    判断是否需要 review：
    - 什么风险等级进入 review
    - 什么 capability 需要 review
    - 什么 profile 需要 review
    """
    
    # 默认审查规则
    DEFAULT_RULES = {
        # 风险等级规则
        "high_risk_level": ReviewRule(
            name="high_risk_level",
            trigger=ReviewTrigger.RISK_LEVEL,
            condition="high",
            enabled=True,
            priority=1,
            description="高风险等级需要审查"
        ),
        "critical_risk_level": ReviewRule(
            name="critical_risk_level",
            trigger=ReviewTrigger.RISK_LEVEL,
            condition="critical",
            enabled=True,
            priority=0,
            description="严重风险等级必须审查"
        ),
        
        # 能力规则
        "high_risk_capability": ReviewRule(
            name="high_risk_capability",
            trigger=ReviewTrigger.CAPABILITY,
            condition="high_risk.*",
            enabled=True,
            priority=2,
            description="高风险能力需要审查"
        ),
        "system_capability": ReviewRule(
            name="system_capability",
            trigger=ReviewTrigger.CAPABILITY,
            condition="system.*",
            enabled=True,
            priority=2,
            description="系统能力需要审查"
        ),
        "external_api": ReviewRule(
            name="external_api",
            trigger=ReviewTrigger.CAPABILITY,
            condition="external.api",
            enabled=True,
            priority=3,
            description="外部 API 调用需要审查"
        ),
        "skill_install": ReviewRule(
            name="skill_install",
            trigger=ReviewTrigger.CAPABILITY,
            condition="skill.install",
            enabled=True,
            priority=3,
            description="技能安装需要审查"
        ),
        "skill_remove": ReviewRule(
            name="skill_remove",
            trigger=ReviewTrigger.CAPABILITY,
            condition="skill.remove",
            enabled=True,
            priority=2,
            description="技能移除需要审查"
        ),
        
        # Profile 规则
        "development_profile": ReviewRule(
            name="development_profile",
            trigger=ReviewTrigger.PROFILE,
            condition="development",
            enabled=False,  # 开发模式默认不审查
            priority=5,
            description="开发模式可选审查"
        ),
    }
    
    def __init__(self):
        self._rules: Dict[str, ReviewRule] = dict(self.DEFAULT_RULES)
        self._custom_rules: Dict[str, ReviewRule] = {}
        
        # 风险等级阈值
        self._risk_thresholds = {
            "low": False,
            "medium": False,
            "high": True,
            "critical": True
        }
        
        # 需要 review 的能力集合
        self._review_capabilities: Set[str] = {
            "high_risk.write",
            "high_risk.delete",
            "high_risk.execute",
            "system.config",
            "system.restart",
            "external.api",
            "skill.install",
            "skill.remove",
            "skill.upgrade",
            "workflow.create",
            "workflow.modify",
            "memory.delete",
            "report.delete"
        }
    
    def should_review(
        self,
        risk_level: Any,
        capabilities: List[str],
        task_meta: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        判断是否需要 review
        
        Args:
            risk_level: 风险等级
            capabilities: 能力列表
            task_meta: 任务元数据
            
        Returns:
            是否需要 review
        """
        # 1. 检查风险等级
        risk_str = risk_level.value if hasattr(risk_level, 'value') else str(risk_level)
        if self._risk_thresholds.get(risk_str, False):
            return True
        
        # 2. 检查能力
        for cap in capabilities:
            if cap in self._review_capabilities:
                return True
            
            # 通配符匹配
            for pattern in self._review_capabilities:
                if self._match_pattern(cap, pattern):
                    return True
        
        # 3. 检查自定义规则
        for rule in self._custom_rules.values():
            if not rule.enabled:
                continue
            
            if rule.trigger == ReviewTrigger.RISK_LEVEL:
                if self._match_pattern(risk_str, rule.condition):
                    return True
            elif rule.trigger == ReviewTrigger.CAPABILITY:
                for cap in capabilities:
                    if self._match_pattern(cap, rule.condition):
                        return True
            elif rule.trigger == ReviewTrigger.PROFILE:
                if task_meta:
                    profile = task_meta.get("profile", "")
                    if self._match_pattern(profile, rule.condition):
                        return True
        
        return False
    
    def add_rule(self, rule: ReviewRule) -> bool:
        """
        添加审查规则
        
        Args:
            rule: 审查规则
            
        Returns:
            是否添加成功
        """
        if rule.name in self._rules:
            return False
        
        self._rules[rule.name] = rule
        self._custom_rules[rule.name] = rule
        return True
    
    def remove_rule(self, name: str) -> bool:
        """
        移除审查规则
        
        Args:
            name: 规则名称
            
        Returns:
            是否移除成功
        """
        if name not in self._rules:
            return False
        
        if name in self.DEFAULT_RULES:
            # 默认规则只禁用，不移除
            self._rules[name].enabled = False
        else:
            del self._rules[name]
            if name in self._custom_rules:
                del self._custom_rules[name]
        
        return True
    
    def enable_rule(self, name: str) -> bool:
        """
        启用规则
        
        Args:
            name: 规则名称
            
        Returns:
            是否成功
        """
        if name not in self._rules:
            return False
        
        self._rules[name].enabled = True
        return True
    
    def disable_rule(self, name: str) -> bool:
        """
        禁用规则
        
        Args:
            name: 规则名称
            
        Returns:
            是否成功
        """
        if name not in self._rules:
            return False
        
        self._rules[name].enabled = False
        return True
    
    def set_risk_threshold(self, level: str, requires_review: bool):
        """
        设置风险等级阈值
        
        Args:
            level: 风险等级
            requires_review: 是否需要审查
        """
        self._risk_thresholds[level] = requires_review
    
    def add_review_capability(self, capability: str):
        """
        添加需要审查的能力
        
        Args:
            capability: 能力名称
        """
        self._review_capabilities.add(capability)
    
    def remove_review_capability(self, capability: str) -> bool:
        """
        移除需要审查的能力
        
        Args:
            capability: 能力名称
            
        Returns:
            是否移除成功
        """
        if capability in self._review_capabilities:
            self._review_capabilities.remove(capability)
            return True
        return False
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """
        获取所有规则
        
        Returns:
            规则列表
        """
        return [rule.to_dict() for rule in self._rules.values()]
    
    def get_review_capabilities(self) -> List[str]:
        """
        获取需要审查的能力列表
        
        Returns:
            能力列表
        """
        return list(self._review_capabilities)
    
    def reload(self) -> Dict[str, Any]:
        """
        重新加载策略
        
        Returns:
            重载结果
        """
        self._rules = dict(self.DEFAULT_RULES)
        self._rules.update(self._custom_rules)
        
        return {
            "status": "reloaded",
            "total_rules": len(self._rules),
            "enabled_rules": sum(1 for r in self._rules.values() if r.enabled),
            "review_capabilities": len(self._review_capabilities)
        }
    
    def _match_pattern(self, value: str, pattern: str) -> bool:
        """
        简单通配符匹配
        
        Args:
            value: 值
            pattern: 模式
            
        Returns:
            是否匹配
        """
        if pattern == "*":
            return True
        
        if "*" not in pattern:
            return value == pattern
        
        # 前缀匹配
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return value.startswith(prefix)
        
        # 后缀匹配
        if pattern.startswith("*"):
            suffix = pattern[1:]
            return value.endswith(suffix)
        
        # 中间匹配
        if "*" in pattern:
            parts = pattern.split("*")
            if len(parts) == 2:
                return value.startswith(parts[0]) and value.endswith(parts[1])
        
        return False
    
    def export(self) -> str:
        """
        导出策略
        
        Returns:
            JSON 字符串
        """
        data = {
            "rules": [rule.to_dict() for rule in self._rules.values()],
            "risk_thresholds": self._risk_thresholds,
            "review_capabilities": list(self._review_capabilities)
        }
        return json.dumps(data, indent=2, ensure_ascii=False)


# 全局单例
_review_policy = None

def get_review_policy() -> ReviewPolicy:
    """获取审查策略单例"""
    global _review_policy
    if _review_policy is None:
        _review_policy = ReviewPolicy()
    return _review_policy
