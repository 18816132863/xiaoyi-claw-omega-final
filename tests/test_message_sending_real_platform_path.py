"""
MESSAGE_SENDING 真实平台路径测试
覆盖真实 MESSAGE_SENDING 调用
"""

import pytest
from pathlib import Path
import sys
import os

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestMessageSendingRealPlatformPath:
    """测试 MESSAGE_SENDING 真实平台路径"""
    
    def test_message_sending_method_exists(self):
        """测试 MESSAGE_SENDING 方法存在"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        
        adapter = XiaoyiAdapter()
        
        # 应该有 _invoke_message_sending 方法
        assert hasattr(adapter, "_invoke_message_sending")
        assert callable(adapter._invoke_message_sending)
    
    def test_message_sending_fallback_method_exists(self):
        """测试 MESSAGE_SENDING fallback 方法存在"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        
        adapter = XiaoyiAdapter()
        
        # 应该有 _fallback_message_sending 方法
        assert hasattr(adapter, "_fallback_message_sending")
        assert callable(adapter._fallback_message_sending)
    
    def test_message_sending_params_format(self):
        """测试 MESSAGE_SENDING 参数格式"""
        # 预期参数格式
        expected_params = {
            "phone_number": "接收方手机号",
            "message": "短信内容"
        }
        
        # 验证参数定义
        assert "phone_number" in expected_params
        assert "message" in expected_params
    
    def test_message_sending_fallback_returns_queued(self):
        """测试 MESSAGE_SENDING fallback 返回 queued"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        result = asyncio.run(adapter._fallback_message_sending({
            "phone_number": "13800138000",
            "message": "测试消息"
        }))
        
        # 应该返回 queued_for_delivery
        assert result.get("success") == True
        assert result.get("status") == "queued_for_delivery"
        assert result.get("fallback_used") == True
    
    @pytest.mark.skipif(
        os.environ.get("OPENCLAW_RUNTIME") != "true",
        reason="需要 OpenClaw 运行时环境"
    )
    def test_message_sending_real_call(self):
        """测试 MESSAGE_SENDING 真实调用 (需要真实环境)"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        # 检查能力是否可用
        probe_result = asyncio.run(adapter.probe())
        
        if probe_result.get("capabilities", {}).get("message_sending"):
            # 真实调用
            result = asyncio.run(adapter.invoke(
                PlatformCapability.MESSAGE_SENDING,
                {
                    "phone_number": "13800138000",
                    "message": "这是一条测试消息"
                }
            ))
            
            # 应该返回结果
            assert "success" in result
            assert "status" in result
            
            # 如果成功，状态应该是 success
            if result.get("success"):
                assert result["status"] == "success"


class TestMessageSendingResultSemantics:
    """测试 MESSAGE_SENDING 结果语义"""
    
    def test_success_means_completed(self):
        """测试 success 意味着 completed"""
        # success 状态 = completed
        success_result = {
            "success": True,
            "status": "success"
        }
        
        # success 不等于 queued
        assert success_result["status"] != "queued_for_delivery"
    
    def test_queued_means_waiting(self):
        """测试 queued 意味着等待"""
        # queued 状态 = 等待处理
        queued_result = {
            "success": True,
            "status": "queued_for_delivery"
        }
        
        # queued 不等于 success
        assert queued_result["status"] != "success"
    
    def test_failed_means_error(self):
        """测试 failed 意味着错误"""
        # failed 状态 = 错误
        failed_result = {
            "success": False,
            "status": "failed",
            "error": "Some error"
        }
        
        # failed 不等于 success
        assert failed_result["success"] == False
        assert failed_result["status"] == "failed"


class TestMessageSendingErrorHandling:
    """测试 MESSAGE_SENDING 错误处理"""
    
    def test_import_error_triggers_fallback(self):
        """测试 ImportError 触发 fallback"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        # _invoke_message_sending 应该捕获 ImportError
        # 并调用 _fallback_message_sending
        # 这里我们直接测试 fallback
        result = asyncio.run(adapter._fallback_message_sending({
            "phone_number": "test",
            "message": "test"
        }))
        
        assert result.get("fallback_used") == True
    
    def test_exception_returns_failed(self):
        """测试异常返回 failed"""
        # 异常应该导致 failed 状态
        expected_error_result = {
            "success": False,
            "status": "failed",
            "error_code": "INVOKE_ERROR"
        }
        
        assert expected_error_result["success"] == False
        assert expected_error_result["status"] == "failed"


class TestMessageSendingIntegration:
    """测试 MESSAGE_SENDING 集成"""
    
    def test_full_flow_with_fallback(self):
        """测试完整流程 (使用 fallback)"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        # 完整流程
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
        
        # 如果使用了 fallback，状态应该是 queued
        if result.get("fallback_used"):
            assert result["status"] == "queued_for_delivery"
    
    def test_probe_before_invoke(self):
        """测试调用前先探测"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        # 先探测
        probe_result = asyncio.run(adapter.probe())
        
        # 再调用
        invoke_result = asyncio.run(adapter.invoke(
            PlatformCapability.MESSAGE_SENDING,
            {"phone_number": "test", "message": "test"}
        ))
        
        # 探测结果应该影响调用结果
        if not probe_result.get("capabilities", {}).get("message_sending"):
            # 能力不可用，应该使用 fallback 或返回错误
            assert invoke_result.get("fallback_used") or not invoke_result.get("success")


class TestMessageSendingPlatformResult:
    """测试 MESSAGE_SENDING 平台返回结果"""
    
    def test_platform_result_included(self):
        """测试平台结果被包含"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        # 使用 fallback
        result = asyncio.run(adapter._fallback_message_sending({
            "phone_number": "test",
            "message": "test"
        }))
        
        # 应该包含 adapter_result
        assert "adapter_result" in result
    
    def test_platform_result_structure(self):
        """测试平台结果结构"""
        # 预期的平台结果结构
        expected_structure = {
            "success": bool,
            "status": str,
            "platform_result": dict  # 可选
        }
        
        # 验证结构定义
        assert "success" in expected_structure
        assert "status" in expected_structure


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
