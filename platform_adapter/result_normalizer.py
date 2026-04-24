"""
平台结果归一化
将不同平台的原始结果统一映射为标准状态
"""

from dataclasses import dataclass
from typing import Any, Optional


class NormalizedStatus:
    """归一化状态"""
    COMPLETED = "completed"
    QUEUED_FOR_DELIVERY = "queued_for_delivery"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RESULT_UNCERTAIN = "result_uncertain"
    AUTH_REQUIRED = "auth_required"
    FALLBACK_USED = "fallback_used"


@dataclass
class NormalizedResult:
    """归一化结果"""
    status: str
    error_code: Optional[str] = None
    should_retry: bool = False
    result_uncertain: bool = False


def normalize_result(
    raw_result: Any,
    capability: str,
    op_name: str,
) -> NormalizedResult:
    """
    归一化平台原始结果
    
    Args:
        raw_result: 原始结果
        capability: 能力名称
        op_name: 操作名称
    
    Returns:
        NormalizedResult: 归一化结果
    """
    from .error_codes import (
        PLATFORM_TIMEOUT,
        PLATFORM_RESULT_UNCERTAIN,
        PLATFORM_AUTH_REQUIRED,
        PLATFORM_PERMISSION_DENIED,
        PLATFORM_NOT_CONNECTED,
        PLATFORM_NOT_AVAILABLE,
        PLATFORM_BAD_PARAMS,
        PLATFORM_EXECUTION_FAILED,
    )
    
    # 处理 None
    if raw_result is None:
        return NormalizedResult(
            status=NormalizedStatus.FAILED,
            error_code=PLATFORM_NOT_AVAILABLE,
            should_retry=True,
            result_uncertain=False,
        )
    
    # 处理字典结果
    if isinstance(raw_result, dict):
        # 检查错误状态
        if raw_result.get("status") == "error":
            error_msg = raw_result.get("error", "")
            
            # 超时
            if "超时" in error_msg or "timeout" in error_msg.lower():
                return NormalizedResult(
                    status=NormalizedStatus.TIMEOUT,
                    error_code=PLATFORM_TIMEOUT,
                    should_retry=False,
                    result_uncertain=True,
                )
            
            # 授权失败
            if "authCode" in error_msg or "授权" in error_msg or "invalid" in error_msg.lower():
                return NormalizedResult(
                    status=NormalizedStatus.AUTH_REQUIRED,
                    error_code=PLATFORM_AUTH_REQUIRED,
                    should_retry=False,
                    result_uncertain=False,
                )
            
            # 其他错误
            return NormalizedResult(
                status=NormalizedStatus.FAILED,
                error_code=PLATFORM_EXECUTION_FAILED,
                should_retry=True,
                result_uncertain=False,
            )
        
        # 检查 call_device_tool 成功格式
        # {"code": 0, "result": {...}}
        if "code" in raw_result:
            code = raw_result.get("code")
            
            # code == 0 或 code == "0" 表示成功
            if code == 0 or code == "0":
                return NormalizedResult(
                    status=NormalizedStatus.COMPLETED,
                    error_code=None,
                    should_retry=False,
                    result_uncertain=False,
                )
            
            # 检查 today-task 成功格式
            # {"code": "0000000000", "desc": "OK"}
            if code == "0000000000":
                return NormalizedResult(
                    status=NormalizedStatus.COMPLETED,
                    error_code=None,
                    should_retry=False,
                    result_uncertain=False,
                )
            
            # 检查 today-task 授权错误格式
            # {"code": "0000900034", "desc": "The authCode is invalid"}
            code_str = str(code)
            desc = raw_result.get("desc", "")
            
            if "0000900034" in code_str or "authCode" in desc or "authCode" in code_str:
                return NormalizedResult(
                    status=NormalizedStatus.AUTH_REQUIRED,
                    error_code=PLATFORM_AUTH_REQUIRED,
                    should_retry=False,
                    result_uncertain=False,
                )
            
            # 其他错误
            return NormalizedResult(
                status=NormalizedStatus.FAILED,
                error_code=PLATFORM_EXECUTION_FAILED,
                should_retry=True,
                result_uncertain=False,
            )
    
    # 处理字符串结果
    if isinstance(raw_result, str):
        if "success" in raw_result.lower() or "ok" in raw_result.lower():
            return NormalizedResult(
                status=NormalizedStatus.COMPLETED,
                error_code=None,
                should_retry=False,
                result_uncertain=False,
            )
        
        if "timeout" in raw_result.lower() or "超时" in raw_result:
            return NormalizedResult(
                status=NormalizedStatus.TIMEOUT,
                error_code=PLATFORM_TIMEOUT,
                should_retry=False,
                result_uncertain=True,
            )
        
        return NormalizedResult(
            status=NormalizedStatus.FAILED,
            error_code=PLATFORM_EXECUTION_FAILED,
            should_retry=True,
            result_uncertain=False,
        )
    
    # 未知格式，视为不确定
    return NormalizedResult(
        status=NormalizedStatus.RESULT_UNCERTAIN,
        error_code=PLATFORM_RESULT_UNCERTAIN,
        should_retry=False,
        result_uncertain=True,
    )
