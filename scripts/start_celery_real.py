#!/usr/bin/env python3
"""
启动真实 Celery 服务 V1.0.0
"""

import subprocess
import sys
import time
import os
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ['CELERY_BROKER_URL'] = 'redis://fake:6379/0'
os.environ['CELERY_RESULT_BACKEND'] = 'redis://fake:6379/1'

print("=" * 60)
print("  启动真实 Celery 服务")
print("=" * 60)
print(f"  工作目录: {project_root}")
print(f"  Broker: {os.environ['CELERY_BROKER_URL']}")
print("=" * 60)

# 启动 Worker
print("\n[1] 启动 Celery Worker...")
worker_process = subprocess.Popen(
    [
        sys.executable, '-m', 'celery',
        '-A', 'infrastructure.celery_config',
        'worker',
        '--loglevel=info',
        '--concurrency=2',
        '--pool=solo',  # 使用 solo 池避免多进程问题
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    bufsize=1,
    universal_newlines=True,
)

print(f"  Worker PID: {worker_process.pid}")

# 启动 Beat
print("\n[2] 启动 Celery Beat...")
beat_process = subprocess.Popen(
    [
        sys.executable, '-m', 'celery',
        '-A', 'infrastructure.celery_config',
        'beat',
        '--loglevel=info',
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    bufsize=1,
    universal_newlines=True,
)

print(f"  Beat PID: {beat_process.pid}")

print("\n[3] 服务已启动，等待日志...")
print("-" * 60)

# 读取日志
import threading
import queue

log_queue = queue.Queue()

def read_output(process, name):
    """读取进程输出"""
    try:
        for line in iter(process.stdout.readline, ''):
            if line:
                log_queue.put(f"[{name}] {line.strip()}")
    except:
        pass

# 启动日志读取线程
threading.Thread(target=read_output, args=(worker_process, "Worker"), daemon=True).start()
threading.Thread(target=read_output, args=(beat_process, "Beat"), daemon=True).start()

# 打印日志
start_time = time.time()
log_count = 0

while time.time() - start_time < 30:  # 运行 30 秒
    try:
        line = log_queue.get(timeout=1)
        print(line)
        log_count += 1
        
        # 收集到足够日志后退出
        if log_count > 50:
            break
            
    except queue.Empty:
        continue

print("\n" + "-" * 60)
print(f"  日志收集完成 ({log_count} 行)")
print("=" * 60)

# 清理
worker_process.terminate()
beat_process.terminate()
