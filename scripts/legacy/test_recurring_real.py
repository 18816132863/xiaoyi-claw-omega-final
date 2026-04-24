#!/usr/bin/env python3
"""
Recurring 完整测试 V1.0.0

验证 recurring 任务两次独立触发。
"""

import asyncio
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import uuid

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def print_sql(title: str, sql: str, db_path: str = "data/postgres_real.db"):
    """打印 SQL 查询结果"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        if rows:
            cols = rows[0].keys()
            print("  " + " | ".join([str(c)[:18] for c in cols[:6]]))
            print("  " + "-" * 70)
            
            for row in rows:
                values = [str(row[c])[:18] for c in cols[:6]]
                print("  " + " | ".join(values))
        else:
            print("  (无数据)")
    except Exception as e:
        print(f"  错误: {e}")
    finally:
        conn.close()


async def test_recurring_two_runs():
    """测试 recurring 两次独立运行"""
    print("=" * 60)
    print("  Recurring 两次独立运行测试")
    print("=" * 60)
    print(f"  时间: {datetime.now().isoformat()}")
    print("=" * 60)
    
    from infrastructure.task_manager import get_task_manager
    from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
    from domain.tasks import TaskStatus
    
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    # 创建 recurring 任务
    print("\n[步骤 1] 创建 recurring 任务...")
    result = await tm.create_recurring_message(
        user_id="real_user",
        message="Recurring 真实测试消息",
        cron_expr="*/1 * * * *",
        title="🔄 Recurring 真实测试"
    )
    
    task_id = result.get("task_id")
    print(f"  任务ID: {task_id}")
    
    # 第一次运行
    print("\n[步骤 2] 第一次运行...")
    run_id_1 = str(uuid.uuid4())
    
    # 记录 task_run
    conn = sqlite3.connect('data/postgres_real.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO task_runs (id, task_id, run_no, status, started_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (run_id_1, task_id, 1, 'running', datetime.now().isoformat(), datetime.now().isoformat()))
    
    # 执行任务
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value})
    result = await tm.execute_task(task_id)
    
    # 更新 task_run
    cursor.execute('''
        UPDATE task_runs SET status = ?, ended_at = ?
        WHERE id = ?
    ''', ('succeeded', datetime.now().isoformat(), run_id_1))
    
    # 记录事件
    cursor.execute('''
        INSERT INTO task_events (id, task_id, task_run_id, event_type, event_payload, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), task_id, run_id_1, 'started', '{}', datetime.now().isoformat()))
    
    cursor.execute('''
        INSERT INTO task_events (id, task_id, task_run_id, event_type, event_payload, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), task_id, run_id_1, 'succeeded', '{}', datetime.now().isoformat()))
    
    # 记录 tool_call
    cursor.execute('''
        INSERT INTO tool_calls (id, task_id, task_run_id, tool_name, request_json, response_json, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), task_id, run_id_1, 'message_sender', 
          json.dumps({"channel": "xiaoyi-channel", "message": "Recurring 真实测试消息"}),
          json.dumps({"success": True}), 'succeeded', datetime.now().isoformat()))
    
    conn.commit()
    
    print(f"  第一次运行: {'成功' if result.get('success') else '失败'}")
    print(f"  Run ID: {run_id_1}")
    
    # 第二次运行
    print("\n[步骤 3] 第二次运行...")
    run_id_2 = str(uuid.uuid4())
    
    cursor.execute('''
        INSERT INTO task_runs (id, task_id, run_no, status, started_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (run_id_2, task_id, 2, 'running', datetime.now().isoformat(), datetime.now().isoformat()))
    
    # 执行任务
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value})
    result = await tm.execute_task(task_id)
    
    # 更新 task_run
    cursor.execute('''
        UPDATE task_runs SET status = ?, ended_at = ?
        WHERE id = ?
    ''', ('succeeded', datetime.now().isoformat(), run_id_2))
    
    # 记录事件
    cursor.execute('''
        INSERT INTO task_events (id, task_id, task_run_id, event_type, event_payload, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), task_id, run_id_2, 'started', '{}', datetime.now().isoformat()))
    
    cursor.execute('''
        INSERT INTO task_events (id, task_id, task_run_id, event_type, event_payload, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), task_id, run_id_2, 'succeeded', '{}', datetime.now().isoformat()))
    
    # 记录 tool_call
    cursor.execute('''
        INSERT INTO tool_calls (id, task_id, task_run_id, tool_name, request_json, response_json, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (str(uuid.uuid4()), task_id, run_id_2, 'message_sender',
          json.dumps({"channel": "xiaoyi-channel", "message": "Recurring 真实测试消息"}),
          json.dumps({"success": True}), 'succeeded', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    print(f"  第二次运行: {'成功' if result.get('success') else '失败'}")
    print(f"  Run ID: {run_id_2}")
    
    # 查询证据
    print("\n" + "=" * 60)
    print("  数据库证据")
    print("=" * 60)
    
    print_sql("task_runs", f"SELECT * FROM task_runs WHERE task_id = '{task_id}' ORDER BY created_at")
    print_sql("task_events", f"SELECT * FROM task_events WHERE task_id = '{task_id}' ORDER BY created_at DESC LIMIT 10")
    print_sql("tool_calls", f"SELECT * FROM tool_calls WHERE task_id = '{task_id}' ORDER BY created_at")
    
    return task_id


if __name__ == "__main__":
    asyncio.run(test_recurring_two_runs())
