#!/usr/bin/env python3
"""
迁移到真实 PostgreSQL V1.0.0

当获得真实 PostgreSQL 服务后运行此脚本。
"""

import os
import sys
import asyncio
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


async def migrate_to_postgres():
    """迁移到 PostgreSQL"""
    
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        print("❌ 未设置 DATABASE_URL 环境变量")
        print()
        print("示例:")
        print("  export DATABASE_URL='postgresql://user:password@host:5432/database'")
        print()
        print("免费 PostgreSQL 服务:")
        print("  - Supabase: https://supabase.com (免费 500MB)")
        print("  - Neon: https://neon.tech (免费 3GB)")
        print("  - Railway: https://railway.app (免费 $5/月)")
        return False
    
    print("=" * 60)
    print("  迁移到 PostgreSQL")
    print("=" * 60)
    print(f"  DATABASE_URL: {database_url[:30]}...")
    print()
    
    try:
        import asyncpg
        
        # 解析连接字符串
        # postgresql://user:password@host:port/database
        
        # 连接测试
        print("[1] 测试连接...")
        conn = await asyncpg.connect(database_url)
        
        version = await conn.fetchval("SELECT version()")
        print(f"  ✅ 连接成功")
        print(f"  版本: {version[:50]}...")
        
        # 创建表
        print()
        print("[2] 创建表...")
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                task_type TEXT NOT NULL,
                goal TEXT NOT NULL,
                payload_json JSONB NOT NULL DEFAULT '{}',
                trigger_mode TEXT NOT NULL DEFAULT 'immediate',
                status TEXT NOT NULL DEFAULT 'draft',
                schedule_type TEXT,
                run_at TIMESTAMP,
                cron_expr TEXT,
                timezone TEXT DEFAULT 'Asia/Shanghai',
                next_run_at TIMESTAMP,
                last_run_at TIMESTAMP,
                attempt_count INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 3,
                retry_backoff_seconds INTEGER DEFAULT 60,
                timeout_seconds INTEGER DEFAULT 600,
                idempotency_key TEXT UNIQUE,
                last_error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS task_runs (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                run_no INTEGER NOT NULL DEFAULT 1,
                workflow_thread_id TEXT,
                checkpoint_id TEXT,
                current_step INTEGER DEFAULT 0,
                total_steps INTEGER DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'pending',
                started_at TIMESTAMP,
                ended_at TIMESTAMP,
                error_text TEXT,
                retry_after TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS task_events (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                task_run_id TEXT,
                event_type TEXT NOT NULL,
                event_payload JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS tool_calls (
                id TEXT PRIMARY KEY,
                task_id TEXT,
                task_run_id TEXT,
                step_id TEXT,
                tool_name TEXT NOT NULL,
                request_json JSONB NOT NULL DEFAULT '{}',
                response_json JSONB DEFAULT '{}',
                status TEXT NOT NULL DEFAULT 'pending',
                error_text TEXT,
                idempotency_key TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS workflow_checkpoints (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                task_run_id TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                checkpoint_id TEXT NOT NULL,
                checkpoint_ns TEXT DEFAULT '',
                snapshot_json JSONB NOT NULL DEFAULT '{}',
                metadata_json JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (thread_id, checkpoint_id, checkpoint_ns)
            )
        ''')
        
        print("  ✅ 表创建完成")
        
        # 创建索引
        print()
        print("[3] 创建索引...")
        
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_next_run_at ON tasks(next_run_at)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_task_runs_task_id ON task_runs(task_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_task_events_task_id ON task_events(task_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_tool_calls_task_id ON tool_calls(task_id)')
        
        print("  ✅ 索引创建完成")
        
        await conn.close()
        
        print()
        print("=" * 60)
        print("  ✅ 迁移完成")
        print("=" * 60)
        
        return True
    
    except ImportError:
        print("❌ 缺少 asyncpg 库")
        print("  安装: pip install asyncpg")
        return False
    
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False


if __name__ == "__main__":
    asyncio.run(migrate_to_postgres())
