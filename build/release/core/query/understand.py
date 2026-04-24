#!/usr/bin/env python3
"""
understand - V4.3.2 融合版

融合自:
- core/query/understand.py
- memory_context/search/understand.py

此模块为统一实现，其他位置通过兼容层引用
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import re

class IntentType(Enum):
    SEARCH = "search"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    QUERY = "query"
    UNKNOWN = "unknown"

@dataclass
class UnderstandingResult:
    """理解结果"""
    intent: IntentType
    entities: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    original_query: str = ""

class QueryUnderstander:
    """查询理解器"""
    
    def __init__(self):
        self._intent_patterns = {
            IntentType.SEARCH: ["搜索", "查找", "找", "search", "find"],
            IntentType.CREATE: ["创建", "新建", "添加", "create", "add"],
            IntentType.UPDATE: ["更新", "修改", "编辑", "update", "edit"],
            IntentType.DELETE: ["删除", "移除", "清除", "delete", "remove"],
            IntentType.QUERY: ["查询", "获取", "查看", "query", "get"],
        }
    
    def understand(self, query: str) -> UnderstandingResult:
        """理解查询"""
        query_lower = query.lower()
        
        # 识别意图
        intent = IntentType.UNKNOWN
        max_matches = 0
        
        for intent_type, keywords in self._intent_patterns.items():
            matches = sum(1 for kw in keywords if kw in query_lower)
            if matches > max_matches:
                max_matches = matches
                intent = intent_type
        
        # 提取实体
        entities = self._extract_entities(query)
        
        confidence = min(max_matches / 3.0, 1.0) if max_matches > 0 else 0.0
        
        return UnderstandingResult(
            intent=intent,
            entities=entities,
            confidence=confidence,
            original_query=query
        )
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """提取实体"""
        entities = {}
        
        # 时间实体
        if "今天" in query:
            entities["time"] = "today"
        elif "明天" in query:
            entities["time"] = "tomorrow"
        
        # 目标实体
        if "备忘录" in query or "note" in query.lower():
            entities["target"] = "note"
        elif "日程" in query or "calendar" in query.lower():
            entities["target"] = "calendar"
        
        return entities

# 全局实例
_understander: Optional[QueryUnderstander] = None

def get_understander() -> QueryUnderstander:
    global _understander
    if _understander is None:
        _understander = QueryUnderstander()
    return _understander
