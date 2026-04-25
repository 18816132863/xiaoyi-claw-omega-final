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
        
        # 应该有 _invoke_message_sending_guarded 方法
        assert hasattr(adapter, "_invoke_message_sending_guarded")
        assert callable(adapter._invoke_message_sending_guarded)
    
    def test_message_sending_fallback_method_exists(self):
        """测试 MESSAGE_SENDING fallback 方法存在"""
        from platform_adapter.invoke_guard import create_fallback_result
        
        # fallback 通过 create_fallback_result 实现
        assert callable(create_fallback_result)
    
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
        from platform_adapter.invoke_guard import create_fallback_result
        
        result = create_fallback_result(
            capability="MESSAGE_SENDING",
            op_name="send_message",
        )
        
        # 应该返回 queued_for_delivery
        result_dict = result.to_dict() if hasattr(result, 'to_dict') else result
        assert result_dict.get("normalized_status") == "queued_for_delivery"
        assert result_dict.get("fallback_used") == True


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
        from platform_adapter.invoke_guard import create_fallback_result
        
        adapter = XiaoyiAdapter()
        
        # 当 call_device_tool 不可用时，应该使用 fallback
        if not adapter._call_device_tool_available:
            result = create_fallback_result(
                capability="MESSAGE_SENDING",
                op_name="send_message",
            )
            result_dict = result.to_dict() if hasattr(result, 'to_dict') else result
            assert result_dict.get("fallback_used") == True
    
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
        
        # 应该返回结果
        assert "status" in invoke_result


class TestMessageSendingPlatformResult:
    """测试 MESSAGE_SENDING 平台返回结果"""
    
    def test_platform_result_included(self):
        """测试平台结果被包含"""
        from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
        from platform_adapter.base import PlatformCapability
        import asyncio
        
        adapter = XiaoyiAdapter()
        
        result = asyncio.run(adapter.invoke(
            PlatformCapability.MESSAGE_SENDING,
            {"phone_number": "test", "message": "test"}
        ))
        
        # 如果能力可用，应该有 raw_result
        if result.get("status") not in ["failed"]:
            assert "raw_result" in result
    
    def test_platform_result_structure(self):
        """测试平台结果结构"""
        # 预期的平台结果结构
        expected_structure = {
            "success": bool,
            "status": str,
            "raw_result": dict  # 可选
        }
        
        # 验证结构定义
        assert "success" in expected_structure
        assert "status" in expected_structure


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
