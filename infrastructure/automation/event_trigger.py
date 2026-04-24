#!/usr/bin/env python3
"""
事件触发器 - V1.0.0

基于事件自动触发操作。
"""

from typing import Any, Dict, List, Optional, Callable, Pattern
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import threading
from collections import defaultdict


class TriggerEventType(Enum):
    """触发器事件类型（与 domain.tasks.specs.EventType 不同）"""
    FILE_CHANGE = "file_change"
    SCHEDULE = "schedule"
    THRESHOLD = "threshold"
    ERROR = "error"
    USER_ACTION = "user_action"
    SYSTEM = "system"
    CUSTOM = "custom"


class TriggerStatus(Enum):
    """触发器状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"


@dataclass
class Event:
    """事件"""
    id: str
    type: TriggerEventType
    source: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    processed: bool = False


@dataclass
class Trigger:
    """触发器"""
    id: str
    name: str
    event_type: TriggerEventType
    condition: str  # 条件表达式
    action: Callable
    status: TriggerStatus = TriggerStatus.ACTIVE
    priority: int = 0
    cooldown_seconds: float = 0
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TriggerResult:
    """触发结果"""
    trigger_id: str
    event_id: str
    matched: bool
    executed: bool
    result: Any = None
    error: Optional[str] = None


class EventTrigger:
    """事件触发器"""
    
    def __init__(self):
        self.triggers: Dict[str, Trigger] = {}
        self.event_history: List[Event] = []
        self.trigger_results: List[TriggerResult] = []
        self.event_counter = 0
        self.trigger_counter = 0
        self._lock = threading.Lock()
    
    def register_trigger(self,
                         name: str,
                         event_type: TriggerEventType,
                         condition: str,
                         action: Callable,
                         priority: int = 0,
                         cooldown_seconds: float = 0) -> str:
        """
        注册触发器
        
        Args:
            name: 触发器名称
            event_type: 事件类型
            condition: 条件表达式
            action: 触发动作
            priority: 优先级
            cooldown_seconds: 冷却时间
        
        Returns:
            触发器ID
        """
        with self._lock:
            trigger_id = f"trigger_{self.trigger_counter}"
            self.trigger_counter += 1
        
        trigger = Trigger(
            id=trigger_id,
            name=name,
            event_type=event_type,
            condition=condition,
            action=action,
            priority=priority,
            cooldown_seconds=cooldown_seconds
        )
        
        self.triggers[trigger_id] = trigger
        return trigger_id
    
    def unregister_trigger(self, trigger_id: str) -> bool:
        """注销触发器"""
        if trigger_id in self.triggers:
            del self.triggers[trigger_id]
            return True
        return False
    
    def emit(self,
             event_type: TriggerEventType,
             source: str,
             data: Dict[str, Any]) -> str:
        """
        发射事件
        
        Args:
            event_type: 事件类型
            source: 事件源
            data: 事件数据
        
        Returns:
            事件ID
        """
        with self._lock:
            event_id = f"event_{self.event_counter}"
            self.event_counter += 1
        
        event = Event(
            id=event_id,
            type=event_type,
            source=source,
            data=data
        )
        
        self.event_history.append(event)
        
        # 处理事件
        self._process_event(event)
        
        return event_id
    
    def _process_event(self, event: Event):
        """处理事件"""
        # 找到匹配的触发器
        matching_triggers = []
        
        for trigger in self.triggers.values():
            if trigger.status != TriggerStatus.ACTIVE:
                continue
            
            if trigger.event_type != event.type:
                continue
            
            # 检查冷却时间
            if trigger.last_triggered:
                elapsed = (datetime.now() - trigger.last_triggered).total_seconds()
                if elapsed < trigger.cooldown_seconds:
                    continue
            
            # 检查条件
            if self._evaluate_condition(trigger.condition, event):
                matching_triggers.append(trigger)
        
        # 按优先级排序
        matching_triggers.sort(key=lambda t: -t.priority)
        
        # 执行触发器
        for trigger in matching_triggers:
            result = self._execute_trigger(trigger, event)
            self.trigger_results.append(result)
    
    def _evaluate_condition(self, condition: str, event: Event) -> bool:
        """评估条件"""
        try:
            # 构建评估上下文
            context = {
                "event": event,
                "data": event.data,
                "source": event.source,
                "type": event.type.value
            }
            
            # 简单条件评估
            # 支持格式: data.key == value, data.key > value 等
            if "data." in condition:
                # 替换 data.key 为实际值
                for key, value in event.data.items():
                    condition = condition.replace(f"data.{key}", repr(value))
            
            return eval(condition, {"__builtins__": {}}, context)
        except:
            return False
    
    def _execute_trigger(self, trigger: Trigger, event: Event) -> TriggerResult:
        """执行触发器"""
        try:
            result = trigger.action(event)
            
            trigger.last_triggered = datetime.now()
            trigger.trigger_count += 1
            event.processed = True
            
            return TriggerResult(
                trigger_id=trigger.id,
                event_id=event.id,
                matched=True,
                executed=True,
                result=result
            )
            
        except Exception as e:
            return TriggerResult(
                trigger_id=trigger.id,
                event_id=event.id,
                matched=True,
                executed=False,
                error=str(e)
            )
    
    def pause_trigger(self, trigger_id: str) -> bool:
        """暂停触发器"""
        trigger = self.triggers.get(trigger_id)
        if trigger:
            trigger.status = TriggerStatus.PAUSED
            return True
        return False
    
    def resume_trigger(self, trigger_id: str) -> bool:
        """恢复触发器"""
        trigger = self.triggers.get(trigger_id)
        if trigger:
            trigger.status = TriggerStatus.ACTIVE
            return True
        return False
    
    def get_triggers_by_event_type(self, event_type: TriggerEventType) -> List[Trigger]:
        """按事件类型获取触发器"""
        return [t for t in self.triggers.values() if t.event_type == event_type]
    
    def get_event_history(self, limit: int = 100) -> List[Event]:
        """获取事件历史"""
        return self.event_history[-limit:]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            "total_triggers": len(self.triggers),
            "active_triggers": sum(1 for t in self.triggers.values() if t.status == TriggerStatus.ACTIVE),
            "total_events": len(self.event_history),
            "total_executions": len(self.trigger_results),
            "trigger_stats": [
                {"id": t.id, "name": t.name, "count": t.trigger_count}
                for t in sorted(self.triggers.values(), key=lambda x: -x.trigger_count)[:5]
            ]
        }


# 全局事件触发器
_event_trigger: Optional[EventTrigger] = None


def get_event_trigger() -> EventTrigger:
    """获取全局事件触发器"""
    global _event_trigger
    if _event_trigger is None:
        _event_trigger = EventTrigger()
    return _event_trigger
