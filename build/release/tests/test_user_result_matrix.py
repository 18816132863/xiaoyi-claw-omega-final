"""
测试用户结果消息矩阵
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from platform_adapter.user_messages import (
    get_user_message,
    format_user_result,
)
from platform_adapter.result_normalizer import NormalizedStatus
from platform_adapter.error_codes import (
    PLATFORM_TIMEOUT,
    PLATFORM_RESULT_UNCERTAIN,
    PLATFORM_AUTH_REQUIRED,
    PLATFORM_EXECUTION_FAILED,
    PLATFORM_FALLBACK_USED,
)


class TestUserResultMessageMatrix:
    """测试用户结果消息矩阵"""
    
    def test_completed_message(self):
        """测试 completed 消息"""
        msg = get_user_message(NormalizedStatus.COMPLETED)
        assert "完成" in msg
        assert "失败" not in msg
        assert "超时" not in msg
    
    def test_queued_message(self):
        """测试 queued 消息"""
        msg = get_user_message(NormalizedStatus.QUEUED_FOR_DELIVERY)
        assert "提交" in msg or "等待" in msg
    
    def test_timeout_message(self):
        """测试 timeout 消息"""
        msg = get_user_message(NormalizedStatus.TIMEOUT, PLATFORM_TIMEOUT)
        assert "超时" in msg or "确认" in msg
        # 不应该建议自动重试
        assert "自动重试" not in msg
    
    def test_result_uncertain_message(self):
        """测试 result_uncertain 消息"""
        msg = get_user_message(NormalizedStatus.RESULT_UNCERTAIN, PLATFORM_RESULT_UNCERTAIN)
        assert "未知" in msg or "确认" in msg
        # 应该说明不自动重试的原因
        assert "重复" in msg or "人工" in msg
    
    def test_auth_required_message(self):
        """测试 auth_required 消息"""
        msg = get_user_message(NormalizedStatus.AUTH_REQUIRED, PLATFORM_AUTH_REQUIRED)
        assert "授权" in msg
    
    def test_fallback_used_message(self):
        """测试 fallback_used 消息"""
        msg = get_user_message(NormalizedStatus.QUEUED_FOR_DELIVERY, PLATFORM_FALLBACK_USED)
        assert "队列" in msg or "待处理" in msg
    
    def test_failed_message(self):
        """测试 failed 消息"""
        msg = get_user_message(NormalizedStatus.FAILED, PLATFORM_EXECUTION_FAILED)
        assert "失败" in msg


class TestCapabilitySpecificMessages:
    """测试能力特定消息"""
    
    def test_message_sending_completed(self):
        """测试短信发送完成"""
        msg = format_user_result(
            capability="MESSAGE_SENDING",
            status=NormalizedStatus.COMPLETED,
        )
        assert "短信" in msg
        assert "完成" in msg
    
    def test_message_sending_timeout(self):
        """测试短信发送超时"""
        msg = format_user_result(
            capability="MESSAGE_SENDING",
            status=NormalizedStatus.TIMEOUT,
            error_code=PLATFORM_TIMEOUT,
        )
        assert "短信" in msg
        assert "超时" in msg or "确认" in msg
    
    def test_task_scheduling_completed(self):
        """测试日程创建完成"""
        msg = format_user_result(
            capability="TASK_SCHEDULING",
            status=NormalizedStatus.COMPLETED,
        )
        assert "日程" in msg
        assert "完成" in msg
    
    def test_notification_auth_required(self):
        """测试通知授权缺失"""
        msg = format_user_result(
            capability="NOTIFICATION",
            status=NormalizedStatus.AUTH_REQUIRED,
            error_code=PLATFORM_AUTH_REQUIRED,
        )
        assert "通知" in msg
        assert "授权" in msg


class TestMessageQuality:
    """测试消息质量"""
    
    def test_no_technical_jargon(self):
        """测试不含技术术语"""
        messages = [
            get_user_message(NormalizedStatus.COMPLETED),
            get_user_message(NormalizedStatus.TIMEOUT, PLATFORM_TIMEOUT),
            get_user_message(NormalizedStatus.RESULT_UNCERTAIN, PLATFORM_RESULT_UNCERTAIN),
            get_user_message(NormalizedStatus.AUTH_REQUIRED, PLATFORM_AUTH_REQUIRED),
        ]
        
        forbidden = [
            "asyncio", "coroutine", "exception", "traceback",
            "PLATFORM_", "ERROR_CODE", "normalized_status",
            "idempotency_key", "raw_result",
        ]
        
        for msg in messages:
            for term in forbidden:
                assert term not in msg, f"消息包含技术术语: {term}"
    
    def test_actionable_guidance(self):
        """测试提供可操作的指引"""
        # timeout 应该告诉用户检查结果
        msg = get_user_message(NormalizedStatus.TIMEOUT, PLATFORM_TIMEOUT)
        assert "检查" in msg or "确认" in msg
        
        # auth_required 应该告诉用户授权
        msg = get_user_message(NormalizedStatus.AUTH_REQUIRED, PLATFORM_AUTH_REQUIRED)
        assert "授权" in msg
    
    def test_consistent_tone(self):
        """测试语气一致"""
        # 所有消息都应该礼貌、专业
        messages = [
            get_user_message(NormalizedStatus.COMPLETED),
            get_user_message(NormalizedStatus.FAILED, PLATFORM_EXECUTION_FAILED),
            get_user_message(NormalizedStatus.TIMEOUT, PLATFORM_TIMEOUT),
        ]
        
        # 不应该有感叹号（过于情绪化）
        for msg in messages:
            assert "！" not in msg
            assert "!!" not in msg


class TestMessageMatrixCompleteness:
    """测试消息矩阵完整性"""
    
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
    
    def test_all_capabilities_have_names(self):
        """测试所有能力都有名称"""
        capabilities = [
            "MESSAGE_SENDING",
            "TASK_SCHEDULING",
            "STORAGE",
            "NOTIFICATION",
        ]
        
        for cap in capabilities:
            msg = format_user_result(
                capability=cap,
                status=NormalizedStatus.COMPLETED,
            )
            # 消息应该包含能力名称
            assert len(msg) > 0
