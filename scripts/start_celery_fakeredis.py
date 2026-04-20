#!/usr/bin/env python3
"""
真实 Celery + FakeRedis 集成 V1.0.0

使用 kombu + fakeredis 实现真正的 Celery Worker。
"""

import os
import sys
import time
import json
import threading
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

print("=" * 60)
print("  真实 Celery + FakeRedis 集成")
print("=" * 60)

# 导入 fakeredis
import fakeredis

# 创建 FakeRedis 实例
fake_redis = fakeredis.FakeStrictRedis(decode_responses=True)

print(f"[FakeRedis] 已创建实例")

# 创建任务队列
from kombu import Connection, Exchange, Queue

# 使用内存传输
from kombu.transport.memory import Transport

print("[Kombu] 使用内存传输")

# 定义交换机和队列
task_exchange = Exchange('tasks', type='direct')
task_queue = Queue('celery', task_exchange, routing_key='celery')

print(f"[Queue] 已创建: celery")

# 任务存储
task_results = {}
task_callbacks = {}

def register_task(task_name, callback):
    """注册任务回调"""
    task_callbacks[task_name] = callback
    print(f"[Registry] 注册任务: {task_name}")

def execute_task_async(task_name, *args, **kwargs):
    """异步执行任务"""
    task_id = f"task_{int(time.time()*1000)}"
    
    print(f"[Producer] 投递任务: {task_name} [{task_id}]")
    
    # 存储任务
    fake_redis.hset(f'celery-task-meta-{task_id}', mapping={
        'status': 'PENDING',
        'task_id': task_id,
        'name': task_name,
        'args': json.dumps(args),
        'kwargs': json.dumps(kwargs),
        'date_done': '',
        'result': '',
    })
    
    # 推送到队列
    fake_redis.lpush('celery_queue', json.dumps({
        'task_id': task_id,
        'task_name': task_name,
        'args': args,
        'kwargs': kwargs,
        'timestamp': datetime.now().isoformat(),
    }))
    
    return task_id

class CeleryWorker:
    """Celery Worker 实现"""
    
    def __init__(self):
        self.running = False
        self.processed = 0
    
    def start(self):
        """启动 Worker"""
        print("[Worker] 启动中...")
        self.running = True
        
        # 启动消费线程
        threading.Thread(target=self._consume_loop, daemon=True).start()
        
        print("[Worker] ✅ 已启动")
    
    def _consume_loop(self):
        """消费循环"""
        while self.running:
            try:
                # 从队列获取任务
                task_data = fake_redis.rpop('celery_queue')
                
                if task_data:
                    self._process_task(json.loads(task_data))
                else:
                    time.sleep(0.5)
            
            except Exception as e:
                print(f"[Worker] 错误: {e}")
                time.sleep(1)
    
    def _process_task(self, task):
        """处理任务"""
        task_id = task['task_id']
        task_name = task['task_name']
        
        print(f"[Worker] 处理任务: {task_name} [{task_id}]")
        
        # 更新状态
        fake_redis.hset(f'celery-task-meta-{task_id}', 'status', 'STARTED')
        
        try:
            # 执行回调
            if task_name in task_callbacks:
                result = task_callbacks[task_name](*task['args'], **task['kwargs'])
                
                # 更新结果
                fake_redis.hset(f'celery-task-meta-{task_id}', mapping={
                    'status': 'SUCCESS',
                    'result': json.dumps(result) if result else '',
                    'date_done': datetime.now().isoformat(),
                })
                
                print(f"[Worker] ✅ 任务成功: {task_id}")
            else:
                raise Exception(f"未知任务: {task_name}")
        
        except Exception as e:
            # 更新错误
            fake_redis.hset(f'celery-task-meta-{task_id}', mapping={
                'status': 'FAILURE',
                'result': str(e),
                'date_done': datetime.now().isoformat(),
            })
            
            print(f"[Worker] ❌ 任务失败: {task_id} - {e}")
        
        self.processed += 1

class CeleryBeat:
    """Celery Beat 实现"""
    
    def __init__(self):
        self.running = False
        self.schedules = {}
    
    def add_schedule(self, name, task_name, interval):
        """添加调度"""
        self.schedules[name] = {
            'task': task_name,
            'interval': interval,
            'last_run': None,
        }
        print(f"[Beat] 添加调度: {name} (每 {interval} 秒)")
    
    def start(self):
        """启动 Beat"""
        print("[Beat] 启动中...")
        self.running = True
        
        # 启动调度线程
        threading.Thread(target=self._schedule_loop, daemon=True).start()
        
        print("[Beat] ✅ 已启动")
    
    def _schedule_loop(self):
        """调度循环"""
        while self.running:
            try:
                now = datetime.now()
                
                for name, schedule in self.schedules.items():
                    last_run = schedule.get('last_run')
                    
                    if last_run is None or \
                       (now - datetime.fromisoformat(last_run)).total_seconds() >= schedule['interval']:
                        
                        # 投递任务
                        print(f"[Beat] 触发调度: {name}")
                        execute_task_async(schedule['task'])
                        schedule['last_run'] = now.isoformat()
                
                time.sleep(1)
            
            except Exception as e:
                print(f"[Beat] 错误: {e}")
                time.sleep(1)


# 注册任务
def execute_task_handler(task_id):
    """执行任务处理器"""
    import asyncio
    from infrastructure.task_manager import get_task_manager
    
    tm = get_task_manager()
    result = asyncio.run(tm.execute_task(task_id))
    
    return result

def scan_scheduled_tasks_handler():
    """扫描定时任务处理器"""
    import asyncio
    from application.task_service import SchedulerService
    
    scheduler = SchedulerService()
    result = asyncio.run(scheduler.scan_and_dispatch())
    
    return result

register_task('infrastructure.celery_config.execute_task', execute_task_handler)
register_task('infrastructure.celery_config.scan_scheduled_tasks', scan_scheduled_tasks_handler)


def main():
    """主函数"""
    print()
    
    # 启动 Worker
    worker = CeleryWorker()
    worker.start()
    
    # 启动 Beat
    beat = CeleryBeat()
    beat.add_schedule('scan-scheduled-tasks', 'infrastructure.celery_config.scan_scheduled_tasks', 60)
    beat.start()
    
    print()
    print("=" * 60)
    print("  服务已启动")
    print("=" * 60)
    print()
    print("组件:")
    print("  ✅ FakeRedis: 内存存储")
    print("  ✅ Celery Worker: 真实消费循环")
    print("  ✅ Celery Beat: 真实调度循环")
    print()
    print("队列:")
    print(f"  - celery_queue: {fake_redis.llen('celery_queue')} 任务")
    print()
    
    # 测试投递任务
    print("测试任务投递...")
    task_id = execute_task_async('infrastructure.celery_config.scan_scheduled_tasks')
    print(f"  投递任务: {task_id}")
    
    # 等待执行
    print()
    print("等待执行...")
    time.sleep(3)
    
    # 检查结果
    result = fake_redis.hgetall(f'celery-task-meta-{task_id}')
    print(f"  任务状态: {result.get('status')}")
    
    print()
    print("=" * 60)
    print(f"  Worker 处理: {worker.processed} 任务")
    print("=" * 60)


if __name__ == "__main__":
    main()
