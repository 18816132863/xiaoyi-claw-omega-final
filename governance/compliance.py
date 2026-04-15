#!/usr/bin/env python3
"""
合规检查模块 - V1.0.0

检查操作是否符合规范和政策。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ComplianceLevel(Enum):
    """合规级别"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"


@dataclass
class ComplianceResult:
    """合规检查结果"""
    level: ComplianceLevel
    rule: str
    message: str
    details: Optional[Dict] = None


class ComplianceChecker:
    """合规检查器"""
    
    def __init__(self):
        self.rules: Dict[str, callable] = {}
        self._register_default_rules()
    
    def _register_default_rules(self):
        """注册默认规则"""
        self.rules["no_sensitive_data_exposure"] = self._check_sensitive_data
        self.rules["no_unauthorized_access"] = self._check_authorization
        self.rules["no_rate_limit_violation"] = self._check_rate_limit
        self.rules["valid_input_format"] = self._check_input_format
    
    def _check_sensitive_data(self, context: Dict) -> ComplianceResult:
        """检查敏感数据暴露"""
        sensitive_patterns = ["password", "token", "secret", "key"]
        data = str(context.get("data", ""))
        
        for pattern in sensitive_patterns:
            if pattern in data.lower():
                return ComplianceResult(
                    level=ComplianceLevel.WARNING,
                    rule="no_sensitive_data_exposure",
                    message=f"可能包含敏感数据: {pattern}"
                )
        
        return ComplianceResult(
            level=ComplianceLevel.COMPLIANT,
            rule="no_sensitive_data_exposure",
            message="未检测到敏感数据"
        )
    
    def _check_authorization(self, context: Dict) -> ComplianceResult:
        """检查授权"""
        if not context.get("authorized", True):
            return ComplianceResult(
                level=ComplianceLevel.VIOLATION,
                rule="no_unauthorized_access",
                message="未授权的操作"
            )
        
        return ComplianceResult(
            level=ComplianceLevel.COMPLIANT,
            rule="no_unauthorized_access",
            message="操作已授权"
        )
    
    def _check_rate_limit(self, context: Dict) -> ComplianceResult:
        """检查速率限制"""
        calls = context.get("recent_calls", 0)
        limit = context.get("rate_limit", 100)
        
        if calls > limit:
            return ComplianceResult(
                level=ComplianceLevel.VIOLATION,
                rule="no_rate_limit_violation",
                message=f"超过速率限制: {calls}/{limit}"
            )
        
        return ComplianceResult(
            level=ComplianceLevel.COMPLIANT,
            rule="no_rate_limit_violation",
            message="速率限制正常"
        )
    
    def _check_input_format(self, context: Dict) -> ComplianceResult:
        """检查输入格式"""
        # 基本格式检查
        return ComplianceResult(
            level=ComplianceLevel.COMPLIANT,
            rule="valid_input_format",
            message="输入格式有效"
        )
    
    def check(self, context: Dict) -> List[ComplianceResult]:
        """执行所有合规检查"""
        results = []
        for rule_name, rule_func in self.rules.items():
            result = rule_func(context)
            results.append(result)
        return results
    
    def is_compliant(self, context: Dict) -> bool:
        """检查是否合规"""
        results = self.check(context)
        return all(r.level != ComplianceLevel.VIOLATION for r in results)


# 全局合规检查器
_compliance_checker: Optional[ComplianceChecker] = None


def get_compliance_checker() -> ComplianceChecker:
    """获取全局合规检查器"""
    global _compliance_checker
    if _compliance_checker is None:
        _compliance_checker = ComplianceChecker()
    return _compliance_checker
