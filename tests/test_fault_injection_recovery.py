"""
Test Fault Injection Recovery - 测试故障注入恢复

验证：
1. contact/calendar/note timeout 都能自动恢复
2. 恢复记录写入 recovery_history
3. 恢复记录写入 audit
"""

import pytest
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.run_fault_injection_tests import FaultInjector
from infrastructure.connected_runtime_recovery_policy import FailureType


class TestFaultInjectionRecovery:
    """故障注入恢复测试"""
    
    @pytest.fixture
    def injector(self):
        """创建故障注入器"""
        return FaultInjector()
    
    @pytest.mark.asyncio
    async def test_contact_service_timeout_recovery(self, injector):
        """测试联系人服务超时恢复"""
        scenario = {
            "name": "contact_service_timeout",
            "failure_type": FailureType.CONTACT_SERVICE_TIMEOUT,
            "capability": "query_contact",
            "route_id": "route.query_contact",
            "simulate_timeout_ms": 5000,
            "expected_recovery": ["retry", "limited_scope_probe", "cache_fallback"]
        }
        
        result = await injector.inject_fault(scenario)
        
        # 验证恢复结果
        assert result.failure_type == "contact_service_timeout"
        assert result.final_result in ["recovered", "pending", "partial_recovered"]
        assert len(result.executed_steps) > 0
        
        # 验证恢复步骤包含预期策略
        strategies = [step["strategy"] for step in result.executed_steps]
        assert "retry" in strategies
    
    @pytest.mark.asyncio
    async def test_calendar_service_timeout_recovery(self, injector):
        """测试日历服务超时恢复"""
        scenario = {
            "name": "calendar_service_timeout",
            "failure_type": FailureType.CALENDAR_SERVICE_TIMEOUT,
            "capability": "query_calendar",
            "route_id": "route.query_calendar",
            "simulate_timeout_ms": 5000,
            "expected_recovery": ["retry", "limited_scope_probe", "pending_queue"]
        }
        
        result = await injector.inject_fault(scenario)
        
        assert result.failure_type == "calendar_service_timeout"
        assert len(result.executed_steps) > 0
    
    @pytest.mark.asyncio
    async def test_note_service_timeout_recovery(self, injector):
        """测试备忘录服务超时恢复"""
        scenario = {
            "name": "note_service_timeout",
            "failure_type": FailureType.NOTE_SERVICE_TIMEOUT,
            "capability": "query_note",
            "route_id": "route.query_note",
            "simulate_timeout_ms": 5000,
            "expected_recovery": ["retry", "limited_scope_probe", "cache_fallback"]
        }
        
        result = await injector.inject_fault(scenario)
        
        assert result.failure_type == "note_service_timeout"
        assert len(result.executed_steps) > 0
    
    @pytest.mark.asyncio
    async def test_recovery_history_written(self, injector):
        """测试恢复历史写入"""
        # 运行所有故障注入
        await injector.run_all_faults()
        
        # 验证恢复历史不为空
        assert len(injector.recovery_history) > 0
        
        # 验证每条记录都有必要字段
        for record in injector.recovery_history:
            assert "recovery_id" in record
            assert "failure_type" in record
            assert "strategy" in record
            assert "timestamp" in record
    
    @pytest.mark.asyncio
    async def test_audit_written(self, injector):
        """测试审计记录写入"""
        # 运行所有故障注入
        await injector.run_all_faults()
        
        # 验证审计记录不为空
        assert len(injector.audit_records) > 0
        
        # 验证每条审计记录都有必要字段
        for audit in injector.audit_records:
            assert "audit_id" in audit
            assert "event_type" in audit
            assert "failure_type" in audit
            assert "recovery_result" in audit
    
    @pytest.mark.asyncio
    async def test_recovery_attempts_not_zero(self, injector):
        """测试恢复尝试次数不为零"""
        await injector.run_all_faults()
        
        stats = injector.get_statistics()
        
        # 恢复尝试次数应该大于 0
        assert stats["total_recovery_attempts"] > 0
    
    @pytest.mark.asyncio
    async def test_fault_injection_matches_recovery_report(self, injector):
        """测试故障注入与恢复报告一致"""
        await injector.run_all_faults()
        
        stats = injector.get_statistics()
        
        # 故障数量应该等于结果数量
        assert stats["total_faults"] == len(injector.results)
        
        # 恢复尝试次数应该等于恢复历史长度
        assert stats["total_recovery_attempts"] == len(injector.recovery_history)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
