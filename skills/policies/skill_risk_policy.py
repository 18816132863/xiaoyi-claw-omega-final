"""Skill Risk Policy - 技能风险策略"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskAssessment:
    """风险评估结果"""
    skill_id: str
    risk_level: RiskLevel
    factors: List[str]
    requires_approval: bool
    mitigations: List[str]


class SkillRiskPolicy:
    """技能风险策略"""
    
    HIGH_RISK_CATEGORIES = ["finance", "code"]
    HIGH_RISK_PERMISSIONS = ["admin", "execute"]
    
    def assess(self, manifest, context: Dict = None) -> RiskAssessment:
        """评估技能风险"""
        factors = []
        risk_score = 0
        
        # 检查分类
        category = manifest.category.value if hasattr(manifest, 'category') else "other"
        if category in self.HIGH_RISK_CATEGORIES:
            factors.append(f"High-risk category: {category}")
            risk_score += 2
        
        # 检查权限
        permissions = manifest.required_permissions if hasattr(manifest, 'required_permissions') else []
        for perm in permissions:
            if perm in self.HIGH_RISK_PERMISSIONS:
                factors.append(f"High-risk permission: {perm}")
                risk_score += 2
        
        # 检查执行器类型
        executor_type = manifest.executor_type if hasattr(manifest, 'executor_type') else "skill_md"
        if executor_type in ["python", "subprocess"]:
            factors.append(f"Executable executor type: {executor_type}")
            risk_score += 1
        
        # 确定风险等级
        if risk_score >= 4:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 3:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 1:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # 是否需要审批
        requires_approval = risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        # 缓解措施
        mitigations = []
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            mitigations.append("Require explicit user approval")
        if executor_type in ["python", "subprocess"]:
            mitigations.append("Run in sandboxed environment")
        
        return RiskAssessment(
            skill_id=manifest.skill_id,
            risk_level=risk_level,
            factors=factors,
            requires_approval=requires_approval,
            mitigations=mitigations
        )
    
    def is_allowed(self, manifest, context: Dict = None) -> bool:
        """检查是否允许执行"""
        assessment = self.assess(manifest, context)
        
        # 关键风险需要审批
        if assessment.risk_level == RiskLevel.CRITICAL:
            if context and context.get("approved"):
                return True
            return False
        
        return True
