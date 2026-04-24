"""
测试用户可见结果消息
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from platform_adapter.result_normalizer import NormalizedStatus
from platform_adapter.error_codes import (
    PLATFORM_TIMEOUT,
    PLATFORM_RESULT_UNCERTAIN,
    PLATFORM_AUTH_REQUIRED,
    PLATFORM_EXECUTION_FAILED,
    PLATFORM_FALLBACK_USED,
)
from platform_adapter.user_messages import (
    get_user_message,
    format_user_result,
)


class TestUserMessages:
    """测试用户消息"""
    
    def test_completed_message(self):
        """测试完成消息"""
        msg = get_user_message(NormalizedStatus.COMPLETED)
        assert "完成" in msg
    
    def test_queued_message(self):
        """测试排队消息"""
        msg = get_user_message(NormalizedStatus.QUEUED_FOR_DELIVERY)
        assert "提交" in msg or "等待" in msg
    
    def test_timeout_message(self):
        """测试超时消息"""
        msg = get_user_message(NormalizedStatus.TIMEOUT, PLATFORM_TIMEOUT)
        assert "超时" in msg or "确认" in msg
    
    def test_result_uncertain_message(self):
        """测试结果不确定消息"""
        msg = get_user_message(NormalizedStatus.RESULT_UNCERTAIN, PLATFORM_RESULT_UNCERTAIN)
        assert "未知" in msg or "确认" in msg or "重试" in msg
    
    def test_auth_required_message(self):
        """测试授权消息"""
        msg = get_user_message(NormalizedStatus.AUTH_REQUIRED, PLATFORM_AUTH_REQUIRED)
        assert "授权" in msg
    
    def test_failed_message(self):
        """测试失败消息"""
        msg = get_user_message(NormalizedStatus.FAILED, PLATFORM_EXECUTION_FAILED)
        assert "失败" in msg or "重试" in msg
    
    def test_fallback_used_message(self):
        """测试 fallback 消息"""
        msg = get_user_message(NormalizedStatus.QUEUED_FOR_DELIVERY, PLATFORM_FALLBACK_USED)
        assert "队列" in msg or "待处理" in msg


class TestFormatUserResult:
    """测试格式化用户结果"""
    
    def test_format_message_sending_completed(self):
        """测试短信发送完成"""
        result = format_user_result(
            capability="MESSAGE_SENDING",
            status=NormalizedStatus.COMPLETED,
        )
        assert "短信" in result
        assert "完成" in result
    
    def test_format_task_scheduling_completed(self):
        """测试日程创建完成"""
        result = format_user_result(
            capability="TASK_SCHEDULING",
            status=NormalizedStatus.COMPLETED,
        )
        assert "日程" in result
        assert "完成" in result
    
    def test_format_notification_timeout(self):
        """测试通知超时"""
        result = format_user_result(
            capability="NOTIFICATION",
            status=NormalizedStatus.TIMEOUT,
            error_code=PLATFORM_TIMEOUT,
        )
        assert "通知" in result
        assert "超时" in result or "确认" in result
    
    def test_format_with_details(self):
        """测试带详情"""
        result = format_user_result(
            capability="MESSAGE_SENDING",
            status=NormalizedStatus.FAILED,
            details="网络错误",
        )
        assert "网络错误" in result


class TestMessageConsistency:
    """测试消息一致性"""
    
    def test_all_statuses_have_messages(self):
        """测试所有状态都有消息"""
        statuses = [
            NormalizedStatus.COMPLETED,
            NormalizedStatus.QUEUED_FOR_DELIVERY,
            NormalizedStatus.FAILED,
            NormalizedStatus.TIMEOUT,
            NormalizedStatus.RESULT_UNCERTAIN,
            NormalizedStatus.AUTH_REQUIRED,
        ]
        
        for status in statuses:
            msg = get_user_message(status)
            assert msg is not None
            assert len(msg) > 0
            assert msg != "操作完成" or status == NormalizedStatus.COMPLETED
    
    def test_no_technical_jargon(self):
        """测试不含技术术语"""
        # 用户消息不应该包含技术术语
        msg = get_user_message(NormalizedStatus.TIMEOUT, PLATFORM_TIMEOUT)
        
        # 不应该包含这些技术术语
        forbidden = ["asyncio", "coroutine", "exception", "traceback", "PLATFORM_"]
        for term in forbidden:
            assert term not in msg
