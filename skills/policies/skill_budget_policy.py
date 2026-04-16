"""Skill Budget Policy - 技能预算策略"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum

from skills.registry.skill_registry import SkillManifest


class BudgetAction(Enum):
    """预算动作"""
    ALLOW = "allow"
    DENY = "deny"
    DEGRADE = "degrade"


@dataclass
class BudgetDecision:
    """预算决策"""
    action: BudgetAction
    allowed: bool
    reason: str
    token_budget: int = 0
    cost_budget: float = 0.0
    degraded_profile: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SkillBudgetPolicy:
    """
    技能预算策略
    
    职责：
    - 基于 governance decision object 判断技能是否可调用
    - budget 不足时 deny 或 degrade
    """
    
    def __init__(self):
        # 预算阈值
        self.token_thresholds = {
            "admin": 32000,
            "developer": 16000,
            "default": 8000,
            "operator": 4000,
            "auditor": 2000,
            "restricted": 1000
        }
        
        self.cost_thresholds = {
            "admin": 100.0,
            "developer": 50.0,
            "default": 20.0,
            "operator": 10.0,
            "auditor": 5.0,
            "restricted": 1.0
        }
        
        # 降级映射
        self.degrade_map = {
            "admin": "developer",
            "developer": "default",
            "default": "operator",
            "operator": "auditor",
            "auditor": "restricted"
        }
    
    def evaluate(
        self,
        manifest: SkillManifest,
        governance_decision: Dict[str, Any],
        current_usage: Dict[str, Any] = None
    ) -> BudgetDecision:
        """
        评估预算
        
        Args:
            manifest: 技能清单
            governance_decision: governance decision object
            current_usage: 当前使用量
        
        Returns:
            BudgetDecision
        """
        current_usage = current_usage or {}
        
        # 从 governance decision 获取预算
        token_budget = governance_decision.get("token_budget", 0)
        cost_budget = governance_decision.get("cost_budget", 0.0)
        profile = governance_decision.get("details", {}).get("token_budget", {}).get("profile", "default")
        
        # 获取当前使用量
        token_used = current_usage.get("token_used", 0)
        cost_used = current_usage.get("cost_used", 0.0)
        
        # 计算剩余
        token_remaining = token_budget - token_used
        cost_remaining = cost_budget - cost_used
        
        # 检查预算是否足够
        token_sufficient = token_remaining > 0
        cost_sufficient = cost_remaining > 0
        
        if token_sufficient and cost_sufficient:
            return BudgetDecision(
                action=BudgetAction.ALLOW,
                allowed=True,
                reason="Budget sufficient",
                token_budget=token_remaining,
                cost_budget=cost_remaining,
                metadata={
                    "profile": profile,
                    "token_budget": token_budget,
                    "token_used": token_used,
                    "cost_budget": cost_budget,
                    "cost_used": cost_used
                }
            )
        
        # 预算不足，尝试降级
        degraded_profile = self.degrade_map.get(profile)
        if degraded_profile:
            new_token = self.token_thresholds.get(degraded_profile, 1000)
            new_cost = self.cost_thresholds.get(degraded_profile, 1.0)
            
            return BudgetDecision(
                action=BudgetAction.DEGRADE,
                allowed=True,
                reason=f"Budget insufficient, degraded from {profile} to {degraded_profile}",
                token_budget=new_token,
                cost_budget=new_cost,
                degraded_profile=degraded_profile,
                metadata={
                    "original_profile": profile,
                    "degraded_profile": degraded_profile,
                    "token_remaining": token_remaining,
                    "cost_remaining": cost_remaining
                }
            )
        
        # 无法降级，拒绝
        return BudgetDecision(
            action=BudgetAction.DENY,
            allowed=False,
            reason=f"Budget exhausted for profile {profile}",
            metadata={
                "profile": profile,
                "token_remaining": token_remaining,
                "cost_remaining": cost_remaining
            }
        )
    
    def check_before_execute(
        self,
        manifest: SkillManifest,
        governance_decision: Dict[str, Any],
        estimated_tokens: int = 1000,
        estimated_cost: float = 0.1
    ) -> BudgetDecision:
        """
        执行前检查预算
        
        Args:
            manifest: 技能清单
            governance_decision: governance decision object
            estimated_tokens: 预估 token 数
            estimated_cost: 预估成本
        
        Returns:
            BudgetDecision
        """
        token_budget = governance_decision.get("token_budget", 0)
        cost_budget = governance_decision.get("cost_budget", 0.0)
        
        if token_budget >= estimated_tokens and cost_budget >= estimated_cost:
            return BudgetDecision(
                action=BudgetAction.ALLOW,
                allowed=True,
                reason="Budget sufficient for execution",
                token_budget=token_budget,
                cost_budget=cost_budget
            )
        
        # 预算不足
        profile = "default"
        degraded_profile = self.degrade_map.get(profile)
        
        if degraded_profile:
            return BudgetDecision(
                action=BudgetAction.DEGRADE,
                allowed=True,
                reason=f"Insufficient budget, consider degraded execution",
                token_budget=self.token_thresholds.get(degraded_profile, 1000),
                cost_budget=self.cost_thresholds.get(degraded_profile, 1.0),
                degraded_profile=degraded_profile
            )
        
        return BudgetDecision(
            action=BudgetAction.DENY,
            allowed=False,
            reason="Insufficient budget for execution"
        )
    
    def set_thresholds(
        self,
        profile: str,
        token_threshold: int,
        cost_threshold: float
    ):
        """设置阈值"""
        self.token_thresholds[profile] = token_threshold
        self.cost_thresholds[profile] = cost_threshold
    
    def get_thresholds(self, profile: str) -> Dict[str, Any]:
        """获取阈值"""
        return {
            "token_threshold": self.token_thresholds.get(profile, 1000),
            "cost_threshold": self.cost_thresholds.get(profile, 1.0)
        }
