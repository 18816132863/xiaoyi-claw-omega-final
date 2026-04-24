"""
任务状态机 V2.0.0

定义任务状态流转规则。
"""

from typing import Dict, Set, Optional

# 从真源导入
from domain.tasks.specs import TaskStatus


# 状态转移规则
STATE_TRANSITIONS: Dict[TaskStatus, Set[TaskStatus]] = {
    TaskStatus.DRAFT: {TaskStatus.VALIDATED, TaskStatus.CANCELLED},
    TaskStatus.VALIDATED: {TaskStatus.PERSISTED, TaskStatus.CANCELLED},
    TaskStatus.PERSISTED: {TaskStatus.QUEUED, TaskStatus.CANCELLED},
    TaskStatus.QUEUED: {TaskStatus.RUNNING, TaskStatus.CANCELLED},
    TaskStatus.RUNNING: {
        TaskStatus.DELIVERY_PENDING,
        TaskStatus.SUCCEEDED,
        TaskStatus.FAILED,
        TaskStatus.WAITING_RETRY,
        TaskStatus.WAITING_HUMAN,
        TaskStatus.PAUSED
    },
    TaskStatus.DELIVERY_PENDING: {
        TaskStatus.SUCCEEDED,
        TaskStatus.PERSISTED,
        TaskStatus.WAITING_RETRY,
        TaskStatus.FAILED,
        TaskStatus.CANCELLED
    },
    TaskStatus.WAITING_RETRY: {TaskStatus.QUEUED, TaskStatus.FAILED, TaskStatus.CANCELLED},
    TaskStatus.WAITING_HUMAN: {TaskStatus.RESUMED, TaskStatus.CANCELLED},
    TaskStatus.PAUSED: {TaskStatus.RESUMED, TaskStatus.CANCELLED},
    TaskStatus.RESUMED: {TaskStatus.RUNNING, TaskStatus.CANCELLED},
    TaskStatus.SUCCEEDED: set(),
    TaskStatus.FAILED: set(),
    TaskStatus.CANCELLED: set(),
}


def can_transition(from_status: TaskStatus, to_status: TaskStatus) -> bool:
    """检查状态转移是否合法"""
    allowed = STATE_TRANSITIONS.get(from_status, set())
    return to_status in allowed


def get_valid_transitions(status: TaskStatus) -> Set[TaskStatus]:
    """获取指定状态的所有合法转移目标"""
    return STATE_TRANSITIONS.get(status, set())


def is_terminal_status(status: TaskStatus) -> bool:
    """检查是否为终态"""
    return status in {TaskStatus.SUCCEEDED, TaskStatus.FAILED, TaskStatus.CANCELLED}
