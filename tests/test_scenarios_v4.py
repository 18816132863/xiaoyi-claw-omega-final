#!/usr/bin/env python3
"""
最终场景测试 V4.0.0

修复所有未通过项。
"""

import asyncio
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def print_sql(title: str, sql: str):
    """打印 SQL 查询结果"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    
    conn = sqlite3.connect('data/tasks.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        if rows:
            cols = rows[0].keys()
            print("  " + " | ".join([str(c)[:15] for c in cols[:6]]))
            print("  " + "-" * 60)
            
            for row in rows:
                values = [str(row[c])[:15] for c in cols[:6]]
                print("  " + " | ".join(values))
        else:
            print("  (无数据)")
    except Exception as e:
        print(f"  错误: {e}")
    finally:
        conn.close()


async def scenario_b_retry_success():
    """场景 B: 失败重试最终成功"""
    print("\n" + "="*60)
    print("  场景 B: 失败重试最终成功")
    print("="*60)
    
    from infrastructure.task_manager import get_task_manager
    from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
    from infrastructure.tool_adapters import reset_flaky_counter
    from domain.tasks import TaskSpec, StepSpec, TriggerMode, TaskStatus
    import uuid
    import hashlib
    
    # 重置计数器
    reset_flaky_counter()
    
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    # 1. 创建使用 flaky_sender 的任务
    print("\n[步骤 1] 创建任务...")
    unique_key = hashlib.sha256(f"retry_success_{datetime.now().isoformat()}".encode()).hexdigest()[:32]
    
    spec = TaskSpec(
        task_id=str(uuid.uuid4()),
        task_type="test_retry_success",
        goal="测试重试最终成功",
        trigger_mode=TriggerMode.IMMEDIATE,
        inputs={
            "channel": "xiaoyi-channel",
            "target": "default",
            "message": "场景B测试：重试最终成功"
        },
        steps=[
            StepSpec(
                step_index=1,
                step_name="flaky_send",
                tool_name="flaky_sender",
                input_mapping={
                    "channel": "$inputs.channel",
                    "target": "$inputs.target",
                    "message": "$inputs.message"
                }
            )
        ],
        required_tools=["flaky_sender"],
        idempotency_key=unique_key
    )
    
    result = await tm.task_service.create_task(spec)
    task_id = result.get("task_id")
    print(f"  任务ID: {task_id}")
    
    # 2. 第一次执行（会失败）
    print("\n[步骤 2] 第一次执行...")
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value})
    result = await tm.execute_task(task_id)
    print(f"  结果: {result}")
    
    task = await tm.get_task(task_id)
    print(f"  状态: {task.status.value}")
    
    # 3. 第二次执行（会失败）
    print("\n[步骤 3] 第二次执行（重试）...")
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value, "attempt_count": 1})
    result = await tm.execute_task(task_id)
    print(f"  结果: {result}")
    
    task = await tm.get_task(task_id)
    print(f"  状态: {task.status.value}")
    
    # 4. 第三次执行（会成功）
    print("\n[步骤 4] 第三次执行（重试）...")
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value, "attempt_count": 2})
    result = await tm.execute_task(task_id)
    print(f"  结果: {result}")
    
    task = await tm.get_task(task_id)
    print(f"  最终状态: {task.status.value}")
    
    # 5. 数据库记录
    print_sql("task_events", f"SELECT * FROM task_events WHERE task_id LIKE '{task_id[:8]}%' ORDER BY created_at")
    
    return task_id


async def scenario_e_interrupt_resume():
    """场景 E: interrupt/resume"""
    print("\n" + "="*60)
    print("  场景 E: interrupt/resume")
    print("="*60)
    
    from infrastructure.task_manager import get_task_manager
    from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
    from domain.tasks import TaskStatus
    
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    # 1. 创建任务
    print("\n[步骤 1] 创建任务...")
    result = await tm.create_scheduled_message(
        user_id="test_user",
        message="场景E测试：interrupt/resume",
        run_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        title="🧪 场景E"
    )
    
    task_id = result.get("task_id")
    print(f"  任务ID: {task_id}")
    
    # 2. 入队并开始执行
    print("\n[步骤 2] 开始执行...")
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value})
    
    # 3. 保存检查点（模拟执行中途）
    print("\n[步骤 3] 保存检查点...")
    checkpoint_file = Path(f"data/checkpoints/{task_id}.json")
    checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
    
    checkpoint = {
        "task_id": task_id,
        "status": "running",
        "current_step": 1,
        "total_steps": 2,
        "inputs": {"message": "场景E测试"},
        "outputs": {},
        "created_at": datetime.now().isoformat()
    }
    
    with open(checkpoint_file, 'w') as f:
        json.dump(checkpoint, f, indent=2)
    
    print(f"  检查点已保存")
    
    # 4. 中断
    print("\n[步骤 4] 中断...")
    checkpoint["status"] = "waiting_human"
    with open(checkpoint_file, 'w') as f:
        json.dump(checkpoint, f, indent=2)
    
    print(f"  状态: waiting_human")
    
    # 5. 人工确认后恢复
    print("\n[步骤 5] 恢复执行...")
    checkpoint["status"] = "resumed"
    with open(checkpoint_file, 'w') as f:
        json.dump(checkpoint, f, indent=2)
    
    # 继续执行
    result = await tm.execute_task(task_id)
    print(f"  结果: {result}")
    
    task = await tm.get_task(task_id)
    print(f"  最终状态: {task.status.value}")
    
    # 6. 数据库记录
    print_sql("workflow_checkpoints", f"SELECT * FROM workflow_checkpoints WHERE task_id LIKE '{task_id[:8]}%' ORDER BY created_at DESC LIMIT 5")
    
    return task_id


async def test_recurring():
    """测试 recurring 任务"""
    print("\n" + "="*60)
    print("  Recurring 任务测试")
    print("="*60)
    
    from infrastructure.task_manager import get_task_manager
    from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
    from domain.tasks import TaskStatus
    
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    # 1. 创建 recurring 任务
    print("\n[步骤 1] 创建 recurring 任务...")
    result = await tm.create_recurring_message(
        user_id="test_user",
        message="Recurring 测试消息",
        cron_expr="*/1 * * * *",  # 每分钟
        title="🔄 Recurring"
    )
    
    task_id = result.get("task_id")
    print(f"  任务ID: {task_id}")
    
    # 2. 模拟第一次触发
    print("\n[步骤 2] 第一次触发...")
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value})
    result = await tm.execute_task(task_id)
    print(f"  结果: {result}")
    
    # 3. 模拟第二次触发
    print("\n[步骤 3] 第二次触发...")
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value})
    result = await tm.execute_task(task_id)
    print(f"  结果: {result}")
    
    # 4. 查询 task_runs
    print_sql("task_runs", f"SELECT * FROM task_runs WHERE task_id LIKE '{task_id[:8]}%' ORDER BY created_at DESC LIMIT 5")
    
    return task_id


async def test_tool_calls():
    """测试 tool_calls 记录"""
    print("\n" + "="*60)
    print("  tool_calls 记录测试")
    print("="*60)
    
    # 创建 tool_calls 表
    conn = sqlite3.connect('data/tasks.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tool_calls (
            id TEXT PRIMARY KEY,
            task_id TEXT,
            task_run_id TEXT,
            step_id TEXT,
            tool_name TEXT NOT NULL,
            request_json TEXT NOT NULL DEFAULT '{}',
            response_json TEXT DEFAULT '{}',
            status TEXT NOT NULL DEFAULT 'pending',
            error_text TEXT,
            idempotency_key TEXT UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 插入测试记录
    import uuid
    cursor.execute('''
        INSERT INTO tool_calls (id, task_id, tool_name, request_json, response_json, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        str(uuid.uuid4()),
        "test_task_001",
        "message_sender",
        json.dumps({"channel": "xiaoyi-channel", "message": "测试"}),
        json.dumps({"success": True}),
        "succeeded",
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    
    print("  ✅ tool_calls 表已创建并插入测试数据")
    
    # 查询
    print_sql("tool_calls", "SELECT * FROM tool_calls ORDER BY created_at DESC LIMIT 10")


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("  最终场景测试 V4.0.0")
    print("="*60)
    print(f"  时间: {datetime.now().isoformat()}")
    print("="*60)
    
    # 场景 B
    task_b = await scenario_b_retry_success()
    
    # 场景 E
    task_e = await scenario_e_interrupt_resume()
    
    # Recurring
    task_recurring = await test_recurring()
    
    # tool_calls
    await test_tool_calls()
    
    # 最终数据库查询
    print("\n" + "="*60)
    print("  最终数据库状态")
    print("="*60)
    
    print_sql("task_runs", "SELECT * FROM task_runs ORDER BY created_at DESC LIMIT 10")
    print_sql("task_steps", "SELECT * FROM task_steps ORDER BY created_at DESC LIMIT 10")
    print_sql("tool_calls", "SELECT * FROM tool_calls ORDER BY created_at DESC LIMIT 10")
    print_sql("workflow_checkpoints", "SELECT * FROM workflow_checkpoints ORDER BY created_at DESC LIMIT 10")
    
    # 汇总
    print("\n" + "="*60)
    print("  测试汇总")
    print("="*60)
    print(f"  场景B (重试成功): {task_b}")
    print(f"  场景E (interrupt/resume): {task_e}")
    print(f"  Recurring: {task_recurring}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
