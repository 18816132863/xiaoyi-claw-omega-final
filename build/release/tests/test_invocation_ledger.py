"""
测试平台调用审计台账
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestInvocationLedger:
    """测试审计台账"""
    
    def setup_method(self):
        """每个测试前设置临时数据库"""
        import platform_adapter.invocation_ledger as ledger_module
        
        # 使用临时数据库
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = Path(self.temp_dir) / "test_tasks.db"
        ledger_module.DB_PATH = self.temp_db
    
    def teardown_method(self):
        """清理临时数据库"""
        import shutil
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_record_invocation(self):
        """测试记录调用"""
        from platform_adapter.invocation_ledger import record_invocation
        
        record_id = record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="completed",
            task_id="test_task_1",
            idempotency_key="key1",
            side_effecting=True,
            request_json={"phone": "13800138000"},
            raw_result_json={"code": 0},
            elapsed_ms=100,
        )
        
        assert record_id > 0
    
    def test_query_invocations(self):
        """测试查询调用"""
        from platform_adapter.invocation_ledger import record_invocation, query_invocations
        
        # 记录几条
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="completed",
        )
        
        record_invocation(
            capability="TASK_SCHEDULING",
            platform_op="create_calendar_event",
            normalized_status="timeout",
        )
        
        # 查询
        results = query_invocations(limit=10)
        assert len(results) >= 2
        
        # 按能力查询
        msg_results = query_invocations(capability="MESSAGE_SENDING")
        assert len(msg_results) >= 1
        
        # 按状态查询
        timeout_results = query_invocations(normalized_status="timeout")
        assert len(timeout_results) >= 1
    
    def test_get_by_idempotency_key(self):
        """测试按幂等键查询"""
        from platform_adapter.invocation_ledger import (
            record_invocation,
            get_invocation_by_idempotency_key,
        )
        
        key = f"test_key_{datetime.now().timestamp()}"
        
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="completed",
            idempotency_key=key,
        )
        
        result = get_invocation_by_idempotency_key(key)
        assert result is not None
        assert result["idempotency_key"] == key
    
    def test_result_uncertain_flag(self):
        """测试结果不确定标志"""
        from platform_adapter.invocation_ledger import record_invocation, query_invocations
        
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="timeout",
            result_uncertain=True,
        )
        
        results = query_invocations(normalized_status="timeout")
        assert len(results) >= 1
        assert results[0]["result_uncertain"] == 1
    
    def test_fallback_used_flag(self):
        """测试 fallback 使用标志"""
        from platform_adapter.invocation_ledger import record_invocation, query_invocations
        
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status="queued_for_delivery",
            fallback_used=True,
        )
        
        results = query_invocations(normalized_status="queued_for_delivery")
        assert len(results) >= 1
        assert results[0]["fallback_used"] == 1
