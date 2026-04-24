"""
测试暂停/恢复语义
"""

import pytest
import sys
import asyncio
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.mark.asyncio
async def test_persisted_task_can_be_paused():
    """
    PERSISTED 状态的任务可以被暂停
    
    预期：
    - pause_task 返回 success=True
    - 状态变为 PAUSED
    """
    from infrastructure.task_manager import get_task_manager
    
    tm = get_task_manager()
    
    # 创建任务
    result = await tm.create_scheduled_message(
        user_id="pause_test",
        message="Test pause from PERSISTED",
        run_at=datetime.now().isoformat()
    )
    task_id = result["task_id"]
    
    # 暂停
    pause_result = await tm.pause_task(task_id)
    
    assert pause_result["success"] == True, f"Pause failed: {pause_result.get('error')}"
    assert pause_result["status"] == "paused"
    assert pause_result.get("previous_status") == "persisted"


@pytest.mark.asyncio
async def test_paused_task_can_be_resumed():
    """
    PAUSED 状态的任务可以被恢复
    
    预期：
    - resume_task 返回 success=True
    - 状态恢复到之前的状态（PERSISTED 或 QUEUED）
    """
    from infrastructure.task_manager import get_task_manager
    
    tm = get_task_manager()
    
    # 创建任务
    result = await tm.create_scheduled_message(
        user_id="resume_test",
        message="Test resume",
        run_at=datetime.now().isoformat()
    )
    task_id = result["task_id"]
    
    # 暂停
    await tm.pause_task(task_id)
    
    # 恢复
    resume_result = await tm.resume_task(task_id)
    
    assert resume_result["success"] == True, f"Resume failed: {resume_result.get('error')}"
    # 恢复后应该是 persisted 或 queued
    assert resume_result["status"] in ["persisted", "queued"]


@pytest.mark.asyncio
async def test_pause_resume_preserves_previous_status():
    """
    暂停/恢复保留之前的状态信息
    
    预期：
    - pause 返回 previous_status
    - resume 返回 previous_status
    """
    from infrastructure.task_manager import get_task_manager
    from domain.tasks import TaskStatus
    from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
    
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    # 创建任务
    result = await tm.create_scheduled_message(
        user_id="preserve_test",
        message="Test preserve status",
        run_at=datetime.now().isoformat()
    )
    task_id = result["task_id"]
    
    # 设置为 QUEUED
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value})
    
    # 暂停
    pause_result = await tm.pause_task(task_id)
    assert pause_result["previous_status"] == "queued"
    
    # 恢复
    resume_result = await tm.resume_task(task_id)
    assert resume_result["previous_status"] == "queued"
    # 恢复后应该是 QUEUED（因为之前是 QUEUED）
    assert resume_result["status"] == "queued"


@pytest.mark.asyncio
async def test_cannot_pause_completed_task():
    """
    已完成的任务不能被暂停
    
    预期：
    - pause_task 返回 success=False
    """
    from infrastructure.task_manager import get_task_manager
    from domain.tasks import TaskStatus
    from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
    
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    # 创建任务
    result = await tm.create_scheduled_message(
        user_id="completed_test",
        message="Test completed",
        run_at=datetime.now().isoformat()
    )
    task_id = result["task_id"]
    
    # 设置为已完成
    await repo.update(task_id, {"status": TaskStatus.SUCCEEDED.value})
    
    # 尝试暂停
    pause_result = await tm.pause_task(task_id)
    
    assert pause_result["success"] == False
    assert "不可暂停" in pause_result.get("error", "")


@pytest.mark.asyncio
async def test_cannot_resume_non_paused_task():
    """
    非 PAUSED 状态的任务不能被恢复
    
    预期：
    - resume_task 返回 success=False
    """
    from infrastructure.task_manager import get_task_manager
    
    tm = get_task_manager()
    
    # 创建任务（状态为 PERSISTED）
    result = await tm.create_scheduled_message(
        user_id="non_paused_test",
        message="Test non paused",
        run_at=datetime.now().isoformat()
    )
    task_id = result["task_id"]
    
    # 尝试恢复（没有先暂停）
    resume_result = await tm.resume_task(task_id)
    
    assert resume_result["success"] == False
    assert "不可恢复" in resume_result.get("error", "")
