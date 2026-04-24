"""High Risk Guard - 高风险守卫"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

from .risk_classifier import RiskLevel, RiskAssessment


class GuardAction(Enum):
    """守卫动作"""
    ALLOW = "allow"
    BLOCK = "block"
    DEGRADE = "degrade"
    REVIEW = "review"


@dataclass
class GuardDecision:
    """守卫决策"""
    action: GuardAction
    reason: str
    degraded_capabilities: List[str] = None
    review_required: bool = False
    fallback_profile: str = None


class HighRiskGuard:
    """
    高风险守卫
    
    职责：
    - 对高风险任务进行拦截
    - 支持降级处理
    - 支持审批流程
    """
    
    def __init__(self):
        # 风险等级对应的默认动作
        self.level_actions = {
            RiskLevel.LOW: GuardAction.ALLOW,
            RiskLevel.MEDIUM: GuardAction.ALLOW,
            RiskLevel.HIGH: GuardAction.REVIEW,
            RiskLevel.CRITICAL: GuardAction.BLOCK
        }
        
        # 高风险能力列表
        self.high_risk_capabilities = [
            "file_delete",
            "database_write",
            "system_config",
            "network_external",
            "permission_change",
            "user_management"
        ]
        
        # 降级映射
        self.degrade_map = {
            "admin": "developer",
            "developer": "operator",
            "operator": "auditor"
        }
    
    def guard(
        self,
        assessment: RiskAssessment,
        profile: str,
        requested_capabilities: List[str] = None,
        approved: bool = False
    ) -> GuardDecision:
        """
        执行守卫
        
        Args:
            assessment: 风险评估
            profile: 执行配置
            requested_capabilities: 请求的能力
            approved: 是否已审批
        
        Returns:
            GuardDecision
        """
        requested_capabilities = requested_capabilities or []
        
        # 获取默认动作
        default_action = self.level_actions.get(assessment.risk_level, GuardAction.ALLOW)
        
        # 检查高风险能力
        high_risk_requested = [
            cap for cap in requested_capabilities
            if cap in self.high_risk_capabilities
        ]
        
        # 关键风险：必须审批
        if assessment.risk_level == RiskLevel.CRITICAL:
            if not approved:
                return GuardDecision(
                    action=GuardAction.BLOCK,
                    reason=f"Critical risk requires approval. Factors: {assessment.factors}",
                    review_required=True
                )
            return GuardDecision(
                action=GuardAction.ALLOW,
                reason="Critical risk approved"
            )
        
        # 高风险：需要审批或降级
        if assessment.risk_level == RiskLevel.HIGH:
            if approved:
                return GuardDecision(
                    action=GuardAction.ALLOW,
                    reason="High risk approved"
                )
            
            if high_risk_requested:
                # 降级处理
                degraded_profile = self.degrade_map.get(profile, "restricted")
                return GuardDecision(
                    action=GuardAction.DEGRADE,
                    reason=f"High risk with sensitive capabilities. Degrading from {profile} to {degraded_profile}",
                    degraded_capabilities=high_risk_requested,
                    fallback_profile=degraded_profile
                )
            
            return GuardDecision(
                action=GuardAction.REVIEW,
                reason=f"High risk requires review. Factors: {assessment.factors}",
                review_required=True
            )
        
        # 中等风险：检查能力
        if assessment.risk_level == RiskLevel.MEDIUM:
            if high_risk_requested and not approved:
                return GuardDecision(
                    action=GuardAction.REVIEW,
                    reason=f"Medium risk with high-risk capabilities: {high_risk_requested}",
                    review_required=True
                )
            return GuardDecision(
                action=GuardAction.ALLOW,
                reason="Medium risk allowed"
            )
        
        # 低风险：直接允许
        return GuardDecision(
            action=GuardAction.ALLOW,
            reason="Low risk allowed"
        )
    
    def set_level_action(self, level: RiskLevel, action: GuardAction):
        """设置风险等级动作"""
        self.level_actions[level] = action
    
    def add_high_risk_capability(self, capability: str):
        """添加高风险能力"""
        if capability not in self.high_risk_capabilities:
            self.high_risk_capabilities.append(capability)
    
    def is_high_risk_capability(self, capability: str) -> bool:
        """检查是否高风险能力"""
        return capability in self.high_risk_capabilities
