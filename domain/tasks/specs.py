"""
任务系统领域模型 V1.0.0

定义：
- 任务状态枚举
- 步骤状态枚举
- 触发模式枚举
- 调度类型枚举
- TaskSpec 结构
- StepSpec 结构
- ScheduleSpec 结构
- RetryPolicy 结构
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


# ==================== 枚举定义 ====================

class TaskStatus(str, Enum):
    """任务状态"""
    DRAFT = "draft"                     # 草稿
    VALIDATED = "validated"             # 已校验
    PERSISTED = "persisted"             # 已持久化
    QUEUED = "queued"                   # 已入队
    RUNNING = "running"                 # 运行中
    WAITING_RETRY = "waiting_retry"     # 等待重试
    WAITING_HUMAN = "waiting_human"     # 等待人工
    PAUSED = "paused"                   # 已暂停
    RESUMED = "resumed"                 # 已恢复
    SUCCEEDED = "succeeded"             # 成功
    FAILED = "failed"                   # 失败
    CANCELLED = "cancelled"             # 已取消


class StepStatus(str, Enum):
    """步骤状态"""
    PENDING = "pending"                 # 待执行
    RUNNING = "running"                 # 运行中
    SUCCEEDED = "succeeded"             # 成功
    FAILED = "failed"                   # 失败
    SKIPPED = "skipped"                 # 已跳过


class TriggerMode(str, Enum):
    """触发模式"""
    IMMEDIATE = "immediate"             # 立即执行
    SCHEDULED = "scheduled"             # 定时执行
    EVENT_DRIVEN = "event_driven"       # 事件驱动


class ScheduleType(str, Enum):
    """调度类型"""
    ONCE = "once"                       # 单次执行
    DELAY = "delay"                     # 延迟执行
    CRON = "cron"                       # Cron 表达式
    RECURRING = "recurring"             # 规则重复


class EventType(str, Enum):
    """事件类型"""
    CREATED = "created"
    VALIDATED = "validated"
    PERSISTED = "persisted"
    QUEUED = "queued"
    STARTED = "started"
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    RETRYING = "retrying"
    WAITING_HUMAN = "waiting_human"
    RESUMED = "resumed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


# ==================== 规格定义 ====================

class RetryPolicy(BaseModel):
    """重试策略"""
    max_attempts: int = Field(default=3, ge=1, le=10)
    backoff_seconds: int = Field(default=60, ge=1, le=3600)
    backoff_multiplier: float = Field(default=2.0, ge=1.0, le=10.0)
    max_backoff_seconds: int = Field(default=3600, ge=60, le=86400)


class TimeoutPolicy(BaseModel):
    """超时策略"""
    task_timeout_seconds: int = Field(default=600, ge=10, le=86400)
    step_timeout_seconds: int = Field(default=300, ge=10, le=3600)


class ScheduleSpec(BaseModel):
    """调度规格"""
    mode: ScheduleType = Field(default=ScheduleType.ONCE)
    run_at: Optional[datetime] = None
    delay_seconds: Optional[int] = None
    cron_expr: Optional[str] = None
    interval_seconds: Optional[int] = None
    timezone: str = Field(default="Asia/Shanghai")
    next_run_at: Optional[str] = None  # ISO 格式字符串
    
    def get_next_run_at(self, from_time: Optional[datetime] = None) -> Optional[datetime]:
        """计算下一次运行时间"""
        from datetime import timedelta
        import croniter
        
        base = from_time or datetime.now()
        
        if self.mode == ScheduleType.ONCE:
            return self.run_at
        
        elif self.mode == ScheduleType.DELAY:
            if self.delay_seconds:
                return base + timedelta(seconds=self.delay_seconds)
        
        elif self.mode == ScheduleType.CRON:
            if self.cron_expr:
                cron = croniter.croniter(self.cron_expr, base)
                return cron.get_next(datetime)
        
        elif self.mode == ScheduleType.RECURRING:
            if self.interval_seconds:
                return base + timedelta(seconds=self.interval_seconds)
        
        return None


class StepSpec(BaseModel):
    """步骤规格"""
    step_index: int = Field(..., ge=1)
    step_name: str
    tool_name: str
    input_mapping: Dict[str, Any] = Field(default_factory=dict)
    output_key: Optional[str] = None
    condition: Optional[str] = None
    on_failure: str = Field(default="retry")  # retry | skip | abort
    timeout_seconds: Optional[int] = None


class TaskSpec(BaseModel):
    """任务规格"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str
    goal: str
    
    # 触发模式
    trigger_mode: TriggerMode = Field(default=TriggerMode.IMMEDIATE)
    schedule: Optional[ScheduleSpec] = None
    
    # 输入
    inputs: Dict[str, Any] = Field(default_factory=dict)
    
    # 步骤
    steps: List[StepSpec] = Field(default_factory=list)
    
    # 工具
    required_tools: List[str] = Field(default_factory=list)
    
    # 成功条件
    success_condition: Optional[str] = None
    
    # 策略
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    timeout_policy: TimeoutPolicy = Field(default_factory=TimeoutPolicy)
    
    # 幂等控制
    idempotency_key: Optional[str] = None
    
    # 状态
    status: TaskStatus = Field(default=TaskStatus.DRAFT)
    
    # 元数据
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    def validate_spec(self) -> List[str]:
        """校验规格，返回错误列表"""
        errors = []
        
        # 校验任务类型
        if not self.task_type:
            errors.append("task_type 不能为空")
        
        # 校验目标
        if not self.goal:
            errors.append("goal 不能为空")
        
        # 校验步骤
        if not self.steps:
            errors.append("steps 不能为空")
        
        step_indices = [s.step_index for s in self.steps]
        if sorted(step_indices) != list(range(1, len(self.steps) + 1)):
            errors.append("step_index 必须从 1 开始连续递增")
        
        # 校验调度
        if self.trigger_mode == TriggerMode.SCHEDULED:
            if not self.schedule:
                errors.append("scheduled 模式必须提供 schedule")
            elif self.schedule.mode == ScheduleType.ONCE and not self.schedule.run_at:
                errors.append("once 模式必须提供 run_at")
            elif self.schedule.mode == ScheduleType.CRON and not self.schedule.cron_expr:
                errors.append("cron 模式必须提供 cron_expr")
        
        # 校验工具
        tool_names_in_steps = {s.tool_name for s in self.steps}
        missing_tools = tool_names_in_steps - set(self.required_tools)
        if missing_tools:
            errors.append(f"步骤使用了未声明的工具: {missing_tools}")
        
        return errors
    
    def generate_idempotency_key(self) -> str:
        """生成幂等键"""
        if self.idempotency_key:
            return self.idempotency_key
        
        import hashlib
        import json
        
        content = json.dumps({
            "task_type": self.task_type,
            "goal": self.goal,
            "trigger_mode": self.trigger_mode.value,
            "schedule": self.schedule.model_dump() if self.schedule else None,
            "inputs": self.inputs,
        }, sort_keys=True, default=str)
        
        return hashlib.sha256(content.encode()).hexdigest()[:32]


# ==================== 任务类型定义 ====================

class TaskType(str, Enum):
    """任务类型"""
    SCHEDULED_MESSAGE = "scheduled_message"     # 定时消息
    HEALTH_REMINDER = "health_reminder"         # 健康提醒
    DAILY_REPORT = "daily_report"               # 日报
    WEEKLY_SUMMARY = "weekly_summary"           # 周报
    DATA_SYNC = "data_sync"                     # 数据同步
    BACKUP = "backup"                           # 备份
    CLEANUP = "cleanup"                         # 清理
    CUSTOM = "custom"                           # 自定义


# ==================== 导出 ====================

__all__ = [
    "TaskStatus",
    "StepStatus",
    "TriggerMode",
    "ScheduleType",
    "EventType",
    "TaskType",
    "RetryPolicy",
    "TimeoutPolicy",
    "ScheduleSpec",
    "StepSpec",
    "TaskSpec",
]
