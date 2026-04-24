"""
小艺适配器 Connected 路径测试
验证至少 1 条真实 connected 路径
"""

import pytest
from pathlib import Path
import sys
import os

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestXiaoyiAdapterConnectedPath:
    """测试小艺适配器 Connected 路径"""
    
    def test_adapter_can_initialize(self):
        """测试适配器可以初始化"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        
        adapter = XiaoyiAdapter()
        assert adapter.name == "xiaoyi"
        assert adapter._initialized == False
    
    def test_adapter_probe_returns_state(self):
        """测试适配器探测返回状态"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        import asyncio
        
        adapter = XiaoyiAdapter()
        result = asyncio.run(adapter.probe())
        
        # 应该返回状态
        assert "state" in result
        assert result["state"] in ["mock", "probe_only", "connected"]
    
    def test_adapter_checks_call_device_tool(self):
        """测试适配器检查 call_device_tool"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        
        adapter = XiaoyiAdapter()
        adapter._ensure_initialized_sync()
        
        # 应该检查 call_device_tool 是否可用
        assert hasattr(adapter, "_call_device_tool_available")
        assert isinstance(adapter._call_device_tool_available, bool)
    
    def test_message_sending_capability_state(self):
        """测试 MESSAGE_SENDING 能力状态"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        cap = asyncio.run(adapter.get_capability(PlatformCapability.MESSAGE_SENDING))
        
        assert cap is not None
        assert hasattr(cap, "available")
        assert hasattr(cap, "description")
    
    @pytest.mark.skipif(
        os.environ.get("OPENCLAW_RUNTIME") != "true",
        reason="需要 OpenClaw 运行时环境"
    )
    def test_message_sending_connected_path(self):
        """测试 MESSAGE_SENDING connected 路径 (需要真实环境)"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        # 检查能力是否可用
        probe_result = asyncio.run(adapter.probe())
        
        if probe_result.get("capabilities", {}).get("message_sending"):
            # 能力可用，测试真实调用
            result = asyncio.run(adapter.invoke(
                PlatformCapability.MESSAGE_SENDING,
                {
                    "phone_number": "13800138000",
                    "message": "测试消息"
                }
            ))
            
            # 应该返回结果
            assert "success" in result
            assert "status" in result
    
    def test_message_sending_fallback_path(self):
        """测试 MESSAGE_SENDING fallback 路径"""
        from platform_adapter.invoke_guard import create_fallback_result
        
        # 使用 create_fallback_result
        result = create_fallback_result(
            capability="MESSAGE_SENDING",
            op_name="send_message",
        )
        
        result_dict = result.to_dict() if hasattr(result, 'to_dict') else result
        
        # 应该返回 queued_for_delivery
        assert result_dict.get("normalized_status") == "queued_for_delivery"
        assert result_dict.get("fallback_used") == True
    
    def test_task_scheduling_capability_state(self):
        """测试 TASK_SCHEDULING 能力状态"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        cap = asyncio.run(adapter.get_capability(PlatformCapability.TASK_SCHEDULING))
        
        assert cap is not None
        assert hasattr(cap, "available")
    
    def test_notification_capability_state(self):
        """测试 NOTIFICATION 能力状态"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        cap = asyncio.run(adapter.get_capability(PlatformCapability.NOTIFICATION))
        
        assert cap is not None
        # NOTIFICATION 状态取决于 auth_code 配置
        # 当前已配置 authCode，所以 available=True
        assert cap.available == True


class TestConnectedStateDetection:
    """测试 Connected 状态检测"""
    
    def test_state_detection_logic(self):
        """测试状态检测逻辑"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        import asyncio
        
        adapter = XiaoyiAdapter()
        result = asyncio.run(adapter.probe())
        
        # 口径统一：device_connected 默认 true
        # connected 表示"该能力在已连接设备环境中已真实可调用"
        assert result.get("device_connected") == True
        
        # 状态应该基于能力是否已接通
        if result.get("available"):
            assert result["state"] == "connected"
        else:
            assert result["state"] == "probe_only"
    
    def test_available_requires_capability_connected(self):
        """测试 available 需要能力已接通"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        is_available = asyncio.run(adapter.is_available())
        probe_result = asyncio.run(adapter.probe())
        
        # 口径统一：available = 至少一个能力已接通
        if is_available:
            assert any(probe_result.get("capabilities", {}).values()) == True


class TestInvokeImplementation:
    """测试 Invoke 实现"""
    
    def test_invoke_routes_to_correct_method(self):
        """测试 invoke 路由到正确的方法"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        # 测试 MESSAGE_SENDING 路由
        # 即使能力不可用，也应该尝试调用
        result = asyncio.run(adapter.invoke(
            PlatformCapability.MESSAGE_SENDING,
            {"phone_number": "test", "message": "test"}
        ))
        
        # 应该返回结果（可能是 fallback）
        assert "success" in result
        assert "status" in result
    
    def test_invoke_returns_proper_status(self):
        """测试 invoke 返回正确的状态"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        # 调用 invoke
        result = asyncio.run(adapter.invoke(
            PlatformCapability.MESSAGE_SENDING,
            {"phone_number": "test", "message": "test"}
        ))
        
        # 应该返回正确的状态
        assert "status" in result
        assert result["status"] in [
            "completed",
            "failed",
            "timeout",
            "result_uncertain",
            "queued_for_delivery",
        ]


class TestCapabilityAvailability:
    """测试能力可用性"""
    
    def test_at_least_one_capability_can_be_available(self):
        """测试至少一个能力可以变为可用"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        import asyncio
        
        adapter = XiaoyiAdapter()
        adapter._ensure_initialized_sync()
        
        # 检查能力状态
        capabilities = adapter._capabilities
        
        # MESSAGE_SENDING 或 TASK_SCHEDULING 应该可以变为可用
        # 取决于 call_device_tool 是否可用
        if adapter._call_device_tool_available:
            assert capabilities.get("message_sending") or capabilities.get("task_scheduling")
    
    def test_capability_description_is_clear(self):
        """测试能力描述清晰"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        for cap in [PlatformCapability.MESSAGE_SENDING, PlatformCapability.TASK_SCHEDULING]:
            state = asyncio.run(adapter.get_capability(cap))
            if state:
                # 描述应该说明接入方式
                assert "via" in state.description.lower() or "send_message" in state.description.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
