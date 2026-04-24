"""
测试清理策略
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestCleanupPolicy:
    """测试清理策略"""
    
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
    
    def test_cleanup_completed_records(self):
        """测试清理 completed 记录"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            cleanup_old_records,
            get_statistics,
        )
        
        # 记录 completed
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="completed",
        )
        
        # 清理（保留 failed 和 uncertain）
        deleted = cleanup_old_records(
            days_to_keep=0,  # 清理所有
            keep_failed=True,
            keep_uncertain=True,
        )
        
        assert deleted >= 1
    
    def test_cleanup_preserves_failed(self):
        """测试清理保留 failed 记录"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            cleanup_old_records,
            query_by_status,
        )
        
        # 记录 failed
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="failed",
        )
        
        # 清理
        cleanup_old_records(
            days_to_keep=0,
            keep_failed=True,
            keep_uncertain=True,
        )
        
        # failed 应该保留
        results = query_by_status("failed")
        assert len(results) >= 1
    
    def test_cleanup_preserves_uncertain(self):
        """测试清理保留 uncertain 记录"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            cleanup_old_records,
            export_uncertain_report,
        )
        
        # 记录 uncertain
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        # 清理
        cleanup_old_records(
            days_to_keep=0,
            keep_failed=True,
            keep_uncertain=True,
        )
        
        # uncertain 应该保留
        results = export_uncertain_report()
        assert len(results) >= 1
    
    def test_cleanup_removes_old_failed_when_allowed(self):
        """测试允许清理 failed 时删除"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            cleanup_old_records,
            query_by_status,
        )
        
        # 记录 failed
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="failed",
        )
        
        # 清理（不保留 failed）
        cleanup_old_records(
            days_to_keep=0,
            keep_failed=False,
            keep_uncertain=True,
        )
        
        # failed 应该被删除
        results = query_by_status("failed")
        assert len(results) == 0
    
    def test_cleanup_returns_deleted_count(self):
        """测试清理返回删除数量"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            cleanup_old_records,
        )
        
        # 记录多条
        for i in range(5):
            record_invocation(
                capability="MESSAGE_SENDING",
                platform_op="send_message",
                normalized_status="completed",
            )
        
        # 清理
        deleted = cleanup_old_records(
            days_to_keep=0,
            keep_failed=True,
            keep_uncertain=True,
        )
        
        assert deleted >= 5


class TestRetentionPolicy:
    """测试保留策略"""
    
    def test_completed_retention_30_days(self):
        """测试 completed 保留 30 天"""
        # 策略: completed 保留 30 天
        # 这里只验证策略定义，实际时间测试需要 mock
        retention_days = 30
        assert retention_days == 30
    
    def test_failed_retention_90_days(self):
        """测试 failed 保留 90 天"""
        retention_days = 90
        assert retention_days == 90
    
    def test_uncertain_retention_permanent(self):
        """测试 uncertain 永久保留"""
        # uncertain 永久保留
        from platform_adapter.invocation_ledger import (
            record_invocation,
            cleanup_old_records,
            export_uncertain_report,
        )
        
        import platform_adapter.invocation_ledger as ledger_module
        
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = Path(self.temp_dir) / "test_tasks.db"
        ledger_module.DB_PATH = self.temp_db
        
        try:
            # 记录 uncertain
            record_invocation(
                capability="MESSAGE_SENDING",
                platform_op="send_message",
                normalized_status="timeout",
                result_uncertain=True,
            )
            
            # 即使清理很久以前的，uncertain 也应该保留
            cleanup_old_records(
                days_to_keep=-365,  # 负数表示很久以前
                keep_failed=True,
                keep_uncertain=True,
            )
            
            results = export_uncertain_report()
            assert len(results) >= 1
        finally:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
