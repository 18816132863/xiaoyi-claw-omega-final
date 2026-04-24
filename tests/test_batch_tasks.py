"""测试批量任务"""
import pytest
from orchestration.batch_orchestrator import BatchOrchestrator


@pytest.mark.asyncio
async def test_create_batch():
    """测试创建批量任务"""
    orchestrator = BatchOrchestrator()

    tasks = [
        {"type": "message", "content": "Task 1"},
        {"type": "message", "content": "Task 2"},
        {"type": "message", "content": "Task 3"},
    ]

    result = await orchestrator.create_batch("test_batch", tasks)

    assert result.batch_id is not None
    assert result.name == "test_batch"
    assert len(result.items) == 3


@pytest.mark.asyncio
async def test_get_batch_status():
    """测试获取批量状态"""
    orchestrator = BatchOrchestrator()

    # 先创建
    create_result = await orchestrator.create_batch("test_status", [{"type": "test"}])
    batch_id = create_result.batch_id

    # 再查询
    status = await orchestrator.get_batch(batch_id)

    assert status is not None
    assert status.batch_id == batch_id
