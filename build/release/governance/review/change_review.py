#!/usr/bin/env python3
"""
变更审查模块 - V1.0.0

审查系统变更的安全性和合规性。
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import re


class ReviewResult(Enum):
    """审查结果"""
    APPROVED = "approved"          # 批准
    REJECTED = "rejected"          # 拒绝
    NEEDS_REVIEW = "needs_review"  # 需要人工审查
    CONDITIONAL = "conditional"    # 有条件批准


class RiskLevel(Enum):
    """风险级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ReviewCheck:
    """审查检查项"""
    name: str
    description: str
    passed: bool
    message: str
    severity: RiskLevel = RiskLevel.MEDIUM


@dataclass
class ChangeReview:
    """变更审查结果"""
    id: str
    change_type: str
    target: str
    result: ReviewResult
    risk_level: RiskLevel
    checks: List[ReviewCheck]
    recommendations: List[str]
    reviewer: str = "system"
    timestamp: datetime = field(default_factory=datetime.now)


class ChangeReviewer:
    """变更审查器"""
    
    def __init__(self):
        self.protected_files = self._load_protected_files()
        self.sensitive_patterns = self._load_sensitive_patterns()
        self.review_history: List[ChangeReview] = []
    
    def _load_protected_files(self) -> List[str]:
        """加载受保护文件列表"""
        return [
            "AGENTS.md",
            "MEMORY.md",
            "TOOLS.md",
            "SOUL.md",
            "USER.md",
            "IDENTITY.md",
            "core/ARCHITECTURE.md",
            "infrastructure/inventory/skill_registry.json",
            "core/RULE_REGISTRY.json",
        ]
    
    def _load_sensitive_patterns(self) -> List[str]:
        """加载敏感模式"""
        return [
            r"password",
            r"secret",
            r"token",
            r"api_key",
            r"private_key",
            r"\.env",
            r"\.pem",
            r"\.key",
        ]
    
    def review_change(self,
                      change_type: str,
                      target: str,
                      content: Any = None,
                      context: Dict = None) -> ChangeReview:
        """
        审查变更
        
        Args:
            change_type: 变更类型 (create, update, delete)
            target: 目标对象
            content: 变更内容
            context: 上下文
        
        Returns:
            审查结果
        """
        checks = []
        
        # 1. 检查是否为受保护文件
        checks.append(self._check_protected_file(target))
        
        # 2. 检查是否包含敏感信息
        if content:
            checks.append(self._check_sensitive_content(str(content)))
        
        # 3. 检查变更类型风险
        checks.append(self._check_change_type_risk(change_type, target))
        
        # 4. 检查文件路径合法性
        checks.append(self._check_path_validity(target))
        
        # 5. 检查依赖影响
        if context:
            checks.append(self._check_dependency_impact(target, context))
        
        # 计算风险级别
        risk_level = self._calculate_risk_level(checks)
        
        # 确定审查结果
        result = self._determine_result(checks, risk_level)
        
        # 生成建议
        recommendations = self._generate_recommendations(checks, result)
        
        review = ChangeReview(
            id=f"review_{len(self.review_history)}",
            change_type=change_type,
            target=target,
            result=result,
            risk_level=risk_level,
            checks=checks,
            recommendations=recommendations
        )
        
        self.review_history.append(review)
        return review
    
    def _check_protected_file(self, target: str) -> ReviewCheck:
        """检查是否为受保护文件"""
        for protected in self.protected_files:
            if protected in target:
                return ReviewCheck(
                    name="protected_file",
                    description="检查是否为受保护文件",
                    passed=False,
                    message=f"目标是受保护文件: {protected}",
                    severity=RiskLevel.HIGH
                )
        
        return ReviewCheck(
            name="protected_file",
            description="检查是否为受保护文件",
            passed=True,
            message="目标不是受保护文件"
        )
    
    def _check_sensitive_content(self, content: str) -> ReviewCheck:
        """检查是否包含敏感信息"""
        for pattern in self.sensitive_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return ReviewCheck(
                    name="sensitive_content",
                    description="检查是否包含敏感信息",
                    passed=False,
                    message=f"检测到敏感模式: {pattern}",
                    severity=RiskLevel.CRITICAL
                )
        
        return ReviewCheck(
            name="sensitive_content",
            description="检查是否包含敏感信息",
            passed=True,
            message="未检测到敏感信息"
        )
    
    def _check_change_type_risk(self, change_type: str, target: str) -> ReviewCheck:
        """检查变更类型风险"""
        risk_map = {
            "delete": RiskLevel.HIGH,
            "create": RiskLevel.MEDIUM,
            "update": RiskLevel.LOW,
        }
        
        risk = risk_map.get(change_type, RiskLevel.MEDIUM)
        
        # 特殊文件提高风险
        if target.endswith(".json") or target.endswith(".yaml"):
            risk = RiskLevel(risk.value + 1) if risk.value < 3 else risk
        
        return ReviewCheck(
            name="change_type_risk",
            description="检查变更类型风险",
            passed=risk != RiskLevel.CRITICAL,
            message=f"变更类型: {change_type}, 风险级别: {risk.value}",
            severity=risk
        )
    
    def _check_path_validity(self, target: str) -> ReviewCheck:
        """检查路径合法性"""
        # 检查路径遍历攻击
        if ".." in target or target.startswith("/"):
            return ReviewCheck(
                name="path_validity",
                description="检查路径合法性",
                passed=False,
                message="检测到非法路径",
                severity=RiskLevel.HIGH
            )
        
        return ReviewCheck(
            name="path_validity",
            description="检查路径合法性",
            passed=True,
            message="路径合法"
        )
    
    def _check_dependency_impact(self, target: str, context: Dict) -> ReviewCheck:
        """检查依赖影响"""
        dependents = context.get("dependents", [])
        
        if dependents:
            return ReviewCheck(
                name="dependency_impact",
                description="检查依赖影响",
                passed=False,
                message=f"有 {len(dependents)} 个依赖项受影响",
                severity=RiskLevel.MEDIUM
            )
        
        return ReviewCheck(
            name="dependency_impact",
            description="检查依赖影响",
            passed=True,
            message="无依赖影响"
        )
    
    def _calculate_risk_level(self, checks: List[ReviewCheck]) -> RiskLevel:
        """计算风险级别"""
        max_risk = RiskLevel.LOW
        
        for check in checks:
            if not check.passed:
                if check.severity.value > max_risk.value:
                    max_risk = check.severity
        
        return max_risk
    
    def _determine_result(self, checks: List[ReviewCheck], risk_level: RiskLevel) -> ReviewResult:
        """确定审查结果"""
        # 任何 CRITICAL 级别失败 -> 拒绝
        if any(not c.passed and c.severity == RiskLevel.CRITICAL for c in checks):
            return ReviewResult.REJECTED
        
        # HIGH 级别失败 -> 需要人工审查
        if any(not c.passed and c.severity == RiskLevel.HIGH for c in checks):
            return ReviewResult.NEEDS_REVIEW
        
        # MEDIUM 级别失败 -> 有条件批准
        if any(not c.passed and c.severity == RiskLevel.MEDIUM for c in checks):
            return ReviewResult.CONDITIONAL
        
        return ReviewResult.APPROVED
    
    def _generate_recommendations(self, checks: List[ReviewCheck], result: ReviewResult) -> List[str]:
        """生成建议"""
        recommendations = []
        
        for check in checks:
            if not check.passed:
                if check.name == "protected_file":
                    recommendations.append("建议: 确认是否需要修改受保护文件")
                elif check.name == "sensitive_content":
                    recommendations.append("建议: 移除敏感信息或使用环境变量")
                elif check.name == "dependency_impact":
                    recommendations.append("建议: 评估对依赖项的影响")
        
        if result == ReviewResult.NEEDS_REVIEW:
            recommendations.append("建议: 提交人工审查")
        elif result == ReviewResult.CONDITIONAL:
            recommendations.append("建议: 在满足条件后执行")
        
        return recommendations
    
    def get_review_statistics(self) -> Dict:
        """获取审查统计"""
        if not self.review_history:
            return {"total": 0}
        
        by_result = {}
        by_risk = {}
        
        for review in self.review_history:
            by_result[review.result.value] = by_result.get(review.result.value, 0) + 1
            by_risk[review.risk_level.value] = by_risk.get(review.risk_level.value, 0) + 1
        
        return {
            "total": len(self.review_history),
            "by_result": by_result,
            "by_risk": by_risk,
            "approval_rate": by_result.get("approved", 0) / len(self.review_history)
        }


# 全局变更审查器
_change_reviewer: Optional[ChangeReviewer] = None


def get_change_reviewer() -> ChangeReviewer:
    """获取全局变更审查器"""
    global _change_reviewer
    if _change_reviewer is None:
        _change_reviewer = ChangeReviewer()
    return _change_reviewer
