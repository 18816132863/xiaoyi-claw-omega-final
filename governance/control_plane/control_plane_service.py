"""
Control Plane Service - 统一控制平面入口
所有任务决策的统一入口，返回正式 control_decision 对象
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid

from .capability_registry import GovernanceCapabilityRegistry
from .profile_switcher import ProfileSwitcher
from .policy_snapshot_store import PolicySnapshotStore
from .decision_audit_log import DecisionAuditLog
from ..review.review_policy import ReviewPolicy
from ..review.review_queue import ReviewQueue
from ..degradation.profile_degradation_strategy import ProfileDegradationStrategy
from ..degradation.capability_degradation_strategy import CapabilityDegradationStrategy
from ..risk.risk_classifier import RiskClassifier
from ..permission.permission_engine import PermissionEngine
from ..budget.token_budget_manager import TokenBudgetManager
from ..budget.cost_budget_manager import CostBudgetManager
from ..guard.high_risk_guard import HighRiskGuard


class DecisionType(Enum):
    """决策类型"""
    ALLOW = "allow"
    DENY = "deny"
    DEGRADE = "degrade"
    REVIEW = "review"


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ControlDecision:
    """
    正式控制决策对象
    所有 control plane 决策统一返回此对象，不再返回散乱 dict
    """
    decision_id: str
    profile: str
    decision: DecisionType
    risk_level: RiskLevel
    token_budget: int
    cost_budget: float
    allowed_capabilities: List[str]
    blocked_capabilities: List[str]
    selected_model_profile: str
    degradation_mode: Optional[str] = None
    requires_review: bool = False
    reasons: List[str] = field(default_factory=list)
    policy_snapshot_id: str = ""
    task_id: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "decision_id": self.decision_id,
            "profile": self.profile,
            "decision": self.decision.value,
            "risk_level": self.risk_level.value,
            "token_budget": self.token_budget,
            "cost_budget": self.cost_budget,
            "allowed_capabilities": self.allowed_capabilities,
            "blocked_capabilities": self.blocked_capabilities,
            "selected_model_profile": self.selected_model_profile,
            "degradation_mode": self.degradation_mode,
            "requires_review": self.requires_review,
            "reasons": self.reasons,
            "policy_snapshot_id": self.policy_snapshot_id,
            "task_id": self.task_id,
            "timestamp": self.timestamp
        }


class ControlPlaneService:
    """
    控制平面服务 - 统一决策入口
    
    对外暴露接口：
    1. decide() - 统一决策
    2. refresh_policies() - 刷新策略
    3. get_policy_snapshot() - 获取策略快照
    4. audit_decision() - 审计决策
    """
    
    def __init__(self):
        # 核心组件
        self.capability_registry = GovernanceCapabilityRegistry()
        self.profile_switcher = ProfileSwitcher()
        self.snapshot_store = PolicySnapshotStore()
        self.audit_log = DecisionAuditLog()
        
        # 风险与权限
        self.risk_classifier = RiskClassifier()
        self.permission_engine = PermissionEngine()
        
        # 预算管理
        self.token_budget_manager = TokenBudgetManager()
        self.cost_budget_manager = CostBudgetManager()
        
        # 高风险守卫
        self.high_risk_guard = HighRiskGuard()
        
        # Review
        self.review_policy = ReviewPolicy()
        self.review_queue = ReviewQueue()
        
        # 降级策略
        self.profile_degradation = ProfileDegradationStrategy()
        self.capability_degradation = CapabilityDegradationStrategy()
        
        # 当前 profile
        self.current_profile = "default"
    
    def decide(
        self,
        task_meta: Dict[str, Any],
        requested_capabilities: List[str],
        context_summary: Optional[Dict[str, Any]] = None
    ) -> ControlDecision:
        """
        统一决策入口
        
        决策流程：
        1. 先判风险
        2. 再判权限
        3. 再算预算
        4. 再决定是否 review
        5. 再决定是否 degrade
        6. 最后生成正式 control_decision
        
        Args:
            task_meta: 任务元数据
            requested_capabilities: 请求的能力列表
            context_summary: 上下文摘要
            
        Returns:
            ControlDecision: 正式决策对象
        """
        decision_id = str(uuid.uuid4())
        task_id = task_meta.get("task_id", str(uuid.uuid4()))
        profile = task_meta.get("profile", self.current_profile)
        reasons = []
        
        # 1. 验证 capability 是否在注册表中
        validated_capabilities = []
        unknown_capabilities = []
        for cap in requested_capabilities:
            if self.capability_registry.is_registered(cap):
                validated_capabilities.append(cap)
            else:
                unknown_capabilities.append(cap)
                reasons.append(f"Unknown capability: {cap}")
        
        # 2. 风险分类
        risk_level = self.risk_classifier.classify(task_meta, validated_capabilities)
        
        # 3. 权限检查
        permission_result = self.permission_engine.check(
            profile, validated_capabilities, context_summary
        )
        allowed_by_permission = permission_result.get("allowed", [])
        blocked_by_permission = permission_result.get("blocked", [])
        
        if blocked_by_permission:
            reasons.append(f"Blocked by permission: {blocked_by_permission}")
        
        # 4. 预算检查
        token_budget = self.token_budget_manager.get_budget(profile)
        cost_budget = self.cost_budget_manager.get_budget(profile)
        
        token_available = self.token_budget_manager.check_available(profile)
        cost_available = self.cost_budget_manager.check_available(profile)
        
        # 5. 高风险守卫
        high_risk_result = self.high_risk_guard.check(
            task_meta, validated_capabilities, risk_level
        )
        blocked_by_guard = high_risk_result.get("blocked", [])
        
        if blocked_by_guard:
            reasons.append(f"Blocked by high risk guard: {blocked_by_guard}")
        
        # 6. 计算最终允许/阻止的能力
        allowed_capabilities = [
            cap for cap in allowed_by_permission
            if cap not in blocked_by_guard and cap not in unknown_capabilities
        ]
        blocked_capabilities = blocked_by_permission + blocked_by_guard + unknown_capabilities
        
        # 7. 判断是否需要 review
        requires_review = self.review_policy.should_review(
            risk_level, validated_capabilities, task_meta
        )
        
        if requires_review:
            reasons.append("Requires review due to risk level or capability")
        
        # 8. 判断是否需要降级
        degradation_mode = None
        selected_model_profile = profile
        
        should_degrade = (
            not token_available or 
            not cost_available or 
            risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
        
        if should_degrade:
            degradation_mode = self.capability_degradation.get_degradation_mode(
                risk_level, token_available, cost_available
            )
            selected_model_profile = self.profile_degradation.get_degraded_profile(
                profile, risk_level
            )
            reasons.append(f"Degraded due to: risk={risk_level.value}, token={token_available}, cost={cost_available}")
        
        # 9. 获取策略快照
        snapshot = self.snapshot_store.get_or_create(profile)
        
        # 10. 确定最终决策类型
        # 如果有未知能力，直接拒绝
        if unknown_capabilities:
            decision_type = DecisionType.DENY
        elif len(allowed_capabilities) == 0 and len(requested_capabilities) > 0:
            decision_type = DecisionType.DENY
        elif requires_review:
            decision_type = DecisionType.REVIEW
            # 入队 review
            self.review_queue.enqueue(
                task_id=task_id,
                profile=profile,
                reason=f"Risk level: {risk_level.value}, Capabilities: {validated_capabilities}",
                decision_id=decision_id
            )
        elif degradation_mode:
            decision_type = DecisionType.DEGRADE
        else:
            decision_type = DecisionType.ALLOW
        
        # 11. 构建决策对象
        decision = ControlDecision(
            decision_id=decision_id,
            profile=profile,
            decision=decision_type,
            risk_level=risk_level,
            token_budget=token_budget if token_available else 0,
            cost_budget=cost_budget if cost_available else 0.0,
            allowed_capabilities=allowed_capabilities,
            blocked_capabilities=blocked_capabilities,
            selected_model_profile=selected_model_profile,
            degradation_mode=degradation_mode,
            requires_review=requires_review,
            reasons=reasons,
            policy_snapshot_id=snapshot["snapshot_id"],
            task_id=task_id
        )
        
        # 12. 审计落盘
        self.audit_log.record(decision)
        
        return decision
    
    def refresh_policies(self) -> Dict[str, Any]:
        """
        刷新所有策略
        
        Returns:
            刷新结果
        """
        results = {
            "capability_registry": self.capability_registry.reload(),
            "profile_switcher": self.profile_switcher.reload(),
            "risk_classifier": self.risk_classifier.reload(),
            "permission_engine": self.permission_engine.reload(),
            "token_budget": self.token_budget_manager.reload(),
            "cost_budget": self.cost_budget_manager.reload(),
            "review_policy": self.review_policy.reload(),
            "degradation": {
                "profile": self.profile_degradation.reload(),
                "capability": self.capability_degradation.reload()
            }
        }
        
        # 刷新所有 profile 的快照
        for profile in self.profile_switcher.list_profiles():
            self.snapshot_store.refresh(profile)
        
        return results
    
    def get_policy_snapshot(self, profile: str) -> Dict[str, Any]:
        """
        获取策略快照
        
        Args:
            profile: 配置文件名
            
        Returns:
            策略快照
        """
        return self.snapshot_store.get_or_create(profile)
    
    def audit_decision(self, decision: ControlDecision) -> Dict[str, Any]:
        """
        审计决策
        
        Args:
            decision: 决策对象
            
        Returns:
            审计结果
        """
        return self.audit_log.query(decision_id=decision.decision_id)


# 全局单例
_control_plane_service = None

def get_control_plane_service() -> ControlPlaneService:
    """获取控制平面服务单例"""
    global _control_plane_service
    if _control_plane_service is None:
        _control_plane_service = ControlPlaneService()
    return _control_plane_service
