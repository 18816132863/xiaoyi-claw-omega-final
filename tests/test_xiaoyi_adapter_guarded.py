"""
测试 XiaoyiAdapter 使用统一防护层
"""

import pytest
import sys
import asyncio
from pathlib import Path

# 标记为设备运行时测试
pytestmark = pytest.mark.device_runtime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
from platform_adapter.base import PlatformCapability


class TestXiaoyiAdapterGuarded:
    """测试 XiaoyiAdapter 使用统一防护层"""
    
    @pytest.mark.asyncio
    async def test_adapter_initialization(self):
        """测试适配器初始化"""
        adapter = XiaoyiAdapter()
        await adapter._ensure_initialized()
        
        assert adapter._initialized == True
        assert adapter._device_connected == True
    
    @pytest.mark.asyncio
    async def test_probe_returns_device_connected_true(self):
        """测试 probe 返回 device_connected=true"""
        adapter = XiaoyiAdapter()
        result = await adapter.probe()
        
        assert result["device_connected"] == True
    
    @pytest.mark.asyncio
    async def test_invoke_returns_normalized_status(self):
        """测试 invoke 返回归一化状态"""
        adapter = XiaoyiAdapter()
        await adapter._ensure_initialized()
        
        # 即使 call_device_tool 不可用，也应该返回正确格式
        result = await adapter.invoke(
            PlatformCapability.MESSAGE_SENDING,
            {"phone_number": "13800138000", "message": "test"}
        )
        
        # 应该有 normalized_status 字段
        assert "status" in result
        assert result["status"] in [
            "completed",
            "failed",
            "timeout",
            "result_uncertain",
            "queued_for_delivery",
        ]
    
    @pytest.mark.asyncio
    async def test_invoke_includes_user_message(self):
        """测试 invoke 包含用户消息"""
        adapter = XiaoyiAdapter()
        await adapter._ensure_initialized()
        
        result = await adapter.invoke(
            PlatformCapability.MESSAGE_SENDING,
            {"phone_number": "13800138000", "message": "test"}
        )
        
        # 应该有 user_message 字段
        assert "user_message" in result
    
    @pytest.mark.asyncio
    async def test_invoke_includes_idempotency_key(self):
        """测试 invoke 包含幂等键"""
        adapter = XiaoyiAdapter()
        await adapter._ensure_initialized()
        
        result = await adapter.invoke(
            PlatformCapability.MESSAGE_SENDING,
            {"phone_number": "13800138000", "message": "test"}
        )
        
        # 如果能力可用，应该有 idempotency_key
        # 如果不可用，可能没有
        if result.get("status") not in ["failed"]:
            assert "idempotency_key" in result
    
    @pytest.mark.asyncio
    async def test_timeout_does_not_auto_retry_side_effecting(self):
        """测试超时不自动重试副作用操作"""
        adapter = XiaoyiAdapter()
        await adapter._ensure_initialized()
        
        # 模拟超时场景（通过不可用的能力）
        # 这里主要验证返回格式正确
        result = await adapter.invoke(
            PlatformCapability.MESSAGE_SENDING,
            {"phone_number": "13800138000", "message": "test"}
        )
        
        # 如果是超时，should_retry 应该是 False
        if result.get("status") == "timeout":
            assert result.get("should_retry") == False
    
    @pytest.mark.asyncio
    async def test_result_uncertain_flag(self):
        """测试结果不确定标志"""
        adapter = XiaoyiAdapter()
        await adapter._ensure_initialized()
        
        result = await adapter.invoke(
            PlatformCapability.MESSAGE_SENDING,
            {"phone_number": "13800138000", "message": "test"}
        )
        
        # 如果能力可用且有调用结果，检查 result_uncertain
        if result.get("status") not in ["failed"]:
            assert "result_uncertain" in result
            assert isinstance(result["result_uncertain"], bool)
    
    @pytest.mark.asyncio
    async def test_fallback_used_flag(self):
        """测试 fallback 使用标志"""
        adapter = XiaoyiAdapter()
        await adapter._ensure_initialized()
        
        result = await adapter.invoke(
            PlatformCapability.MESSAGE_SENDING,
            {"phone_number": "13800138000", "message": "test"}
        )
        
        # 如果能力可用且有调用结果，检查 fallback_used
        if result.get("status") not in ["failed"]:
            assert "fallback_used" in result
            assert isinstance(result["fallback_used"], bool)
    
    @pytest.mark.asyncio
    async def test_elapsed_ms_recorded(self):
        """测试耗时记录"""
        adapter = XiaoyiAdapter()
        await adapter._ensure_initialized()
        
        result = await adapter.invoke(
            PlatformCapability.MESSAGE_SENDING,
            {"phone_number": "13800138000", "message": "test"}
        )
        
        # 如果能力可用且有调用结果，检查 elapsed_ms
        if result.get("status") not in ["failed"]:
            assert "elapsed_ms" in result
            assert isinstance(result["elapsed_ms"], int)
