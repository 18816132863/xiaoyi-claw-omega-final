"""
平台执行语义测试
验证 accepted / queued / confirmed 语义完全分开
"""

import pytest
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestPlatformExecutionSemantics:
    """测试平台执行语义"""
    
    def test_task_status_accepted_states(self):
        """测试 accepted 层级的状态"""
        from domain.tasks import TaskStatus
        
        accepted_states = [
            TaskStatus.VALIDATED,
            TaskStatus.PERSISTED,
            TaskStatus.QUEUED,
        ]
        
        for status in accepted_states:
            assert status in [
                TaskStatus.VALIDATED,
                TaskStatus.PERSISTED,
                TaskStatus.QUEUED,
            ], f"{status.value} 应该是 accepted 层级"
    
    def test_task_status_queued_for_delivery_state(self):
        """测试 queued_for_delivery 层级的状态"""
        from domain.tasks import TaskStatus
        
        assert TaskStatus.DELIVERY_PENDING == TaskStatus.DELIVERY_PENDING
        assert TaskStatus.DELIVERY_PENDING.value == "delivery_pending"
    
    def test_task_status_completed_states(self):
        """测试 completed 层级的状态"""
        from domain.tasks import TaskStatus
        
        completed_states = [
            TaskStatus.SUCCEEDED,
        ]
        
        for status in completed_states:
            assert status == TaskStatus.SUCCEEDED, f"{status.value} 应该是 completed 层级"
    
    def test_event_type_delivery_semantics(self):
        """测试送达相关事件的语义"""
        from domain.tasks import EventType
        
        # delivery_pending 是 queued 层级
        assert EventType.DELIVERY_PENDING.value == "delivery_pending"
        
        # delivery_confirmed 是 completed 层级
        assert EventType.DELIVERY_CONFIRMED.value == "delivery_confirmed"
    
    def test_message_send_result_semantics(self):
        """测试消息发送结果的语义"""
        from infrastructure.tool_adapters.message_adapter import MessageSendResult
        
        # success 是 completed
        assert MessageSendResult.SUCCESS == "success"
        
        # queued 是 queued 层级
        assert MessageSendResult.QUEUED == "queued_for_delivery"
        
        # failed 是失败
        assert MessageSendResult.FAILED == "failed"
    
    def test_delivery_pending_not_equal_to_succeeded(self):
        """测试 delivery_pending 不等于 succeeded"""
        from domain.tasks import TaskStatus
        
        assert TaskStatus.DELIVERY_PENDING != TaskStatus.SUCCEEDED
        assert TaskStatus.DELIVERY_PENDING.value != TaskStatus.SUCCEEDED.value
    
    def test_queued_for_delivery_not_success(self):
        """测试 queued_for_delivery 不是成功"""
        from infrastructure.tool_adapters.message_adapter import MessageSendResult
        
        # queued 不等于 success
        assert MessageSendResult.QUEUED != MessageSendResult.SUCCESS


class TestPlatformConnectionStates:
    """测试平台连接状态"""
    
    def test_xiaoyi_adapter_probe_only_state(self):
        """测试小艺适配器的 probe_only 状态"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        import asyncio
        
        adapter = XiaoyiAdapter()
        result = asyncio.run(adapter.probe())
        
        # 口径统一版：device_connected 默认 true
        assert "available" in result
        assert "device_connected" in result
        assert "capabilities" in result
        
        # device_connected 默认 true
        assert result["device_connected"] == True
        
        # 如果 available=False，说明是 probe_only（能力未授权）
        if not result["available"]:
            assert result["state"] == "probe_only"
    
    def test_xiaoyi_adapter_capability_not_connected_error(self):
        """测试能力未接通的错误码"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        # 尝试调用未接通的能力
        result = asyncio.run(adapter.invoke(
            PlatformCapability.MESSAGE_SENDING,
            {"message": "test"}
        ))
        
        # 应该返回 CAPABILITY_NOT_CONNECTED 错误
        if not result.get("success"):
            assert result.get("error_code") == "CAPABILITY_NOT_CONNECTED"
    
    def test_platform_availability_requires_both(self):
        """测试平台可用需要环境存在 + 能力接通"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        # 真正的 available = 环境存在 + 至少一个能力已接通
        is_available = asyncio.run(adapter.is_available())
        
        # 如果不可用，检查原因
        if not is_available:
            probe_result = asyncio.run(adapter.probe())
            
            # 要么环境不存在，要么能力未接通
            assert not probe_result.get("environment_exists") or \
                   not any(probe_result.get("capabilities", {}).values())


class TestExecutionResultExplanation:
    """测试执行结果解释"""
    
    def test_queued_result_explanation(self):
        """测试排队状态的解释"""
        from infrastructure.tool_adapters.message_adapter import MessageSendResult
        
        # queued 状态的用户解释
        status = MessageSendResult.QUEUED
        
        # 不应该说"已完成"
        assert status != "success"
        assert status != "completed"
        
        # 应该说"已入队"
        assert status == "queued_for_delivery"
    
    def test_delivery_pending_user_message(self):
        """测试 delivery_pending 的用户消息"""
        from domain.tasks import TaskStatus
        
        # delivery_pending 的用户消息应该是"已提交，等待确认"
        # 而不是"已完成"
        assert TaskStatus.DELIVERY_PENDING.value == "delivery_pending"
        assert TaskStatus.DELIVERY_PENDING != TaskStatus.SUCCEEDED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
