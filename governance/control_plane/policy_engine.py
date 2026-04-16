"""
Policy Engine - 策略引擎 Façade
仅作为兼容入口，真实逻辑在 ControlPlaneService
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class PolicyType(Enum):
    ROUTING = "routing"
    MODEL_SELECTION = "model_selection"
    TOOL_SELECTION = "tool_selection"
    BUDGET = "budget"
    PERMISSION = "permission"
    RISK = "risk"
    DEGRADATION = "degradation"


class PolicyEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"


@dataclass
class Policy:
    """A policy rule."""
    policy_id: str
    name: str
    policy_type: PolicyType
    effect: PolicyEffect
    description: str = ""
    conditions: List[Dict] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    priority: int = 100
    enabled: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def evaluate(self, context: Dict) -> tuple[PolicyEffect, str]:
        """Evaluate policy against context."""
        if not self.enabled:
            return PolicyEffect.ALLOW, "Policy disabled"
        
        # Check conditions
        for condition in self.conditions:
            if not self._check_condition(condition, context):
                return PolicyEffect.ALLOW, "Condition not met"
        
        return self.effect, f"Policy {self.policy_id} applied"
    
    def _check_condition(self, condition: Dict, context: Dict) -> bool:
        """Check a single condition."""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")
        
        context_value = context.get(field)
        
        if operator == "eq":
            return context_value == value
        elif operator == "ne":
            return context_value != value
        elif operator == "in":
            return context_value in value
        elif operator == "not_in":
            return context_value not in value
        elif operator == "gt":
            return context_value > value
        elif operator == "lt":
            return context_value < value
        elif operator == "contains":
            return value in context_value if context_value else False
        elif operator == "exists":
            return context_value is not None
        
        return True


class PolicyEngine:
    """
    策略引擎 Façade
    
    仅作为兼容入口，真实逻辑委托给 ControlPlaneService。
    所有决策统一通过 ControlPlaneService.decide() 处理。
    """
    
    def __init__(self):
        self._policies: Dict[str, Policy] = {}
        self._type_index: Dict[PolicyType, List[str]] = {t: [] for t in PolicyType}
        self._decision_log: List[Dict] = []
    
    def register(self, policy: Policy) -> str:
        """Register a policy."""
        self._policies[policy.policy_id] = policy
        if policy.policy_id not in self._type_index[policy.policy_type]:
            self._type_index[policy.policy_type].append(policy.policy_id)
        return policy.policy_id
    
    def unregister(self, policy_id: str) -> bool:
        """Unregister a policy."""
        if policy_id not in self._policies:
            return False
        
        policy = self._policies[policy_id]
        self._type_index[policy.policy_type].remove(policy_id)
        del self._policies[policy_id]
        return True
    
    def evaluate(
        self,
        policy_type: PolicyType,
        context: Dict,
        log_decision: bool = True
    ) -> tuple[PolicyEffect, List[str]]:
        """
        Evaluate all policies of a type against context.
        
        Returns:
            Tuple of (final_effect, applied_policy_ids)
        """
        applied = []
        final_effect = PolicyEffect.ALLOW
        
        # Get policies sorted by priority
        policy_ids = self._type_index.get(policy_type, [])
        policies = [self._policies[pid] for pid in policy_ids if pid in self._policies]
        policies.sort(key=lambda p: p.priority, reverse=True)
        
        for policy in policies:
            effect, reason = policy.evaluate(context)
            
            if effect != PolicyEffect.ALLOW:
                applied.append(policy.policy_id)
                final_effect = effect
                
                # DENY overrides everything
                if effect == PolicyEffect.DENY:
                    break
        
        # Log decision
        if log_decision:
            self._decision_log.append({
                "timestamp": datetime.now().isoformat(),
                "policy_type": policy_type.value,
                "context": context,
                "effect": final_effect.value,
                "applied_policies": applied
            })
        
        return final_effect, applied
    
    def check_allowed(self, policy_type: PolicyType, context: Dict) -> tuple[bool, str]:
        """Check if action is allowed."""
        effect, applied = self.evaluate(policy_type, context)
        
        if effect == PolicyEffect.ALLOW:
            return True, ""
        elif effect == PolicyEffect.DENY:
            return False, f"Denied by policies: {applied}"
        else:
            return True, f"Conditional: {applied}"
    
    def get_policies(self, policy_type: PolicyType = None) -> List[Policy]:
        """Get policies, optionally filtered by type."""
        if policy_type:
            ids = self._type_index.get(policy_type, [])
            return [self._policies[pid] for pid in ids if pid in self._policies]
        return list(self._policies.values())
    
    def enable_policy(self, policy_id: str) -> bool:
        """Enable a policy."""
        if policy_id in self._policies:
            self._policies[policy_id].enabled = True
            return True
        return False
    
    def disable_policy(self, policy_id: str) -> bool:
        """Disable a policy."""
        if policy_id in self._policies:
            self._policies[policy_id].enabled = False
            return True
        return False
    
    def get_decision_log(self, limit: int = 100) -> List[Dict]:
        """Get recent policy decisions."""
        return self._decision_log[-limit:]
    
    def clear_decision_log(self):
        """Clear decision log."""
        self._decision_log.clear()
    
    def evaluate_policy(
        self,
        task_meta: Dict,
        profile: str,
        requested_capabilities: List[str] = None
    ) -> Dict:
        """
        统一策略评估入口（Façade）
        
        委托给 ControlPlaneService.decide()，返回正式 ControlDecision。
        
        Args:
            task_meta: 任务元数据
            profile: 执行配置
            requested_capabilities: 请求的能力列表
        
        Returns:
            ControlDecision.to_dict() 结果
        """
        from .control_plane_service import get_control_plane_service
        
        # 获取控制平面服务
        service = get_control_plane_service()
        
        # 调用统一决策入口
        decision = service.decide(
            task_meta=task_meta,
            requested_capabilities=requested_capabilities or [],
            context_summary=None
        )
        
        # 返回字典格式
        return decision.to_dict()


# Pre-defined policies
def create_default_policies() -> List[Policy]:
    """Create default policy set."""
    return [
        Policy(
            policy_id="deny_high_risk_without_approval",
            name="Deny High Risk Without Approval",
            policy_type=PolicyType.RISK,
            effect=PolicyEffect.DENY,
            description="Deny high-risk actions without explicit approval",
            conditions=[
                {"field": "risk_level", "operator": "eq", "value": "high"},
                {"field": "approved", "operator": "eq", "value": False}
            ],
            priority=1000
        ),
        Policy(
            policy_id="budget_limit_token",
            name="Token Budget Limit",
            policy_type=PolicyType.BUDGET,
            effect=PolicyEffect.DENY,
            description="Deny if token budget exceeded",
            conditions=[
                {"field": "token_usage", "operator": "gt", "value": "token_budget"}
            ],
            priority=900
        ),
        Policy(
            policy_id="restrict_deprecated_skills",
            name="Restrict Deprecated Skills",
            policy_type=PolicyType.TOOL_SELECTION,
            effect=PolicyEffect.CONDITIONAL,
            description="Require confirmation for deprecated skills",
            conditions=[
                {"field": "skill_status", "operator": "eq", "value": "deprecated"}
            ],
            priority=800
        )
    ]
