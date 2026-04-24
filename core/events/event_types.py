"""Event types for the event system."""

from enum import Enum


class CoreEventType(Enum):
    """核心系统事件类型（与 domain.tasks.specs.EventType 不同）"""
    
    # Task events
    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_CANCELLED = "task_cancelled"
    
    # Context events
    CONTEXT_BUILT = "context_built"
    CONTEXT_CLEARED = "context_cleared"
    CONTEXT_UPDATED = "context_updated"
    
    # Workflow events
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_PAUSED = "workflow_paused"
    WORKFLOW_RESUMED = "workflow_resumed"
    
    # Step events
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    STEP_SKIPPED = "step_skipped"
    RETRY_TRIGGERED = "retry_triggered"
    FALLBACK_TRIGGERED = "fallback_triggered"
    CHECKPOINT_CREATED = "checkpoint_created"
    CHECKPOINT_RESTORED = "checkpoint_restored"
    
    # Skill events
    SKILL_SELECTED = "skill_selected"
    SKILL_EXECUTED = "skill_executed"
    SKILL_FAILED = "skill_failed"
    SKILL_REGISTERED = "skill_registered"
    SKILL_UNREGISTERED = "skill_unregistered"
    SKILL_DEPRECATED = "skill_deprecated"
    
    # Policy events
    POLICY_APPLIED = "policy_applied"
    POLICY_DENIED = "policy_denied"
    POLICY_EVALUATED = "policy_evaluated"
    
    # Degradation events
    DEGRADATION_TRIGGERED = "degradation_triggered"
    DEGRADATION_RECOVERED = "degradation_recovered"
    KILL_SWITCH_ACTIVATED = "kill_switch_activated"
    KILL_SWITCH_DEACTIVATED = "kill_switch_deactivated"
    
    # Memory events
    MEMORY_STORED = "memory_stored"
    MEMORY_RETRIEVED = "memory_retrieved"
    MEMORY_UPDATED = "memory_updated"
    MEMORY_DELETED = "memory_deleted"
    
    # Budget events
    BUDGET_EXCEEDED = "budget_exceeded"
    BUDGET_WARNING = "budget_warning"
    BUDGET_RESET = "budget_reset"


# 别名，兼容旧代码
EventType = CoreEventType
