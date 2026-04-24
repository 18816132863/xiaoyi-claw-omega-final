"""
测试统一防护层
"""

import pytest
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from platform_adapter.invoke_guard import (
    guarded_platform_call,
    generate_idempotency_key,
    check_idempotency,
    store_idempotency_result,
    InvokeResult,
)
from platform_adapter.result_normalizer import normalize_result, NormalizedStatus
from platform_adapter.error_codes import (
    PLATFORM_TIMEOUT,
    PLATFORM_RESULT_UNCERTAIN,
    PLATFORM_AUTH_REQUIRED,
    PLATFORM_EXECUTION_FAILED,
)


class TestInvokeGuard:
    """测试统一防护层"""
    
    @pytest.mark.asyncio
    async def test_successful_call(self):
        """测试成功调用"""
        async def success_call():
            return {"code": 0, "result": {"message": "success"}}
        
        result = await guarded_platform_call(
            capability="TEST",
            op_name="test_op",
            call_coro=success_call(),
            timeout_seconds=5,
        )
        
        assert result.normalized_status == NormalizedStatus.COMPLETED
        assert result.error_code is None
        assert result.result_uncertain == False
    
    @pytest.mark.asyncio
    async def test_timeout_call(self):
        """测试超时调用"""
        async def slow_call():
            await asyncio.sleep(10)
            return {"code": 0}
        
        result = await guarded_platform_call(
            capability="TEST",
            op_name="test_timeout",
            call_coro=slow_call(),
            timeout_seconds=1,
        )
        
        assert result.normalized_status == NormalizedStatus.TIMEOUT
        assert result.error_code == PLATFORM_TIMEOUT
        assert result.result_uncertain == True
        assert result.should_retry == False  # 超时不允许自动重试
    
    @pytest.mark.asyncio
    async def test_failed_call(self):
        """测试失败调用"""
        async def fail_call():
            raise Exception("Test error")
        
        result = await guarded_platform_call(
            capability="TEST",
            op_name="test_fail",
            call_coro=fail_call(),
            timeout_seconds=5,
        )
        
        assert result.normalized_status == NormalizedStatus.FAILED
        assert result.error_code == PLATFORM_EXECUTION_FAILED
        assert result.result_uncertain == False
    
    @pytest.mark.asyncio
    async def test_side_effecting_no_auto_retry_on_timeout(self):
        """测试副作用操作超时不自动重试"""
        async def slow_call():
            await asyncio.sleep(10)
            return {"code": 0}
        
        result = await guarded_platform_call(
            capability="MESSAGE_SENDING",
            op_name="send_message",
            call_coro=slow_call(),
            timeout_seconds=1,
            side_effecting=True,
        )
        
        assert result.normalized_status == NormalizedStatus.TIMEOUT
        assert result.should_retry == False
        assert result.side_effecting == True


class TestResultNormalizer:
    """测试结果归一化"""
    
    def test_normalize_success_code_zero(self):
        """测试 code=0 成功"""
        result = normalize_result({"code": 0, "result": {}}, "TEST", "test")
        assert result.status == NormalizedStatus.COMPLETED
    
    def test_normalize_success_today_task(self):
        """测试 today-task 成功格式"""
        result = normalize_result({"code": "0000000000", "desc": "OK"}, "NOTIFICATION", "push")
        assert result.status == NormalizedStatus.COMPLETED
    
    def test_normalize_timeout(self):
        """测试超时"""
        result = normalize_result({"status": "error", "error": "发送短信超时（60秒）"}, "TEST", "test")
        assert result.status == NormalizedStatus.TIMEOUT
        assert result.result_uncertain == True
    
    def test_normalize_auth_error(self):
        """测试授权错误"""
        result = normalize_result({"status": "error", "error": "authCode is invalid"}, "TEST", "test")
        assert result.status == NormalizedStatus.AUTH_REQUIRED
    
    def test_normalize_unknown_format(self):
        """测试未知格式"""
        # 传入一个非字符串、非字典的值
        result = normalize_result(None, "TEST", "test")
        assert result.status == NormalizedStatus.FAILED  # None 视为不可用


class TestIdempotency:
    """测试幂等保护"""
    
    def test_generate_idempotency_key(self):
        """测试生成幂等键"""
        key1 = generate_idempotency_key("task1", "CAP", {"a": 1})
        key2 = generate_idempotency_key("task1", "CAP", {"a": 1})
        key3 = generate_idempotency_key("task1", "CAP", {"a": 2})
        
        assert key1 == key2  # 相同参数生成相同键
        assert key1 != key3  # 不同参数生成不同键
    
    def test_idempotency_cache(self):
        """测试幂等缓存"""
        key = generate_idempotency_key("task1", "TEST", {"x": 1})
        
        # 第一次检查应该为空
        cached = check_idempotency(key)
        assert cached is None
        
        # 存储结果
        result = InvokeResult(
            capability="TEST",
            op_name="test",
            normalized_status=NormalizedStatus.COMPLETED,
        )
        store_idempotency_result(key, result)
        
        # 第二次检查应该有结果
        cached = check_idempotency(key)
        assert cached is not None
        assert cached.normalized_status == NormalizedStatus.COMPLETED


class TestErrorCodes:
    """测试错误码"""
    
    def test_error_codes_exist(self):
        """测试错误码存在"""
        from platform_adapter.error_codes import (
            PLATFORM_TIMEOUT,
            PLATFORM_RESULT_UNCERTAIN,
            PLATFORM_AUTH_REQUIRED,
            PLATFORM_EXECUTION_FAILED,
            PLATFORM_FALLBACK_USED,
        )
        
        assert PLATFORM_TIMEOUT == "PLATFORM_TIMEOUT"
        assert PLATFORM_RESULT_UNCERTAIN == "PLATFORM_RESULT_UNCERTAIN"
        assert PLATFORM_AUTH_REQUIRED == "PLATFORM_AUTH_REQUIRED"
    
    def test_error_descriptions(self):
        """测试错误描述"""
        from platform_adapter.error_codes import get_error_description
        
        desc = get_error_description(PLATFORM_TIMEOUT)
        assert "超时" in desc


class TestUserMessages:
    """测试用户消息"""
    
    def test_completed_message(self):
        """测试完成消息"""
        from platform_adapter.user_messages import get_user_message
        
        msg = get_user_message(NormalizedStatus.COMPLETED)
        assert "完成" in msg
    
    def test_timeout_message(self):
        """测试超时消息"""
        from platform_adapter.user_messages import get_user_message
        
        msg = get_user_message(NormalizedStatus.TIMEOUT, PLATFORM_TIMEOUT)
        assert "超时" in msg or "确认" in msg
    
    def test_auth_required_message(self):
        """测试授权消息"""
        from platform_adapter.user_messages import get_user_message
        
        msg = get_user_message(NormalizedStatus.AUTH_REQUIRED, PLATFORM_AUTH_REQUIRED)
        assert "授权" in msg
