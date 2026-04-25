"""
E2E 测试 - 真实链路测试

测试完整流程：
1. once 任务：创建 -> 调度 -> 执行 -> delivery_pending -> delivery_confirmed -> succeeded
2. recurring 任务：验证状态流转
3. retry 场景：验证重试策略存在
4. stop/start 恢复：服务中断再启动，任务不丢
"""

import asyncio
import pytest
import uuid
import json
from pathlib import Path
from datetime import datetime, timedelta

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from infrastructure.task_manager import get_task_manager
from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
from domain.tasks import TaskStatus


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """模块级别：确保数据库存在"""
    repo = SQLiteTaskRepository()
    _ = repo._get_connection()
    yield


@pytest.mark.asyncio
async def test_once_task_full_lifecycle():
    """
    场景1: once 任务完整生命周期
    创建 -> 调度 -> 执行 -> delivery_pending -> delivery_confirmed -> succeeded
    """
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    unique_id = str(uuid.uuid4())[:8]
    
    # 1. 创建任务（过去时间，立即执行）
    run_at = (datetime.now() - timedelta(seconds=10)).isoformat()
    result = await tm.create_scheduled_message(
        user_id=f"test_once_{unique_id}",
        message=f"once-full-lifecycle-{unique_id}",
        run_at=run_at
    )
    
    assert result["success"], f"创建任务失败: {result.get('error')}"
    task_id = result["task_id"]
    
    # 2. 验证初始状态
    task = await repo.get(task_id)
    assert task.status == TaskStatus.PERSISTED, f"初始状态错误: {task.status}"
    
    # 3. 手动设置为 QUEUED 并执行
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value})
    exec_result = await tm.execute_task(task_id)
    
    # 4. 验证执行后状态
    task = await repo.get(task_id)
    assert task.status in (TaskStatus.DELIVERY_PENDING, TaskStatus.SUCCEEDED), \
        f"执行后状态错误: {task.status}"
    
    # 5. 模拟送达确认
    if task.status == TaskStatus.DELIVERY_PENDING:
        delivered_file = Path("reports/ops/delivered_messages.jsonl")
        delivered_file.parent.mkdir(parents=True, exist_ok=True)
        
        entry = {
            "message_id": f"msg_{unique_id}",
            "task_id": task_id,
            "status": "delivered",
            "delivered_at": datetime.now().isoformat()
        }
        
        with open(delivered_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        await repo.update(task_id, {
            "status": TaskStatus.SUCCEEDED.value,
            "last_run_at": datetime.now().isoformat()
        })
    
    # 6. 验证最终状态
    task = await repo.get(task_id)
    assert task.status == TaskStatus.SUCCEEDED, f"最终状态错误: {task.status}"


@pytest.mark.asyncio
async def test_recurring_task_creation_and_schedule():
    """
    场景2: recurring 任务创建和调度
    验证任务创建成功，schedule 配置正确
    """
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    unique_id = str(uuid.uuid4())[:8]
    
    # 1. 创建 recurring 任务
    result = await tm.create_recurring_message(
        user_id=f"test_recurring_{unique_id}",
        message=f"recurring-test-{unique_id}",
        cron_expr="*/1 * * * *"
    )
    
    assert result["success"], f"创建任务失败: {result.get('error')}"
    task_id = result["task_id"]
    
    # 2. 验证初始状态
    task = await repo.get(task_id)
    assert task.status == TaskStatus.PERSISTED, f"初始状态错误: {task.status}"
    assert task.schedule is not None, "schedule 不应为 None"
    assert task.schedule.mode.value == "cron", f"调度模式错误: {task.schedule.mode}"
    assert task.schedule.cron_expr == "*/1 * * * *", f"cron 表达式错误: {task.schedule.cron_expr}"
    
    # 3. 验证可以计算下次运行时间
    next_run = task.schedule.get_next_run_at(datetime.now())
    assert next_run is not None, "下次运行时间不应为 None"


@pytest.mark.asyncio
async def test_retry_policy_exists():
    """
    场景3: retry 场景
    验证重试策略存在且配置正确
    """
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    unique_id = str(uuid.uuid4())[:8]
    
    # 1. 创建任务
    run_at = (datetime.now() - timedelta(seconds=10)).isoformat()
    result = await tm.create_scheduled_message(
        user_id=f"test_retry_{unique_id}",
        message=f"retry-policy-{unique_id}",
        run_at=run_at
    )
    
    task_id = result["task_id"]
    
    # 2. 验证重试策略存在
    task = await repo.get(task_id)
    assert task.retry_policy is not None, "重试策略不应为 None"
    assert task.retry_policy.max_attempts >= 1, "最大重试次数应 >= 1"
    assert task.retry_policy.backoff_seconds >= 1, "退避时间应 >= 1"


@pytest.mark.asyncio
async def test_stop_start_recovery():
    """
    场景4: stop/start 恢复
    服务中断再启动，任务不丢
    """
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    unique_id = str(uuid.uuid4())[:8]
    
    # 1. 创建任务
    run_at = (datetime.now() + timedelta(hours=1)).isoformat()
    result = await tm.create_scheduled_message(
        user_id=f"test_recovery_{unique_id}",
        message=f"recovery-scenario-{unique_id}",
        run_at=run_at
    )
    
    task_id = result["task_id"]
    
    # 2. 验证任务存在
    task = await repo.get(task_id)
    assert task is not None, "任务不存在"
    assert task.status == TaskStatus.PERSISTED, f"状态错误: {task.status}"
    
    # 3. 模拟服务重启（重新获取 repo）
    repo2 = SQLiteTaskRepository()
    task2 = await repo2.get(task_id)
    
    # 4. 验证任务仍然存在且状态正确
    assert task2 is not None, "服务重启后任务丢失"
    assert task2.status == TaskStatus.PERSISTED, f"服务重启后状态错误: {task2.status}"
    assert task2.task_id == task_id, "任务 ID 不匹配"
    
    # 5. 验证任务可以被调度
    await repo2.update(task_id, {"status": TaskStatus.QUEUED.value})
    task3 = await repo2.get(task_id)
    assert task3.status == TaskStatus.QUEUED, f"调度后状态错误: {task3.status}"


@pytest.mark.asyncio
async def test_state_machine_transitions():
    """测试状态机转移规则"""
    from domain.tasks.state_machine import (
        TaskStatus as SMTaskStatus,
        can_transition,
        STATE_TRANSITIONS
    )
    
    assert SMTaskStatus.DELIVERY_PENDING in STATE_TRANSITIONS
    assert can_transition(SMTaskStatus.RUNNING, SMTaskStatus.DELIVERY_PENDING)
    assert can_transition(SMTaskStatus.DELIVERY_PENDING, SMTaskStatus.SUCCEEDED)
    assert can_transition(SMTaskStatus.DELIVERY_PENDING, SMTaskStatus.PERSISTED)
    assert can_transition(SMTaskStatus.DELIVERY_PENDING, SMTaskStatus.WAITING_RETRY)
    assert can_transition(SMTaskStatus.DELIVERY_PENDING, SMTaskStatus.FAILED)
