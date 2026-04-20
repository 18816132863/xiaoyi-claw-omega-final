#!/usr/bin/env python3
"""
统一任务守护进程 V2.0.0

整合调度器和执行器，持续运行。

使用方式：
    python scripts/task_daemon_v2.py [--interval 5]
"""

import asyncio
import signal
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# 添加项目路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from application.task_service import TaskService, SchedulerService
from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
from domain.tasks import TaskStatus


class TaskDaemon:
    """任务守护进程"""
    
    def __init__(self, check_interval: float = 5.0):
        self.check_interval = check_interval
        self.task_repo = SQLiteTaskRepository()
        self.task_service = TaskService(task_repo=self.task_repo)
        self.scheduler = SchedulerService(task_repo=self.task_repo)
        self.running = False
        self.root = project_root
        
        # PID 文件
        self.pid_file = self.root / "data" / "task_daemon.pid"
        
        # 注册信号处理
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
    
    def _handle_signal(self, signum, frame):
        """处理终止信号"""
        print(f"\n[Daemon] 收到信号 {signum}，正在停止...")
        self.stop()
    
    def start(self):
        """启动守护进程"""
        # 写入 PID
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        print("=" * 60)
        print("  任务守护进程 V2.0.0")
        print("=" * 60)
        print(f"  PID: {os.getpid()}")
        print(f"  检查间隔: {self.check_interval} 秒")
        print(f"  启动时间: {datetime.now().isoformat()}")
        print("=" * 60)
        print("  按 Ctrl+C 停止")
        print("=" * 60)
        print()
        
        self.running = True
        asyncio.run(self._run_loop())
    
    def stop(self):
        """停止守护进程"""
        self.running = False
        
        # 删除 PID 文件
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    async def _run_loop(self):
        """运行循环"""
        while self.running:
            try:
                # 1. 扫描并投递到期任务
                result = await self.scheduler.scan_and_dispatch()
                if result["dispatched"] > 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 投递 {result['dispatched']} 个任务")
                
                # 2. 执行队列中的任务
                executed = await self._process_queue()
                if executed > 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 执行 {executed} 个任务")
                
            except Exception as e:
                print(f"[Daemon] 错误: {e}")
                import traceback
                traceback.print_exc()
            
            await asyncio.sleep(self.check_interval)
        
        print("[Daemon] 已停止")
    
    async def _process_queue(self) -> int:
        """执行队列中的任务"""
        queue_file = self.root / "data" / "task_queue.jsonl"
        
        if not queue_file.exists():
            return 0
        
        # 读取队列
        with open(queue_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            return 0
        
        # 处理任务
        processed = 0
        remaining = []
        
        for line in lines:
            try:
                entry = json.loads(line.strip())
                
                if entry.get("status") == "pending":
                    # 执行任务
                    result = await self.task_service.execute_task(entry["task_id"])
                    
                    if result.get("success"):
                        print(f"  ✓ {entry['task_id'][:8]}...")
                    else:
                        print(f"  ✗ {entry['task_id'][:8]}... - {result.get('error', '')}")
                    
                    processed += 1
                else:
                    remaining.append(line)
            
            except Exception as e:
                print(f"[Daemon] 处理失败: {e}")
                remaining.append(line)
        
        # 更新队列文件
        with open(queue_file, 'w', encoding='utf-8') as f:
            f.writelines(remaining)
        
        return processed


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="任务守护进程")
    parser.add_argument("--interval", "-i", type=float, default=5.0, help="检查间隔（秒）")
    
    args = parser.parse_args()
    
    daemon = TaskDaemon(check_interval=args.interval)
    
    try:
        daemon.start()
    except KeyboardInterrupt:
        daemon.stop()


if __name__ == "__main__":
    main()
