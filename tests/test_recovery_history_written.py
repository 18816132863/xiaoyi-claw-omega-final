"""
Test Recovery History Written - 测试恢复历史写入

验证恢复历史正确写入文件
"""

import pytest
import sys
import os
import json
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.run_fault_injection_tests import FaultInjector
from infrastructure.connected_runtime_recovery_policy import FailureType


class TestRecoveryHistoryWritten:
    """恢复历史写入测试"""
    
    @pytest.fixture
    def injector(self):
        return FaultInjector()
    
    @pytest.mark.asyncio
    async def test_recovery_history_has_required_fields(self, injector):
        """测试恢复历史有必要字段"""
        await injector.run_all_faults()
        
        for record in injector.recovery_history:
            assert "recovery_id" in record
            assert "failure_type" in record
            assert "capability" in record
            assert "route_id" in record
            assert "strategy" in record
            assert "timestamp" in record
            assert "audit_id" in record
    
    @pytest.mark.asyncio
    async def test_recovery_history_count_matches_results(self, injector):
        """测试恢复历史数量匹配结果"""
        await injector.run_all_faults()
        
        # 每个故障注入应该有多条恢复历史
        assert len(injector.recovery_history) >= len(injector.results)


class TestRecoveryAuditWritten:
    """恢复审计写入测试"""
    
    @pytest.fixture
    def injector(self):
        return FaultInjector()
    
    @pytest.mark.asyncio
    async def test_audit_has_required_fields(self, injector):
        """测试审计有必要字段"""
        await injector.run_all_faults()
        
        for audit in injector.audit_records:
            assert "audit_id" in audit
            assert "event_type" in audit
            assert "timestamp" in audit
    
    @pytest.mark.asyncio
    async def test_audit_count_matches_results(self, injector):
        """测试审计数量匹配结果"""
        await injector.run_all_faults()
        
        # 每个故障注入应该有一条审计记录
        assert len(injector.audit_records) == len(injector.results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
