"""
测试 NOTIFICATION 授权和确认语义
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
from platform_adapter.base import PlatformCapability
from platform_adapter.result_normalizer import NormalizedStatus


class TestNotificationAuthAndConfirmation:
    """测试 NOTIFICATION 授权和确认"""
    
    @pytest.mark.asyncio
    async def test_notification_capability_exists(self):
        """测试 NOTIFICATION 能力存在"""
        adapter = XiaoyiAdapter()
        await adapter._ensure_initialized()
        
        cap = await adapter.get_capability(PlatformCapability.NOTIFICATION)
        assert cap is not None
    
    @pytest.mark.asyncio
    async def test_notification_available_when_configured(self):
        """测试 NOTIFICATION 配置后可用"""
        adapter = XiaoyiAdapter()
        await adapter._ensure_initialized()
        
        cap = await adapter.get_capability(PlatformCapability.NOTIFICATION)
        # authCode 已配置，应该可用
        assert cap.available == True
    
    @pytest.mark.asyncio
    async def test_notification_invoke_returns_status(self):
        """测试 NOTIFICATION 调用返回状态"""
        adapter = XiaoyiAdapter()
        await adapter._ensure_initialized()
        
        # NOTIFICATION 应该可用
        result = await adapter.invoke(
            PlatformCapability.NOTIFICATION,
            {"title": "测试", "content": "测试内容", "result": "完成"}
        )
        
        assert "status" in result
        # 状态可能是 completed, failed, timeout, result_uncertain
        assert result["status"] in [
            NormalizedStatus.COMPLETED,
            NormalizedStatus.FAILED,
            NormalizedStatus.TIMEOUT,
            NormalizedStatus.RESULT_UNCERTAIN,
            NormalizedStatus.AUTH_REQUIRED,
        ]
    
    @pytest.mark.asyncio
    async def test_notification_success_is_interface_level(self):
        """测试 NOTIFICATION 成功是接口级别"""
        adapter = XiaoyiAdapter()
        await adapter._ensure_initialized()
        
        result = await adapter.invoke(
            PlatformCapability.NOTIFICATION,
            {"title": "测试", "content": "测试内容", "result": "完成"}
        )
        
        # 如果成功，应该是接口接收成功
        # 不应该直接说"用户已看到"
        if result.get("status") == NormalizedStatus.COMPLETED:
            # 检查 user_message 不应该说"用户已看到"
            user_msg = result.get("user_message", "")
            assert "用户已看到" not in user_msg
            assert "已看到" not in user_msg
    
    @pytest.mark.asyncio
    async def test_notification_timeout_is_uncertain(self):
        """测试 NOTIFICATION 超时是不确定"""
        adapter = XiaoyiAdapter()
        await adapter._ensure_initialized()
        
        result = await adapter.invoke(
            PlatformCapability.NOTIFICATION,
            {"title": "测试", "content": "测试内容", "result": "完成"}
        )
        
        # 如果超时，应该是 result_uncertain
        if result.get("status") == NormalizedStatus.TIMEOUT:
            assert result.get("result_uncertain") == True
            assert result.get("should_retry") == False
    
    @pytest.mark.asyncio
    async def test_notification_has_idempotency_key(self):
        """测试 NOTIFICATION 有幂等键"""
        adapter = XiaoyiAdapter()
        await adapter._ensure_initialized()
        
        result = await adapter.invoke(
            PlatformCapability.NOTIFICATION,
            {"title": "测试", "content": "测试内容", "result": "完成"}
        )
        
        # 应该有 idempotency_key
        assert "idempotency_key" in result


class TestNotificationAuthCodeHandling:
    """测试 authCode 处理"""
    
    def test_auth_code_not_in_logs(self):
        """测试 authCode 不出现在日志中"""
        # 检查适配器描述不应包含完整 authCode
        adapter = XiaoyiAdapter()
        
        # 描述中不应该有完整 authCode
        cap = adapter._capabilities.get(PlatformCapability.NOTIFICATION)
        if cap:
            assert "8I5Rqg0anHkU" not in cap.description
    
    @pytest.mark.asyncio
    async def test_auth_error_returns_auth_required(self):
        """测试授权错误返回 AUTH_REQUIRED"""
        from platform_adapter.result_normalizer import normalize_result
        
        # 模拟授权错误
        result = normalize_result(
            {"code": "0000900034", "desc": "The authCode is invalid"},
            "NOTIFICATION",
            "push"
        )
        
        assert result.status == NormalizedStatus.AUTH_REQUIRED
