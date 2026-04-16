"""
Workflow Event Store - Workflow 事件存储
记录 workflow 执行过程中的所有事件
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json
import os


class EventType(Enum):
    """事件类型"""
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    RETRY_TRIGGERED = "retry_triggered"
    FALLBACK_TRIGGERED = "fallback_triggered"
    ROLLBACK_TRIGGERED = "rollback_triggered"
    CHECKPOINT_SAVED = "checkpoint_saved"
    CAPABILITY_BLOCKED = "capability_blocked"
    SAFE_MODE_ACTIVATED = "safe_mode_activated"


@dataclass
class WorkflowEvent:
    """Workflow 事件"""
    event_id: str
    instance_id: str
    event_type: EventType
    timestamp: str
    step_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "instance_id": self.instance_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "step_id": self.step_id,
            "data": self.data,
            "metadata": self.metadata
        }


class WorkflowEventStore:
    """
    Workflow 事件存储
    
    记录 workflow 执行过程中的所有事件：
    - workflow_started
    - step_started
    - step_completed
    - step_failed
    - retry_triggered
    - fallback_triggered
    - rollback_triggered
    - checkpoint_saved
    - workflow_completed
    """
    
    def __init__(self, store_dir: str = "reports/workflow/events"):
        self._events: Dict[str, WorkflowEvent] = {}
        self._instance_index: Dict[str, List[str]] = {}  # instance_id -> event_ids
        self._type_index: Dict[str, List[str]] = {e.value: [] for e in EventType}
        self._store_dir = store_dir
        self._ensure_dir()
    
    def record(
        self,
        instance_id: str,
        event_type: EventType,
        step_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowEvent:
        """
        记录事件
        
        Args:
            instance_id: 实例 ID
            event_type: 事件类型
            step_id: 步骤 ID
            data: 事件数据
            metadata: 元数据
            
        Returns:
            Workflow 事件
        """
        import uuid
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now().isoformat()
        
        event = WorkflowEvent(
            event_id=event_id,
            instance_id=instance_id,
            event_type=event_type,
            timestamp=timestamp,
            step_id=step_id,
            data=data or {},
            metadata=metadata or {}
        )
        
        # 存储
        self._events[event_id] = event
        
        # 更新索引
        if instance_id not in self._instance_index:
            self._instance_index[instance_id] = []
        self._instance_index[instance_id].append(event_id)
        
        self._type_index[event_type.value].append(event_id)
        
        # 持久化
        self._persist(event)
        
        return event
    
    def record_workflow_started(
        self,
        instance_id: str,
        workflow_id: str,
        version: str,
        profile: str,
        control_decision_id: Optional[str] = None
    ) -> WorkflowEvent:
        """记录 workflow 开始"""
        return self.record(
            instance_id=instance_id,
            event_type=EventType.WORKFLOW_STARTED,
            data={
                "workflow_id": workflow_id,
                "version": version,
                "profile": profile,
                "control_decision_id": control_decision_id
            }
        )
    
    def record_workflow_completed(
        self,
        instance_id: str,
        status: str,
        output: Optional[Dict[str, Any]] = None
    ) -> WorkflowEvent:
        """记录 workflow 完成"""
        return self.record(
            instance_id=instance_id,
            event_type=EventType.WORKFLOW_COMPLETED,
            data={
                "status": status,
                "output": output or {}
            }
        )
    
    def record_step_started(
        self,
        instance_id: str,
        step_id: str,
        step_name: str,
        action: str
    ) -> WorkflowEvent:
        """记录步骤开始"""
        return self.record(
            instance_id=instance_id,
            event_type=EventType.STEP_STARTED,
            step_id=step_id,
            data={
                "step_name": step_name,
                "action": action
            }
        )
    
    def record_step_completed(
        self,
        instance_id: str,
        step_id: str,
        output: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None
    ) -> WorkflowEvent:
        """记录步骤完成"""
        return self.record(
            instance_id=instance_id,
            event_type=EventType.STEP_COMPLETED,
            step_id=step_id,
            data={
                "output": output or {},
                "duration_ms": duration_ms
            }
        )
    
    def record_step_failed(
        self,
        instance_id: str,
        step_id: str,
        error_type: str,
        error_message: str
    ) -> WorkflowEvent:
        """记录步骤失败"""
        return self.record(
            instance_id=instance_id,
            event_type=EventType.STEP_FAILED,
            step_id=step_id,
            data={
                "error_type": error_type,
                "error_message": error_message
            }
        )
    
    def record_retry_triggered(
        self,
        instance_id: str,
        step_id: str,
        retry_count: int,
        max_retries: int
    ) -> WorkflowEvent:
        """记录重试触发"""
        return self.record(
            instance_id=instance_id,
            event_type=EventType.RETRY_TRIGGERED,
            step_id=step_id,
            data={
                "retry_count": retry_count,
                "max_retries": max_retries
            }
        )
    
    def record_fallback_triggered(
        self,
        instance_id: str,
        step_id: str,
        fallback_skill: str
    ) -> WorkflowEvent:
        """记录 fallback 触发"""
        return self.record(
            instance_id=instance_id,
            event_type=EventType.FALLBACK_TRIGGERED,
            step_id=step_id,
            data={
                "fallback_skill": fallback_skill
            }
        )
    
    def record_rollback_triggered(
        self,
        instance_id: str,
        step_id: str,
        rollback_to_step: str
    ) -> WorkflowEvent:
        """记录 rollback 触发"""
        return self.record(
            instance_id=instance_id,
            event_type=EventType.ROLLBACK_TRIGGERED,
            step_id=step_id,
            data={
                "rollback_to_step": rollback_to_step
            }
        )
    
    def record_checkpoint_saved(
        self,
        instance_id: str,
        step_id: str,
        checkpoint_id: str
    ) -> WorkflowEvent:
        """记录检查点保存"""
        return self.record(
            instance_id=instance_id,
            event_type=EventType.CHECKPOINT_SAVED,
            step_id=step_id,
            data={
                "checkpoint_id": checkpoint_id
            }
        )
    
    def get(self, event_id: str) -> Optional[WorkflowEvent]:
        """
        获取事件
        
        Args:
            event_id: 事件 ID
            
        Returns:
            Workflow 事件
        """
        return self._events.get(event_id)
    
    def get_by_instance(self, instance_id: str) -> List[WorkflowEvent]:
        """
        按实例获取事件
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            事件列表
        """
        event_ids = self._instance_index.get(instance_id, [])
        return [self._events[eid] for eid in event_ids if eid in self._events]
    
    def get_by_type(self, event_type: EventType) -> List[WorkflowEvent]:
        """
        按类型获取事件
        
        Args:
            event_type: 事件类型
            
        Returns:
            事件列表
        """
        event_ids = self._type_index.get(event_type.value, [])
        return [self._events[eid] for eid in event_ids if eid in self._events]
    
    def get_timeline(self, instance_id: str) -> List[Dict[str, Any]]:
        """
        获取事件时间线
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            事件时间线
        """
        events = self.get_by_instance(instance_id)
        events.sort(key=lambda e: e.timestamp)
        return [e.to_dict() for e in events]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息
        """
        return {
            "total": len(self._events),
            "by_type": {
                event_type: len(ids)
                for event_type, ids in self._type_index.items()
            },
            "instances": len(self._instance_index)
        }
    
    def _ensure_dir(self):
        """确保目录存在"""
        if self._store_dir:
            os.makedirs(self._store_dir, exist_ok=True)
    
    def _persist(self, event: WorkflowEvent):
        """
        持久化事件
        
        Args:
            event: 事件
        """
        if not self._store_dir:
            return
        
        try:
            file_path = os.path.join(self._store_dir, f"{event.event_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(event.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception:
            pass


# 全局单例
_workflow_event_store = None

def get_workflow_event_store() -> WorkflowEventStore:
    """获取事件存储单例"""
    global _workflow_event_store
    if _workflow_event_store is None:
        _workflow_event_store = WorkflowEventStore()
    return _workflow_event_store
