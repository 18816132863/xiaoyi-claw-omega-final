"""
任务状态机 V1.0.0

定义任务状态流转规则。
"""

from enum import Enum
from typing import Dict, Set, Optional


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


# 状态转移规则
STATE_TRANSITIONS: Dict[TaskStatus, Set[TaskStatus]] = {
    TaskStatus.DRAFT: {TaskStatus.VALIDATED, TaskStatus.CANCELLED},
    TaskStatus.VALIDATED: {TaskStatus.PERSISTED, TaskStatus.CANCELLED},
    TaskStatus.PERSISTED: {TaskStatus.QUEUED, TaskStatus.CANCELLED},
    TaskStatus.QUEUED: {TaskStatus.RUNNING, TaskStatus.CANCELLED},
    TaskStatus.RUNNING: {
        TaskStatus.SUCCEEDED,
        TaskStatus.FAILED,
        TaskStatus.WAITING_RETRY,
        TaskStatus.WAITING_HUMAN,
        TaskStatus.PAUSED
    },
    TaskStatus.WAITING_RETRY: {TaskStatus.QUEUED, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.WAITING_HUMAN: {TaskStatus.RESUMED, TaskStatus.CANCELLED},
    TaskStatus.PAUSED: {TaskStatus.RESUMED, TaskStatus.CANCELLED},
    TaskStatus.RESUMED: {TaskStatus.QUEUED},
    TaskStatus.SUCCEEDED: set(),  # 终态
    TaskStatus.FAILED: set(),     # 终态
    TaskStatus.CANCELLED: set(),  # 终态
}


def can_transition(from_status: TaskStatus, to_status: TaskStatus) -> bool:
    """检查是否可以从 from_status 转移到 to_status"""
    allowed = STATE_TRANSITIONS.get(from_status, set())
    return to_status in allowed


def get_next_status(current: TaskStatus, event: str) -> Optional[TaskStatus]:
    """根据事件获取下一个状态"""
    transitions = {
        (TaskStatus.DRAFT, "validate"): TaskStatus.VALIDATED,
        (TaskStatus.VALIDATED, "persist"): TaskStatus.PERSISTED,
        (TaskStatus.PERSISTED, "queue"): TaskStatus.QUEUED,
        (TaskStatus.QUEUED, "start"): TaskStatus.RUNNING,
        (TaskStatus.RUNNING, "succeed"): TaskStatus.SUCCEEDED,
        (TaskStatus.RUNNING, "fail"): TaskStatus.WAITING_RETRY,
        (TaskStatus.WAITING_RETRY, "retry"): TaskStatus.QUEUED,
        (TaskStatus.WAITING_RETRY, "give_up"): TaskStatus.FAILED,
        (TaskStatus.RUNNING, "pause"): TaskStatus.PAUSED,
        (TaskStatus.PAUSED, "resume"): TaskStatus.RESUMED,
        (TaskStatus.RUNNING, "wait_human"): TaskStatus.WAITING_HUMAN,
        (TaskStatus.WAITING_HUMAN, "resume"): TaskStatus.RESUMED,
    }
    
    return transitions.get((current, event))
