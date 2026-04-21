#!/usr/bin/env python3
"""结果守卫 - V1.0.0

最终总闸，统一判定任务是否可以 success。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class GuardReason(Enum):
    """拦截原因"""
    NO_REAL_EXECUTION = "no_real_execution"
    NO_EVIDENCE = "no_evidence"
    VERIFICATION_FAILED = "verification_failed"
    EMPTY_USER_RESPONSE = "empty_user_response"
    EMPTY_COMPLETED_ITEMS = "empty_completed_items"
    ALL_PASSED = "all_passed"


@dataclass
class GuardResult:
    """守卫结果"""
    passed: bool
    reason: GuardReason
    message: str
    details: Dict[str, Any]


class ResultGuard:
    """结果守卫"""
    
    def guard(
        self,
        has_real_execution: bool,
        verify_status: str,
        evidence: Dict[str, Any],
        user_response: str,
        completed_items: List[str]
    ) -> GuardResult:
        """
        统一判定最终是否可以 success
        
        只有下面全部满足，才允许最终 success：
        1. has_real_execution = True
        2. verify_result.status == success
        3. evidence_formatter.has_evidence(evidence) == True
        4. user_response 非空
        5. completed_items 非空
        """
        details = {
            "has_real_execution": has_real_execution,
            "verify_status": verify_status,
            "has_evidence": self._has_evidence(evidence),
            "user_response_empty": not bool(user_response and user_response.strip()),
            "completed_items_empty": not bool(completed_items)
        }
        
        # 1. 至少一个真实 skill 执行成功
        if not has_real_execution:
            return GuardResult(
                passed=False,
                reason=GuardReason.NO_REAL_EXECUTION,
                message="没有真实执行的技能",
                details=details
            )
        
        # 2. verify 成功
        if verify_status != "success":
            return GuardResult(
                passed=False,
                reason=GuardReason.VERIFICATION_FAILED,
                message="验证失败",
                details=details
            )
        
        # 3. evidence 不为空
        if not self._has_evidence(evidence):
            return GuardResult(
                passed=False,
                reason=GuardReason.NO_EVIDENCE,
                message="没有有效证据",
                details=details
            )
        
        # 4. user_response 不为空
        if not user_response or not user_response.strip():
            return GuardResult(
                passed=False,
                reason=GuardReason.EMPTY_USER_RESPONSE,
                message="用户响应为空",
                details=details
            )
        
        # 5. completed_items 不为空
        if not completed_items:
            return GuardResult(
                passed=False,
                reason=GuardReason.EMPTY_COMPLETED_ITEMS,
                message="完成项为空",
                details=details
            )
        
        return GuardResult(
            passed=True,
            reason=GuardReason.ALL_PASSED,
            message="所有检查通过",
            details=details
        )
    
    def _has_evidence(self, evidence: Dict[str, Any]) -> bool:
        """检查是否有有效证据"""
        if not evidence:
            return False
        
        return any([
            evidence.get("files"),
            evidence.get("db_records"),
            evidence.get("messages"),
            evidence.get("tool_calls"),
            evidence.get("extra")
        ])


# 全局实例
_guard: Optional[ResultGuard] = None

def get_guard() -> ResultGuard:
    """获取全局守卫"""
    global _guard
    if _guard is None:
        _guard = ResultGuard()
    return _guard

def guard_result(
    has_real_execution: bool,
    verify_status: str,
    evidence: Dict[str, Any],
    user_response: str,
    completed_items: List[str]
) -> GuardResult:
    """守卫结果（便捷函数）"""
    return get_guard().guard(
        has_real_execution,
        verify_status,
        evidence,
        user_response,
        completed_items
    )
