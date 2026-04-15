#!/usr/bin/env python3
"""
合规审查模块 - V1.0.0

审查操作是否符合规范和政策。
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ComplianceStatus(Enum):
    """合规状态"""
    COMPLIANT = "compliant"          # 合规
    NON_COMPLIANT = "non_compliant"  # 不合规
    PARTIAL = "partial"              # 部分合规
    UNKNOWN = "unknown"              # 无法确定


@dataclass
class ComplianceRule:
    """合规规则"""
    id: str
    name: str
    description: str
    check_fn: callable
    severity: str = "medium"


@dataclass
class ComplianceReview:
    """合规审查结果"""
    id: str
    operation: str
    status: ComplianceStatus
    rules_checked: int
    rules_passed: int
    violations: List[Dict]
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


class ComplianceReviewer:
    """合规审查器"""
    
    def __init__(self):
        self.rules: Dict[str, ComplianceRule] = {}
        self.reviews: List[ComplianceReview] = []
        self._register_default_rules()
    
    def _register_default_rules(self):
        """注册默认规则"""
        self.register_rule(ComplianceRule(
            id="data_privacy",
            name="数据隐私",
            description="检查是否遵守数据隐私规定",
            check_fn=self._check_data_privacy,
            severity="high"
        ))
        
        self.register_rule(ComplianceRule(
            id="access_control",
            name="访问控制",
            description="检查是否有适当的访问控制",
            check_fn=self._check_access_control,
            severity="high"
        ))
        
        self.register_rule(ComplianceRule(
            id="audit_trail",
            name="审计追踪",
            description="检查是否有审计记录",
            check_fn=self._check_audit_trail,
            severity="medium"
        ))
        
        self.register_rule(ComplianceRule(
            id="error_handling",
            name="错误处理",
            description="检查是否有适当的错误处理",
            check_fn=self._check_error_handling,
            severity="medium"
        ))
    
    def register_rule(self, rule: ComplianceRule):
        """注册规则"""
        self.rules[rule.id] = rule
    
    def review_operation(self,
                         operation: str,
                         context: Dict = None) -> ComplianceReview:
        """
        审查操作合规性
        
        Args:
            operation: 操作类型
            context: 上下文
        
        Returns:
            审查结果
        """
        violations = []
        rules_passed = 0
        
        for rule_id, rule in self.rules.items():
            try:
                passed, message = rule.check_fn(operation, context or {})
                
                if passed:
                    rules_passed += 1
                else:
                    violations.append({
                        "rule_id": rule_id,
                        "rule_name": rule.name,
                        "severity": rule.severity,
                        "message": message
                    })
            except Exception as e:
                violations.append({
                    "rule_id": rule_id,
                    "rule_name": rule.name,
                    "severity": "unknown",
                    "message": f"检查失败: {str(e)}"
                })
        
        # 确定合规状态
        if not violations:
            status = ComplianceStatus.COMPLIANT
        elif rules_passed == 0:
            status = ComplianceStatus.NON_COMPLIANT
        else:
            status = ComplianceStatus.PARTIAL
        
        # 生成建议
        recommendations = self._generate_recommendations(violations)
        
        review = ComplianceReview(
            id=f"comp_review_{len(self.reviews)}",
            operation=operation,
            status=status,
            rules_checked=len(self.rules),
            rules_passed=rules_passed,
            violations=violations,
            recommendations=recommendations
        )
        
        self.reviews.append(review)
        return review
    
    def _check_data_privacy(self, operation: str, context: Dict) -> tuple:
        """检查数据隐私"""
        sensitive_fields = ["password", "token", "secret", "key"]
        data = str(context.get("data", ""))
        
        for field in sensitive_fields:
            if field in data.lower():
                return False, f"检测到敏感字段: {field}"
        
        return True, "数据隐私检查通过"
    
    def _check_access_control(self, operation: str, context: Dict) -> tuple:
        """检查访问控制"""
        if operation in ["delete", "write", "execute"]:
            if not context.get("authorized"):
                return False, "操作未授权"
        
        return True, "访问控制检查通过"
    
    def _check_audit_trail(self, operation: str, context: Dict) -> tuple:
        """检查审计追踪"""
        if operation in ["create", "update", "delete"]:
            if not context.get("audit_enabled"):
                return False, "未启用审计"
        
        return True, "审计追踪检查通过"
    
    def _check_error_handling(self, operation: str, context: Dict) -> tuple:
        """检查错误处理"""
        if context.get("has_error") and not context.get("error_handled"):
            return False, "错误未处理"
        
        return True, "错误处理检查通过"
    
    def _generate_recommendations(self, violations: List[Dict]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        for v in violations:
            if v["rule_id"] == "data_privacy":
                recommendations.append("建议: 对敏感数据进行脱敏处理")
            elif v["rule_id"] == "access_control":
                recommendations.append("建议: 实施适当的访问控制机制")
            elif v["rule_id"] == "audit_trail":
                recommendations.append("建议: 启用操作审计")
            elif v["rule_id"] == "error_handling":
                recommendations.append("建议: 添加错误处理逻辑")
        
        return recommendations
    
    def get_compliance_statistics(self) -> Dict:
        """获取合规统计"""
        if not self.reviews:
            return {"total": 0}
        
        by_status = {}
        for review in self.reviews:
            by_status[review.status.value] = by_status.get(review.status.value, 0) + 1
        
        return {
            "total": len(self.reviews),
            "by_status": by_status,
            "compliance_rate": by_status.get("compliant", 0) / len(self.reviews)
        }


# 全局合规审查器
_compliance_reviewer: Optional[ComplianceReviewer] = None


def get_compliance_reviewer() -> ComplianceReviewer:
    """获取全局合规审查器"""
    global _compliance_reviewer
    if _compliance_reviewer is None:
        _compliance_reviewer = ComplianceReviewer()
    return _compliance_reviewer
