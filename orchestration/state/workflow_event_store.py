"""
Workflow Event Store
工作流事件存储

记录工作流执行过程中的所有事件
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import json
import threading
from pathlib import Path


def _get_project_root() -> Path:
    """动态获取项目根目录"""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "core").exists() and (parent / "infrastructure").exists():
            return parent
    return current.parents[3]


class WorkflowEventType(Enum):
    """工作流事件类型（与 domain.tasks.specs.EventType 不同）"""
    # 工作流事件
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    WORKFLOW_PAUSED = "workflow_paused"
    WORKFLOW_RESUMED = "workflow_resumed"
    WORKFLOW_CANCELLED = "workflow_cancelled"
    
    # 步骤事件
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    STEP_SKIPPED = "step_skipped"
    STEP_RETRY = "step_retry"
    
    # 恢复事件
    CHECKPOINT_SAVED = "checkpoint_saved"
    CHECKPOINT_RESTORED = "checkpoint_restored"
    FALLBACK_TRIGGERED = "fallback_triggered"
    ROLLBACK_TRIGGERED = "rollback_triggered"
    RETRY_TRIGGERED = "retry_triggered"
    
    # 其他事件
    ERROR_OCCURRED = "error_occurred"
    STATE_CHANGED = "state_changed"


@dataclass
class WorkflowEvent:
    """工作流事件"""
    event_id: str
    instance_id: str
    event_type: WorkflowEventType
    timestamp: str
    payload: Dict[str, Any] = field(default_factory=dict)
    step_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "instance_id": self.instance_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "step_id": self.step_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowEvent':
        return cls(
            event_id=data["event_id"],
            instance_id=data["instance_id"],
            event_type=EventType(data["event_type"]),
            timestamp=data["timestamp"],
            payload=data.get("payload", {}),
            step_id=data.get("step_id"),
            metadata=data.get("metadata", {})
        )


class WorkflowEventStore:
    """工作流事件存储"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            project_root = _get_project_root()
            storage_path = project_root / "data" / "workflow_events.jsonl"
        
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._events: List[WorkflowEvent] = []
        self._lock = threading.RLock()
        self._load()
    
    def _load(self):
        """从文件加载事件"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            data = json.loads(line)
                            event = WorkflowEvent.from_dict(data)
                            self._events.append(event)
            except Exception:
                self._events = []
    
    def _append(self, event: WorkflowEvent):
        """追加事件到文件"""
        with open(self.storage_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False) + '\n')
    
    def record(self, instance_id: str, event_type: WorkflowEventType,
               payload: Optional[Dict[str, Any]] = None,
               step_id: Optional[str] = None,
               metadata: Optional[Dict[str, Any]] = None) -> WorkflowEvent:
        """记录事件"""
        event_id = f"{instance_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        event = WorkflowEvent(
            event_id=event_id,
            instance_id=instance_id,
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            payload=payload or {},
            step_id=step_id,
            metadata=metadata or {}
        )
        
        with self._lock:
            self._events.append(event)
            self._append(event)
        
        return event
    
    def record_workflow_started(self, instance_id: str, workflow_id: str = None,
                                version: str = None, profile: str = None,
                                control_decision_id: str = None, **kwargs) -> WorkflowEvent:
        """记录工作流启动事件"""
        return self.record(
            instance_id=instance_id,
            event_type=WorkflowEventType.WORKFLOW_STARTED,
            payload={
                "workflow_id": workflow_id,
                "version": version,
                "profile": profile,
                "control_decision_id": control_decision_id
            },
            metadata=kwargs
        )
    
    def record_workflow_completed(self, instance_id: str, **kwargs) -> WorkflowEvent:
        """记录工作流完成事件"""
        return self.record(
            instance_id=instance_id,
            event_type=WorkflowEventType.WORKFLOW_COMPLETED,
            payload=kwargs
        )
    
    def record_workflow_failed(self, instance_id: str, error: str = None, **kwargs) -> WorkflowEvent:
        """记录工作流失败事件"""
        return self.record(
            instance_id=instance_id,
            event_type=WorkflowEventType.WORKFLOW_FAILED,
            payload={"error": error},
            metadata=kwargs
        )
    
    def record_step_started(self, instance_id: str, step_id: str, **kwargs) -> WorkflowEvent:
        """记录步骤启动事件"""
        return self.record(
            instance_id=instance_id,
            event_type=WorkflowEventType.STEP_STARTED,
            step_id=step_id,
            payload=kwargs
        )
    
    def record_step_completed(self, instance_id: str, step_id: str, **kwargs) -> WorkflowEvent:
        """记录步骤完成事件"""
        return self.record(
            instance_id=instance_id,
            event_type=WorkflowEventType.STEP_COMPLETED,
            step_id=step_id,
            payload=kwargs
        )
    
    def record_step_failed(self, instance_id: str, step_id: str, error: str = None, **kwargs) -> WorkflowEvent:
        """记录步骤失败事件"""
        return self.record(
            instance_id=instance_id,
            event_type=WorkflowEventType.STEP_FAILED,
            step_id=step_id,
            payload={"error": error},
            metadata=kwargs
        )
    
    def record_checkpoint_saved(self, instance_id: str, step_id: str, 
                                checkpoint_id: str = None, **kwargs) -> WorkflowEvent:
        """记录检查点保存事件"""
        return self.record(
            instance_id=instance_id,
            event_type=WorkflowEventType.CHECKPOINT_SAVED,
            step_id=step_id,
            payload={"checkpoint_id": checkpoint_id},
            metadata=kwargs
        )
    
    def record_rollback_triggered(self, instance_id: str, step_id: str = None,
                                  reason: str = None, **kwargs) -> WorkflowEvent:
        """记录回滚触发事件"""
        return self.record(
            instance_id=instance_id,
            event_type=WorkflowEventType.ROLLBACK_TRIGGERED,
            step_id=step_id,
            payload={"reason": reason},
            metadata=kwargs
        )
    
    def get(self, event_id: str) -> Optional[WorkflowEvent]:
        """获取事件"""
        for event in self._events:
            if event.event_id == event_id:
                return event
        return None
    
    def list_by_instance(self, instance_id: str) -> List[WorkflowEvent]:
        """按实例列出事件"""
        return [e for e in self._events if e.instance_id == instance_id]
    
    def list_by_type(self, event_type: WorkflowEventType) -> List[WorkflowEvent]:
        """按类型列出事件"""
        return [e for e in self._events if e.event_type == event_type]
    
    def list_by_step(self, instance_id: str, step_id: str) -> List[WorkflowEvent]:
        """按步骤列出事件"""
        return [e for e in self._events 
                if e.instance_id == instance_id and e.step_id == step_id]
    
    def get_latest(self, instance_id: str, 
                   event_types: Optional[List[WorkflowEventType]] = None) -> Optional[WorkflowEvent]:
        """获取最新事件"""
        events = self.list_by_instance(instance_id)
        if event_types:
            events = [e for e in events if e.event_type in event_types]
        return events[-1] if events else None
    
    def clear(self, instance_id: Optional[str] = None):
        """清除事件"""
        with self._lock:
            if instance_id:
                self._events = [e for e in self._events if e.instance_id != instance_id]
            else:
                self._events = []
            
            # 重写文件
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                for event in self._events:
                    f.write(json.dumps(event.to_dict(), ensure_ascii=False) + '\n')


# 单例实例
_event_store: Optional[WorkflowEventStore] = None
_store_lock = threading.Lock()


def get_workflow_event_store() -> WorkflowEventStore:
    """获取工作流事件存储单例"""
    global _event_store
    if _event_store is None:
        with _store_lock:
            if _event_store is None:
                _event_store = WorkflowEventStore()
    return _event_store
