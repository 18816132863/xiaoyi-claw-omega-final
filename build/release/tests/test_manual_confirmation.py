"""
测试人工确认链路
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestManualConfirmation:
    """测试人工确认"""
    
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
        from platform_adapter.invocation_ledger import (
            record_invocation,
            confirm_invocation,
            get_invocation_by_id,
        )
        
        # 记录一条 uncertain
        record_id = record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        # 确认成功
        result = confirm_invocation(
            record_id=record_id,
            confirmed_status="confirmed_success",
            confirm_note="用户确认短信已收到",
        )
        
        assert result == True
        
        # 验证确认结果
        record = get_invocation_by_id(record_id)
        assert record["confirmed_status"] == "confirmed_success"
        assert record["confirm_note"] == "用户确认短信已收到"
        assert record["confirmed_at"] is not None
    
    def test_confirm_failed(self):
        """测试确认失败"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            confirm_invocation,
            get_invocation_by_id,
        )
        
        record_id = record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        result = confirm_invocation(
            record_id=record_id,
            confirmed_status="confirmed_failed",
            confirm_note="用户确认未收到短信",
        )
        
        assert result == True
        
        record = get_invocation_by_id(record_id)
        assert record["confirmed_status"] == "confirmed_failed"
    
    def test_confirm_duplicate(self):
        """测试确认重复"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            confirm_invocation,
            get_invocation_by_id,
        )
        
        record_id = record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        result = confirm_invocation(
            record_id=record_id,
            confirmed_status="confirmed_duplicate",
            confirm_note="与记录 #1 重复",
        )
        
        assert result == True
        
        record = get_invocation_by_id(record_id)
        assert record["confirmed_status"] == "confirmed_duplicate"
    
    def test_confirm_nonexistent_record(self):
        """测试确认不存在的记录"""
        from platform_adapter.invocation_ledger import confirm_invocation
        
        result = confirm_invocation(
            record_id=99999,
            confirmed_status="confirmed_success",
            confirm_note="test",
        )
        
        assert result == False
    
    def test_confirmation_updates_statistics(self):
        """测试确认后统计更新"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            confirm_invocation,
            get_statistics,
        )
        
        # 记录 uncertain
        record_id = record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        # 确认前
        stats_before = get_statistics()
        confirmed_before = stats_before["confirmed_count"]
        
        # 确认
        confirm_invocation(
            record_id=record_id,
            confirmed_status="confirmed_success",
            confirm_note="test",
        )
        
        # 确认后
        stats_after = get_statistics()
        assert stats_after["confirmed_count"] == confirmed_before + 1


class TestConfirmationWorkflow:
    """测试确认工作流"""
    
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
    
    def test_full_confirmation_workflow(self):
        """测试完整确认工作流"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            export_uncertain_report,
            confirm_invocation,
            get_statistics,
        )
        
        # 1. 记录 uncertain
        record_id = record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        # 2. 查询 uncertain 记录
        uncertain_records = export_uncertain_report()
        assert len(uncertain_records) >= 1
        
        # 3. 人工确认
        confirm_invocation(
            record_id=record_id,
            confirmed_status="confirmed_success",
            confirm_note="用户确认短信已收到",
        )
        
        # 4. 验证统计
        stats = get_statistics()
        assert stats["confirmed_count"] >= 1
    
    def test_batch_confirmation(self):
        """测试批量确认"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            confirm_invocation,
            export_uncertain_report,
        )
        
        # 记录多条 uncertain
        record_ids = []
        for i in range(5):
            record_id = record_invocation(
                capability="MESSAGE_SENDING",
                platform_op="send_message",
                normalized_status="timeout",
                result_uncertain=True,
            )
            record_ids.append(record_id)
        
        # 批量确认
        for record_id in record_ids:
            confirm_invocation(
                record_id=record_id,
                confirmed_status="confirmed_success",
                confirm_note=f"批量确认 #{record_id}",
            )
        
        # 验证
        stats = confirm_invocation.__module__
        # 所有记录已确认
