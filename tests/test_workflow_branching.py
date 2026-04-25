"""测试工作流分支"""

import pytest


def test_evaluate_condition():
    """测试条件评估"""
    from orchestration.workflows.branching import evaluate_condition, BranchCondition
    
    # 测试成功条件
    result = {"success": True, "normalized_status": "completed"}
    assert evaluate_condition(BranchCondition.SUCCESS, result) == True
    
    # 测试失败条件
    result = {"success": False, "normalized_status": "failed"}
    assert evaluate_condition(BranchCondition.FAILURE, result) == True
    
    # 测试超时条件
    result = {"normalized_status": "timeout"}
    assert evaluate_condition(BranchCondition.TIMEOUT, result) == True
    
    # 测试不确定条件
    result = {"normalized_status": "result_uncertain"}
    assert evaluate_condition(BranchCondition.UNCERTAIN, result) == True


def test_execute_branching_workflow_dry_run():
    """测试执行分支工作流（dry_run）"""
    from orchestration.workflows.branching import execute_branching_workflow, Branch, BranchCondition
    
    steps = [
        {"name": "step1", "capability": "send_message", "params": {"to": "test", "message": "test"}}
    ]
    
    branches = [
        Branch(
            condition=BranchCondition.SUCCESS,
            steps=[{"name": "success_step", "capability": "send_notification", "params": {}}]
        )
    ]
    
    result = execute_branching_workflow(steps, branches, dry_run=True)
    assert result["success"] == True
    assert result["dry_run"] == True
