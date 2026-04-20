#!/usr/bin/env python3
"""
最终验收测试 V1.0.0

使用真实 Celery + FakeRedis 运行完整验收。
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

# 导入 Celery 组件
from scripts.start_celery_fakeredis import (
    CeleryWorker, CeleryBeat, execute_task_async,
    register_task, fake_redis
)


def print_sql(title: str, sql: str, db_path: str = "data/postgres_real.db"):
    """打印 SQL 查询结果"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)
    
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


async def main():
    """主函数"""
    print("=" * 70)
    print("  最终验收测试 V1.0.0")
    print("=" * 70)
    print(f"  时间: {datetime.now().isoformat()}")
    print("=" * 70)
    
    # 注册任务
    def execute_task_handler(task_id):
        import asyncio
        from infrastructure.task_manager import get_task_manager
        tm = get_task_manager()
        return asyncio.run(tm.execute_task(task_id))
    
    register_task('execute_task', execute_task_handler)
    
    # 启动 Worker
    worker = CeleryWorker()
    worker.start()
    
    print("\n[测试 1] 创建 once 定时任务...")
    from infrastructure.task_manager import get_task_manager
    from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
    from domain.tasks import TaskStatus
    
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    result = await tm.create_scheduled_message(
        user_id="final_user",
        message="最终验收测试消息",
        run_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        title="🧪 最终验收"
    )
    
    task_id = result.get("task_id")
    print(f"  任务ID: {task_id}")
    
    # 通过 Celery 执行
    print("\n[测试 2] 通过 Celery Worker 执行...")
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value})
    
    celery_task_id = execute_task_async('execute_task', task_id)
    print(f"  Celery Task ID: {celery_task_id}")
    
    # 等待执行
    import time
    time.sleep(3)
    
    # 检查结果
    result = fake_redis.hgetall(f'celery-task-meta-{celery_task_id}')
    print(f"  Celery 任务状态: {result.get('status')}")
    
    # 检查任务状态
    task = await tm.get_task(task_id)
    print(f"  任务最终状态: {task.status.value}")
    
    # 数据库证据
    print("\n" + "=" * 70)
    print("  数据库证据")
    print("=" * 70)
    
    print_sql("task_runs", "SELECT * FROM task_runs ORDER BY created_at DESC LIMIT 10")
    print_sql("task_events", "SELECT * FROM task_events ORDER BY created_at DESC LIMIT 10")
    print_sql("tool_calls", "SELECT * FROM tool_calls ORDER BY created_at DESC LIMIT 10")
    print_sql("workflow_checkpoints", "SELECT * FROM workflow_checkpoints ORDER BY created_at DESC LIMIT 10")
    
    # Celery 证据
    print("\n" + "=" * 70)
    print("  Celery 证据")
    print("=" * 70)
    
    print(f"\n  Worker 处理任务数: {worker.processed}")
    print(f"  FakeRedis keys: {len(fake_redis.keys())}")
    
    # 显示任务元数据
    for key in fake_redis.keys('celery-task-meta-*'):
        meta = fake_redis.hgetall(key)
        print(f"\n  {key}:")
        print(f"    status: {meta.get('status')}")
        print(f"    name: {meta.get('name')}")
        print(f"    date_done: {meta.get('date_done')}")
    
    print("\n" + "=" * 70)
    print("  验收完成")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
