"""Policy engine - central policy management and enforcement."""

from typing import Dict, List, Optional, Any, Callable
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
    Central policy management and enforcement.
    
    Manages policies for:
    - Routing decisions
    - Model selection
    - Tool/skill access
    - Budget limits
    - Permissions
    - Risk controls
    - Degradation modes
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
        统一策略评估入口（正式控制平面）
        
        接入组件：
        1. risk_classifier - 风险分类
        2. permission_engine - 权限检查
        3. token_budget_manager - Token 预算
        4. cost_budget_manager - 成本预算
        5. high_risk_guard - 高风险守卫
        
        Args:
            task_meta: 任务元数据（包含 intent, action 等）
            profile: 执行配置
            requested_capabilities: 请求的能力列表
        
        Returns:
            正式 decision object，包含：
            - decision: allow / deny / degrade / review
            - allowed: bool
            - risk_level: str
            - token_budget: int
            - cost_budget: float
            - allowed_capabilities: list
            - blocked_capabilities: list
            - requires_review: bool
            - reason: str
        """
        from ..risk.risk_classifier import RiskClassifier
        from ..risk.high_risk_guard import HighRiskGuard
        from ..permissions.permission_engine import PermissionEngine
        from ..budget.token_budget_manager import TokenBudgetManager
        from ..budget.cost_budget_manager import CostBudgetManager, CostType
        
        requested_capabilities = requested_capabilities or []
        
        # 1. 风险分类
        risk_classifier = RiskClassifier()
        risk_assessment = risk_classifier.classify(task_meta, profile)
        
        # 2. 权限检查
        permission_engine = PermissionEngine()
        perm_check = permission_engine.check_permissions(
            profile,
            requested_permissions=["read", "write", "execute"],
            requested_capabilities=requested_capabilities
        )
        
        # 3. Token 预算
        token_budget_mgr = TokenBudgetManager()
        token_budget_info = token_budget_mgr.get_decision_budget(profile)
        
        # 4. 成本预算
        cost_budget_mgr = CostBudgetManager()
        cost_budget_info = cost_budget_mgr.get_decision_budget(profile)
        
        # 5. 高风险守卫
        high_risk_guard = HighRiskGuard()
        guard_decision = high_risk_guard.guard(
            assessment=risk_assessment,
            profile=profile,
            requested_capabilities=requested_capabilities,
            approved=task_meta.get("approved", False)
        )
        
        # 6. 综合决策
        decision = guard_decision.action.value
        allowed = guard_decision.action.value in ["allow", "degrade"]
        requires_review = guard_decision.review_required
        
        # 获取允许/禁止的能力
        allowed_capabilities = permission_engine.get_allowed_capabilities(profile)
        blocked_capabilities = permission_engine.get_blocked_capabilities(profile)
        
        # 获取预算
        profile_budgets = permission_engine.get_profile_budgets(profile)
        token_budget = min(
            token_budget_info["remaining"],
            profile_budgets["max_token_budget"]
        )
        cost_budget = min(
            cost_budget_info["api_call"]["remaining"],
            profile_budgets["max_cost_budget"]
        )
        
        # 构建决策对象
        result = {
            "decision": decision,
            "allowed": allowed,
            "risk_level": risk_assessment.risk_level.value,
            "risk_score": risk_assessment.risk_score,
            "risk_factors": risk_assessment.factors,
            "token_budget": token_budget,
            "cost_budget": cost_budget,
            "allowed_capabilities": allowed_capabilities,
            "blocked_capabilities": blocked_capabilities,
            "requires_review": requires_review,
            "reason": guard_decision.reason,
            "mitigations": risk_assessment.mitigations,
            "details": {
                "risk_assessment": {
                    "level": risk_assessment.risk_level.value,
                    "score": risk_assessment.risk_score,
                    "factors": risk_assessment.factors
                },
                "permission_check": {
                    "allowed": perm_check.allowed,
                    "granted": perm_check.granted,
                    "denied": perm_check.denied
                },
                "token_budget": token_budget_info,
                "cost_budget": cost_budget_info,
                "guard_decision": {
                    "action": guard_decision.action.value,
                    "reason": guard_decision.reason,
                    "degraded_capabilities": guard_decision.degraded_capabilities,
                    "fallback_profile": guard_decision.fallback_profile
                }
            }
        }
        
        # 记录决策
        self._decision_log.append({
            "timestamp": datetime.now().isoformat(),
            "task_meta": task_meta,
            "profile": profile,
            "requested_capabilities": requested_capabilities,
            "decision": decision,
            "allowed": allowed,
            "risk_level": risk_assessment.risk_level.value
        })
        
        return result


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
