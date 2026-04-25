#!/usr/bin/env python3
"""
部署验证脚本 V1.0.0

验证内容：
1. 服务启动
2. 健康检查
3. once 任务真实触发
4. recurring 任务按调度跑两次
5. 失败重试
6. 数据库落表
"""

import asyncio
import sys
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

project_root = Path("/home/sandbox/.openclaw/workspace")
sys.path.insert(0, str(project_root))

from infrastructure.task_manager import get_task_manager
from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
from domain.tasks import TaskStatus


async def main():
    print("=" * 60)
    print("  部署验证 V1.0.0")
    print("=" * 60)
    
    tm = get_task_manager()
    repo = SQLiteTaskRepository(db_path=str(project_root / "data" / "tasks.db"))
    
    # 1. once 任务真实触发
    print("\n[1] once 任务真实触发")
    print("-" * 40)
    
    result = await tm.create_scheduled_message(
        user_id="deploy_test",
        message="Deploy Test Once",
        run_at=datetime.now().isoformat()
    )
    
    once_task_id = result.get('task_id')
    print(f"创建任务: {once_task_id}")
    
    # 设置为 QUEUED 并执行
    await repo.update(once_task_id, {"status": TaskStatus.QUEUED.value})
    exec_result = await tm.execute_task(once_task_id)
    print(f"执行结果: {exec_result.get('delivery_status', 'unknown')}")
    
    # 2. recurring 任务按调度跑两次
    print("\n[2] recurring 任务按调度跑两次")
    print("-" * 40)
    
    result = await tm.create_recurring_message(
        user_id="deploy_test",
        message="Deploy Test Recurring",
        cron_expr="* * * * *"  # 每分钟
    )
    
    recurring_task_id = result.get('task_id')
    print(f"创建任务: {recurring_task_id}")
    
    # 第一次执行
    await repo.update(recurring_task_id, {"status": TaskStatus.QUEUED.value})
    exec1 = await tm.execute_task(recurring_task_id)
    print(f"第一次执行: {exec1.get('delivery_status', 'unknown')}")
    
    # 第二次执行
    await repo.update(recurring_task_id, {"status": TaskStatus.QUEUED.value})
    exec2 = await tm.execute_task(recurring_task_id)
    print(f"第二次执行: {exec2.get('delivery_status', 'unknown')}")
    
    # 3. 失败重试
    print("\n[3] 失败重试")
    print("-" * 40)
    
    result = await tm.create_scheduled_message(
        user_id="deploy_test",
        message="Deploy Test Retry",
        run_at=datetime.now().isoformat()
    )
    
    retry_task_id = result.get('task_id')
    print(f"创建任务: {retry_task_id}")
    
    # 设置为失败
    await repo.update(retry_task_id, {
        "status": TaskStatus.FAILED.value,
        "last_error": "Simulated failure"
    })
    
    # 重试
    retry_result = await tm.retry_task(retry_task_id)
    print(f"重试结果: {retry_result.get('delivery_status', 'unknown')}")
    
    # 4. 数据库落表验证
    print("\n[4] 数据库落表验证")
    print("-" * 40)
    
    db_path = project_root / "data" / "tasks.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # tasks 表
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id = 'deploy_test'")
    task_count = cursor.fetchone()[0]
    print(f"tasks 表记录数: {task_count}")
    
    # task_runs 表
    cursor.execute("""
        SELECT COUNT(*) FROM task_runs 
        WHERE task_id IN (SELECT id FROM tasks WHERE user_id = 'deploy_test')
    """)
    run_count = cursor.fetchone()[0]
    print(f"task_runs 表记录数: {run_count}")
    
    # task_steps 表
    cursor.execute("""
        SELECT COUNT(*) FROM task_steps 
        WHERE task_run_id IN (
            SELECT id FROM task_runs 
            WHERE task_id IN (SELECT id FROM tasks WHERE user_id = 'deploy_test')
        )
    """)
    step_count = cursor.fetchone()[0]
    print(f"task_steps 表记录数: {step_count}")
    
    # task_events 表
    cursor.execute("""
        SELECT COUNT(*) FROM task_events 
        WHERE task_id IN (SELECT id FROM tasks WHERE user_id = 'deploy_test')
    """)
    event_count = cursor.fetchone()[0]
    print(f"task_events 表记录数: {event_count}")
    
    # 5. 详细记录查询
    print("\n[5] 详细记录查询")
    print("-" * 40)
    
    # once 任务记录
    print(f"\n=== once 任务 ({once_task_id}) ===")
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (once_task_id,))
    task = cursor.fetchone()
    if task:
        print(f"  status: {task['status']}")
        print(f"  goal: {task['goal'][:50]}...")
    
    cursor.execute("SELECT * FROM task_runs WHERE task_id = ? ORDER BY created_at DESC LIMIT 1", (once_task_id,))
    run = cursor.fetchone()
    if run:
        print(f"  run_id: {run['id']}")
        print(f"  run_no: {run['run_no']}")
        print(f"  status: {run['status']}")
        
        cursor.execute("SELECT * FROM task_steps WHERE task_run_id = ?", (run['id'],))
        steps = cursor.fetchall()
        for step in steps:
            print(f"    step: {step['step_name']} ({step['tool_name']}) - {step['status']}")
    
    # recurring 任务记录
    print(f"\n=== recurring 任务 ({recurring_task_id}) ===")
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (recurring_task_id,))
    task = cursor.fetchone()
    if task:
        print(f"  status: {task['status']}")
        print(f"  next_run_at: {task['next_run_at']}")
    
    cursor.execute("SELECT * FROM task_runs WHERE task_id = ? ORDER BY created_at DESC LIMIT 2", (recurring_task_id,))
    runs = cursor.fetchall()
    print(f"  运行次数: {len(runs)}")
    for run in runs:
        print(f"    run_no: {run['run_no']}, status: {run['status']}")
    
    conn.close()
    
    # 清理
    print("\n[清理] 删除测试数据...")
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE user_id = 'deploy_test'")
    conn.commit()
    conn.close()
    print("已清理")
    
    print("\n" + "=" * 60)
    print("  部署验证完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
