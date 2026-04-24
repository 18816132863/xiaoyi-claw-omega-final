"""
平台调用统一防护层
提供超时保护、错误归一、审计、幂等保护
"""

import asyncio
import hashlib
import json
import time
from typing import Any, Callable, Coroutine, Optional
from datetime import datetime

from .error_codes import (
    ErrorCode,
    PLATFORM_TIMEOUT,
    PLATFORM_RESULT_UNCERTAIN,
    PLATFORM_AUTH_REQUIRED,
    PLATFORM_PERMISSION_DENIED,
    PLATFORM_NOT_CONNECTED,
    PLATFORM_NOT_AVAILABLE,
    PLATFORM_BAD_PARAMS,
    PLATFORM_EXECUTION_FAILED,
    PLATFORM_FALLBACK_USED,
)
from .result_normalizer import normalize_result, NormalizedStatus
from .user_messages import get_user_message


class InvokeResult:
    """统一调用结果"""
    
    def __init__(
        self,
        capability: str,
        op_name: str,
        normalized_status: str,
        error_code: Optional[str] = None,
        user_message: str = "",
        raw_result: Optional[dict] = None,
        should_retry: bool = False,
        result_uncertain: bool = False,
        side_effecting: bool = False,
        fallback_used: bool = False,
        idempotency_key: Optional[str] = None,
        elapsed_ms: int = 0,
    ):
        self.capability = capability
        self.op_name = op_name
        self.normalized_status = normalized_status
        self.error_code = error_code
        self.user_message = user_message
        self.raw_result = raw_result or {}
        self.should_retry = should_retry
        self.result_uncertain = result_uncertain
        self.side_effecting = side_effecting
        self.fallback_used = fallback_used
        self.idempotency_key = idempotency_key
        self.elapsed_ms = elapsed_ms
    
    def to_dict(self) -> dict:
        return {
            "capability": self.capability,
            "op_name": self.op_name,
            "normalized_status": self.normalized_status,
            "error_code": self.error_code,
            "user_message": self.user_message,
            "raw_result": self.raw_result,
            "should_retry": self.should_retry,
            "result_uncertain": self.result_uncertain,
            "side_effecting": self.side_effecting,
            "fallback_used": self.fallback_used,
            "idempotency_key": self.idempotency_key,
            "elapsed_ms": self.elapsed_ms,
        }


# 幂等键缓存（内存级，生产环境应使用 Redis 或数据库）
_idempotency_cache: dict[str, InvokeResult] = {}


def generate_idempotency_key(
    task_id: Optional[str],
    capability: str,
    payload: dict,
) -> str:
    """生成幂等键"""
    # 规范化 payload
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    payload_hash = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    
    if task_id:
        return f"{task_id}:{capability}:{payload_hash}"
    else:
        return f"{capability}:{payload_hash}:{int(time.time() * 1000)}"


def check_idempotency(idempotency_key: str) -> Optional[InvokeResult]:
    """检查幂等键是否已有结果"""
    return _idempotency_cache.get(idempotency_key)


def store_idempotency_result(idempotency_key: str, result: InvokeResult):
    """存储幂等结果"""
    _idempotency_cache[idempotency_key] = result


async def guarded_platform_call(
    capability: str,
    op_name: str,
    call_coro: Coroutine,
    *,
    timeout_seconds: int = 60,
    idempotency_key: Optional[str] = None,
    side_effecting: bool = False,
    allow_fallback: bool = False,
    task_id: Optional[str] = None,
    payload: Optional[dict] = None,
) -> InvokeResult:
    """
    统一平台调用防护
    
    Args:
        capability: 能力名称
        op_name: 操作名称
        call_coro: 实际调用协程
        timeout_seconds: 超时秒数
        idempotency_key: 幂等键
        side_effecting: 是否有副作用
        allow_fallback: 是否允许 fallback
        task_id: 任务 ID
        payload: 调用参数
    
    Returns:
        InvokeResult: 统一结果
    """
    start_time = time.time()
    
    # 生成幂等键
    if not idempotency_key:
        idempotency_key = generate_idempotency_key(task_id, capability, payload or {})
    
    # 检查幂等
    if side_effecting:
        cached = check_idempotency(idempotency_key)
        if cached and cached.normalized_status == NormalizedStatus.COMPLETED:
            return cached
    
    try:
        # 执行调用（带超时）
        raw_result = await asyncio.wait_for(
            call_coro,
            timeout=timeout_seconds,
        )
        
        # 归一化结果
        normalized = normalize_result(raw_result, capability, op_name)
        
        # 计算耗时
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # 构造结果
        result = InvokeResult(
            capability=capability,
            op_name=op_name,
            normalized_status=normalized.status,
            error_code=normalized.error_code,
            user_message=get_user_message(normalized.status, normalized.error_code),
            raw_result=raw_result,
            should_retry=normalized.should_retry and not side_effecting,
            result_uncertain=normalized.result_uncertain,
            side_effecting=side_effecting,
            fallback_used=False,
            idempotency_key=idempotency_key,
            elapsed_ms=elapsed_ms,
        )
        
        # 存储幂等结果
        if side_effecting and normalized.status == NormalizedStatus.COMPLETED:
            store_idempotency_result(idempotency_key, result)
        
        return result
        
    except asyncio.TimeoutError:
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # 超时 = 结果不确定
        return InvokeResult(
            capability=capability,
            op_name=op_name,
            normalized_status=NormalizedStatus.TIMEOUT,
            error_code=PLATFORM_TIMEOUT,
            user_message=get_user_message(NormalizedStatus.TIMEOUT, PLATFORM_TIMEOUT),
            raw_result={"error": f"Timeout after {timeout_seconds}s"},
            should_retry=False,  # 超时不允许自动重试
            result_uncertain=True,
            side_effecting=side_effecting,
            fallback_used=False,
            idempotency_key=idempotency_key,
            elapsed_ms=elapsed_ms,
        )
        
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # 异常 = 失败
        return InvokeResult(
            capability=capability,
            op_name=op_name,
            normalized_status=NormalizedStatus.FAILED,
            error_code=PLATFORM_EXECUTION_FAILED,
            user_message=get_user_message(NormalizedStatus.FAILED, PLATFORM_EXECUTION_FAILED),
            raw_result={"error": str(e)},
            should_retry=not side_effecting,
            result_uncertain=False,
            side_effecting=side_effecting,
            fallback_used=False,
            idempotency_key=idempotency_key,
            elapsed_ms=elapsed_ms,
        )


def create_fallback_result(
    capability: str,
    op_name: str,
    idempotency_key: Optional[str] = None,
) -> InvokeResult:
    """创建 fallback 结果"""
    return InvokeResult(
        capability=capability,
        op_name=op_name,
        normalized_status=NormalizedStatus.QUEUED_FOR_DELIVERY,
        error_code=PLATFORM_FALLBACK_USED,
        user_message=get_user_message(NormalizedStatus.QUEUED_FOR_DELIVERY, PLATFORM_FALLBACK_USED),
        raw_result={},
        should_retry=False,
        result_uncertain=False,
        side_effecting=True,
        fallback_used=True,
        idempotency_key=idempotency_key,
        elapsed_ms=0,
    )
