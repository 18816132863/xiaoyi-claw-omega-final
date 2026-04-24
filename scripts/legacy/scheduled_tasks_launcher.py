#!/usr/bin/env python3
"""
定时任务启动器（Python 版） - V1.0.0

功能：
1. 在后台持续运行
2. 每 15 分钟执行一次心跳
3. 支持优雅退出
4. 适合在没有 crontab 权限的环境使用

使用方式：
    # 前台运行
    python scripts/scheduled_tasks_launcher.py
    
    # 后台运行
    nohup python scripts/scheduled_tasks_launcher.py > logs/launcher.log 2>&1 &
    
    # 使用 screen
    screen -dmS openclaw-scheduler python scripts/scheduled_tasks_launcher.py
"""

import sys
import time
import signal
import subprocess
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


class ScheduledTasksLauncher:
    """定时任务启动器"""
    
    def __init__(self, root: Path = None):
        self.root = root or self._get_project_root()
        self.logs_dir = self.root / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.pid_file = self.logs_dir / "launcher.pid"
        self.running = True
        self.interval_seconds = 900  # 15 分钟
        
        # 信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _get_project_root(self) -> Path:
        current = Path(__file__).resolve().parent.parent
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        return Path(__file__).resolve().parent.parent
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print("\n🛑 收到停止信号")
        self.running = False
        self._cleanup()
    
    def _cleanup(self):
        """清理"""
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    def _save_pid(self):
        """保存 PID"""
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
    
    def _execute_heartbeat(self) -> bool:
        """执行心跳"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] 🔧 执行心跳...")
        
        try:
            # 执行心跳执行器
            result = subprocess.run(
                [sys.executable, str(self.root / "scripts/heartbeat_executor.py")],
                cwd=str(self.root),
                capture_output=True,
                text=True,
                timeout=300  # 5 分钟超时
            )
            
            if result.returncode == 0:
                print(f"[{timestamp}] ✅ 心跳完成")
                return True
            else:
                print(f"[{timestamp}] ⚠️  心跳异常 (exit code: {result.returncode})")
                if result.stderr:
                    print(f"错误: {result.stderr[:200]}")
                return False
        
        except subprocess.TimeoutExpired:
            print(f"[{timestamp}] ⚠️  心跳超时")
            return False
        
        except Exception as e:
            print(f"[{timestamp}] ❌ 心跳失败: {e}")
            return False
    
    def run(self):
        """运行启动器"""
        
        print("")
        print("=" * 60)
        print("  OpenClaw 定时任务启动器 V1.0.0")
        print("=" * 60)
        print("")
        print(f"⏰ 心跳间隔: {self.interval_seconds // 60} 分钟")
        print(f"📁 日志目录: {self.logs_dir}")
        print(f"🛑 停止方式: kill {os.getpid()}")
        print("")
        print("按 Ctrl+C 停止")
        print("")
        
        # 保存 PID
        self._save_pid()
        
        # 主循环
        while self.running:
            # 执行心跳
            self._execute_heartbeat()
            
            # 等待
            if self.running:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] 😴 等待 {self.interval_seconds // 60} 分钟...")
                
                # 分段睡眠，以便更快响应信号
                for _ in range(self.interval_seconds):
                    if not self.running:
                        break
                    time.sleep(1)
        
        # 清理
        self._cleanup()
        print("👋 启动器已停止")


def main():
    launcher = ScheduledTasksLauncher()
    launcher.run()


if __name__ == "__main__":
    main()
