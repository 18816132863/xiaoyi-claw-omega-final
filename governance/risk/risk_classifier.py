"""Risk Classifier - 风险分类器"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
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
    risk_level: RiskLevel
    risk_score: float
    factors: List[str]
    requires_review: bool
    mitigations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class RiskClassifier:
    """
    风险分类器
    
    职责：
    - 评估任务风险等级
    - 识别风险因素
    - 推荐缓解措施
    """
    
    def __init__(self):
        # 高风险关键词
        self.high_risk_keywords = [
            "delete", "删除", "remove", "移除",
            "drop", "truncate", "清空",
            "sudo", "root", "admin",
            "execute", "执行", "run",
            "network", "网络", "upload", "上传",
            "database", "数据库", "production", "生产"
        ]
        
        # 关键风险操作
        self.critical_operations = [
            "file_delete", "database_drop", "system_config",
            "user_delete", "permission_change"
        ]
        
        # 风险因素权重
        self.factor_weights = {
            "high_risk_keyword": 0.3,
            "critical_operation": 0.5,
            "unapproved_action": 0.4,
            "external_network": 0.2,
            "data_modification": 0.2
        }
    
    def classify(
        self,
        task_meta: Dict[str, Any],
        profile: str = "default"
    ) -> RiskAssessment:
        """
        分类风险
        
        Args:
            task_meta: 任务元数据
            profile: 执行配置
        
        Returns:
            RiskAssessment
        """
        factors = []
        risk_score = 0.0
        
        intent = task_meta.get("intent", "").lower()
        action = task_meta.get("action", "").lower()
        approved = task_meta.get("approved", False)
        
        # 检查高风险关键词
        for keyword in self.high_risk_keywords:
            if keyword in intent or keyword in action:
                factors.append(f"high_risk_keyword: {keyword}")
                risk_score += self.factor_weights["high_risk_keyword"]
                break
        
        # 检查关键操作
        for op in self.critical_operations:
            if op in action:
                factors.append(f"critical_operation: {op}")
                risk_score += self.factor_weights["critical_operation"]
                break
        
        # 检查未审批的高风险操作
        if risk_score > 0.3 and not approved:
            factors.append("unapproved_action")
            risk_score += self.factor_weights["unapproved_action"]
        
        # 检查网络操作
        if "network" in intent or "http" in action:
            factors.append("external_network")
            risk_score += self.factor_weights["external_network"]
        
        # 检查数据修改
        if any(kw in intent for kw in ["write", "modify", "update", "修改", "更新"]):
            factors.append("data_modification")
            risk_score += self.factor_weights["data_modification"]
        
        # 确定风险等级
        risk_level = self._determine_level(risk_score)
        
        # 是否需要审批
        requires_review = risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        
        # 缓解措施
        mitigations = self._get_mitigations(risk_level, factors)
        
        return RiskAssessment(
            risk_level=risk_level,
            risk_score=min(risk_score, 1.0),
            factors=factors,
            requires_review=requires_review,
            mitigations=mitigations,
            metadata={
                "profile": profile,
                "approved": approved
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
            mitigations.append("Run in isolated environment")
            mitigations.append("Create backup before execution")
        elif level == RiskLevel.HIGH:
            mitigations.append("Require user confirmation")
            mitigations.append("Log all operations")
        elif level == RiskLevel.MEDIUM:
            mitigations.append("Review operation details")
        
        if "external_network" in factors:
            mitigations.append("Validate network targets")
        
        if "data_modification" in factors:
            mitigations.append("Create data backup")
        
        return mitigations
    
    def add_high_risk_keyword(self, keyword: str):
        """添加高风险关键词"""
        if keyword not in self.high_risk_keywords:
            self.high_risk_keywords.append(keyword)
    
    def add_critical_operation(self, operation: str):
        """添加关键操作"""
        if operation not in self.critical_operations:
            self.critical_operations.append(operation)
