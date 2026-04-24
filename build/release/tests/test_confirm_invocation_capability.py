"""
测试手动确认能力
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestConfirmInvocationCapability:
    """测试手动确认能力"""
    
    def setup_method(self):
        """每个测试前设置临时数据库"""
        import platform_adapter.invocation_ledger as ledger_module
        
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = Path(self.temp_dir) / "test_tasks.db"
        ledger_module.DB_PATH = self.temp_db
    
    def teardown_method(self):
        """清理临时数据库"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_confirm_success(self):
        """测试确认成功"""
        from capabilities.confirm_invocation import ConfirmInvocation
        from platform_adapter.invocation_ledger import record_invocation, get_invocation_by_id
        
        # 记录
        record_id = record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        # 确认成功
        result = ConfirmInvocation.confirm_success(record_id, "用户确认短信已收到")
        
        assert result == True
        
        # 验证
        record = get_invocation_by_id(record_id)
        assert record["confirmed_status"] == "confirmed_success"
        assert record["confirm_note"] == "用户确认短信已收到"
    
    def test_confirm_failed(self):
        """测试确认失败"""
        from capabilities.confirm_invocation import ConfirmInvocation
        from platform_adapter.invocation_ledger import record_invocation, get_invocation_by_id
        
        record_id = record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        result = ConfirmInvocation.confirm_failed(record_id, "用户确认未收到")
        
        assert result == True
        
        record = get_invocation_by_id(record_id)
        assert record["confirmed_status"] == "confirmed_failed"
    
    def test_confirm_duplicate(self):
        """测试确认重复"""
        from capabilities.confirm_invocation import ConfirmInvocation
        from platform_adapter.invocation_ledger import record_invocation, get_invocation_by_id
        
        record_id = record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        result = ConfirmInvocation.confirm_duplicate(record_id, "与记录 #1 重复")
        
        assert result == True
        
        record = get_invocation_by_id(record_id)
        assert record["confirmed_status"] == "confirmed_duplicate"
    
    def test_get_confirmation_stats(self):
        """测试获取确认统计"""
        from capabilities.confirm_invocation import ConfirmInvocation
        from platform_adapter.invocation_ledger import record_invocation
        
        # 记录 uncertain
        record_id = record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        # 确认
        ConfirmInvocation.confirm_success(record_id)
        
        # 获取统计
        stats = ConfirmInvocation.get_confirmation_stats()
        
        assert "total" in stats
        assert "uncertain_count" in stats
        assert "confirmed_count" in stats
        assert "unconfirmed_count" in stats
        assert "confirmation_rate" in stats
    
    def test_convenience_functions(self):
        """测试便捷函数"""
        from capabilities.confirm_invocation import (
            confirm_success,
            confirm_failed,
            confirm_duplicate,
        )
        from platform_adapter.invocation_ledger import record_invocation, get_invocation_by_id
        
        # 测试 confirm_success
        record_id = record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        result = confirm_success(record_id, "test")
        assert result == True
        
        # 测试 confirm_failed
        record_id = record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        result = confirm_failed(record_id, "test")
        assert result == True
        
        # 测试 confirm_duplicate
        record_id = record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        result = confirm_duplicate(record_id, "test")
        assert result == True
