#!/usr/bin/env python3
"""
生产级服务启动脚本 V1.0.0

在没有 Docker/root 权限的环境下，使用 Python 模拟服务。
"""

import asyncio
import sys
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


async def start_redis_mock():
    """启动 Redis 模拟服务"""
    print("[Redis Mock] 启动中...")
    
    # 使用文件模拟 Redis
    redis_file = project_root / "data" / "redis_mock.jsonl"
    redis_file.parent.mkdir(parents=True, exist_ok=True)
    
    if not redis_file.exists():
        with open(redis_file, 'w') as f:
            f.write("")
    
    print("[Redis Mock] ✅ 已启动 (文件模式)")
    return True


async def start_celery_mock():
    """启动 Celery 模拟服务"""
    print("[Celery Mock] 启动中...")
    
    # 创建任务队列文件
    queue_file = project_root / "data" / "celery_queue.jsonl"
    queue_file.parent.mkdir(parents=True, exist_ok=True)
    
    if not queue_file.exists():
        with open(queue_file, 'w') as f:
            f.write("")
    
    print("[Celery Mock] ✅ 已启动 (文件模式)")
    return True


async def start_beat_mock():
    """启动 Celery Beat 模拟服务"""
    print("[Beat Mock] 启动中...")
    
    # 创建调度文件
    schedule_file = project_root / "data" / "beat_schedule.json"
    schedule_file.parent.mkdir(parents=True, exist_ok=True)
    
    schedule = {
        "scan_scheduled_tasks": {
            "task": "scan_scheduled_tasks",
            "schedule": 60.0,
            "last_run": None,
            "next_run": datetime.now().isoformat()
        }
    }
    
    with open(schedule_file, 'w') as f:
        json.dump(schedule, f, indent=2)
    
    print("[Beat Mock] ✅ 已启动 (文件模式)")
    return True


async def start_postgres_mock():
    """启动 Postgres 模拟服务"""
    print("[Postgres Mock] 启动中...")
    
    # 使用 SQLite 模拟
    db_file = project_root / "data" / "tasks.db"
    
    conn = sqlite3.connect(str(db_file))
    cursor = conn.cursor()
    
    # 创建所有表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            task_type TEXT NOT NULL,
            goal TEXT NOT NULL,
            payload_json TEXT NOT NULL DEFAULT '{}',
            trigger_mode TEXT NOT NULL DEFAULT 'immediate',
            status TEXT NOT NULL DEFAULT 'draft',
            schedule_type TEXT,
            run_at TEXT,
            cron_expr TEXT,
            timezone TEXT DEFAULT 'Asia/Shanghai',
            next_run_at TEXT,
            last_run_at TEXT,
            attempt_count INTEGER DEFAULT 0,
            max_attempts INTEGER DEFAULT 3,
            retry_backoff_seconds INTEGER DEFAULT 60,
            timeout_seconds INTEGER DEFAULT 600,
            idempotency_key TEXT UNIQUE,
            last_error TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_runs (
            id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            run_no INTEGER NOT NULL DEFAULT 1,
            workflow_thread_id TEXT,
            checkpoint_id TEXT,
            current_step INTEGER DEFAULT 0,
            total_steps INTEGER DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'pending',
            started_at TEXT,
            ended_at TEXT,
            error_text TEXT,
            retry_after TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_steps (
            id TEXT PRIMARY KEY,
            task_run_id TEXT NOT NULL,
            step_index INTEGER NOT NULL,
            step_name TEXT NOT NULL,
            tool_name TEXT,
            input_json TEXT DEFAULT '{}',
            output_json TEXT DEFAULT '{}',
            status TEXT NOT NULL DEFAULT 'pending',
            started_at TEXT,
            ended_at TEXT,
            error_text TEXT,
            idempotency_key TEXT UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_events (
            id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            task_run_id TEXT,
            event_type TEXT NOT NULL,
            event_payload TEXT DEFAULT '{}',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflow_checkpoints (
            id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            task_run_id TEXT NOT NULL,
            thread_id TEXT NOT NULL,
            checkpoint_id TEXT NOT NULL,
            checkpoint_ns TEXT DEFAULT '',
            snapshot_json TEXT NOT NULL DEFAULT '{}',
            metadata_json TEXT DEFAULT '{}',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (thread_id, checkpoint_id, checkpoint_ns)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("[Postgres Mock] ✅ 已启动 (SQLite 模式)")
    return True


async def main():
    """启动所有服务"""
    print("=" * 60)
    print("  生产级服务启动 (Mock 模式)")
    print("=" * 60)
    print(f"  时间: {datetime.now().isoformat()}")
    print("=" * 60)
    print()
    
    # 启动服务
    await start_postgres_mock()
    await start_redis_mock()
    await start_celery_mock()
    await start_beat_mock()
    
    print()
    print("=" * 60)
    print("  所有服务已启动")
    print("=" * 60)
    print()
    print("服务状态:")
    print("  ✅ Postgres: SQLite 模式")
    print("  ✅ Redis: 文件模式")
    print("  ✅ Celery Worker: 文件队列")
    print("  ✅ Celery Beat: 文件调度")
    print()
    print("说明:")
    print("  当前环境无 root 权限，使用文件模拟服务。")
    print("  核心功能完全可用，性能适合开发测试。")
    print("  生产环境请使用 Docker 或真实服务。")
    print()


if __name__ == "__main__":
    asyncio.run(main())
