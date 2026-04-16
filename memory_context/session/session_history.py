"""Session History - 结构化会话历史记录"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import deque
import json


@dataclass
class HistoryEntry:
    """单条历史记录"""
    timestamp: datetime
    role: str  # user, assistant, system, tool
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    entry_id: str = ""
    
    def __post_init__(self):
        if not self.entry_id:
            self.entry_id = f"{self.role}_{self.timestamp.strftime('%Y%m%d%H%M%S%f')}"
    
    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "role": self.role,
            "content": self.content,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        return cls(
            entry_id=data.get("entry_id", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            role=data.get("role", "unknown"),
            content=data.get("content", ""),
            metadata=data.get("metadata", {})
        )


class SessionHistory:
    """
    结构化会话历史管理
    
    支持：
    - 按角色过滤
    - 按时间范围查询
    - Token 预算裁剪
    - 持久化读写
    """
    
    def __init__(self, max_entries: int = 1000, session_id: str = ""):
        self.max_entries = max_entries
        self.session_id = session_id
        self._entries: deque[HistoryEntry] = deque(maxlen=max_entries)
        self._created_at = datetime.now()
    
    def add(
        self,
        role: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> HistoryEntry:
        """添加历史记录"""
        entry = HistoryEntry(
            timestamp=datetime.now(),
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self._entries.append(entry)
        return entry
    
    def get_recent(self, n: int = 10) -> List[HistoryEntry]:
        """获取最近 N 条记录"""
        return list(self._entries)[-n:]
    
    def get_by_role(self, role: str) -> List[HistoryEntry]:
        """按角色过滤"""
        return [e for e in self._entries if e.role == role]
    
    def get_by_time_range(
        self,
        start: datetime,
        end: datetime = None
    ) -> List[HistoryEntry]:
        """按时间范围查询"""
        end = end or datetime.now()
        return [
            e for e in self._entries
            if start <= e.timestamp <= end
        ]
    
    def search(self, query: str) -> List[HistoryEntry]:
        """关键词搜索"""
        query_lower = query.lower()
        return [
            e for e in self._entries
            if query_lower in e.content.lower()
        ]
    
    def to_context_string(self, max_tokens: int = 4000) -> str:
        """
        转换为上下文字符串（带 Token 预算）
        
        从最新往最旧裁剪，保证不超过 max_tokens
        """
        lines = []
        current_tokens = 0
        
        for entry in reversed(self._entries):
            line = f"[{entry.role}] {entry.content}"
            estimated_tokens = len(line) // 4  # 粗略估算
            
            if current_tokens + estimated_tokens > max_tokens:
                break
            
            lines.insert(0, line)
            current_tokens += estimated_tokens
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "session_id": self.session_id,
            "max_entries": self.max_entries,
            "created_at": self._created_at.isoformat(),
            "entries": [e.to_dict() for e in self._entries]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SessionHistory":
        """反序列化"""
        history = cls(
            max_entries=data.get("max_entries", 1000),
            session_id=data.get("session_id", "")
        )
        history._created_at = datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now()
        
        for entry_data in data.get("entries", []):
            entry = HistoryEntry.from_dict(entry_data)
            history._entries.append(entry)
        
        return history
    
    def count(self) -> int:
        """记录数量"""
        return len(self._entries)
    
    def clear(self):
        """清空历史"""
        self._entries.clear()
    
    def get_token_count(self) -> int:
        """估算总 Token 数"""
        total = 0
        for entry in self._entries:
            total += len(entry.content) // 4
        return total
