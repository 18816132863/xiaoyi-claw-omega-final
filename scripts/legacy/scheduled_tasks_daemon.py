#!/usr/bin/env python3
"""
定时任务守护进程 V2.0.0

特性：
1. 完全后台运行，不依赖任何会话
2. 独立的进程组，不受父进程影响
3. 自动重启机制
4. 信号隔离，不会被意外终止
5. 独立的日志和 PID 管理

使用方式：
    # 启动守护进程
    python scripts/scheduled_tasks_daemon.py start
    
    # 停止守护进程
    python scripts/scheduled_tasks_daemon.py stop
    
    # 查看状态
    python scripts/scheduled_tasks_daemon.py status
"""

import sys
import os
import time
import signal
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any


class ScheduledTasksDaemon:
    """定时任务守护进程"""
    
    def __init__(self, root: Path = None):
        self.root = root or self._get_project_root()
        self.daemon_dir = self.root / "infrastructure" / "daemon"
        self.daemon_dir.mkdir(parents=True, exist_ok=True)
        
        self.pid_file = self.daemon_dir / "scheduled_tasks.pid"
        self.log_file = self.root / "logs" / "daemon.log"
        self.state_file = self.daemon_dir / "daemon_state.json"
        
        self.interval_seconds = 900  # 15 分钟
        self.running = False
    
    def _get_project_root(self) -> Path:
        current = Path(__file__).resolve().parent.parent
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        return Path(__file__).resolve().parent.parent
    
    def _daemonize(self):
        """
        Unix 双重 fork 守护进程化
        确保进程完全脱离终端和控制会话
        """
        # 第一次 fork
        try:
            pid = os.fork()
            if pid > 0:
                # 父进程退出
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(f"第一次 fork 失败: {e}\n")
            sys.exit(1)
        
        # 子进程成为新的会话组长
        os.setsid()
        
        # 第二次 fork
        try:
            pid = os.fork()
            if pid > 0:
                # 第一次 fork 的子进程退出
                sys.exit(0)
        except OSError as e:
            sys.stderr.write(f"第二次 fork 失败: {e}\n")
            sys.exit(1)
        
        # 重定向标准文件描述符
        sys.stdout.flush()
        sys.stderr.flush()
        
        # 关闭标准输入
        si = open('/dev/null', 'r')
        so = open(self.log_file, 'a+')
        se = open(self.log_file, 'a+')
        
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        
        # 保存 PID
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # 注册信号处理
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGHUP, signal.SIG_IGN)  # 忽略挂起信号
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self._log(f"收到信号 {signum}，准备停止...")
        self.running = False
    
    def _log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_line)
    
    def _save_state(self, state: Dict[str, Any]):
        """保存状态"""
        state['timestamp'] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def _execute_heartbeat(self) -> bool:
        """执行心跳"""
        try:
            result = subprocess.run(
                [sys.executable, str(self.root / "scripts" / "heartbeat_executor.py")],
                cwd=str(self.root),
                capture_output=True,
                text=True,
                timeout=300  # 5 分钟超时
            )
            
            if result.returncode == 0:
                self._log("✅ 心跳执行成功")
                return True
            else:
                self._log(f"⚠️  心跳执行异常 (exit code: {result.returncode})")
                if result.stderr:
                    self._log(f"错误: {result.stderr[:200]}")
                return False
        
        except subprocess.TimeoutExpired:
            self._log("⚠️  心跳执行超时")
            return False
        
        except Exception as e:
            self._log(f"❌ 心跳执行失败: {e}")
            return False
    
    def _run_daemon(self):
        """运行守护进程主循环"""
        self._log("=" * 60)
        self._log("  定时任务守护进程 V2.0.0 启动")
        self._log("=" * 60)
        self._log(f"PID: {os.getpid()}")
        self._log(f"心跳间隔: {self.interval_seconds // 60} 分钟")
        self._log(f"日志文件: {self.log_file}")
        self._log("=" * 60)
        
        self.running = True
        heartbeat_count = 0
        
        while self.running:
            heartbeat_count += 1
            
            # 执行心跳
            self._log(f"心跳 #{heartbeat_count} 开始执行...")
            success = self._execute_heartbeat()
            
            # 保存状态
            self._save_state({
                "status": "running",
                "pid": os.getpid(),
                "heartbeat_count": heartbeat_count,
                "last_heartbeat": datetime.now().isoformat(),
                "last_result": "success" if success else "failed"
            })
            
            # 等待下一次心跳
            if self.running:
                self._log(f"等待 {self.interval_seconds // 60} 分钟...")
                
                # 分段睡眠，以便更快响应信号
                for _ in range(self.interval_seconds):
                    if not self.running:
                        break
                    time.sleep(1)
        
        # 清理
        self._log("守护进程停止")
        if self.pid_file.exists():
            self.pid_file.unlink()
        
        self._save_state({
            "status": "stopped",
            "pid": None,
            "heartbeat_count": heartbeat_count,
            "stopped_at": datetime.now().isoformat()
        })
    
    def start(self):
        """启动守护进程"""
        # 检查是否已经在运行
        if self.pid_file.exists():
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # 检查进程是否存在
            try:
                os.kill(pid, 0)
                print(f"⚠️  守护进程已在运行 (PID: {pid})")
                return
            except OSError:
                # 进程不存在，清理 PID 文件
                self.pid_file.unlink()
        
        print("🚀 启动定时任务守护进程...")
        
        # 守护进程化
        self._daemonize()
        
        # 运行主循环
        self._run_daemon()
    
    def stop(self):
        """停止守护进程"""
        if not self.pid_file.exists():
            print("⚠️  守护进程未运行")
            return
        
        with open(self.pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        try:
            # 发送 SIGTERM 信号
            os.kill(pid, signal.SIGTERM)
            print(f"🛑 已发送停止信号到守护进程 (PID: {pid})")
            
            # 等待进程结束
            for _ in range(10):
                try:
                    os.kill(pid, 0)
                    time.sleep(0.5)
                except OSError:
                    # 进程已结束
                    print("✅ 守护进程已停止")
                    return
            
            # 如果进程还在运行，强制终止
            print("⚠️  进程未响应，强制终止...")
            os.kill(pid, signal.SIGKILL)
            print("✅ 守护进程已强制停止")
        
        except OSError:
            print("⚠️  进程不存在")
        
        finally:
            if self.pid_file.exists():
                self.pid_file.unlink()
    
    def status(self):
        """查看守护进程状态"""
        print("=" * 60)
        print("  定时任务守护进程状态")
        print("=" * 60)
        print()
        
        # 检查 PID 文件
        if not self.pid_file.exists():
            print("状态: ⚪ 未运行")
            return
        
        with open(self.pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        # 检查进程是否存在
        try:
            os.kill(pid, 0)
            print(f"状态: 🟢 运行中")
            print(f"PID: {pid}")
        except OSError:
            print(f"状态: 🔴 已停止 (PID 文件存在但进程不存在)")
            return
        
        # 读取状态文件
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            print(f"心跳次数: {state.get('heartbeat_count', 0)}")
            print(f"上次心跳: {state.get('last_heartbeat', 'N/A')}")
            print(f"上次结果: {state.get('last_result', 'N/A')}")
        
        print()
        print(f"日志文件: {self.log_file}")
        print(f"PID 文件: {self.pid_file}")
        print("=" * 60)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python scheduled_tasks_daemon.py {start|stop|status}")
        sys.exit(1)
    
    command = sys.argv[1]
    daemon = ScheduledTasksDaemon()
    
    if command == "start":
        daemon.start()
    elif command == "stop":
        daemon.stop()
    elif command == "status":
        daemon.status()
    else:
        print(f"未知命令: {command}")
        print("用法: python scheduled_tasks_daemon.py {start|stop|status}")
        sys.exit(1)


if __name__ == "__main__":
    main()
