"""
Test L0 Auto Downgrade Triggered - 测试 L0 自动降级触发

验证：
1. success_rate < 80% 触发降级
2. 降级链正确执行
3. 恢复历史记录降级事件
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.simulate_l0_auto_recovery import L0AutoRecoverySimulator
from infrastructure.connected_runtime_recovery_policy import ProbeMode


class TestL0AutoDowngradeTriggered:
    """L0 自动降级触发测试"""
    
    def test_success_rate_below_80_triggers_downgrade(self):
        """测试成功率低于 80% 触发降级"""
        simulator = L0AutoRecoverySimulator()
        simulator.simulate_probes()
        
        stats = simulator.get_statistics()
        
        # 成功率应该是 70%
        assert stats["success_rate"] == 0.7
        
        # 应该触发降级
        assert stats["downgrade_triggered"] == True
    
    def test_downgrade_chain_correct(self):
        """测试降级链正确"""
        simulator = L0AutoRecoverySimulator()
        simulator.simulate_probes()
        
        # 验证降级事件
        assert len(simulator.downgrade_events) > 0
        
        event = simulator.downgrade_events[0]
        
        # 从 normal_probe 降级
        assert event.before_mode == "normal_probe"
        
        # 降级后的模式应该在降级链中
        assert event.after_mode in [
            "fast_probe",
            "limited_scope_probe",
            "cache_fallback",
            "permission_diagnosis"
        ]
    
    def test_recovery_history_records_downgrade(self):
        """测试恢复历史记录降级"""
        simulator = L0AutoRecoverySimulator()
        simulator.simulate_probes()
        
        # 恢复历史应该有记录
        assert len(simulator.recovery_history) > 0
        
        # 验证降级记录
        record = simulator.recovery_history[0]
        assert "before_mode" in record
        assert "after_mode" in record
        assert "success_rate" in record
        assert record["success_rate"] < 0.8
    
    def test_simulated_probes_count(self):
        """测试模拟探测数量"""
        simulator = L0AutoRecoverySimulator()
        simulator.simulate_probes()
        
        # 应该有 10 次探测
        assert len(simulator.probe_results) == 10
    
    def test_success_failure_counts(self):
        """测试成功失败计数"""
        simulator = L0AutoRecoverySimulator()
        simulator.simulate_probes()
        
        stats = simulator.get_statistics()
        
        # 7 成功，3 失败
        assert stats["success_count"] == 7
        assert stats["failure_count"] == 3


class TestL0DowngradeChain:
    """L0 降级链测试"""
    
    def test_downgrade_from_normal_to_fast(self):
        """测试从 normal_probe 降级到 fast_probe"""
        from infrastructure.connected_runtime_recovery_policy import L0AutoAdjustment
        
        adjustment = L0AutoAdjustment()
        adjustment.current_mode = ProbeMode.NORMAL_PROBE
        
        # 模拟低成功率
        for _ in range(5):
            adjustment.record_result(False)
        
        assert adjustment.should_downgrade() == True
        
        new_mode = adjustment.downgrade()
        assert new_mode == ProbeMode.FAST_PROBE
    
    def test_downgrade_chain_continues(self):
        """测试降级链继续"""
        from infrastructure.connected_runtime_recovery_policy import L0AutoAdjustment
        
        adjustment = L0AutoAdjustment()
        adjustment.current_mode = ProbeMode.FAST_PROBE
        
        # 模拟低成功率
        for _ in range(5):
            adjustment.record_result(False)
        
        new_mode = adjustment.downgrade()
        assert new_mode == ProbeMode.LIMITED_SCOPE_PROBE
    
    def test_downgrade_stops_at_permission_diagnosis(self):
        """测试降级停在 permission_diagnosis"""
        from infrastructure.connected_runtime_recovery_policy import L0AutoAdjustment
        
        adjustment = L0AutoAdjustment()
        adjustment.current_mode = ProbeMode.PERMISSION_DIAGNOSIS
        
        # 已经是最低级别
        new_mode = adjustment.downgrade()
        assert new_mode is None


class TestL0RecoveryStopsBeforeHumanWhenCacheAvailable:
    """测试有缓存时不进入人工干预"""
    
    def test_cache_fallback_prevents_human_action(self):
        """测试缓存降级阻止人工干预"""
        simulator = L0AutoRecoverySimulator()
        simulator.simulate_probes()
        
        stats = simulator.get_statistics()
        
        # 如果降级到 cache_fallback，不应该需要人工干预
        if stats["current_mode"] == "cache_fallback":
            assert stats["human_action_required"] == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
