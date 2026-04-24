"""
Risk Classifier - 风险分类器
对任务和能力进行风险评估
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
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
    level: RiskLevel
    score: float
    factors: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "score": self.score,
            "factors": self.factors
        }


class RiskClassifier:
    """
    风险分类器
    
    评估任务和能力组合的风险等级
    """
    
    # 能力风险权重
    CAPABILITY_RISK_WEIGHTS = {
        "skill.execute": 1.0,
        "skill.install": 2.5,
        "skill.remove": 3.0,
        "skill.upgrade": 2.5,
        "workflow.execute": 1.5,
        "workflow.create": 2.0,
        "workflow.modify": 2.0,
        "memory.read": 0.5,
        "memory.write": 1.0,
        "memory.delete": 2.5,
        "report.read": 0.5,
        "report.write": 1.0,
        "report.delete": 2.5,
        "external.access": 2.0,
        "external.api": 3.0,
        "external.network": 2.5,
        "system.config": 3.5,
        "system.restart": 4.0,
        "high_risk.write": 5.0,
        "high_risk.delete": 5.0,
        "high_risk.execute": 5.0,
    }
    
    # 风险阈值
    RISK_THRESHOLDS = {
        RiskLevel.LOW: 0.0,
        RiskLevel.MEDIUM: 2.0,
        RiskLevel.HIGH: 4.0,
        RiskLevel.CRITICAL: 6.0
    }
    
    def __init__(self):
        self._custom_weights: Dict[str, float] = {}
    
    def classify(
        self,
        task_meta: Dict[str, Any],
        capabilities: List[str]
    ) -> RiskLevel:
        """
        分类风险等级
        
        Args:
            task_meta: 任务元数据
            capabilities: 能力列表
            
        Returns:
            风险等级
        """
        assessment = self.assess(task_meta, capabilities)
        return assessment.level
    
    def assess(
        self,
        task_meta: Dict[str, Any],
        capabilities: List[str]
    ) -> RiskAssessment:
        """
        评估风险
        
        Args:
            task_meta: 任务元数据
            capabilities: 能力列表
            
        Returns:
            风险评估结果
        """
        factors = []
        total_score = 0.0
        
        # 1. 能力风险
        for cap in capabilities:
            weight = self._get_capability_weight(cap)
            total_score += weight
            if weight >= 3.0:
                factors.append(f"High risk capability: {cap}")
        
        # 2. 任务类型风险
        task_type = task_meta.get("type", "")
        if task_type in ["delete", "remove", "destructive"]:
            total_score += 2.0
            factors.append(f"Destructive task type: {task_type}")
        
        # 3. 外部访问风险
        if any("external" in cap for cap in capabilities):
            total_score += 1.0
            factors.append("External access required")
        
        # 4. 系统操作风险
        if any("system" in cap for cap in capabilities):
            total_score += 1.5
            factors.append("System operation required")
        
        # 5. 确定风险等级
        level = RiskLevel.LOW
        for risk_level, threshold in sorted(
            self.RISK_THRESHOLDS.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if total_score >= threshold:
                level = risk_level
                break
        
        return RiskAssessment(
            level=level,
            score=total_score,
            factors=factors
        )
    
    def set_capability_weight(self, capability: str, weight: float):
        """
        设置能力风险权重
        
        Args:
            capability: 能力名称
            weight: 风险权重
        """
        self._custom_weights[capability] = weight
    
    def get_capability_weight(self, capability: str) -> float:
        """
        获取能力风险权重
        
        Args:
            capability: 能力名称
            
        Returns:
            风险权重
        """
        return self._get_capability_weight(capability)
    
    def reload(self) -> Dict[str, Any]:
        """
        重新加载
        
        Returns:
            重载结果
        """
        return {
            "status": "reloaded",
            "capability_weights": len(self.CAPABILITY_RISK_WEIGHTS),
            "custom_weights": len(self._custom_weights)
        }
    
    def _get_capability_weight(self, capability: str) -> float:
        """
        获取能力风险权重（内部）
        
        Args:
            capability: 能力名称
            
        Returns:
            风险权重
        """
        # 优先使用自定义权重
        if capability in self._custom_weights:
            return self._custom_weights[capability]
        
        # 精确匹配
        if capability in self.CAPABILITY_RISK_WEIGHTS:
            return self.CAPABILITY_RISK_WEIGHTS[capability]
        
        # 通配符匹配
        for pattern, weight in self.CAPABILITY_RISK_WEIGHTS.items():
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                if capability.startswith(prefix):
                    return weight
        
        # 默认权重
        return 1.0


# 全局单例
_risk_classifier = None

def get_risk_classifier() -> RiskClassifier:
    """获取风险分类器单例"""
    global _risk_classifier
    if _risk_classifier is None:
        _risk_classifier = RiskClassifier()
    return _risk_classifier
