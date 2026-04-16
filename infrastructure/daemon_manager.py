#!/usr/bin/env python3
"""
守护进程管理器 V7.2.0

功能：
1. 后台持续运行关键服务
2. 自动重启崩溃的服务
3. 监控服务健康状态
4. 支持服务启停控制

守护服务列表：
- 心跳执行器 (每30分钟)
- 永久守护器 (每5分钟刷新)
- 性能监控器 (每1分钟)
- 事件监听器 (持续监听)

使用方式：
  python infrastructure/daemon_manager.py start    # 启动所有守护服务
  python infrastructure/daemon_manager.py stop     # 停止所有守护服务
  python infrastructure/daemon_manager.py status   # 查看服务状态
  python infrastructure/daemon_manager.py restart  # 重启所有服务
"""

import sys
import os
import json
import time
import signal
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class ServiceStatus(Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    CRASHED = "crashed"


@dataclass
class DaemonService:
    """守护服务"""
    id: str
    name: str
    command: List[str]
    interval_seconds: int = 0  # 0 表示持续运行
    auto_restart: bool = True
    max_restarts: int = 3
    restart_delay_seconds: int = 5
    status: ServiceStatus = ServiceStatus.STOPPED
    pid: Optional[int] = None
    last_start: Optional[str] = None
    last_stop: Optional[str] = None
    restart_count: int = 0
    error: Optional[str] = None


class DaemonManager:
    """守护进程管理器"""
    
    def __init__(self, root: Path = None):
        self.root = root or self._get_project_root()
        self.pid_file = self.root / "infrastructure/daemon_manager.pid"
        self.state_file = self.root / "reports/ops/daemon_state.json"
        self.log_file = self.root / "logs/daemon_manager.log"
        
        self.running = False
        self.services: Dict[str, DaemonService] = {}
        self.threads: Dict[str, threading.Thread] = {}
        
        # 初始化服务
        self._init_services()
        
        # 信号处理
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _get_project_root(self) -> Path:
        current = Path(__file__).resolve().parent.parent
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        return Path(__file__).resolve().parent.parent
    
    def _init_services(self):
        """初始化守护服务"""
        self.services = {
            "heartbeat": DaemonService(
                id="heartbeat",
                name="心跳执行器",
                command=[sys.executable, str(self.root / "scripts/heartbeat_executor.py")],
                interval_seconds=1800,  # 30分钟
                auto_restart=True
            ),
            "keeper": DaemonService(
                id="keeper",
                name="永久守护器",
                command=[sys.executable, str(self.root / "scripts/permanent_keeper.py"), "refresh"],
                interval_seconds=300,  # 5分钟
                auto_restart=True
            ),
            "metrics": DaemonService(
                id="metrics",
                name="Metrics 生成器",
                command=[sys.executable, str(self.root / "scripts/generate_metrics.py")],
                interval_seconds=3600,  # 1小时
                auto_restart=True
            ),
            "fusion_check": DaemonService(
                id="fusion_check",
                name="融合检查器",
                command=[sys.executable, str(self.root / "scripts/auto_fusion_hook.py")],
                interval_seconds=600,  # 10分钟
                auto_restart=True
            )
        }
    
    def _log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] {message}\n"
        
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'a') as f:
            f.write(log_line)
        
        print(log_line.strip())
    
    def _signal_handler(self, signum, frame):
        """信号处理"""
        self._log(f"收到信号 {signum}，准备停止...")
        self.stop_all()
        sys.exit(0)
    
    def _run_service(self, service: DaemonService):
        """运行单个服务"""
        while self.running and service.status == ServiceStatus.RUNNING:
            try:
                self._log(f"[{service.id}] 执行: {' '.join(service.command)}")
                
                proc = subprocess.run(
                    service.command,
                    cwd=str(self.root),
                    capture_output=True,
                    text=True,
                    timeout=300  # 5分钟超时
                )
                
                if proc.returncode == 0:
                    self._log(f"[{service.id}] 执行成功")
                else:
                    self._log(f"[{service.id}] 执行失败: {proc.stderr[:200]}")
                
            except subprocess.TimeoutExpired:
                self._log(f"[{service.id}] 执行超时")
            except Exception as e:
                self._log(f"[{service.id}] 执行异常: {e}")
            
            # 等待下次执行
            if service.interval_seconds > 0:
                for _ in range(service.interval_seconds):
                    if not self.running:
                        break
                    time.sleep(1)
            else:
                time.sleep(60)  # 持续服务每分钟检查一次
    
    def start_service(self, service_id: str) -> bool:
        """启动单个服务"""
        if service_id not in self.services:
            self._log(f"服务不存在: {service_id}")
            return False
        
        service = self.services[service_id]
        
        if service.status == ServiceStatus.RUNNING:
            self._log(f"[{service_id}] 服务已在运行")
            return True
        
        service.status = ServiceStatus.STARTING
        service.last_start = datetime.now().isoformat()
        
        # 启动线程
        thread = threading.Thread(
            target=self._run_service,
            args=(service,),
            daemon=True
        )
        thread.start()
        
        self.threads[service_id] = thread
        service.status = ServiceStatus.RUNNING
        
        self._log(f"[{service_id}] 服务已启动")
        return True
    
    def stop_service(self, service_id: str) -> bool:
        """停止单个服务"""
        if service_id not in self.services:
            return False
        
        service = self.services[service_id]
        
        if service.status != ServiceStatus.RUNNING:
            return True
        
        service.status = ServiceStatus.STOPPING
        service.last_stop = datetime.now().isoformat()
        
        # 等待线程结束
        if service_id in self.threads:
            self.threads[service_id].join(timeout=10)
        
        service.status = ServiceStatus.STOPPED
        self._log(f"[{service_id}] 服务已停止")
        return True
    
    def start_all(self):
        """启动所有服务"""
        self._log("=" * 60)
        self._log("  守护进程管理器 V7.2.0 - 启动")
        self._log("=" * 60)
        
        self.running = True
        
        # 写入 PID 文件
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        self.pid_file.write_text(str(os.getpid()))
        
        # 启动所有服务
        for service_id in self.services:
            self.start_service(service_id)
        
        self._log(f"\n已启动 {len(self.services)} 个守护服务")
        self._save_state()
        
        # 主循环
        self._main_loop()
    
    def stop_all(self):
        """停止所有服务"""
        self._log("\n停止所有守护服务...")
        
        self.running = False
        
        for service_id in self.services:
            self.stop_service(service_id)
        
        # 删除 PID 文件
        if self.pid_file.exists():
            self.pid_file.unlink()
        
        self._log("所有服务已停止")
        self._save_state()
    
    def _main_loop(self):
        """主循环"""
        try:
            while self.running:
                # 检查服务状态
                for service_id, service in self.services.items():
                    if service.status == ServiceStatus.RUNNING:
                        # 检查线程是否存活
                        if service_id in self.threads:
                            if not self.threads[service_id].is_alive():
                                if service.auto_restart and service.restart_count < service.max_restarts:
                                    self._log(f"[{service_id}] 服务崩溃，尝试重启...")
                                    service.restart_count += 1
                                    time.sleep(service.restart_delay_seconds)
                                    self.start_service(service_id)
                                else:
                                    service.status = ServiceStatus.CRASHED
                                    self._log(f"[{service_id}] 服务崩溃，已达最大重启次数")
                
                # 保存状态
                self._save_state()
                
                # 每分钟检查一次
                time.sleep(60)
        
        except KeyboardInterrupt:
            self._log("收到中断信号")
            self.stop_all()
    
    def _save_state(self):
        """保存状态"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        state = {
            "timestamp": datetime.now().isoformat(),
            "running": self.running,
            "services": {
                service_id: {
                    "name": service.name,
                    "status": service.status.value,
                    "last_start": service.last_start,
                    "last_stop": service.last_stop,
                    "restart_count": service.restart_count,
                    "error": service.error
                }
                for service_id, service in self.services.items()
            }
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "running": self.running,
            "pid": int(self.pid_file.read_text()) if self.pid_file.exists() else None,
            "services": {
                service_id: {
                    "name": service.name,
                    "status": service.status.value,
                    "interval_seconds": service.interval_seconds,
                    "restart_count": service.restart_count
                }
                for service_id, service in self.services.items()
            }
        }
    
    def print_status(self):
        """打印状态"""
        status = self.get_status()
        
        print("\n" + "=" * 60)
        print("  守护进程管理器 V7.2.0 - 状态")
        print("=" * 60)
        print(f"\n  运行状态: {'运行中' if status['running'] else '已停止'}")
        print(f"  PID: {status['pid'] or '无'}")
        print("\n  服务列表:")
        
        for service_id, service in status['services'].items():
            status_icon = {
                "running": "✅",
                "stopped": "⏹️",
                "starting": "🔄",
                "stopping": "🔄",
                "crashed": "❌"
            }.get(service['status'], "❓")
            
            interval = service['interval_seconds']
            interval_str = f"{interval // 60}分钟" if interval >= 60 else f"{interval}秒"
            
            print(f"    {status_icon} [{service_id}] {service['name']}")
            print(f"       状态: {service['status']}")
            print(f"       间隔: {interval_str}")
            print(f"       重启: {service['restart_count']}次")
        
        print("\n" + "=" * 60)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python daemon_manager.py {start|stop|status|restart}")
        sys.exit(1)
    
    command = sys.argv[1]
    manager = DaemonManager()
    
    if command == "start":
        manager.start_all()
    elif command == "stop":
        manager.stop_all()
    elif command == "status":
        manager.print_status()
    elif command == "restart":
        manager.stop_all()
        time.sleep(2)
        manager.start_all()
    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
