#!/usr/bin/env python3
"""
启动真实 Celery 服务 V2.0.0

使用真实 Redis 作为 broker。
"""

import os
import sys
import subprocess
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

# 检查 Redis 连接
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")

print("=" * 60)
print("  启动真实 Celery 服务")
print("=" * 60)
print(f"  REDIS_URL: {redis_url}")
print()

# 测试 Redis 连接
print("[1] 测试 Redis 连接...")
try:
    import redis
    r = redis.from_url(redis_url)
    r.ping()
    print("  ✅ Redis 连接成功")
except Exception as e:
    print(f"  ❌ Redis 连接失败: {e}")
    print()
    print("请先启动 Redis 服务:")
    print("  docker run -d -p 6379:6379 redis:7")
    print()
    print("或使用云服务:")
    print("  export REDIS_URL='redis://default:password@host:6379'")
    sys.exit(1)

# 设置环境变量
os.environ['CELERY_BROKER_URL'] = redis_url + '/0'
os.environ['CELERY_RESULT_BACKEND'] = redis_url + '/1'

print()
print("[2] 启动 Celery Worker...")

# 启动 Worker
worker_process = subprocess.Popen(
    [
        sys.executable, '-m', 'celery',
        '-A', 'infrastructure.celery_config',
        'worker',
        '--loglevel=info',
        '--concurrency=2',
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    bufsize=1,
    universal_newlines=True,
)

print(f"  Worker PID: {worker_process.pid}")

print()
print("[3] 启动 Celery Beat...")

# 启动 Beat
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

print()
print("=" * 60)
print("  服务已启动")
print("=" * 60)
print()
print("日志:")
print("  Worker: 查看 worker_process.stdout")
print("  Beat: 查看 beat_process.stdout")
print()
print("停止:")
print("  worker_process.terminate()")
print("  beat_process.terminate()")
print()

# 保持运行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n停止服务...")
    worker_process.terminate()
    beat_process.terminate()
    print("服务已停止")
