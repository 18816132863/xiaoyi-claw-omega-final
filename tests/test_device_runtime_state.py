"""
Test Device Runtime State - 测试设备运行时状态

验证：
1. 小艺 Claw 连接端默认 session_connected = true
2. 单个能力 timeout 不判设备断开
3. 状态拆分为 5 个独立维度
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.device_runtime_state import (
    DeviceRuntimeState,
    DeviceRuntimeStateChecker,
    SessionState,
    BridgeState,
    PermissionState,
    CapabilityState,
    ActionState
)


class TestDeviceRuntimeState:
    """设备运行时状态测试"""
    
    def test_xiaoyi_channel_session_connected_by_default(self):
        """测试小艺连接端默认会话已连接"""
        checker = DeviceRuntimeStateChecker(is_xiaoyi_channel=True)
        
        assert checker.is_xiaoyi_channel == True
        assert checker.state.session_connected == SessionState.UNKNOWN  # 初始状态
        
        # 执行检查后应该是 CONNECTED
        import asyncio
        state = asyncio.run(checker.full_check())
        
        assert state.session_connected == SessionState.CONNECTED
        assert state.is_xiaoyi_channel == True
    
    def test_single_capability_timeout_not_device_disconnect(self):
        """测试单个能力 timeout 不判设备断开"""
        checker = DeviceRuntimeStateChecker(is_xiaoyi_channel=True)
        
        import asyncio
        state = asyncio.run(checker.full_check())
        
        # 模拟单个能力 timeout
        from infrastructure.device_runtime_state import CapabilityCheckResult
        from datetime import datetime
        
        state.capabilities["contact_service"] = CapabilityCheckResult(
            capability_name="contact_service",
            state=CapabilityState.TIMEOUT,
            last_check_time=datetime.now(),
            error_message="timeout after 5000ms"
        )
        
        # 会话仍然应该是 CONNECTED
        assert state.session_connected == SessionState.CONNECTED
        
        # 获取摘要，不应该出现 "no real device"
        summary = state.get_summary()
        assert "no real device" not in summary.lower()
        assert "session_connected=true" in summary
    
    def test_state_split_into_five_dimensions(self):
        """测试状态拆分为 5 个独立维度"""
        checker = DeviceRuntimeStateChecker(is_xiaoyi_channel=True)
        
        import asyncio
        state = asyncio.run(checker.full_check())
        
        # 验证 5 个维度都存在
        assert hasattr(state, "session_connected")
        assert hasattr(state, "runtime_bridge_ready")
        assert hasattr(state, "permissions")
        assert hasattr(state, "capabilities")
        assert hasattr(state, "action_ready")
        
        # 验证权限和能力是字典
        assert isinstance(state.permissions, dict)
        assert isinstance(state.capabilities, dict)
    
    def test_get_failure_breakdown(self):
        """测试失败明细"""
        checker = DeviceRuntimeStateChecker(is_xiaoyi_channel=True)
        
        import asyncio
        state = asyncio.run(checker.full_check())
        
        # 模拟一些失败
        from infrastructure.device_runtime_state import (
            PermissionCheckResult,
            CapabilityCheckResult
        )
        from datetime import datetime
        
        state.permissions["contact"] = PermissionCheckResult(
            permission_name="contact",
            state=PermissionState.DENIED,
            last_check_time=datetime.now()
        )
        
        state.capabilities["calendar_service"] = CapabilityCheckResult(
            capability_name="calendar_service",
            state=CapabilityState.TIMEOUT,
            last_check_time=datetime.now(),
            error_message="timeout"
        )
        
        breakdown = checker.get_failure_breakdown()
        
        # 验证失败分类
        assert "permission_issues" in breakdown
        assert "capability_timeouts" in breakdown
        assert any("contact_denied" in issue for issue in breakdown["permission_issues"])
        assert any("calendar_service_timeout" in issue for issue in breakdown["capability_timeouts"])
    
    def test_is_partial_ready(self):
        """测试部分就绪判断"""
        checker = DeviceRuntimeStateChecker(is_xiaoyi_channel=True)
        
        import asyncio
        state = asyncio.run(checker.full_check())
        
        # 小艺连接端，会话连接就算部分就绪
        assert checker.is_partial_ready() == True
    
    def test_to_dict(self):
        """测试转换为字典"""
        checker = DeviceRuntimeStateChecker(is_xiaoyi_channel=True)
        
        import asyncio
        state = asyncio.run(checker.full_check())
        
        result = state.to_dict()
        
        # 验证字典结构
        assert "session_connected" in result
        assert "runtime_bridge_ready" in result
        assert "permissions" in result
        assert "capabilities" in result
        assert "action_ready" in result
        assert "is_xiaoyi_channel" in result


class TestNoFalseNoRealDevice:
    """测试不再误报 no real device"""
    
    def test_timeout_not_reported_as_no_real_device(self):
        """测试 timeout 不报告为 no real device"""
        checker = DeviceRuntimeStateChecker(is_xiaoyi_channel=True)
        
        import asyncio
        state = asyncio.run(checker.full_check())
        
        # 模拟多个能力 timeout
        from infrastructure.device_runtime_state import CapabilityCheckResult
        from datetime import datetime
        
        for cap in ["contact_service", "calendar_service", "note_service"]:
            state.capabilities[cap] = CapabilityCheckResult(
                capability_name=cap,
                state=CapabilityState.TIMEOUT,
                last_check_time=datetime.now(),
                error_message="timeout"
            )
        
        summary = state.get_summary()
        
        # 不应该出现 no real device
        assert "no real device" not in summary.lower()
        assert "unavailable" not in summary.lower() or "partial" in summary.lower()
    
    def test_adapter_loaded_false_not_device_disconnect(self):
        """测试 adapter_loaded=false 不判设备断开"""
        checker = DeviceRuntimeStateChecker(is_xiaoyi_channel=True)
        
        import asyncio
        state = asyncio.run(checker.full_check())
        
        # 即使 bridge 是 ERROR，会话仍然可能是 CONNECTED
        state.runtime_bridge_ready = BridgeState.ERROR
        
        # 小艺连接端会话仍然连接
        assert state.session_connected == SessionState.CONNECTED


class TestServiceTimeoutNotSessionDisconnect:
    """测试服务超时不等于会话断开"""
    
    def test_contact_timeout_keeps_session_connected(self):
        """测试联系人超时保持会话连接"""
        checker = DeviceRuntimeStateChecker(is_xiaoyi_channel=True)
        
        import asyncio
        state = asyncio.run(checker.full_check())
        
        from infrastructure.device_runtime_state import CapabilityCheckResult
        from datetime import datetime
        
        state.capabilities["contact_service"] = CapabilityCheckResult(
            capability_name="contact_service",
            state=CapabilityState.TIMEOUT,
            last_check_time=datetime.now(),
            error_message="contact_service_timeout"
        )
        
        # 会话仍然连接
        assert state.session_connected == SessionState.CONNECTED
        assert state.capabilities["contact_service"].state == CapabilityState.TIMEOUT
    
    def test_multiple_timeouts_keeps_session_connected(self):
        """测试多个超时保持会话连接"""
        checker = DeviceRuntimeStateChecker(is_xiaoyi_channel=True)
        
        import asyncio
        state = asyncio.run(checker.full_check())
        
        from infrastructure.device_runtime_state import CapabilityCheckResult
        from datetime import datetime
        
        # 模拟多个超时
        for cap in ["contact_service", "calendar_service", "note_service", "location_service"]:
            state.capabilities[cap] = CapabilityCheckResult(
                capability_name=cap,
                state=CapabilityState.TIMEOUT,
                last_check_time=datetime.now(),
                error_message=f"{cap}_timeout"
            )
        
        # 会话仍然连接
        assert state.session_connected == SessionState.CONNECTED
        
        # 状态应该是 partial
        summary = state.get_summary()
        assert "partial" in summary.lower() or "connected" in summary.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
