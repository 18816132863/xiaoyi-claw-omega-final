"""测试 dry_run 控制"""

import pytest


def test_preview_side_effect():
    """测试副作用预览"""
    from capabilities.preview_side_effect import preview_side_effect
    
    # 测试消息发送预览
    result = preview_side_effect(
        capability="send_message",
        params={"to": "13800138000", "message": "测试消息"}
    )
    assert result["success"] == True
    assert result["is_side_effect"] == True
    assert len(result["estimated_effects"]) > 0
    
    # 测试日程创建预览
    result = preview_side_effect(
        capability="schedule_task",
        params={"title": "测试日程", "start_time": "2026-04-25T10:00:00"}
    )
    assert result["success"] == True
    assert result["is_side_effect"] == True
    
    # 测试非副作用操作
    result = preview_side_effect(
        capability="query_message_status",
        params={}
    )
    assert result["success"] == True
    assert result["is_side_effect"] == False


def test_batch_preview():
    """测试批量预览"""
    from capabilities.preview_side_effect import batch_preview
    
    actions = [
        {"capability": "send_message", "params": {"to": "test", "message": "test"}},
        {"capability": "schedule_task", "params": {"title": "test"}}
    ]
    
    result = batch_preview(actions)
    assert result["success"] == True
    assert result["total_actions"] == 2
    assert result["side_effect_count"] == 2


def test_dry_run_workflow():
    """测试 dry_run 工作流"""
    from orchestration.workflows.preview import dry_run_workflow
    
    steps = [
        {"name": "step1", "capability": "send_message", "params": {"to": "test", "message": "test"}},
        {"name": "step2", "capability": "schedule_task", "params": {"title": "test"}}
    ]
    
    result = dry_run_workflow(steps)
    assert result["success"] == True
    assert result["dry_run"] == True
    assert result["total_steps"] == 2
