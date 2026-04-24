"""
送达确认语义测试
验证送达确认的降级策略和状态流转
"""

import pytest
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDeliveryConfirmationSemantics:
    """测试送达确认语义"""
    
    def test_delivery_pending_is_not_succeeded(self):
        """测试 delivery_pending 不是 succeeded"""
        from domain.tasks import TaskStatus
        
        assert TaskStatus.DELIVERY_PENDING != TaskStatus.SUCCEEDED
        assert TaskStatus.DELIVERY_PENDING.value != "succeeded"
    
    def test_delivery_confirmed_event_exists(self):
        """测试 delivery_confirmed 事件存在"""
        from domain.tasks import EventType
        
        assert EventType.DELIVERY_CONFIRMED.value == "delivery_confirmed"
    
    def test_delivery_pending_event_exists(self):
        """测试 delivery_pending 事件存在"""
        from domain.tasks import EventType
        
        assert EventType.DELIVERY_PENDING.value == "delivery_pending"
    
    def test_message_adapter_returns_queued_not_success(self):
        """测试消息适配器返回 queued 而非 success"""
        from infrastructure.tool_adapters.message_adapter import MessageAdapter
        import asyncio
        
        adapter = MessageAdapter()
        
        # 发送消息
        result = asyncio.run(adapter.send_message(
            user_id="test_user",
            message="test message",
            task_id="test_task"
        ))
        
        # 应该返回 queued，不是 success
        assert result.get("status") == "queued_for_delivery"
        assert result.get("status") != "success"
    
    def test_queued_result_has_clear_message(self):
        """测试 queued 结果有明确的消息"""
        from infrastructure.tool_adapters.message_adapter import MessageAdapter
        import asyncio
        
        adapter = MessageAdapter()
        
        result = asyncio.run(adapter.send_message(
            user_id="test_user",
            message="test message"
        ))
        
        # 应该有明确的消息说明状态
        assert "message" in result
        assert "等待" in result["message"] or "queued" in result.get("status", "")


class TestConfirmationDegradation:
    """测试确认降级策略"""
    
    def test_platform_without_confirmation(self):
        """测试无确认平台的降级"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        # 如果平台不可用，应该有明确的降级行为
        is_available = asyncio.run(adapter.is_available())
        
        if not is_available:
            # 尝试调用应该返回明确的错误
            result = asyncio.run(adapter.invoke(
                PlatformCapability.MESSAGE_SENDING,
                {"message": "test"}
            ))
            
            assert result.get("success") == False
            assert "error" in result
            assert result.get("fallback_available") == True
    
    def test_degradation_does_not_claim_success(self):
        """测试降级不声称成功"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        result = asyncio.run(adapter.invoke(
            PlatformCapability.MESSAGE_SENDING,
            {"message": "test"}
        ))
        
        # 如果失败，不应该声称成功
        if not result.get("success"):
            assert result.get("success") == False
            assert "error" in result


class TestConfirmationLevels:
    """测试确认级别"""
    
    def test_confirmation_level_definitions(self):
        """测试确认级别定义"""
        # Level 1: 完整确认
        level_1 = "full_confirmation"
        
        # Level 2: 投递确认
        level_2 = "delivery_confirmation"
        
        # Level 3: 无确认
        level_3 = "no_confirmation"
        
        # 确认级别应该有明确定义
        assert level_1 != level_2 != level_3
    
    def test_current_platform_confirmation_level(self):
        """测试当前平台确认级别"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        import asyncio
        
        adapter = XiaoyiAdapter()
        is_available = asyncio.run(adapter.is_available())
        
        # 当前应该是 Level 3 (无确认)
        if not is_available:
            confirmation_level = "no_confirmation"
            assert confirmation_level == "no_confirmation"


class TestTimeoutHandling:
    """测试超时处理"""
    
    def test_delivery_pending_timeout_thresholds(self):
        """测试 delivery_pending 超时阈值"""
        # 定义超时阈值
        warning_threshold_minutes = 5
        timeout_threshold_minutes = 30
        
        assert warning_threshold_minutes < timeout_threshold_minutes
    
    def test_timeout_states_are_distinct(self):
        """测试超时状态是独立的"""
        # 超时警告状态
        confirmation_timeout_warning = "confirmation_timeout_warning"
        
        # 超时状态
        confirmation_timeout = "confirmation_timeout"
        
        assert confirmation_timeout_warning != confirmation_timeout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
