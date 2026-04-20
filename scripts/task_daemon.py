#!/usr/bin/env python3
"""
任务系统守护进程 V1.0.0

整合调度器和执行器，持续运行。

使用方式：
    python scripts/task_daemon.py [--interval 1]
"""

import asyncio
import signal
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# 添加项目路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from infrastructure.task_manager import get_task_manager
from infrastructure.storage.repositories import SQLiteTaskRepository
from domain.tasks import TaskStatus


class TaskDaemon:
    """任务系统守护进程"""
    
    def __init__(self, check_interval: float = 1.0):
        self.check_interval = check_interval
        self.tm = get_task_manager()
        self.repo = SQLiteTaskRepository()
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
        print("  任务系统守护进程 V1.0.0")
        print("=" * 60)
        print(f"  PID: {os.getpid()}")
        print(f"  检查间隔: {self.check_interval} 秒")
        print(f"  启动时间: {datetime.now().isoformat()}")
        print(f"  数据库: {self.root / 'data' / 'tasks.db'}")
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
                # 1. 检查并投递到期任务
                await self._check_scheduled()
                
                # 2. 执行队列中的任务
                await self._process_queue()
                
                # 3. 处理待发送消息
                await self._process_pending_sends()
                
            except Exception as e:
                print(f"[Daemon] 错误: {e}")
                import traceback
                traceback.print_exc()
            
            await asyncio.sleep(self.check_interval)
        
        print("[Daemon] 已停止")
    
    async def _check_scheduled(self):
        """检查并投递到期任务"""
        from datetime import datetime
        
        now = datetime.now()
        tasks = await self.repo.list_pending_scheduled(now, limit=10)
        
        for task in tasks:
            try:
                # 获取锁
                locked = await self.repo.acquire_lock(task.task_id, lock_ttl=60)
                if not locked:
                    continue
                
                try:
                    # 更新状态为已入队
                    await self.repo.update(task.task_id, {
                        "status": TaskStatus.QUEUED.value
                    })
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 投递任务: {task.task_id[:8]}... ({task.task_type})")
                
                finally:
                    await self.repo.release_lock(task.task_id)
            
            except Exception as e:
                print(f"[Daemon] 投递任务失败: {e}")
    
    async def _process_queue(self):
        """执行队列中的任务"""
        queue_file = self.root / "data" / "task_queue.jsonl"
        
        if not queue_file.exists():
            return
        
        import json
        
        # 读取队列
        with open(queue_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            return
        
        # 处理任务
        processed = 0
        remaining = []
        
        for line in lines:
            try:
                entry = json.loads(line.strip())
                
                if entry.get("status") == "pending":
                    # 执行任务
                    result = await self.tm.execute_task(entry["task_id"])
                    
                    if result["success"]:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 执行成功: {entry['task_id'][:8]}...")
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 执行失败: {entry['task_id'][:8]}... - {result.get('error', '')}")
                    
                    processed += 1
                else:
                    remaining.append(line)
            
            except Exception as e:
                print(f"[Daemon] 处理失败: {e}")
                remaining.append(line)
        
        # 更新队列文件
        with open(queue_file, 'w', encoding='utf-8') as f:
            f.writelines(remaining)
        
        if processed > 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 处理了 {processed} 个任务")
    
    async def _process_pending_sends(self):
        """处理待发送消息"""
        pending_file = self.root / "reports" / "ops" / "pending_sends.jsonl"
        
        if not pending_file.exists():
            return
        
        import json
        
        # 读取待发送消息
        with open(pending_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            return
        
        # 这里只记录，实际发送由 AI 完成
        # 因为 Python 脚本无法直接调用 message 工具
        count = len(lines)
        
        if count > 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 待发送消息: {count} 条")
            
            # 写入通知文件
            notify_file = self.root / "reports" / "ops" / "notify_send.txt"
            with open(notify_file, 'w', encoding='utf-8') as f:
                f.write(f"PENDING_SENDS:{count}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="任务系统守护进程")
    parser.add_argument("--interval", "-i", type=float, default=1.0, help="检查间隔（秒）")
    parser.add_argument("--daemon", "-d", action="store_true", help="以守护进程方式运行")
    
    args = parser.parse_args()
    
    daemon = TaskDaemon(check_interval=args.interval)
    
    try:
        daemon.start()
    except KeyboardInterrupt:
        daemon.stop()


if __name__ == "__main__":
    main()
