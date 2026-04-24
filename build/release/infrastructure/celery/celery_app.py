"""
Celery 应用 V1.0.0

职责：
- 异步任务执行
- 定时任务调度
- 失败重试
"""

from celery import Celery
from pathlib import Path
import json
import sys

# 添加项目路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# 创建 Celery 应用
app = Celery(
    'openclaw_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# 配置
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=60,
    task_max_retries=3,
)


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def execute_task(self, task_id: str):
    """执行任务"""
    try:
        import asyncio
        from infrastructure.task_manager import get_task_manager
        
        tm = get_task_manager()
        
        # 运行异步任务
        result = asyncio.run(tm.execute_task(task_id))
        
        if not result.get("success"):
            # 重试
            raise Exception(result.get("error", "执行失败"))
        
        return result
    
    except Exception as e:
        # 重试
        raise self.retry(exc=e)


@app.task(bind=True)
def send_scheduled_message(self, task_id: str, message: str, channel: str = "xiaoyi-channel"):
    """发送定时消息"""
    try:
        from infrastructure.tool_adapters.message_adapter import MessageSenderAdapter
        import asyncio
        
        adapter = MessageSenderAdapter()
        result = asyncio.run(adapter.send(
            channel=channel,
            target="default",
            message=message
        ))
        
        if not result.get("success"):
            raise Exception(result.get("error", "发送失败"))
        
        return result
    
    except Exception as e:
        raise self.retry(exc=e)


@app.task
def scan_scheduled_tasks():
    """扫描定时任务"""
    import asyncio
    from application.task_service import SchedulerService
    
    scheduler = SchedulerService()
    result = asyncio.run(scheduler.scan_and_dispatch())
    
    return result


@app.task
def cleanup_old_tasks(days: int = 30):
    """清理旧任务"""
    from datetime import datetime, timedelta
    import sqlite3
    from infrastructure.storage.sqlite_utils import serialize_datetime
    
    root = project_root
    db_path = str(root / "data" / "tasks.db")
    
    cutoff = datetime.now() - timedelta(days=days)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 删除已完成的旧任务
    cursor.execute('''
        DELETE FROM tasks
        WHERE status IN ('succeeded', 'failed', 'cancelled')
          AND created_at < ?
    ''', (serialize_datetime(cutoff),))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return {"deleted": deleted}


# Celery Beat 调度配置
app.conf.beat_schedule = {
    'scan-scheduled-tasks': {
        'task': 'infrastructure.celery.celery_app.scan_scheduled_tasks',
        'schedule': 60.0,  # 每 60 秒
    },
    'cleanup-old-tasks': {
        'task': 'infrastructure.celery.celery_app.cleanup_old_tasks',
        'schedule': 86400.0,  # 每天
    },
}
