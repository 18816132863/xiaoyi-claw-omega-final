"""
事件总线

提供事件的发布/订阅功能
"""

from typing import Callable, Dict, List, Any, Optional
from threading import Lock
from datetime import datetime
import queue

from core.events.event_types import CoreEventType

# 别名
BusEventType = CoreEventType


class EventBus:
    """事件总线"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = Lock()
        self._event_queue: queue.Queue = queue.Queue()
        self._history: List[Dict[str, Any]] = []
        self._max_history = 1000
    
    def subscribe(self, event_type: str, handler: Callable) -> bool:
        """订阅事件"""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)
            return True
    
    def unsubscribe(self, event_type: str, handler: Callable) -> bool:
        """取消订阅"""
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(handler)
                    return True
                except ValueError:
                    return False
            return False
    
    def publish(self, event_type: str, data: Dict[str, Any] = None) -> bool:
        """发布事件"""
        event = {
            "type": event_type,
            "data": data or {},
            "timestamp": datetime.now().isoformat(),
        }
        
        # 记录历史
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        
        # 加入队列
        self._event_queue.put(event)
        
        # 通知订阅者
        with self._lock:
            handlers = self._subscribers.get(event_type, [])
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    print(f"事件处理器错误: {e}")
        
        return True
    
    def publish_async(self, event_type: str, data: Dict[str, Any] = None) -> bool:
        """异步发布事件"""
        event = {
            "type": event_type,
            "data": data or {},
            "timestamp": datetime.now().isoformat(),
        }
        self._event_queue.put(event)
        return True
    
    def get_event(self, timeout: float = None) -> Optional[Dict[str, Any]]:
        """获取事件"""
        try:
            return self._event_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_history(self, event_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """获取事件历史"""
        if event_type:
            return [e for e in self._history if e.get("type") == event_type][-limit:]
        return self._history[-limit:]
    
    def clear_history(self):
        """清除历史"""
        self._history.clear()
    
    def get_subscribers(self, event_type: str = None) -> Dict[str, List[Callable]]:
        """获取订阅者"""
        with self._lock:
            if event_type:
                return {event_type: self._subscribers.get(event_type, [])}
            return dict(self._subscribers)


# 单例
_event_bus: Optional[EventBus] = None
_event_bus_lock = Lock()


def get_event_bus() -> EventBus:
    """获取事件总线单例"""
    global _event_bus
    if _event_bus is None:
        with _event_bus_lock:
            if _event_bus is None:
                _event_bus = EventBus()
    return _event_bus


__all__ = ["EventBus", "get_event_bus"]
