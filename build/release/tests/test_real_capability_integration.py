"""
测试真实能力集成
验证能力接入真实任务内核
"""

import pytest
import sys
import asyncio
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.mark.asyncio
async def test_schedule_task_creates_real_task():
    """测试 schedule_task 创建真实任务"""
    from capabilities.schedule_task import ScheduleTaskCapability
    from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
    
    cap = ScheduleTaskCapability()
    result = await cap.execute({
        "task_type": "once",
        "message": "Integration test task",
        "user_id": "integration_test"
    })
    
    assert result["success"] == True
    assert "task_id" in result
    
    # 验证数据库中有记录
    repo = SQLiteTaskRepository()
    task = await repo.get(result["task_id"])
    
    assert task is not None
    assert "Integration test task" in task.goal


@pytest.mark.asyncio
async def test_retry_task_hits_task_manager():
    """测试 retry_task 命中 TaskManager"""
    from capabilities.retry_task import RetryTaskCapability
    from infrastructure.task_manager import get_task_manager
    from domain.tasks import TaskStatus
    
    tm = get_task_manager()
    
    # 创建任务
    create_result = await tm.create_scheduled_message(
        user_id="retry_test",
        message="Retry test task",
        run_at=datetime.now().isoformat()
    )
    task_id = create_result["task_id"]
    
    # 设置为失败
    from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
    repo = SQLiteTaskRepository()
    await repo.update(task_id, {"status": TaskStatus.FAILED.value})
    
    # 重试
    cap = RetryTaskCapability()
    result = await cap.execute({"task_id": task_id})
    
    assert result["success"] == True
    assert "status" in result


@pytest.mark.asyncio
async def test_export_history_returns_real_data():
    """测试 export_history 返回真实数据"""
    from capabilities.export_history import ExportHistoryCapability
    from infrastructure.task_manager import get_task_manager
    
    tm = get_task_manager()
    
    # 创建任务
    create_result = await tm.create_scheduled_message(
        user_id="export_test",
        message="Export test task",
        run_at=datetime.now().isoformat()
    )
    task_id = create_result["task_id"]
    
    # 导出
    cap = ExportHistoryCapability()
    result = await cap.execute({"task_id": task_id})
    
    assert result["success"] == True
    assert result["task_id"] == task_id
    assert result["task"] is not None
    assert "runs" in result
    assert "events" in result
    assert result["record_count"] >= 1


@pytest.mark.asyncio
async def test_replay_run_returns_real_steps():
    """测试 replay_run 返回真实步骤"""
    from capabilities.replay_run import ReplayRunCapability
    from infrastructure.task_manager import get_task_manager
    from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
    from domain.tasks import TaskStatus
    
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    # 创建并执行任务
    create_result = await tm.create_scheduled_message(
        user_id="replay_test",
        message="Replay test task",
        run_at=datetime.now().isoformat()
    )
    task_id = create_result["task_id"]
    
    # 设置为 QUEUED 并执行
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value})
    exec_result = await tm.execute_task(task_id)
    
    # 获取 run_id
    import sqlite3
    db_path = project_root / "data" / "tasks.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM task_runs WHERE task_id = ? ORDER BY created_at DESC LIMIT 1", (task_id,))
    run_row = cursor.fetchone()
    conn.close()
    
    if run_row:
        run_id = run_row["id"]
        
        # 回放
        cap = ReplayRunCapability()
        result = await cap.execute({"run_id": run_id})
        
        assert result["success"] == True
        assert result["run_id"] == run_id
        assert result["run"] is not None
        assert "steps" in result
        assert "timeline" in result


@pytest.mark.asyncio
async def test_pause_resume_cancel_chain():
    """测试暂停/恢复/取消链"""
    from capabilities.pause_task import PauseTaskCapability
    from capabilities.resume_task import ResumeTaskCapability
    from capabilities.cancel_task import CancelTaskCapability
    from infrastructure.task_manager import get_task_manager
    
    tm = get_task_manager()
    
    # 创建任务
    create_result = await tm.create_scheduled_message(
        user_id="chain_test",
        message="Chain test task",
        run_at=datetime.now().isoformat()
    )
    task_id = create_result["task_id"]
    
    # 暂停
    pause_cap = PauseTaskCapability()
    pause_result = await pause_cap.execute({"task_id": task_id})
    assert pause_result["success"] == True
    
    # 恢复
    resume_cap = ResumeTaskCapability()
    resume_result = await resume_cap.execute({"task_id": task_id})
    assert resume_result["success"] == True
    
    # 取消
    cancel_cap = CancelTaskCapability()
    cancel_result = await cancel_cap.execute({"task_id": task_id})
    assert cancel_result["success"] == True
