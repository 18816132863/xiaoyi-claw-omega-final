"""Skill Risk Policy - 技能风险策略"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from skills.registry.skill_registry import SkillManifest, SkillCategory, SkillStatus


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
    risk_score: float
    factors: List[str]
    requires_approval: bool
    mitigations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class SkillRiskPolicy:
    """
    技能风险策略
    
    职责：
    - 评估技能风险等级
    - 识别风险因素
    - 推荐缓解措施
    """
    
    def __init__(self):
        # 高风险分类
        self.high_risk_categories = [
            SkillCategory.FINANCE,
            SkillCategory.CODE
        ]
        
        # 高风险执行器
        self.high_risk_executors = ["python", "subprocess"]
        
        # 高风险权限
        self.high_risk_permissions = ["admin", "execute", "network"]
        
        # 风险因素权重
        self.factor_weights = {
            "high_risk_category": 0.3,
            "high_risk_executor": 0.3,
            "high_risk_permission": 0.2,
            "deprecated_status": 0.2,
            "experimental_status": 0.1
        }
    
    def assess(
        self,
        manifest: SkillManifest,
        context: Dict[str, Any] = None
    ) -> RiskAssessment:
        """
        评估技能风险
        
        Args:
            manifest: 技能清单
            context: 执行上下文
        
        Returns:
            RiskAssessment
        """
        factors = []
        risk_score = 0.0
        
        # 检查分类
        if manifest.category in self.high_risk_categories:
            factors.append(f"high_risk_category: {manifest.category.value}")
            risk_score += self.factor_weights["high_risk_category"]
        
        # 检查执行器
        if manifest.executor_type in self.high_risk_executors:
            factors.append(f"high_risk_executor: {manifest.executor_type}")
            risk_score += self.factor_weights["high_risk_executor"]
        
        # 检查权限
        for perm in manifest.required_permissions:
            if perm in self.high_risk_permissions:
                factors.append(f"high_risk_permission: {perm}")
                risk_score += self.factor_weights["high_risk_permission"]
                break
        
        # 检查状态
        if manifest.status == SkillStatus.DEPRECATED:
            factors.append("deprecated_status")
            risk_score += self.factor_weights["deprecated_status"]
        elif manifest.status == SkillStatus.EXPERIMENTAL:
            factors.append("experimental_status")
            risk_score += self.factor_weights["experimental_status"]
        
        # 确定风险等级
        risk_level = self._determine_level(risk_score)
        
        # 是否需要审批
        requires_approval = risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        # 缓解措施
        mitigations = self._get_mitigations(risk_level, factors)
        
        return RiskAssessment(
            skill_id=manifest.skill_id,
            risk_level=risk_level,
            risk_score=min(risk_score, 1.0),
            factors=factors,
            requires_approval=requires_approval,
            mitigations=mitigations,
            metadata={
                "category": manifest.category.value,
                "executor_type": manifest.executor_type,
                "status": manifest.status.value
            }
        )
    
    def _determine_level(self, score: float) -> RiskLevel:
        """确定风险等级"""
        if score >= 0.7:
            return RiskLevel.CRITICAL
        elif score >= 0.5:
            return RiskLevel.HIGH
        elif score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _get_mitigations(
        self,
        level: RiskLevel,
        factors: List[str]
    ) -> List[str]:
        """获取缓解措施"""
        mitigations = []
        
        if level == RiskLevel.CRITICAL:
            mitigations.append("Require explicit user approval")
            mitigations.append("Run in sandboxed environment")
        elif level == RiskLevel.HIGH:
            mitigations.append("Require user confirmation")
            mitigations.append("Log all operations")
        elif level == RiskLevel.MEDIUM:
            mitigations.append("Review skill details")
        
        if "high_risk_executor" in str(factors):
            mitigations.append("Validate execution environment")
        
        if "deprecated_status" in factors:
            mitigations.append("Consider using alternative skill")
        
        return mitigations
    
    def is_allowed(
        self,
        manifest: SkillManifest,
        profile: str,
        approved: bool = False
    ) -> tuple[bool, str]:
        """
        检查是否允许执行
        
        Args:
            manifest: 技能清单
            profile: 执行配置
            approved: 是否已审批
        
        Returns:
            Tuple of (allowed, reason)
        """
        assessment = self.assess(manifest)
        
        # 禁用的技能不允许
        if manifest.status == SkillStatus.DISABLED:
            return False, f"Skill {manifest.skill_id} is disabled"
        
        # 关键风险需要审批
        if assessment.risk_level == RiskLevel.CRITICAL and not approved:
            return False, f"Skill {manifest.skill_id} requires approval (critical risk)"
        
        # 高风险需要审批或高级配置
        if assessment.risk_level == RiskLevel.HIGH:
            if not approved and profile not in ["admin", "developer"]:
                return False, f"Skill {manifest.skill_id} requires approval or elevated profile"
        
        return True, "Allowed"
    
    def add_high_risk_category(self, category: SkillCategory):
        """添加高风险分类"""
        if category not in self.high_risk_categories:
            self.high_risk_categories.append(category)
    
    def add_high_risk_executor(self, executor_type: str):
        """添加高风险执行器"""
        if executor_type not in self.high_risk_executors:
            self.high_risk_executors.append(executor_type)
