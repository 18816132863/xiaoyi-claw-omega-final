#!/usr/bin/env python3
"""
feedback - V4.3.2 融合版

融合自:
- governance/audit/feedback.py
- memory_context/feedback/feedback.py

此模块为统一实现，其他位置通过兼容层引用
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class FeedbackType(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

@dataclass
class Feedback:
    """反馈"""
    id: str
    type: FeedbackType
    content: str
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class FeedbackManager:
    """反馈管理器"""
    
    def __init__(self):
        self._feedbacks: List[Feedback] = []
    
    def add(self, feedback: Feedback):
        """添加反馈"""
        self._feedbacks.append(feedback)
    
    def get_by_type(self, feedback_type: FeedbackType) -> List[Feedback]:
        """按类型获取反馈"""
        return [f for f in self._feedbacks if f.type == feedback_type]
    
    def get_by_source(self, source: str) -> List[Feedback]:
        """按来源获取反馈"""
        return [f for f in self._feedbacks if f.source == source]
    
    def get_all(self) -> List[Feedback]:
        """获取所有反馈"""
        return self._feedbacks.copy()
    
    def clear(self):
        """清空反馈"""
        self._feedbacks.clear()

# 全局实例
_manager: Optional[FeedbackManager] = None

def get_feedback_manager() -> FeedbackManager:
    global _manager
    if _manager is None:
        _manager = FeedbackManager()
    return _manager
