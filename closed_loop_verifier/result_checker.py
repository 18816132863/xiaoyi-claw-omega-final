"""结果检查器"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class VerificationResult:
    """验证结果"""
    verified: bool
    status: str  # success, failed, uncertain
    message: str
    evidence: Dict[str, Any]


class ResultChecker:
    """结果检查器"""
    
    def verify_platform_result(self, result: Dict[str, Any]) -> VerificationResult:
        """验证平台返回"""
        success = result.get("success", False)
        status = result.get("status", "unknown")
        
        if success and status == "completed":
            return VerificationResult(
                verified=True,
                status="success",
                message="平台返回成功",
                evidence=result,
            )
        elif status == "result_uncertain":
            return VerificationResult(
                verified=False,
                status="uncertain",
                message="结果不确定，需要人工确认",
                evidence=result,
            )
        else:
            return VerificationResult(
                verified=False,
                status="failed",
                message=f"平台返回失败: {result.get('error', 'unknown')}",
                evidence=result,
            )
    
    def verify_screen_state(self, expected: str, actual: str) -> VerificationResult:
        """验证屏幕状态"""
        if expected == actual:
            return VerificationResult(
                verified=True,
                status="success",
                message="屏幕状态符合预期",
                evidence={"expected": expected, "actual": actual},
            )
        else:
            return VerificationResult(
                verified=False,
                status="failed",
                message=f"屏幕状态不符合预期: 期望 {expected}, 实际 {actual}",
                evidence={"expected": expected, "actual": actual},
            )
    
    def verify_skill_output(self, output: Dict[str, Any], schema: Dict[str, Any]) -> VerificationResult:
        """验证技能输出"""
        # 检查必需字段
        required = schema.get("required", [])
        missing = [f for f in required if f not in output]
        
        if missing:
            return VerificationResult(
                verified=False,
                status="failed",
                message=f"缺少必需字段: {missing}",
                evidence={"missing": missing},
            )
        
        return VerificationResult(
            verified=True,
            status="success",
            message="输出符合预期",
            evidence=output,
        )
