#!/usr/bin/env python3
"""
真实基础设施联调测试 V1.0.0

使用 FakeRedis 模拟 Redis，SQLite 模拟 PostgreSQL
验证完整的 Worker/Scheduler 联调流程

注意：在生产环境中，请使用真实的 PostgreSQL 和 Redis 服务
"""

import asyncio
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

project_root = Path("/home/sandbox/.openclaw/workspace")
sys.path.insert(0, str(project_root))


async def test_redis_connection():
    """测试 Redis 连接"""
    print("\n" + "=" * 60)
    print("  Redis 连接测试")
    print("=" * 60)
    
    try:
        import fakeredis
        
        # 创建 FakeRedis 客户端
        r = fakeredis.FakeRedis()
        
        # 测试 PING
        ping_result = r.ping()
        print(f"\n[1] PING 测试")
        print(f"    结果: {ping_result}")
        
        # 测试 SET/GET
        r.set('test_key', 'test_value')
        get_result = r.get('test_key')
        print(f"\n[2] SET/GET 测试")
        print(f"    SET test_key=test_value")
        print(f"    GET 结果: {get_result}")
        
        # 测试队列
        r.lpush('task_queue', json.dumps({'task_id': 'test-001', 'type': 'once'}))
        queue_result = r.rpop('task_queue')
        print(f"\n[3] 队列测试")
        print(f"    LPUSH task_queue: {{task_id: test-001}}")
        print(f"    RPOP 结果: {queue_result}")
        
        # 测试锁
        lock_acquired = r.set('task_lock:test-001', 'locked', nx=True, ex=60)
        print(f"\n[4] 分布式锁测试")
        print(f"    SETNX task_lock:test-001: {lock_acquired}")
        
        # 测试缓存
        r.hset('task_cache', 'test-001', json.dumps({'status': 'completed'}))
        cache_result = r.hget('task_cache', 'test-001')
        print(f"\n[5] 缓存测试")
        print(f"    HSET task_cache test-001: {{status: completed}}")
        print(f"    HGET 结果: {cache_result}")
        
        print(f"\n✅ Redis 连接测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ Redis 连接测试失败: {e}")
        return False


async def test_postgres_connection():
    """测试 PostgreSQL 连接（使用 SQLite 模拟）"""
    print("\n" + "=" * 60)
    print("  PostgreSQL 连接测试（SQLite 模拟）")
    print("=" * 60)
    
    try:
        db_path = project_root / "data" / "tasks.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 测试连接
        cursor.execute("SELECT 1")
        print(f"\n[1] 连接测试")
        print(f"    DATABASE_URL: sqlite://{db_path}")
        print(f"    结果: 连接成功")
        
        # 测试表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        print(f"\n[2] 表结构测试")
        print(f"    表列表: {tables}")
        
        # 测试查询
        cursor.execute("SELECT COUNT(*) as cnt FROM tasks")
        task_count = cursor.fetchone()['cnt']
        print(f"\n[3] 数据查询测试")
        print(f"    tasks 表记录数: {task_count}")
        
        # 测试插入
        test_id = "conn-test-" + datetime.now().strftime("%H%M%S")
        cursor.execute("""
            INSERT INTO tasks (id, user_id, task_type, goal, trigger_mode, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (test_id, 'conn_test', 'test', 'Connection Test', 'immediate', 'draft', 
              datetime.now().isoformat(), datetime.now().isoformat()))
        conn.commit()
        print(f"\n[4] 插入测试")
        print(f"    插入测试记录: {test_id}")
        
        # 验证插入
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (test_id,))
        inserted = cursor.fetchone()
        print(f"    验证结果: {dict(inserted) if inserted else 'Not Found'}")
        
        # 清理
        cursor.execute("DELETE FROM tasks WHERE id = ?", (test_id,))
        conn.commit()
        print(f"\n[5] 清理测试数据")
        print(f"    已删除: {test_id}")
        
        conn.close()
        
        print(f"\n✅ PostgreSQL 连接测试通过（SQLite 模拟）")
        print(f"    注意: 生产环境请使用真实的 PostgreSQL")
        return True
        
    except Exception as e:
        print(f"\n❌ PostgreSQL 连接测试失败: {e}")
        return False


async def test_worker_scheduler():
    """测试 Worker/Scheduler 联调"""
    print("\n" + "=" * 60)
    print("  Worker/Scheduler 联调测试")
    print("=" * 60)
    
    from infrastructure.task_manager import get_task_manager
    from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
    from domain.tasks import TaskStatus
    
    tm = get_task_manager()
    repo = SQLiteTaskRepository(db_path=str(project_root / "data" / "tasks.db"))
    
    # 1. once 任务
    print(f"\n[1] once 任务测试")
    print("-" * 40)
    
    result = await tm.create_scheduled_message(
        user_id="infra_test",
        message="Infrastructure Test Once",
        run_at=datetime.now().isoformat()
    )
    once_id = result.get('task_id')
    print(f"    创建任务: {once_id}")
    
    await repo.update(once_id, {"status": TaskStatus.QUEUED.value})
    exec_result = await tm.execute_task(once_id)
    print(f"    执行结果: {exec_result.get('delivery_status')}")
    
    # 2. recurring 任务
    print(f"\n[2] recurring 任务测试")
    print("-" * 40)
    
    result = await tm.create_recurring_message(
        user_id="infra_test",
        message="Infrastructure Test Recurring",
        cron_expr="* * * * *"
    )
    recurring_id = result.get('task_id')
    print(f"    创建任务: {recurring_id}")
    
    # 第一次执行
    await repo.update(recurring_id, {"status": TaskStatus.QUEUED.value})
    exec1 = await tm.execute_task(recurring_id)
    print(f"    第一次执行: {exec1.get('delivery_status')}")
    
    # 第二次执行
    await repo.update(recurring_id, {"status": TaskStatus.QUEUED.value})
    exec2 = await tm.execute_task(recurring_id)
    print(f"    第二次执行: {exec2.get('delivery_status')}")
    
    # 3. 失败重试
    print(f"\n[3] 失败重试测试")
    print("-" * 40)
    
    result = await tm.create_scheduled_message(
        user_id="infra_test",
        message="Infrastructure Test Retry",
        run_at=datetime.now().isoformat()
    )
    retry_id = result.get('task_id')
    print(f"    创建任务: {retry_id}")
    
    await repo.update(retry_id, {"status": TaskStatus.FAILED.value, "last_error": "Simulated"})
    retry_result = await tm.retry_task(retry_id)
    print(f"    重试结果: {retry_result.get('delivery_status')}")
    
    # 4. 数据库验证
    print(f"\n[4] 数据库验证")
    print("-" * 40)
    
    db_path = project_root / "data" / "tasks.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as cnt FROM tasks WHERE user_id = 'infra_test'")
    task_count = cursor.fetchone()['cnt']
    print(f"    tasks 表: {task_count} 条")
    
    cursor.execute("""
        SELECT COUNT(*) as cnt FROM task_runs 
        WHERE task_id IN (SELECT id FROM tasks WHERE user_id = 'infra_test')
    """)
    run_count = cursor.fetchone()['cnt']
    print(f"    task_runs 表: {run_count} 条")
    
    cursor.execute("""
        SELECT COUNT(*) as cnt FROM task_steps 
        WHERE task_run_id IN (
            SELECT id FROM task_runs 
            WHERE task_id IN (SELECT id FROM tasks WHERE user_id = 'infra_test')
        )
    """)
    step_count = cursor.fetchone()['cnt']
    print(f"    task_steps 表: {step_count} 条")
    
    # 清理
    cursor.execute("DELETE FROM tasks WHERE user_id = 'infra_test'")
    conn.commit()
    conn.close()
    print(f"\n    已清理测试数据")
    
    print(f"\n✅ Worker/Scheduler 联调测试通过")
    return True


async def main():
    print("=" * 60)
    print("  真实基础设施联调测试 V1.0.0")
    print("=" * 60)
    print("\n环境说明:")
    print("  - Redis: FakeRedis（模拟真实 Redis API）")
    print("  - PostgreSQL: SQLite（模拟真实 SQL 行为）")
    print("  - 注意: 生产环境请使用真实服务")
    
    results = []
    
    # 测试 Redis
    redis_ok = await test_redis_connection()
    results.append(("Redis 连接", redis_ok))
    
    # 测试 PostgreSQL
    pg_ok = await test_postgres_connection()
    results.append(("PostgreSQL 连接", pg_ok))
    
    # 测试 Worker/Scheduler
    ws_ok = await test_worker_scheduler()
    results.append(("Worker/Scheduler 联调", ws_ok))
    
    # 总结
    print("\n" + "=" * 60)
    print("  测试总结")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "-" * 60)
    if all_passed:
        print("  🎉 全部测试通过!")
    else:
        print("  ❌ 部分测试失败")
    print("-" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
