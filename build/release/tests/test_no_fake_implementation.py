"""
测试空实现和假实现会被卡住
"""

import pytest
import sys
import asyncio
import inspect
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_send_message_not_hardcoded():
    """测试 send_message 不是硬编码返回"""
    from capabilities.send_message import SendMessageCapability
    
    cap = SendMessageCapability()
    source = inspect.getsource(cap.execute)
    
    # 不应该有硬编码的 success: True
    assert '"success": True' not in source or 'result.get("success"' in source


def test_schedule_task_not_hardcoded():
    """测试 schedule_task 不是硬编码返回"""
    from capabilities.schedule_task import ScheduleTaskCapability
    
    cap = ScheduleTaskCapability()
    source = inspect.getsource(cap.execute)
    
    # 应该调用 TaskManager
    assert "get_task_manager" in source or "TaskManager" in source


def test_export_history_reads_database():
    """测试 export_history 读取数据库"""
    from capabilities.export_history import ExportHistoryCapability
    
    cap = ExportHistoryCapability()
    source = inspect.getsource(cap.execute)
    
    # 应该有数据库查询
    assert "sqlite3" in source or "cursor.execute" in source


def test_replay_run_reads_database():
    """测试 replay_run 读取数据库"""
    from capabilities.replay_run import ReplayRunCapability
    
    cap = ReplayRunCapability()
    source = inspect.getsource(cap.execute)
    
    # 应该有数据库查询
    assert "sqlite3" in source or "cursor.execute" in source


def test_diagnostics_calls_real_check():
    """测试 diagnostics 调用真实检查"""
    from capabilities.diagnostics import DiagnosticsCapability
    
    cap = DiagnosticsCapability()
    source = inspect.getsource(cap.execute)
    
    # 应该调用 RuntimeSelfCheck
    assert "RuntimeSelfCheck" in source


def test_self_repair_checks_database():
    """测试 self_repair 检查数据库"""
    from capabilities.self_repair import SelfRepairCapability
    
    cap = SelfRepairCapability()
    source = inspect.getsource(cap.execute)
    
    # 应该有数据库检查
    assert "sqlite3" in source or "cursor.execute" in source


@pytest.mark.asyncio
async def test_schedule_task_returns_real_task_id():
    """测试 schedule_task 返回真实 task_id"""
    from capabilities.schedule_task import ScheduleTaskCapability
    from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
    
    cap = ScheduleTaskCapability()
    result = await cap.execute({
        "task_type": "once",
        "message": "Real task test",
        "user_id": "real_test"
    })
    
    # 应该返回真实的 task_id
    assert result["success"] == True
    assert "task_id" in result
    
    # 验证 task_id 格式（UUID）
    task_id = result["task_id"]
    assert len(task_id) == 36  # UUID 格式
    assert task_id.count("-") == 4
    
    # 验证数据库中存在
    repo = SQLiteTaskRepository()
    task = await repo.get(task_id)
    assert task is not None


@pytest.mark.asyncio
async def test_export_history_not_empty_result():
    """测试 export_history 返回非空结果"""
    from capabilities.export_history import ExportHistoryCapability
    from infrastructure.task_manager import get_task_manager
    from datetime import datetime
    import uuid
    
    tm = get_task_manager()
    
    # 使用唯一的 user_id 和动态 run_at 避免幂等键冲突
    unique_user = f"export_test_{uuid.uuid4().hex[:8]}"
    unique_run_at = datetime.now().isoformat()  # 动态时间
    
    # 先创建任务
    create_result = await tm.create_scheduled_message(
        user_id=unique_user,
        message="Export not empty test",
        run_at=unique_run_at
    )
    task_id = create_result["task_id"]
    
    # 导出
    cap = ExportHistoryCapability()
    result = await cap.execute({"task_id": task_id})
    
    # 应该有真实数据
    assert result["success"] == True
    assert result["task"] is not None
    assert result["task"]["id"] == task_id
    assert result["record_count"] >= 1
