#!/usr/bin/env python3
"""
启动本地 Celery 服务 V1.0.0
"""

import subprocess
import sys
import os
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

# 确保 data 目录存在
Path("data").mkdir(exist_ok=True)

print("=" * 60)
print("  启动本地 Celery 服务")
print("=" * 60)
print(f"  Broker: SQLite (data/celery_broker.db)")
print(f"  Backend: SQLite (data/celery_results.db)")
print("=" * 60)

# 启动 Worker
print("\n[1] 启动 Celery Worker...")
worker_process = subprocess.Popen(
    [
        sys.executable, '-m', 'celery',
        '-A', 'infrastructure.local_celery',
        'worker',
        '--loglevel=info',
        '--concurrency=2',
        '--pool=solo',
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
        '-A', 'infrastructure.local_celery',
        'beat',
        '--loglevel=info',
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    bufsize=1,
    universal_newlines=True,
)
print(f"  Beat PID: {beat_process.pid}")

print("\n" + "=" * 60)
print("  服务已启动")
print("=" * 60)
print()
print("停止: Ctrl+C")
print()

try:
    # 实时输出日志
    import threading
    import queue
    
    log_queue = queue.Queue()
    
    def read_output(process, name):
        try:
            for line in iter(process.stdout.readline, ''):
                if line:
                    log_queue.put(f"[{name}] {line.strip()}")
        except:
            pass
    
    threading.Thread(target=read_output, args=(worker_process, "Worker"), daemon=True).start()
    threading.Thread(target=read_output, args=(beat_process, "Beat"), daemon=True).start()
    
    while True:
        try:
            line = log_queue.get(timeout=1)
            print(line)
        except queue.Empty:
            continue
            
except KeyboardInterrupt:
    print("\n\n停止服务...")
    worker_process.terminate()
    beat_process.terminate()
    print("服务已停止")
