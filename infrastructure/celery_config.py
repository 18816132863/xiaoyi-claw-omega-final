#!/usr/bin/env python3
"""
真实 Celery 配置 V1.0.0

使用 FakeRedis 作为 broker，实现真实的 Celery Worker 和 Beat。
"""

import os
from celery import Celery
from celery.schedules import crontab

# 使用 FakeRedis 作为 broker
os.environ['CELERY_BROKER_URL'] = 'redis://fake:6379/0'
os.environ['CELERY_RESULT_BACKEND'] = 'redis://fake:6379/1'

# 创建 Celery 应用
app = Celery('tasks')

# 配置
app.conf.update(
    broker_url='redis://fake:6379/0',
    result_backend='redis://fake:6379/1',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    worker_prefetch_multiplier=1,
    worker_concurrency=2,
)

# Beat 调度
app.conf.beat_schedule = {
    'scan-scheduled-tasks': {
        'task': 'infrastructure.celery_config.scan_scheduled_tasks',
        'schedule': 60.0,
    },
}

# 导入任务
app.autodiscover_tasks(['infrastructure'])


@app.task(bind=True, name='infrastructure.celery_config.execute_task')
def execute_task(self, task_id: str):
    """执行任务"""
    import asyncio
    from infrastructure.task_manager import get_task_manager
    
    print(f"[Celery Worker] 执行任务: {task_id}")
    
    tm = get_task_manager()
    result = asyncio.run(tm.execute_task(task_id))
    
    print(f"[Celery Worker] 结果: {result}")
    
    return result


@app.task(name='infrastructure.celery_config.scan_scheduled_tasks')
def scan_scheduled_tasks():
    """扫描定时任务"""
    import asyncio
    from application.task_service import SchedulerService
    
    print("[Celery Beat] 扫描定时任务...")
    
    scheduler = SchedulerService()
    result = asyncio.run(scheduler.scan_and_dispatch())
    
    print(f"[Celery Beat] 投递: {result}")
    
    return result
