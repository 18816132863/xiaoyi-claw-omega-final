"""
Test Connected Runtime Recovery Policy - 测试连接运行时恢复策略
"""

import pytest
import asyncio
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.connected_runtime_recovery_policy import (
    RecoveryStrategy,
    ProbeMode,
    FailureType,
    RecoveryStep,
    RecoveryPlan,
    L0AutoAdjustment,
    ConnectedRuntimeRecoveryPolicy,
    TaskProgressTracker,
    format_recovery_report
)


class TestRecoveryEnums:
    """测试恢复相关枚举"""
    
    def test_recovery_strategy_enum(self):
        """测试恢复策略枚举"""
        assert RecoveryStrategy.RETRY.value == "retry"
        assert RecoveryStrategy.LIMITED_SCOPE_PROBE.value == "limited_scope_probe"
        assert RecoveryStrategy.CACHE_FALLBACK.value == "cache_fallback"
        assert RecoveryStrategy.HUMAN_ACTION_REQUIRED.value == "human_action_required"
    
    def test_probe_mode_enum(self):
        """测试探测模式枚举"""
        assert ProbeMode.NORMAL_PROBE.value == "normal_probe"
        assert ProbeMode.FAST_PROBE.value == "fast_probe"
        assert ProbeMode.LIMITED_SCOPE_PROBE.value == "limited_scope_probe"
    
    def test_failure_type_enum(self):
        """测试失败类型枚举"""
        assert FailureType.CONTACT_SERVICE_TIMEOUT.value == "contact_service_timeout"
        assert FailureType.PERMISSION_REQUIRED.value == "permission_required"
        assert FailureType.SESSION_DISCONNECTED.value == "session_disconnected"


class TestL0AutoAdjustment:
    """测试 L0 自动调整"""
    
    def test_initial_state(self):
        """测试初始状态"""
        adj = L0AutoAdjustment()
        assert adj.current_mode == ProbeMode.NORMAL_PROBE
        assert adj.success_rate == 1.0
    
    def test_record_result(self):
        """测试记录结果"""
        adj = L0AutoAdjustment()
        adj.record_result(True)
        adj.record_result(True)
        adj.record_result(False)
        
        assert len(adj.adjustment_history) == 3
        assert adj.success_rate == 2/3
    
    def test_should_downgrade(self):
        """测试是否需要降级"""
        adj = L0AutoAdjustment()
        
        # 不足 5 次，不应降级
        for _ in range(3):
            adj.record_result(False)
        assert adj.should_downgrade() == False
        
        # 满 5 次且成功率低于 80%，应降级
        adj.record_result(False)
        adj.record_result(False)
        assert adj.should_downgrade() == True
    
    def test_downgrade(self):
        """测试降级"""
        adj = L0AutoAdjustment()
        adj.success_rate = 0.5
        adj.adjustment_history = [{}] * 5  # 模拟 5 次记录
        
        new_mode = adj.downgrade()
        assert new_mode == ProbeMode.FAST_PROBE
        assert adj.current_mode == ProbeMode.FAST_PROBE


class TestConnectedRuntimeRecoveryPolicy:
    """测试连接运行时恢复策略"""
    
    def test_classify_failure_timeout(self):
        """测试分类超时失败"""
        policy = ConnectedRuntimeRecoveryPolicy()
        
        ft = policy.classify_failure("contact service timeout", "contact_service")
        assert ft == FailureType.CONTACT_SERVICE_TIMEOUT
        
        ft = policy.classify_failure("calendar timeout", "calendar_service")
        assert ft == FailureType.CALENDAR_SERVICE_TIMEOUT
    
    def test_classify_failure_permission(self):
        """测试分类权限失败"""
        policy = ConnectedRuntimeRecoveryPolicy()
        
        ft = policy.classify_failure("permission denied", None)
        assert ft == FailureType.PERMISSION_REQUIRED
    
    def test_classify_failure_session(self):
        """测试分类会话失败"""
        policy = ConnectedRuntimeRecoveryPolicy()
        
        ft = policy.classify_failure("session disconnected", None)
        assert ft == FailureType.SESSION_DISCONNECTED
    
    def test_create_recovery_plan_timeout(self):
        """测试创建超时恢复计划"""
        policy = ConnectedRuntimeRecoveryPolicy()
        plan = policy.create_recovery_plan(FailureType.CONTACT_SERVICE_TIMEOUT)
        
        assert plan.failure_type == FailureType.CONTACT_SERVICE_TIMEOUT
        assert len(plan.steps) > 0
        assert plan.steps[0].strategy == RecoveryStrategy.RETRY
        assert plan.steps[-1].strategy == RecoveryStrategy.HUMAN_ACTION_REQUIRED
    
    def test_create_recovery_plan_permission(self):
        """测试创建权限恢复计划"""
        policy = ConnectedRuntimeRecoveryPolicy()
        plan = policy.create_recovery_plan(FailureType.PERMISSION_REQUIRED)
        
        # 权限问题直接进入权限诊断
        assert plan.steps[0].strategy == RecoveryStrategy.PERMISSION_DIAGNOSIS
    
    def test_get_current_probe_mode(self):
        """测试获取当前探测模式"""
        policy = ConnectedRuntimeRecoveryPolicy()
        assert policy.get_current_probe_mode() == ProbeMode.NORMAL_PROBE


class TestTaskProgressTracker:
    """测试任务进度追踪器"""
    
    def test_initial_state(self):
        """测试初始状态"""
        tracker = TaskProgressTracker("test_task")
        assert tracker.task_id == "test_task"
        assert tracker.current_stage is None
    
    def test_update_progress(self):
        """测试更新进度"""
        tracker = TaskProgressTracker("test_task")
        tracker.update_progress("stage1", "testing")
        
        assert tracker.current_stage == "stage1"
        assert len(tracker.progress_stages) == 1
    
    def test_check_timeout_no_timeout(self):
        """测试未超时"""
        tracker = TaskProgressTracker("test_task", timeout_seconds=180.0)
        result = tracker.check_timeout()
        
        assert result["action"] == "continue"
        assert result["should_degrade"] == False
    
    def test_get_progress_report(self):
        """测试进度报告"""
        tracker = TaskProgressTracker("test_task")
        tracker.update_progress("stage1", "testing")
        
        report = tracker.get_progress_report()
        assert "Task: test_task" in report
        assert "stage1" in report


class TestFormatRecoveryReport:
    """测试恢复报告格式化"""
    
    def test_format_basic_report(self):
        """测试基本报告格式化"""
        policy = ConnectedRuntimeRecoveryPolicy()
        report = format_recovery_report(policy)
        
        assert "CONNECTED RUNTIME RECOVERY REPORT" in report
        assert "current_mode: normal_probe" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
