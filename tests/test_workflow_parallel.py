"""测试工作流并行步骤"""

import pytest


def test_execute_parallel_steps_dry_run():
    """测试并行执行步骤（dry_run）"""
    from orchestration.workflows.parallel_steps import execute_parallel_steps
    
    steps = [
        {"name": "step1", "capability": "send_message", "params": {"to": "test1", "message": "test"}},
        {"name": "step2", "capability": "send_message", "params": {"to": "test2", "message": "test"}}
    ]
    
    result = execute_parallel_steps(steps, dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True
    assert "steps" in result


def test_parallel_send_messages_dry_run():
    """测试并行发送消息（dry_run）"""
    from orchestration.workflows.parallel_steps import parallel_send_messages
    
    recipients = [
        {"to": "phone1", "name": "用户1"},
        {"to": "phone2", "name": "用户2"}
    ]
    
    result = parallel_send_messages(recipients, message_template="你好 {name}", dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True
