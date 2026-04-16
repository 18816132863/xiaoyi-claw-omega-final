"""Event types for the event system."""

from enum import Enum


class EventType(Enum):
    """All system event types."""
    
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
    
    # Risk events
    RISK_ASSESSED = "risk_assessed"
    HIGH_RISK_BLOCKED = "high_risk_blocked"
    
    # Audit events
    AUDIT_LOG_CREATED = "audit_log_created"
    AUDIT_LOG_EXPORTED = "audit_log_exported"
    
    # System events
    SYSTEM_STARTED = "system_started"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_ERROR = "system_error"
    HEALTH_CHECK = "health_check"


# Event type categories
TASK_EVENTS = [
    EventType.TASK_CREATED,
    EventType.TASK_STARTED,
    EventType.TASK_COMPLETED,
    EventType.TASK_FAILED,
    EventType.TASK_CANCELLED
]

WORKFLOW_EVENTS = [
    EventType.WORKFLOW_STARTED,
    EventType.WORKFLOW_COMPLETED,
    EventType.WORKFLOW_FAILED,
    EventType.WORKFLOW_PAUSED,
    EventType.WORKFLOW_RESUMED
]

STEP_EVENTS = [
    EventType.STEP_STARTED,
    EventType.STEP_COMPLETED,
    EventType.STEP_FAILED,
    EventType.STEP_SKIPPED,
    EventType.RETRY_TRIGGERED,
    EventType.FALLBACK_TRIGGERED
]

SKILL_EVENTS = [
    EventType.SKILL_SELECTED,
    EventType.SKILL_EXECUTED,
    EventType.SKILL_FAILED,
    EventType.SKILL_REGISTERED,
    EventType.SKILL_UNREGISTERED,
    EventType.SKILL_DEPRECATED
]

POLICY_EVENTS = [
    EventType.POLICY_APPLIED,
    EventType.POLICY_DENIED,
    EventType.POLICY_EVALUATED
]

DEGRADATION_EVENTS = [
    EventType.DEGRADATION_TRIGGERED,
    EventType.DEGRADATION_RECOVERED,
    EventType.KILL_SWITCH_ACTIVATED,
    EventType.KILL_SWITCH_DEACTIVATED
]

MEMORY_EVENTS = [
    EventType.MEMORY_STORED,
    EventType.MEMORY_RETRIEVED,
    EventType.MEMORY_UPDATED,
    EventType.MEMORY_DELETED
]

BUDGET_EVENTS = [
    EventType.BUDGET_EXCEEDED,
    EventType.BUDGET_WARNING,
    EventType.BUDGET_RESET
]
