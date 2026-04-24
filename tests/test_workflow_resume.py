"""测试工作流恢复"""
import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.mark.asyncio
async def test_create_workflow():
    """测试创建工作流"""
    from orchestration.workflow_orchestrator import WorkflowOrchestrator, WorkflowStep
    
    orchestrator = WorkflowOrchestrator()

    # 创建 WorkflowStep 对象
    async def dummy_action(ctx):
        return {"success": True}
    
    steps = [
        WorkflowStep("step1", "Send Message", dummy_action),
        WorkflowStep("step2", "Wait", dummy_action),
        WorkflowStep("step3", "Send Message", dummy_action),
    ]

    result = await orchestrator.create_workflow("test_workflow", steps)

    assert result.workflow_id is not None
    assert len(result.steps) == 3


@pytest.mark.asyncio
async def test_pause_and_resume():
    """测试暂停和恢复"""
    from orchestration.workflow_orchestrator import WorkflowOrchestrator, WorkflowStep, WorkflowState
    
    orchestrator = WorkflowOrchestrator()

    async def dummy_action(ctx):
        return {"success": True}
    
    steps = [WorkflowStep("step1", "Test", dummy_action)]

    # 创建
    create_result = await orchestrator.create_workflow("pause_test", steps)
    wf_id = create_result.workflow_id
    
    # 设置为 RUNNING 状态
    create_result.state = WorkflowState.RUNNING

    # 暂停
    pause_result = await orchestrator.pause_workflow(wf_id)
    assert pause_result == True
    
    # 验证状态
    assert create_result.state == WorkflowState.PAUSED
