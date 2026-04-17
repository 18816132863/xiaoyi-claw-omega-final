"""
Source Policy Router - 来源策略路由器
决定当前任务允许检索哪些来源
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum


class SourceType(Enum):
    """来源类型"""
    SESSION_HISTORY = "session_history"
    LONG_TERM_MEMORY = "long_term_memory"
    REPORT_MEMORY = "report_memory"
    WORKFLOW_HISTORY = "workflow_history"
    SKILL_HISTORY = "skill_history"
    USER_PREFERENCE = "user_preference"
    COMPANY_KNOWLEDGE = "company_knowledge"
    EXTERNAL_KNOWLEDGE = "external_knowledge"


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SourcePolicy:
    """来源策略"""
    source_type: SourceType
    allowed_profiles: List[str] = field(default_factory=lambda: ["*"])
    required_capabilities: List[str] = field(default_factory=list)
    max_risk_level: RiskLevel = RiskLevel.HIGH
    user_scope_only: bool = False
    company_scope: bool = True
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_type": self.source_type.value,
            "allowed_profiles": self.allowed_profiles,
            "required_capabilities": self.required_capabilities,
            "max_risk_level": self.max_risk_level.value,
            "user_scope_only": self.user_scope_only,
            "company_scope": self.company_scope,
            "enabled": self.enabled
        }


@dataclass
class RoutingResult:
    """路由结果"""
    allowed_sources: List[SourceType]
    denied_sources: List[SourceType]
    reasons: Dict[str, str] = field(default_factory=dict)
    profile: str = ""
    risk_level: RiskLevel = RiskLevel.LOW
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed_sources": [s.value for s in self.allowed_sources],
            "denied_sources": [s.value for s in self.denied_sources],
            "reasons": self.reasons,
            "profile": self.profile,
            "risk_level": self.risk_level.value,
            "timestamp": self.timestamp
        }


class SourcePolicyRouter:
    """
    来源策略路由器

    职责：
    - 根据配置决定允许检索的来源
    - 根据风险等级限制来源范围
    - 根据 capability 限制来源范围
    - 支持用户/企业范围控制
    """

    def __init__(self):
        self._policies: Dict[SourceType, SourcePolicy] = self._create_default_policies()

    def _create_default_policies(self) -> Dict[SourceType, SourcePolicy]:
        """创建默认策略"""
        return {
            SourceType.SESSION_HISTORY: SourcePolicy(
                source_type=SourceType.SESSION_HISTORY,
                allowed_profiles=["*"],
                max_risk_level=RiskLevel.HIGH
            ),
            SourceType.LONG_TERM_MEMORY: SourcePolicy(
                source_type=SourceType.LONG_TERM_MEMORY,
                allowed_profiles=["*"],
                required_capabilities=["memory.read"],
                max_risk_level=RiskLevel.MEDIUM
            ),
            SourceType.REPORT_MEMORY: SourcePolicy(
                source_type=SourceType.REPORT_MEMORY,
                allowed_profiles=["developer", "admin"],
                required_capabilities=["report.read"],
                max_risk_level=RiskLevel.MEDIUM
            ),
            SourceType.WORKFLOW_HISTORY: SourcePolicy(
                source_type=SourceType.WORKFLOW_HISTORY,
                allowed_profiles=["developer", "admin"],
                required_capabilities=["workflow.execute"],
                max_risk_level=RiskLevel.MEDIUM
            ),
            SourceType.SKILL_HISTORY: SourcePolicy(
                source_type=SourceType.SKILL_HISTORY,
                allowed_profiles=["*"],
                max_risk_level=RiskLevel.HIGH
            ),
            SourceType.USER_PREFERENCE: SourcePolicy(
                source_type=SourceType.USER_PREFERENCE,
                allowed_profiles=["*"],
                user_scope_only=True,
                max_risk_level=RiskLevel.LOW
            ),
            SourceType.COMPANY_KNOWLEDGE: SourcePolicy(
                source_type=SourceType.COMPANY_KNOWLEDGE,
                allowed_profiles=["developer", "admin"],
                company_scope=True,
                max_risk_level=RiskLevel.MEDIUM
            ),
            SourceType.EXTERNAL_KNOWLEDGE: SourcePolicy(
                source_type=SourceType.EXTERNAL_KNOWLEDGE,
                allowed_profiles=["admin"],
                required_capabilities=["external.access"],
                max_risk_level=RiskLevel.LOW
            ),
        }

    def route(
        self,
        profile: str,
        risk_level: RiskLevel = RiskLevel.LOW,
        capabilities: List[str] = None,
        user_scope: bool = True,
        company_scope: bool = True,
        safe_mode: bool = False
    ) -> RoutingResult:
        """
        路由决策

        Args:
            profile: 执行配置
            risk_level: 风险等级
            capabilities: 已授权的能力列表
            user_scope: 是否允许用户范围
            company_scope: 是否允许企业范围
            safe_mode: 安全模式（严格限制）

        Returns:
            RoutingResult
        """
        capabilities = capabilities or []
        allowed = []
        denied = []
        reasons = {}

        for source_type, policy in self._policies.items():
            reason = self._check_source(
                policy, profile, risk_level, capabilities,
                user_scope, company_scope, safe_mode
            )

            if reason:
                denied.append(source_type)
                reasons[source_type.value] = reason
            else:
                allowed.append(source_type)

        return RoutingResult(
            allowed_sources=allowed,
            denied_sources=denied,
            reasons=reasons,
            profile=profile,
            risk_level=risk_level
        )

    def _check_source(
        self,
        policy: SourcePolicy,
        profile: str,
        risk_level: RiskLevel,
        capabilities: List[str],
        user_scope: bool,
        company_scope: bool,
        safe_mode: bool
    ) -> Optional[str]:
        """检查来源是否允许，返回拒绝原因或 None"""
        if not policy.enabled:
            return "Source disabled"

        # 检查 profile
        if "*" not in policy.allowed_profiles and profile not in policy.allowed_profiles:
            return f"Profile '{profile}' not allowed. Required: {policy.allowed_profiles}"

        # 检查风险等级
        risk_order = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        if risk_order.index(risk_level) > risk_order.index(policy.max_risk_level):
            return f"Risk level '{risk_level.value}' exceeds max '{policy.max_risk_level.value}'"

        # 检查 capability
        for cap in policy.required_capabilities:
            if cap not in capabilities:
                return f"Missing required capability: {cap}"

        # 检查范围
        if policy.user_scope_only and not user_scope:
            return "User scope required but not allowed"

        if not policy.company_scope and company_scope:
            return "Company scope not allowed for this source"

        # 安全模式检查
        if safe_mode:
            safe_sources = [
                SourceType.SESSION_HISTORY,
                SourceType.USER_PREFERENCE
            ]
            if policy.source_type not in safe_sources:
                return "Blocked by safe mode"

        return None

    def get_policy(self, source_type: SourceType) -> Optional[SourcePolicy]:
        """获取来源策略"""
        return self._policies.get(source_type)

    def set_policy(self, policy: SourcePolicy):
        """设置来源策略"""
        self._policies[policy.source_type] = policy

    def get_all_policies(self) -> Dict[SourceType, SourcePolicy]:
        """获取所有策略"""
        return dict(self._policies)


# 全局单例
_source_policy_router = None


def get_source_policy_router() -> SourcePolicyRouter:
    """获取来源策略路由器单例"""
    global _source_policy_router
    if _source_policy_router is None:
        _source_policy_router = SourcePolicyRouter()
    return _source_policy_router
