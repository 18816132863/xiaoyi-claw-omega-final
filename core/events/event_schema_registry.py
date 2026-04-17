"""
Event Schema Registry - 事件 Schema 注册表
Phase3 Group5 核心模块
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum


class EventCategory(Enum):
    """事件分类"""
    TASK = "task"
    POLICY = "policy"
    CONTEXT = "context"
    WORKFLOW = "workflow"
    SKILL = "skill"
    MEMORY = "memory"
    SYSTEM = "system"


@dataclass
class EventSchema:
    """事件 Schema"""
    event_type: str
    category: EventCategory
    required_fields: Set[str]
    optional_fields: Set[str] = field(default_factory=set)
    description: str = ""
    
    def validate(self, payload: Dict[str, Any]) -> tuple[bool, List[str]]:
        """验证 payload"""
        errors = []
        
        # 检查必需字段
        for field_name in self.required_fields:
            if field_name not in payload:
                errors.append(f"Missing required field: {field_name}")
        
        return len(errors) == 0, errors


class EventSchemaRegistry:
    """
    事件 Schema 注册表
    
    统一管理所有事件类型，确保事件 payload 规范化
    """
    
    def __init__(self):
        self._schemas: Dict[str, EventSchema] = {}
        self._register_default_schemas()
    
    def _register_default_schemas(self):
        """注册默认事件 Schema"""
        
        # ========== Task 事件 ==========
        self.register(EventSchema(
            event_type="task_created",
            category=EventCategory.TASK,
            required_fields={"task_id", "intent", "profile"},
            optional_fields={"context", "metadata"},
            description="任务创建"
        ))
        
        # ========== Policy 事件 ==========
        self.register(EventSchema(
            event_type="policy_decided",
            category=EventCategory.POLICY,
            required_fields={"decision_id", "task_id", "decision"},
            optional_fields={"risk_level", "degradation_mode", "allowed_capabilities", "blocked_capabilities"},
            description="策略决策"
        ))
        
        # ========== Context 事件 ==========
        self.register(EventSchema(
            event_type="context_built",
            category=EventCategory.CONTEXT,
            required_fields={"task_id", "token_count"},
            optional_fields={"sources", "trace_id", "injection_plan"},
            description="上下文构建完成"
        ))
        
        # ========== Workflow 事件 ==========
        self.register(EventSchema(
            event_type="workflow_started",
            category=EventCategory.WORKFLOW,
            required_fields={"instance_id", "workflow_id"},
            optional_fields={"version", "profile"},
            description="Workflow 启动"
        ))
        
        self.register(EventSchema(
            event_type="step_started",
            category=EventCategory.WORKFLOW,
            required_fields={"instance_id", "step_id"},
            optional_fields={"step_name", "action"},
            description="步骤开始"
        ))
        
        self.register(EventSchema(
            event_type="step_completed",
            category=EventCategory.WORKFLOW,
            required_fields={"instance_id", "step_id", "status"},
            optional_fields={"output", "duration_ms"},
            description="步骤完成"
        ))
        
        self.register(EventSchema(
            event_type="step_failed",
            category=EventCategory.WORKFLOW,
            required_fields={"instance_id", "step_id", "error_type"},
            optional_fields={"error_message", "retry_count"},
            description="步骤失败"
        ))
        
        self.register(EventSchema(
            event_type="retry_triggered",
            category=EventCategory.WORKFLOW,
            required_fields={"instance_id", "step_id", "retry_count"},
            optional_fields={"max_retries", "error_message"},
            description="重试触发"
        ))
        
        self.register(EventSchema(
            event_type="fallback_triggered",
            category=EventCategory.WORKFLOW,
            required_fields={"instance_id", "step_id"},
            optional_fields={"fallback_skill", "original_error"},
            description="Fallback 触发"
        ))
        
        self.register(EventSchema(
            event_type="rollback_triggered",
            category=EventCategory.WORKFLOW,
            required_fields={"instance_id", "step_id"},
            optional_fields={"rollback_point_id", "reason"},
            description="Rollback 触发"
        ))
        
        self.register(EventSchema(
            event_type="checkpoint_saved",
            category=EventCategory.WORKFLOW,
            required_fields={"instance_id", "checkpoint_id"},
            optional_fields={"step_id", "phase"},
            description="Checkpoint 保存"
        ))
        
        self.register(EventSchema(
            event_type="workflow_completed",
            category=EventCategory.WORKFLOW,
            required_fields={"instance_id", "status"},
            optional_fields={"output", "total_duration_ms"},
            description="Workflow 完成"
        ))
        
        # ========== Skill 事件 ==========
        self.register(EventSchema(
            event_type="skill_selected",
            category=EventCategory.SKILL,
            required_fields={"skill_id", "task_id"},
            optional_fields={"version", "confidence", "selection_chain"},
            description="技能选择"
        ))
        
        self.register(EventSchema(
            event_type="skill_executed",
            category=EventCategory.SKILL,
            required_fields={"skill_id", "status"},
            optional_fields={"version", "latency_ms", "output"},
            description="技能执行"
        ))
        
        self.register(EventSchema(
            event_type="skill_failed",
            category=EventCategory.SKILL,
            required_fields={"skill_id", "error_type"},
            optional_fields={"version", "error_message", "retry_count"},
            description="技能失败"
        ))
        
        # ========== Memory 事件 ==========
        self.register(EventSchema(
            event_type="memory_retrieved",
            category=EventCategory.MEMORY,
            required_fields={"query", "results_count"},
            optional_fields={"sources", "tokens_used", "latency_ms"},
            description="记忆检索"
        ))
        
        self.register(EventSchema(
            event_type="memory_stored",
            category=EventCategory.MEMORY,
            required_fields={"memory_id", "memory_type"},
            optional_fields={"content", "importance", "tags"},
            description="记忆存储"
        ))
        
        # ========== System 事件 ==========
        self.register(EventSchema(
            event_type="system_health_changed",
            category=EventCategory.SYSTEM,
            required_fields={"previous_health", "new_health"},
            optional_fields={"reason", "metrics"},
            description="系统健康状态变化"
        ))
        
        self.register(EventSchema(
            event_type="alert_raised",
            category=EventCategory.SYSTEM,
            required_fields={"alert_id", "severity", "alert_type"},
            optional_fields={"reason", "related_metric"},
            description="告警触发"
        ))
    
    def register(self, schema: EventSchema):
        """注册事件 Schema"""
        self._schemas[schema.event_type] = schema
    
    def get(self, event_type: str) -> Optional[EventSchema]:
        """获取事件 Schema"""
        return self._schemas.get(event_type)
    
    def validate(self, event_type: str, payload: Dict[str, Any]) -> tuple[bool, List[str]]:
        """验证事件 payload"""
        schema = self._schemas.get(event_type)
        if not schema:
            return False, [f"Unknown event type: {event_type}"]
        return schema.validate(payload)
    
    def list_event_types(self) -> List[str]:
        """列出所有事件类型"""
        return list(self._schemas.keys())
    
    def list_by_category(self, category: EventCategory) -> List[str]:
        """按分类列出事件类型"""
        return [
            event_type for event_type, schema in self._schemas.items()
            if schema.category == category
        ]


# 全局单例
_event_schema_registry = None


def get_event_schema_registry() -> EventSchemaRegistry:
    """获取事件 Schema 注册表单例"""
    global _event_schema_registry
    if _event_schema_registry is None:
        _event_schema_registry = EventSchemaRegistry()
    return _event_schema_registry
