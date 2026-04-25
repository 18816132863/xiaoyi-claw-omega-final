"""测试学习第二次执行复用成功路径"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from learning_loop import ExecutionMemory, ExecutionRecord, PlanOptimizer


def test_second_run_reuses_success_path():
    """测试第二次执行复用成功路径"""
    memory = ExecutionMemory(storage_path="data/test_learning_reuse.jsonl")
    
    # 清空旧数据
    memory._cache = []
    
    # 第一次执行：写入成功记录
    first_record = ExecutionRecord(
        goal="明天提醒我开会",
        plan=[
            {"step_id": 1, "capability": "schedule.create_calendar_event"},
            {"step_id": 2, "capability": "notification.push"},
        ],
        capabilities_used=["schedule.create_calendar_event", "notification.push"],
        successful_steps=[1, 2],
        failed_steps=[],
        final_result="success",
        user_satisfied=True,
    )
    memory.record(first_record)
    
    # 第二次执行：查找相似记录
    similar = memory.find_similar("后天提醒我交报告")
    
    assert len(similar) > 0, "应该找到相似记录"
    assert similar[0].final_result == "success", "应该复用成功的记录"
    assert "schedule.create_calendar_event" in similar[0].capabilities_used


def test_second_run_gets_preference_hints():
    """测试第二次执行获取偏好提示"""
    memory = ExecutionMemory(storage_path="data/test_learning_reuse.jsonl")
    
    # 写入成功记录
    record = ExecutionRecord(
        goal="明天提醒我开会",
        plan=[{"step_id": 1, "capability": "schedule.create_calendar_event"}],
        capabilities_used=["schedule.create_calendar_event"],
        successful_steps=[1],
        failed_steps=[],
        final_result="success",
        user_satisfied=True,
    )
    memory.record(record)
    
    # 获取偏好提示
    hints = memory.get_preference_hints("后天提醒我")
    
    assert "preferred_capabilities" in hints
    assert "schedule.create_calendar_event" in hints["preferred_capabilities"]


def test_optimizer_uses_history():
    """测试优化器使用历史记录"""
    memory = ExecutionMemory(storage_path="data/test_learning_reuse.jsonl")
    
    # 写入成功记录
    record = ExecutionRecord(
        goal="明天提醒我开会",
        plan=[{"step_id": 1, "capability": "schedule.create_calendar_event"}],
        capabilities_used=["schedule.create_calendar_event"],
        successful_steps=[1],
        failed_steps=[],
        final_result="success",
    )
    memory.record(record)
    
    # 优化计划
    optimizer = PlanOptimizer(memory=memory)
    result = optimizer.optimize("后天提醒我", [{"step_id": 1, "capability": "default"}])
    
    assert "optimizations" in result
    assert result["confidence"] >= 0.5
