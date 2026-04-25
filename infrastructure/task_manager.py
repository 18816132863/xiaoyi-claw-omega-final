"""
任务管理器 V1.0.0

统一入口，整合：
- 任务服务
- 调度器
- 执行器
- 工具注册

使用方式：
    from infrastructure.task_manager import TaskManager
    
    tm = TaskManager()
    
    # 创建定时消息任务
    result = await tm.create_scheduled_message(
        user_id="user123",
        message="提醒内容",
        run_at="2026-04-20 15:00:00"
    )
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

from domain.tasks import (
    TaskSpec,
    StepSpec,
    ScheduleSpec,
    RetryPolicy,
    TimeoutPolicy,
    TaskStatus,
    TriggerMode,
    ScheduleType,
    TaskType,
)
from application.task_service import TaskService
from infrastructure.scheduler import SimpleScheduler
from infrastructure.workers import TaskExecutor, SimpleExecutor
from infrastructure.storage.repositories import (
    SQLiteTaskRepository,
    SQLiteTaskEventRepository,
    SQLiteCheckpointRepository,
)
from infrastructure.tool_adapters import TOOL_REGISTRY


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        # 初始化仓储
        self.task_repo = SQLiteTaskRepository()
        self.event_repo = SQLiteTaskEventRepository()
        self.checkpoint_repo = SQLiteCheckpointRepository()
        
        # 初始化服务
        self.task_service = TaskService(
            task_repo=self.task_repo,
            event_repo=self.event_repo
        )
        
        # 初始化执行器
        self.executor = TaskExecutor(
            task_repo=self.task_repo,
            event_repo=self.event_repo,
            checkpoint_repo=self.checkpoint_repo,
            tool_registry=TOOL_REGISTRY
        )
        
        # 初始化调度器
        self.scheduler = SimpleScheduler(check_interval=1.0)
        
        self.root = get_project_root()
    
    # ==================== 任务创建 ====================
    
    async def create_scheduled_message(
        self,
        user_id: str,
        message: str,
        run_at: str,
        channel: str = "xiaoyi-channel",
        target: str = "default",
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建定时消息任务
        
        Args:
            user_id: 用户 ID
            message: 消息内容
            run_at: 执行时间 (ISO 格式)
            channel: 渠道
            target: 目标
            title: 标题
        
        Returns:
            创建结果
        """
        # 解析时间
        if isinstance(run_at, str):
            run_at_dt = datetime.fromisoformat(run_at.replace('Z', '+00:00'))
        else:
            run_at_dt = run_at
        
        # 创建任务规格
        spec = TaskSpec(
            task_type=TaskType.SCHEDULED_MESSAGE.value,
            goal=f"在 {run_at} 发送消息: {message[:50]}...",
            user_id=user_id,
            trigger_mode=TriggerMode.SCHEDULED,
            schedule=ScheduleSpec(
                mode=ScheduleType.ONCE,
                run_at=run_at_dt,
                timezone="Asia/Shanghai"
            ),
            inputs={
                "channel": channel,
                "target": target,
                "message": message,
                "title": title or "定时消息"
            },
            steps=[
                StepSpec(
                    step_index=1,
                    step_name="send_message",
                    tool_name="send_message",
                    input_mapping={
                        "user_id": "$inputs.target",
                        "message": "$inputs.message"
                    },
                    output_key="send_result"
                )
            ],
            required_tools=["send_message"],
            retry_policy=RetryPolicy(max_attempts=3, backoff_seconds=60),
            timeout_policy=TimeoutPolicy(task_timeout_seconds=300)
        )
        
        return await self.task_service.create_task(spec)
    
    async def create_health_reminder(
        self,
        user_id: str,
        reminder_type: str = "daily",
        run_at: Optional[str] = None,
        cron_expr: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建健康提醒任务"""
        # 生成提醒内容
        message = self._generate_health_reminder(reminder_type)
        
        # 确定调度方式
        if cron_expr:
            schedule = ScheduleSpec(
                mode=ScheduleType.CRON,
                cron_expr=cron_expr,
                timezone="Asia/Shanghai"
            )
        elif run_at:
            run_at_dt = datetime.fromisoformat(run_at.replace('Z', '+00:00'))
            schedule = ScheduleSpec(
                mode=ScheduleType.ONCE,
                run_at=run_at_dt,
                timezone="Asia/Shanghai"
            )
        else:
            return {"success": False, "error": "必须提供 run_at 或 cron_expr"}
        
        spec = TaskSpec(
            task_type=TaskType.HEALTH_REMINDER.value,
            goal=f"发送健康提醒: {reminder_type}",
            user_id=user_id,
            trigger_mode=TriggerMode.SCHEDULED,
            schedule=schedule,
            inputs={
                "channel": "xiaoyi-channel",
                "target": "default",
                "message": message,
                "title": "🌅 每日健康提醒"
            },
            steps=[
                StepSpec(
                    step_index=1,
                    step_name="send_reminder",
                    tool_name="send_message",
                    input_mapping={
                        "user_id": "$inputs.target",
                        "message": "$inputs.message"
                    }
                )
            ],
            required_tools=["send_message"]
        )
        
        return await self.task_service.create_task(spec)
    
    async def create_recurring_message(
        self,
        user_id: str,
        message: str,
        cron_expr: str,
        channel: str = "xiaoyi-channel",
        target: str = "default",
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建重复消息任务"""
        spec = TaskSpec(
            task_type=TaskType.SCHEDULED_MESSAGE.value,
            goal=f"Cron {cron_expr} 发送消息: {message[:50]}...",
            user_id=user_id,
            trigger_mode=TriggerMode.SCHEDULED,
            schedule=ScheduleSpec(
                mode=ScheduleType.CRON,
                cron_expr=cron_expr,
                timezone="Asia/Shanghai"
            ),
            inputs={
                "channel": channel,
                "target": target,
                "message": message,
                "title": title or "定时消息"
            },
            steps=[
                StepSpec(
                    step_index=1,
                    step_name="send_message",
                    tool_name="send_message",
                    input_mapping={
                        "user_id": "$inputs.target",
                        "message": "$inputs.message"
                    },
                    output_key="send_result"
                )
            ],
            required_tools=["send_message"],
            retry_policy=RetryPolicy(max_attempts=3, backoff_seconds=60),
            timeout_policy=TimeoutPolicy(task_timeout_seconds=300)
        )
        
        return await self.task_service.create_task(spec)
    
    # ==================== 任务查询 ====================
    
    async def get_task(self, task_id: str) -> Optional[TaskSpec]:
        """获取任务"""
        return await self.task_service.get_task(task_id)
    
    async def list_tasks(
        self,
        user_id: str,
        status: Optional[TaskStatus] = None,
        limit: int = 100
    ) -> List[TaskSpec]:
        """列出任务"""
        return await self.task_service.list_tasks(user_id, status, limit)
    
    async def get_task_events(self, task_id: str) -> List[Dict[str, Any]]:
        """获取任务事件"""
        return await self.task_service.get_task_events(task_id)
    
    async def get_task_runs(self, task_id: str) -> List[Dict[str, Any]]:
        """获取任务运行记录"""
        # 简化实现：从事件中提取
        events = await self.event_repo.list_events(task_id)
        runs = []
        for event in events:
            if event.get("event_type") in ("started", "succeeded", "failed"):
                runs.append(event)
        return runs
    
    async def get_tool_calls(self, task_id: str) -> List[Dict[str, Any]]:
        """获取工具调用记录"""
        tool_calls_file = self.root / "data" / "tool_calls.jsonl"
        
        if not tool_calls_file.exists():
            return []
        
        calls = []
        with open(tool_calls_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("task_id") == task_id:
                        calls.append(entry)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse tool call line: {e}")
                except Exception as e:
                    logger.warning(f"Unexpected error parsing tool call: {e}")
        
        return calls
    
    # ==================== 任务管理 ====================
    
    async def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """取消任务"""
        return await self.task_service.cancel_task(task_id)
    
    async def pause_task(self, task_id: str) -> Dict[str, Any]:
        """暂停任务"""
        return await self.task_service.pause_task(task_id)
    
    async def resume_task(self, task_id: str) -> Dict[str, Any]:
        """恢复任务"""
        return await self.task_service.resume_task(task_id)
    
    async def trigger_task_now(self, task_id: str) -> Dict[str, Any]:
        """立即触发任务"""
        task = await self.task_repo.get(task_id)
        if not task:
            return {"success": False, "error": "任务不存在"}
        
        # 更新状态为已入队
        await self.task_repo.update(task_id, {"status": TaskStatus.QUEUED.value})
        
        # 执行任务
        return await self.executor.execute_task(task_id)
    
    async def retry_task(self, task_id: str) -> Dict[str, Any]:
        """重试任务"""
        task = await self.task_repo.get(task_id)
        if not task:
            return {"success": False, "error": "任务不存在"}
        
        # 重置状态
        await self.task_repo.update(task_id, {
            "status": TaskStatus.QUEUED.value,
            "attempt_count": 0
        })
        
        # 执行任务
        return await self.executor.execute_task(task_id)
    
    async def update_schedule(
        self,
        task_id: str,
        run_at: Optional[str] = None,
        cron_expr: Optional[str] = None
    ) -> Dict[str, Any]:
        """更新调度时间"""
        updates = {}
        
        if run_at:
            updates["run_at"] = run_at
            updates["schedule_type"] = "once"
        
        if cron_expr:
            updates["cron_expr"] = cron_expr
            updates["schedule_type"] = "cron"
        
        if not updates:
            return {"success": False, "error": "必须提供 run_at 或 cron_expr"}
        
        success = await self.task_repo.update(task_id, updates)
        
        return {"success": success, "task_id": task_id}
    
    # ==================== 任务执行 ====================
    
    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """执行任务"""
        return await self.executor.execute_task(task_id)
    
    async def process_queue(self) -> int:
        """处理队列"""
        simple_executor = SimpleExecutor()
        return await simple_executor.process_queue()
    
    # ==================== 调度器控制 ====================
    
    def start_scheduler(self):
        """启动调度器"""
        self.scheduler.start()
    
    def stop_scheduler(self):
        """停止调度器"""
        self.scheduler.stop()
    
    # ==================== 辅助方法 ====================
    
    def _generate_health_reminder(self, reminder_type: str) -> str:
        """生成健康提醒内容"""
        reminders = {
            "morning": """
🌅 每日健康提醒
📅 {date}

😴 睡眠提醒
  如果睡眠质量不好，可以试试睡前冥想

⏰ 作息提醒
  避免熬夜，保护肝脏

💪 保持健康，从每一天开始！
""",
            "noon": """
🌅 每日健康提醒
📅 {date}

💧 饮水提醒
  记得喝水，每天8杯水

🏃 运动提醒
  久坐记得起来活动一下

💪 保持健康，从每一天开始！
""",
            "evening": """
🌅 每日健康提醒
📅 {date}

😴 睡眠提醒
  晚上11点前入睡最佳

⏰ 作息提醒
  保持规律作息，早睡早起

💪 保持健康，从每一天开始！
"""
        }
        
        template = reminders.get(reminder_type, reminders["morning"])
        return template.format(date=datetime.now().strftime("%Y-%m-%d %H:%M"))


# 全局实例
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """获取全局任务管理器"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager
