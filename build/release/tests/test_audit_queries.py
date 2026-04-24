"""
测试审计查询功能
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestAuditQueries:
    """测试审计查询"""
    
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
    
    def test_query_by_task_id(self):
        """测试按 task_id 查询"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            query_by_task_id,
        )
        
        # 记录几条
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="completed",
            task_id="task_001",
        )
        
        record_invocation(
            capability="TASK_SCHEDULING",
            platform_op="create_calendar_event",
            normalized_status="completed",
            task_id="task_001",
        )
        
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="completed",
            task_id="task_002",
        )
        
        # 按 task_id 查询
        results = query_by_task_id("task_001")
        assert len(results) == 2
        
        results = query_by_task_id("task_002")
        assert len(results) == 1
    
    def test_query_by_capability(self):
        """测试按 capability 查询"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            query_by_capability,
        )
        
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="completed",
        )
        
        record_invocation(
            capability="TASK_SCHEDULING",
            platform_op="create_calendar_event",
            normalized_status="completed",
        )
        
        results = query_by_capability("MESSAGE_SENDING")
        assert len(results) >= 1
        assert all(r["capability"] == "MESSAGE_SENDING" for r in results)
    
    def test_query_by_status(self):
        """测试按状态查询"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            query_by_status,
        )
        
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="completed",
        )
        
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        results = query_by_status("timeout")
        assert len(results) >= 1
        assert all(r["normalized_status"] == "timeout" for r in results)
    
    def test_export_recent(self):
        """测试导出最近记录"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            export_recent,
        )
        
        # 记录多条
        for i in range(10):
            record_invocation(
                capability="MESSAGE_SENDING",
                platform_op="send_message",
                normalized_status="completed",
            )
        
        # 导出最近 5 条
        results = export_recent(5)
        assert len(results) == 5
    
    def test_export_failed_report(self):
        """测试导出 failed 报告"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            export_failed_report,
        )
        
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="failed",
            error_code="PLATFORM_EXECUTION_FAILED",
        )
        
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="completed",
        )
        
        results = export_failed_report()
        assert len(results) >= 1
        assert all(r["normalized_status"] == "failed" for r in results)
    
    def test_export_timeout_report(self):
        """测试导出 timeout 报告"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            export_timeout_report,
        )
        
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        results = export_timeout_report()
        assert len(results) >= 1
        assert all(r["normalized_status"] == "timeout" for r in results)
    
    def test_export_uncertain_report(self):
        """测试导出 uncertain 报告"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            export_uncertain_report,
        )
        
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="completed",
            result_uncertain=False,
        )
        
        results = export_uncertain_report()
        assert len(results) >= 1
        assert all(r["result_uncertain"] == 1 for r in results)
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            get_statistics,
        )
        
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="completed",
        )
        
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        stats = get_statistics()
        assert "total" in stats
        assert "by_status" in stats
        assert "uncertain_count" in stats
        assert stats["total"] >= 2
