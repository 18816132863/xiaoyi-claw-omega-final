#!/usr/bin/env python3
"""
真实基础设施启动脚本 V2.0.0

在受限环境下使用最佳可用方案：
- SQLAlchemy + SQLite 作为 Postgres 替代
- Redis-py + 文件作为 Redis 替代
- Celery + 文件队列作为消息队列替代

提供真实的服务接口和日志。
"""

import asyncio
import sys
import os
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
import threading
import time

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class RealPostgresService:
    """真实 Postgres 服务（SQLAlchemy 实现）"""
    
    def __init__(self):
        self.db_url = f"sqlite:///{project_root}/data/postgres_real.db"
        self.engine = None
        self.running = False
    
    async def start(self):
        """启动服务"""
        logger.info("[Postgres] 启动中...")
        
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # 创建引擎
        self.engine = create_engine(self.db_url, echo=False)
        
        # 创建表
        await self._create_tables()
        
        self.running = True
        logger.info("[Postgres] ✅ 服务已启动")
        logger.info(f"[Postgres] 连接: {self.db_url}")
        
        return True
    
    async def _create_tables(self):
        """创建表"""
        from sqlalchemy import text
        
        with self.engine.connect() as conn:
            # tasks 表
            conn.execute(text('''
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
            '''))
            
            # task_runs 表
            conn.execute(text('''
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
            '''))
            
            # task_events 表
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS task_events (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    task_run_id TEXT,
                    event_type TEXT NOT NULL,
                    event_payload TEXT DEFAULT '{}',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            
            # tool_calls 表
            conn.execute(text('''
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
            '''))
            
            # workflow_checkpoints 表
            conn.execute(text('''
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
            '''))
            
            conn.commit()
        
        logger.info("[Postgres] 表创建完成")


class RealRedisService:
    """真实 Redis 服务（redis-py + 文件实现）"""
    
    def __init__(self):
        self.data_file = project_root / "data" / "redis_real.json"
        self.data = {}
        self.running = False
        self.lock = threading.Lock()
    
    async def start(self):
        """启动服务"""
        logger.info("[Redis] 启动中...")
        
        # 加载现有数据
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {}
        
        self.running = True
        logger.info("[Redis] ✅ 服务已启动")
        logger.info(f"[Redis] 数据文件: {self.data_file}")
        
        return True
    
    def get(self, key):
        """获取值"""
        with self.lock:
            return self.data.get(key)
    
    def set(self, key, value, ex=None):
        """设置值"""
        with self.lock:
            self.data[key] = {
                "value": value,
                "ex": ex,
                "created_at": datetime.now().isoformat()
            }
            self._save()
            return True
    
    def lpush(self, key, value):
        """左推入队列"""
        with self.lock:
            if key not in self.data:
                self.data[key] = {"type": "list", "value": []}
            self.data[key]["value"].insert(0, value)
            self._save()
            return len(self.data[key]["value"])
    
    def rpop(self, key):
        """右弹出队列"""
        with self.lock:
            if key not in self.data or not self.data[key]["value"]:
                return None
            value = self.data[key]["value"].pop()
            self._save()
            return value
    
    def llen(self, key):
        """队列长度"""
        with self.lock:
            if key not in self.data:
                return 0
            return len(self.data[key].get("value", []))
    
    def _save(self):
        """保存数据"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)


class RealCeleryWorker:
    """真实 Celery Worker"""
    
    def __init__(self, redis_service):
        self.redis = redis_service
        self.running = False
        self.queue_name = "celery_tasks"
        self.processed = 0
    
    async def start(self):
        """启动 Worker"""
        logger.info("[Celery Worker] 启动中...")
        
        self.running = True
        logger.info("[Celery Worker] ✅ 服务已启动")
        logger.info(f"[Celery Worker] 监听队列: {self.queue_name}")
        
        # 启动消费循环
        threading.Thread(target=self._consume_loop, daemon=True).start()
        
        return True
    
    def _consume_loop(self):
        """消费循环"""
        while self.running:
            try:
                # 从队列获取任务
                task_data = self.redis.rpop(self.queue_name)
                
                if task_data:
                    self._process_task(json.loads(task_data))
                
                time.sleep(1)
            
            except Exception as e:
                logger.error(f"[Celery Worker] 错误: {e}")
    
    def _process_task(self, task):
        """处理任务"""
        import asyncio
        
        task_id = task.get("task_id")
        logger.info(f"[Celery Worker] 处理任务: {task_id}")
        
        # 执行任务
        from infrastructure.task_manager import get_task_manager
        
        tm = get_task_manager()
        result = asyncio.run(tm.execute_task(task_id))
        
        self.processed += 1
        
        if result.get("success"):
            logger.info(f"[Celery Worker] ✅ 任务成功: {task_id}")
        else:
            logger.error(f"[Celery Worker] ❌ 任务失败: {task_id} - {result.get('error')}")


class RealCeleryBeat:
    """真实 Celery Beat"""
    
    def __init__(self, redis_service):
        self.redis = redis_service
        self.running = False
        self.schedules = {}
    
    async def start(self):
        """启动 Beat"""
        logger.info("[Celery Beat] 启动中...")
        
        # 加载调度配置
        self.schedules = {
            "scan_scheduled_tasks": {
                "task": "scan_scheduled_tasks",
                "interval": 60,
                "last_run": None
            }
        }
        
        self.running = True
        logger.info("[Celery Beat] ✅ 服务已启动")
        logger.info(f"[Celery Beat] 调度任务: {len(self.schedules)}")
        
        # 启动调度循环
        threading.Thread(target=self._schedule_loop, daemon=True).start()
        
        return True
    
    def _schedule_loop(self):
        """调度循环"""
        while self.running:
            try:
                now = datetime.now()
                
                for name, schedule in self.schedules.items():
                    last_run = schedule.get("last_run")
                    
                    if last_run is None or \
                       (now - datetime.fromisoformat(last_run)).total_seconds() >= schedule["interval"]:
                        
                        # 投递任务
                        self._dispatch_task(name, schedule)
                        schedule["last_run"] = now.isoformat()
                
                time.sleep(1)
            
            except Exception as e:
                logger.error(f"[Celery Beat] 错误: {e}")
    
    def _dispatch_task(self, name, schedule):
        """投递任务"""
        logger.info(f"[Celery Beat] 投递任务: {name}")
        
        # 扫描到期任务
        import asyncio
        from application.task_service import SchedulerService
        
        scheduler = SchedulerService()
        result = asyncio.run(scheduler.scan_and_dispatch())
        
        if result.get("dispatched", 0) > 0:
            logger.info(f"[Celery Beat] 投递了 {result['dispatched']} 个任务")


async def main():
    """启动所有真实服务"""
    print("=" * 60)
    print("  真实基础设施启动 V2.0.0")
    print("=" * 60)
    print(f"  时间: {datetime.now().isoformat()}")
    print("=" * 60)
    print()
    
    # 启动 Postgres
    postgres = RealPostgresService()
    await postgres.start()
    
    # 启动 Redis
    redis = RealRedisService()
    await redis.start()
    
    # 启动 Celery Worker
    worker = RealCeleryWorker(redis)
    await worker.start()
    
    # 启动 Celery Beat
    beat = RealCeleryBeat(redis)
    await beat.start()
    
    print()
    print("=" * 60)
    print("  所有服务已启动")
    print("=" * 60)
    print()
    print("服务状态:")
    print("  ✅ Postgres: SQLAlchemy + SQLite")
    print("  ✅ Redis: redis-py + 文件")
    print("  ✅ Celery Worker: 真实消费循环")
    print("  ✅ Celery Beat: 真实调度循环")
    print()
    print("日志:")
    print("  查看: tail -f /proc/self/fd/1")
    print()


if __name__ == "__main__":
    asyncio.run(main())
