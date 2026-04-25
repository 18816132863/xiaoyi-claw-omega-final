#!/usr/bin/env python3
"""
任务系统守护进程 V8.0.0

完整闭环 + 可观测性 + 配置中心：
- 从 settings 读取配置
- 结构化日志
- 业务指标
- 健康检查
"""

import asyncio
import signal
import sys
import os
import json
import aiohttp
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from infrastructure.task_manager import get_task_manager
from infrastructure.storage.repositories.sqlite_repo import (
    SQLiteTaskRepository,
    SQLiteTaskEventRepository,
)
from infrastructure.storage.sqlite_utils import serialize_datetime
from application.task_service.scheduler import SchedulerService
from domain.tasks import TaskStatus
from infrastructure.observability import get_logger, get_metrics, HealthChecker, HealthStatus
from config import get_settings


class TaskDaemon:
    """任务系统守护进程 V8.0.0"""
    
    def __init__(self):
        # 从配置中心读取配置
        self.settings = get_settings()
        self.check_interval = self.settings.daemon.check_interval
        self.message_server_url = f"http://{self.settings.message_server.host}:{self.settings.message_server.port}"
        
        self.tm = get_task_manager()
        self.repo = SQLiteTaskRepository()
        self.event_repo = SQLiteTaskEventRepository()
        self.scheduler = SchedulerService(task_repo=self.repo)
        self.running = False
        self.root = project_root
        self.pid_file = self.root / "data" / "task_daemon.pid"
        
        # 可观测性
        log_dir = self.root / self.settings.observability.log_dir
        log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = get_logger(
            service="task_daemon",
            component="daemon",
            log_dir=log_dir
        )
        self.metrics = get_metrics(
            metrics_dir=self.root / self.settings.observability.metrics_dir
        )
        self.health = HealthChecker("task_daemon")
        
        # 注册健康检查
        self.health.register("daemon_running", self._check_daemon_running)
        self.health.register("db_connection", self._check_db_connection)
        self.health.register("queue_writable", self._check_queue_writable)
        
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
    
    def _check_daemon_running(self) -> dict:
        return {"status": "healthy" if self.running else "unhealthy"}
    
    def _check_db_connection(self) -> dict:
        try:
            self.repo._get_connection()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def _check_queue_writable(self) -> dict:
        try:
            queue_file = self.root / "data" / "task_queue.jsonl"
            queue_file.parent.mkdir(parents=True, exist_ok=True)
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    def _handle_signal(self, signum, frame):
        self.logger.warning(f"收到信号 {signum}，正在停止...")
        self.stop()
    
    def start(self):
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        self.logger.info(
            "守护进程启动",
            event_type="daemon_start",
            check_interval=self.check_interval,
            message_server_url=self.message_server_url
        )
        
        print("=" * 60)
        print("  任务系统守护进程 V8.0.0")
        print("=" * 60)
        print(f"  PID: {os.getpid()}")
        print(f"  环境: {self.settings.env.value}")
        print(f"  检查间隔: {self.check_interval} 秒")
        print(f"  消息服务: {self.message_server_url}")
        print("=" * 60)
        
        self.running = True
        asyncio.run(self._run_loop())
    
    def stop(self):
        self.running = False
        self.logger.info("守护进程停止", event_type="daemon_stop")
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    async def _run_loop(self):
        while self.running:
            try:
                cycle_start = datetime.now()
                
                # 1. 扫描并投递
                result = await self.scheduler.scan_and_dispatch()
                if result["dispatched"] > 0:
                    self.logger.info(
                        f"投递 {result['dispatched']} 个任务",
                        event_type="tasks_dispatched",
                        status="success"
                    )
                    self.metrics.increment("tasks_dispatched", result["dispatched"])
                
                # 2. 执行队列
                executed = await self._process_queue()
                if executed > 0:
                    self.metrics.increment("tasks_executed", executed)
                
                # 3. 真实送达
                delivered = await self._process_pending_sends()
                if delivered > 0:
                    self.metrics.increment("messages_delivered", delivered)
                
                # 4. 确认送达状态
                confirmed = await self._confirm_deliveries()
                if confirmed > 0:
                    self.metrics.increment("deliveries_confirmed", confirmed)
                
                # 记录周期耗时
                cycle_duration = (datetime.now() - cycle_start).total_seconds()
                self.metrics.histogram("cycle_duration_seconds", cycle_duration)
                
                # 定期保存指标
                if self.settings.observability.enable_metrics:
                    self.metrics.save()
                
            except Exception as e:
                self.logger.error(
                    f"运行循环错误: {e}",
                    event_type="loop_error",
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
            
            await asyncio.sleep(self.check_interval)
        
        self.logger.info("守护进程已停止", event_type="daemon_stopped")
    
    async def _process_queue(self) -> int:
        """执行队列中的任务"""
        queue_file = self.root / "data" / "task_queue.jsonl"
        if not queue_file.exists():
            return 0
        
        with open(queue_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            return 0
        
        processed = 0
        remaining = []
        
        for line in lines:
            try:
                entry = json.loads(line.strip())
                if entry.get("status") == "pending":
                    task_id = entry["task_id"]
                    
                    self.logger.info(
                        "开始执行任务",
                        task_id=task_id,
                        event_type="task_execution_start"
                    )
                    
                    result = await self.tm.execute_task(task_id)
                    
                    if result.get("success"):
                        self.logger.info(
                            "任务执行成功",
                            task_id=task_id,
                            event_type="task_execution_success",
                            delivery_status=result.get("delivery_status")
                        )
                        self.metrics.increment("tasks_succeeded")
                    else:
                        self.logger.error(
                            "任务执行失败",
                            task_id=task_id,
                            event_type="task_execution_failed",
                            error_message=result.get("error")
                        )
                        self.metrics.increment("tasks_failed")
                    
                    processed += 1
                else:
                    remaining.append(line)
            except Exception as e:
                self.logger.error(
                    f"处理队列条目失败: {e}",
                    event_type="queue_process_error",
                    error_type=type(e).__name__
                )
                remaining.append(line)
        
        with open(queue_file, 'w', encoding='utf-8') as f:
            f.writelines(remaining)
        
        return processed
    
    async def _process_pending_sends(self) -> int:
        """真实送达消息"""
        pending_file = self.root / "reports" / "ops" / "pending_sends.jsonl"
        if not pending_file.exists():
            return 0
        
        with open(pending_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            return 0
        
        delivered = 0
        failed = 0
        remaining = []
        
        timeout = self.settings.message_server.timeout
        async with aiohttp.ClientSession() as session:
            for line in lines:
                try:
                    entry = json.loads(line.strip())
                    message = entry.get("message", "")
                    user_id = entry.get("user_id", "default")
                    task_id = entry.get("task_id")
                    run_id = entry.get("run_id")
                    
                    self.logger.debug(
                        "尝试发送消息",
                        task_id=task_id,
                        run_id=run_id,
                        event_type="message_send_attempt"
                    )
                    
                    try:
                        async with session.post(
                            f"{self.message_server_url}/send",
                            json={
                                "channel": "xiaoyi-channel",
                                "target": user_id,
                                "message": message,
                                "task_id": task_id,
                                "run_id": run_id
                            },
                            timeout=aiohttp.ClientTimeout(total=timeout)
                        ) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                if data.get("status") == "delivered":
                                    delivered += 1
                                    self.logger.info(
                                        "消息送达成功",
                                        task_id=task_id,
                                        run_id=run_id,
                                        event_type="message_delivered"
                                    )
                                else:
                                    failed += 1
                                    remaining.append(line)
                            else:
                                failed += 1
                                remaining.append(line)
                    except aiohttp.ClientError as e:
                        failed += 1
                        remaining.append(line)
                        self.logger.warning(
                            f"消息服务连接失败: {e}",
                            task_id=task_id,
                            event_type="message_send_error"
                        )
                        
                except Exception as e:
                    remaining.append(line)
        
        self.metrics.increment("message_send_failures", failed)
        
        with open(pending_file, 'w', encoding='utf-8') as f:
            f.writelines(remaining)
        
        return delivered
    
    async def _confirm_deliveries(self) -> int:
        """确认送达状态"""
        delivered_file = self.root / "reports" / "ops" / "delivered_messages.jsonl"
        if not delivered_file.exists():
            return 0

        with open(delivered_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            return 0

        confirmed = 0
        remaining = []

        for line in lines:
            try:
                entry = json.loads(line.strip())
                if entry.get("status") != "delivered":
                    remaining.append(line)
                    continue

                task_id = entry.get("task_id")
                if not task_id:
                    remaining.append(line)
                    continue

                task = await self.repo.get(task_id)
                if not task:
                    continue

                delivered_at = entry.get("delivered_at") or serialize_datetime(datetime.now())

                if task.schedule and task.schedule.mode.value in ("cron", "recurring"):
                    next_run = task.schedule.get_next_run_at(datetime.now())
                    await self.repo.update(task_id, {
                        "status": TaskStatus.PERSISTED.value,
                        "last_run_at": delivered_at,
                        "next_run_at": serialize_datetime(next_run) if next_run else None,
                        "last_error": None
                    })
                    self.logger.info(
                        "recurring 任务送达确认",
                        task_id=task_id,
                        event_type="delivery_confirmed",
                        schedule_mode="recurring",
                        next_run_at=serialize_datetime(next_run) if next_run else None
                    )
                else:
                    await self.repo.update(task_id, {
                        "status": TaskStatus.SUCCEEDED.value,
                        "last_run_at": delivered_at,
                        "next_run_at": None,
                        "last_error": None
                    })
                    self.logger.info(
                        "once 任务送达确认",
                        task_id=task_id,
                        event_type="delivery_confirmed",
                        schedule_mode="once"
                    )

                await self.event_repo.record_event(
                    task_id=task_id,
                    event_type="delivery_confirmed",
                    event_payload={
                        "message_id": entry.get("message_id"),
                        "delivered_at": delivered_at
                    }
                )
                confirmed += 1

            except Exception as e:
                remaining.append(line)
                self.logger.error(
                    f"确认送达失败: {e}",
                    event_type="delivery_confirm_error",
                    error_type=type(e).__name__
                )

        with open(delivered_file, 'w', encoding='utf-8') as f:
            f.writelines(remaining)

        return confirmed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="任务系统守护进程 V8.0.0")
    parser.add_argument("--interval", "-i", type=float, help="检查间隔（秒），默认从配置读取")
    args = parser.parse_args()
    
    daemon = TaskDaemon()
    
    # 命令行参数覆盖配置
    if args.interval:
        daemon.check_interval = args.interval
    
    try:
        daemon.start()
    except KeyboardInterrupt:
        daemon.stop()


if __name__ == "__main__":
    main()
