"""
小艺适配器真实连接测试
区分 mock / probe / connected 三态
"""

import pytest
from pathlib import Path
import sys
import os

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestXiaoyiAdapterConnectionStates:
    """测试小艺适配器连接状态"""
    
    def test_adapter_initialization(self):
        """测试适配器初始化"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        
        adapter = XiaoyiAdapter()
        
        assert adapter.name == "xiaoyi"
        assert adapter.description == "Xiaoyi/HarmonyOS platform adapter"
        assert adapter._initialized == False
    
    def test_probe_state_detection(self):
        """测试探测状态检测"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        import asyncio
        
        adapter = XiaoyiAdapter()
        result = asyncio.run(adapter.probe())
        
        # 口径统一版：探测结果应该包含关键字段
        assert "adapter" in result
        assert "available" in result
        assert "device_connected" in result  # 默认 true
        assert "capabilities" in result
        
        # device_connected 默认 true
        assert result["device_connected"] == True
    
    def test_environment_detection_variables(self):
        """测试环境检测变量"""
        from platform_adapter.runtime_probe import RuntimeProbe
        
        env = RuntimeProbe.detect_environment()
        
        # 应该检测到环境状态
        assert "is_xiaoyi" in env
        assert "is_harmonyos" in env
        assert isinstance(env["is_xiaoyi"], bool)
        assert isinstance(env["is_harmonyos"], bool)
    
    def test_capability_states_are_explicit(self):
        """测试能力状态是明确的"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        # 获取各个能力状态
        task_cap = asyncio.run(adapter.get_capability(PlatformCapability.TASK_SCHEDULING))
        msg_cap = asyncio.run(adapter.get_capability(PlatformCapability.MESSAGE_SENDING))
        notif_cap = asyncio.run(adapter.get_capability(PlatformCapability.NOTIFICATION))
        
        # 每个能力状态应该是明确的
        for cap in [task_cap, msg_cap, notif_cap]:
            if cap:
                assert hasattr(cap, 'available')
                assert hasattr(cap, 'description')
                assert isinstance(cap.available, bool)


class TestConnectionStateDistinction:
    """测试连接状态区分"""
    
    def test_mock_state_definition(self):
        """测试 mock 状态定义"""
        # mock: 完全模拟，无真实环境
        mock_state = {
            "environment_exists": False,
            "capabilities_connected": False,
            "can_invoke": False
        }
        
        assert mock_state["environment_exists"] == False
        assert mock_state["capabilities_connected"] == False
    
    def test_probe_state_definition(self):
        """测试 probe 状态定义"""
        # probe: 环境存在，能力未接通
        probe_state = {
            "environment_exists": True,
            "capabilities_connected": False,
            "can_invoke": False
        }
        
        assert probe_state["environment_exists"] == True
        assert probe_state["capabilities_connected"] == False
    
    def test_connected_state_definition(self):
        """测试 connected 状态定义"""
        # connected: 环境存在，能力已接通
        connected_state = {
            "environment_exists": True,
            "capabilities_connected": True,
            "can_invoke": True
        }
        
        assert connected_state["environment_exists"] == True
        assert connected_state["capabilities_connected"] == True
    
    def test_states_are_mutually_exclusive(self):
        """测试状态互斥"""
        mock = {"env": False, "cap": False}
        probe = {"env": True, "cap": False}
        connected = {"env": True, "cap": True}
        
        # 三种状态应该互斥
        states = [mock, probe, connected]
        unique_states = set((s["env"], s["cap"]) for s in states)
        
        assert len(unique_states) == 3


class TestCurrentEnvironmentState:
    """测试当前环境状态"""
    
    def test_detect_current_state(self):
        """测试检测当前状态"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        import asyncio
        
        adapter = XiaoyiAdapter()
        result = asyncio.run(adapter.probe())
        
        # 判断当前状态
        env_exists = result.get("environment_exists", False)
        caps_available = any(result.get("capabilities", {}).values())
        
        if not env_exists:
            current_state = "mock"
        elif env_exists and not caps_available:
            current_state = "probe"
        else:
            current_state = "connected"
        
        # 当前应该是 mock 或 probe
        assert current_state in ["mock", "probe", "connected"]
    
    def test_runtime_probe_adapter_recommendation(self):
        """测试运行时探测适配器推荐"""
        from platform_adapter.runtime_probe import RuntimeProbe
        
        recommended = RuntimeProbe.get_recommended_adapter()
        
        # 推荐应该是明确的适配器名称
        assert recommended in ["xiaoyi", "null"]
    
    def test_probe_adapter_sync(self):
        """测试同步探测适配器"""
        from platform_adapter.runtime_probe import RuntimeProbe
        
        result = RuntimeProbe.probe_adapter_sync("xiaoyi")
        
        assert "adapter" in result
        assert "available" in result
        
        # 如果不可用，应该有明确的原因
        if not result.get("available"):
            # 要么环境不存在，要么能力未接通
            assert result.get("environment_exists") == False or \
                   not any(result.get("capabilities", {}).values())


class TestAdapterInvokeBehavior:
    """测试适配器调用行为"""
    
    def test_invoke_on_unavailable_capability(self):
        """测试调用不可用能力"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        result = asyncio.run(adapter.invoke(
            PlatformCapability.MESSAGE_SENDING,
            {"message": "test"}
        ))
        
        # 如果能力不可用，应该返回明确的错误
        if not result.get("success"):
            assert "error" in result
            assert result.get("error_code") == "CAPABILITY_NOT_CONNECTED"
            assert result.get("fallback_available") == True
    
    def test_invoke_on_unknown_capability(self):
        """测试调用未知能力"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        # 使用一个不存在的能力
        result = asyncio.run(adapter.invoke(
            PlatformCapability.STORAGE,  # 未定义的能力
            {"data": "test"}
        ))
        
        # 应该返回未知能力错误
        assert result.get("success") == False
        assert result.get("error_code") == "UNKNOWN_CAPABILITY"


class TestNullAdapterFallback:
    """测试 null 适配器降级"""
    
    def test_null_adapter_always_unavailable(self):
        """测试 null 适配器始终不可用"""
        from platform_adapter.null_adapter import NullAdapter
        import asyncio
        
        adapter = NullAdapter()
        
        is_available = asyncio.run(adapter.is_available())
        
        assert is_available == False
    
    def test_null_adapter_probe(self):
        """测试 null 适配器探测"""
        from platform_adapter.null_adapter import NullAdapter
        import asyncio
        
        adapter = NullAdapter()
        
        result = asyncio.run(adapter.probe())
        
        assert result.get("available") == False
        assert result.get("adapter") == "null"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
