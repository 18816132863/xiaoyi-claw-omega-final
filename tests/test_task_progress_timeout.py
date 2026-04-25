"""
Test Task Progress Timeout - 测试任务进度超时

验证：
1. heartbeat 正确触发
2. degrade 正确触发
3. stop_probe 正确触发
4. output_partial 正确触发
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.simulate_task_progress_timeout import (
    TaskProgressSimulator,
    TimeoutAction
)


class TestTaskProgressHeartbeat:
    """任务进度心跳测试"""
    
    def test_heartbeat_emitted(self):
        """测试心跳发送"""
        simulator = TaskProgressSimulator(task_id="test_heartbeat")
        result = simulator.simulate(scenario="timeout")
        
        # 应该有心跳
        assert result["heartbeat_count"] > 0
    
    def test_heartbeat_count_reasonable(self):
        """测试心跳次数合理"""
        simulator = TaskProgressSimulator(task_id="test_heartbeat_count")
        result = simulator.simulate(scenario="timeout")
        
        # 180 秒，每 20 秒一次心跳，应该有 9 次
        assert result["heartbeat_count"] >= 8


class TestTaskTimeoutDegradeTriggered:
    """任务超时降级触发测试"""
    
    def test_degrade_triggered_after_60s(self):
        """测试 60 秒后触发降级"""
        simulator = TaskProgressSimulator(task_id="test_degrade")
        result = simulator.simulate(scenario="timeout")
        
        # 应该触发降级
        assert result["degrade_triggered"] == True
    
    def test_degrade_event_recorded(self):
        """测试降级事件记录"""
        simulator = TaskProgressSimulator(task_id="test_degrade_event")
        simulator.simulate(scenario="timeout")
        
        # 应该有降级事件
        degrade_events = [e for e in simulator.timeout_events if e.action == "degrade"]
        assert len(degrade_events) > 0


class TestTaskTimeoutStopProbeTriggered:
    """任务超时停止探测触发测试"""
    
    def test_stop_probe_triggered_after_120s(self):
        """测试 120 秒后触发停止探测"""
        simulator = TaskProgressSimulator(task_id="test_stop_probe")
        result = simulator.simulate(scenario="timeout")
        
        # 应该触发停止探测
        assert result["stop_probe_triggered"] == True
    
    def test_stop_probe_event_recorded(self):
        """测试停止探测事件记录"""
        simulator = TaskProgressSimulator(task_id="test_stop_probe_event")
        simulator.simulate(scenario="timeout")
        
        # 应该有停止探测事件
        stop_events = [e for e in simulator.timeout_events if e.action == "stop_probe"]
        assert len(stop_events) > 0


class TestTaskTimeoutPartialOutputTriggered:
    """任务超时部分输出触发测试"""
    
    def test_output_partial_triggered_after_180s(self):
        """测试 180 秒后触发部分输出"""
        simulator = TaskProgressSimulator(task_id="test_partial")
        result = simulator.simulate(scenario="timeout")
        
        # 应该触发部分输出
        assert result["output_partial_triggered"] == True
    
    def test_partial_result_generated(self):
        """测试部分结果生成"""
        simulator = TaskProgressSimulator(task_id="test_partial_result")
        result = simulator.simulate(scenario="timeout")
        
        # 应该有部分结果
        assert result["partial_result"] is not None
        assert result["partial_result"]["status"] == "partial"
    
    def test_no_infinite_processing(self):
        """测试不会无限处理"""
        simulator = TaskProgressSimulator(task_id="test_no_infinite")
        result = simulator.simulate(scenario="timeout")
        
        # 最终状态不应该是 processing
        assert result["no_infinite_processing"] == True
        assert result["final_status"] != "processing"


class TestTaskProgressGuard:
    """任务进度守卫测试"""
    
    def test_guard_initialization(self):
        """测试守卫初始化"""
        from infrastructure.task_progress_guard import TaskProgressGuard
        
        guard = TaskProgressGuard(task_id="test_guard")
        
        assert guard.task_id == "test_guard"
        assert guard.final_status == "processing"
    
    def test_guard_update_progress(self):
        """测试守卫更新进度"""
        from infrastructure.task_progress_guard import TaskProgressGuard
        
        guard = TaskProgressGuard(task_id="test_progress")
        guard.update_progress("initialization", "Task started")
        
        assert len(guard.checkpoints) == 1
        assert guard.checkpoints[0].stage == "initialization"
    
    def test_guard_check_returns_continue_initially(self):
        """测试守卫初始检查返回继续或心跳"""
        from infrastructure.task_progress_guard import TaskProgressGuard, ProgressAction
        
        guard = TaskProgressGuard(task_id="test_check")
        action = guard.check()
        
        # 初始应该返回 CONTINUE 或 HEARTBEAT（取决于时间）
        assert action.value in ["continue", "heartbeat"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
