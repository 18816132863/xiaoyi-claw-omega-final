"""
Event Persistence - 事件持久化
Phase3 Group5 核心模块
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import os
import uuid


@dataclass
class Event:
    """事件"""
    event_id: str
    event_type: str
    timestamp: str
    payload: Dict[str, Any]
    task_id: Optional[str] = None
    workflow_instance_id: Optional[str] = None
    skill_id: Optional[str] = None
    decision_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "task_id": self.task_id,
            "workflow_instance_id": self.workflow_instance_id,
            "skill_id": self.skill_id,
            "decision_id": self.decision_id
        }


class EventPersistence:
    """
    事件持久化
    
    职责：
    - 追加事件
    - 按条件查询事件
    - 生成时间线
    """
    
    def __init__(self, store_path: str = "reports/observability/events.jsonl"):
        self.store_path = store_path
        self._events: List[Event] = []
        self._task_index: Dict[str, List[str]] = {}
        self._workflow_index: Dict[str, List[str]] = {}
        self._type_index: Dict[str, List[str]] = {}
        self._ensure_dir()
        self._load()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
    
    def _load(self):
        """加载已有事件"""
        if not os.path.exists(self.store_path):
            return
        
        try:
            with open(self.store_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        event = Event(
                            event_id=data.get("event_id", ""),
                            event_type=data.get("event_type", ""),
                            timestamp=data.get("timestamp", ""),
                            payload=data.get("payload", {}),
                            task_id=data.get("task_id"),
                            workflow_instance_id=data.get("workflow_instance_id"),
                            skill_id=data.get("skill_id"),
                            decision_id=data.get("decision_id")
                        )
                        self._index_event(event)
                        self._events.append(event)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
    
    def _index_event(self, event: Event):
        """索引事件"""
        # task 索引
        if event.task_id:
            if event.task_id not in self._task_index:
                self._task_index[event.task_id] = []
            self._task_index[event.task_id].append(event.event_id)
        
        # workflow 索引
        if event.workflow_instance_id:
            if event.workflow_instance_id not in self._workflow_index:
                self._workflow_index[event.workflow_instance_id] = []
            self._workflow_index[event.workflow_instance_id].append(event.event_id)
        
        # type 索引
        if event.event_type not in self._type_index:
            self._type_index[event.event_type] = []
        self._type_index[event.event_type].append(event.event_id)
    
    def append(
        self,
        event_type: str,
        payload: Dict[str, Any],
        task_id: str = None,
        workflow_instance_id: str = None,
        skill_id: str = None,
        decision_id: str = None,
        validate: bool = True
    ) -> Event:
        """
        追加事件
        
        Args:
            event_type: 事件类型
            payload: 事件 payload
            task_id: 任务 ID
            workflow_instance_id: Workflow 实例 ID
            skill_id: 技能 ID
            decision_id: 决策 ID
            validate: 是否验证 schema
        
        Returns:
            Event
        """
        # 验证 schema
        if validate:
            from core.events.event_schema_registry import get_event_schema_registry
            registry = get_event_schema_registry()
            valid, errors = registry.validate(event_type, payload)
            if not valid:
                raise ValueError(f"Event validation failed: {errors}")
        
        # 创建事件
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            payload=payload,
            task_id=task_id,
            workflow_instance_id=workflow_instance_id,
            skill_id=skill_id,
            decision_id=decision_id
        )
        
        # 索引
        self._index_event(event)
        self._events.append(event)
        
        # 持久化
        self._persist(event)
        
        return event
    
    def _persist(self, event: Event):
        """持久化事件"""
        try:
            with open(self.store_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event.to_dict(), ensure_ascii=False) + '\n')
        except Exception:
            pass
    
    def list(
        self,
        task_id: str = None,
        workflow_instance_id: str = None,
        event_type: str = None,
        limit: int = 100
    ) -> List[Event]:
        """
        查询事件
        
        Args:
            task_id: 任务 ID
            workflow_instance_id: Workflow 实例 ID
            event_type: 事件类型
            limit: 最大返回数
        
        Returns:
            List[Event]
        """
        results = []
        
        # 使用索引加速
        if task_id:
            event_ids = set(self._task_index.get(task_id, []))
            candidates = [e for e in self._events if e.event_id in event_ids]
        elif workflow_instance_id:
            event_ids = set(self._workflow_index.get(workflow_instance_id, []))
            candidates = [e for e in self._events if e.event_id in event_ids]
        else:
            candidates = self._events
        
        # 过滤
        for event in candidates:
            if event_type and event.event_type != event_type:
                continue
            results.append(event)
        
        # 按时间排序
        results.sort(key=lambda e: e.timestamp)
        
        return results[-limit:]
    
    def get_timeline(
        self,
        task_id: str = None,
        workflow_instance_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        获取时间线
        
        Args:
            task_id: 任务 ID
            workflow_instance_id: Workflow 实例 ID
        
        Returns:
            List[Dict]
        """
        events = self.list(task_id=task_id, workflow_instance_id=workflow_instance_id)
        
        timeline = []
        for event in events:
            timeline.append({
                "event_id": event.event_id,
                "event_type": event.event_type,
                "timestamp": event.timestamp,
                "summary": self._summarize_event(event)
            })
        
        return timeline
    
    def _summarize_event(self, event: Event) -> str:
        """总结事件"""
        summaries = {
            "task_created": f"Task created: {event.payload.get('intent', 'unknown')}",
            "policy_decided": f"Policy decision: {event.payload.get('decision', 'unknown')}",
            "context_built": f"Context built: {event.payload.get('token_count', 0)} tokens",
            "workflow_started": f"Workflow started: {event.payload.get('workflow_id', 'unknown')}",
            "step_started": f"Step started: {event.payload.get('step_id', 'unknown')}",
            "step_completed": f"Step completed: {event.payload.get('step_id', 'unknown')}",
            "step_failed": f"Step failed: {event.payload.get('step_id', 'unknown')} - {event.payload.get('error_type', 'unknown')}",
            "retry_triggered": f"Retry triggered: attempt {event.payload.get('retry_count', 0)}",
            "fallback_triggered": f"Fallback triggered: {event.payload.get('fallback_skill', 'unknown')}",
            "rollback_triggered": f"Rollback triggered",
            "checkpoint_saved": f"Checkpoint saved: {event.payload.get('checkpoint_id', 'unknown')}",
            "workflow_completed": f"Workflow completed: {event.payload.get('status', 'unknown')}",
            "skill_selected": f"Skill selected: {event.payload.get('skill_id', 'unknown')}",
            "skill_executed": f"Skill executed: {event.payload.get('skill_id', 'unknown')}",
            "skill_failed": f"Skill failed: {event.payload.get('skill_id', 'unknown')}",
        }
        return summaries.get(event.event_type, f"Event: {event.event_type}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        type_counts = {}
        for event_type, ids in self._type_index.items():
            type_counts[event_type] = len(ids)
        
        return {
            "total_events": len(self._events),
            "by_type": type_counts,
            "unique_tasks": len(self._task_index),
            "unique_workflows": len(self._workflow_index)
        }


# 全局单例
_event_persistence = None


def get_event_persistence() -> EventPersistence:
    """获取事件持久化单例"""
    global _event_persistence
    if _event_persistence is None:
        _event_persistence = EventPersistence()
    return _event_persistence
