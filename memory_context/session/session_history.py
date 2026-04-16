"""Session history tracking."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from collections import deque


@dataclass
class HistoryEntry:
    """Single history entry."""
    timestamp: datetime
    event_type: str
    content: str
    metadata: dict = field(default_factory=dict)


class SessionHistory:
    """Manages session conversation history."""
    
    def __init__(self, max_entries: int = 1000):
        self.max_entries = max_entries
        self._history: deque[HistoryEntry] = deque(maxlen=max_entries)
    
    def add(self, event_type: str, content: str, metadata: dict = None) -> None:
        entry = HistoryEntry(
            timestamp=datetime.now(),
            event_type=event_type,
            content=content,
            metadata=metadata or {}
        )
        self._history.append(entry)
    
    def get_recent(self, n: int = 10) -> list[HistoryEntry]:
        return list(self._history)[-n:]
    
    def get_by_type(self, event_type: str) -> list[HistoryEntry]:
        return [e for e in self._history if e.event_type == event_type]
    
    def search(self, query: str) -> list[HistoryEntry]:
        return [e for e in self._history if query.lower() in e.content.lower()]
    
    def to_context_string(self, max_tokens: int = 4000) -> str:
        """Convert history to context string for LLM."""
        lines = []
        current_tokens = 0
        for entry in reversed(self._history):
            line = f"[{entry.event_type}] {entry.content}"
            estimated_tokens = len(line) // 4  # Rough estimate
            if current_tokens + estimated_tokens > max_tokens:
                break
            lines.insert(0, line)
            current_tokens += estimated_tokens
        return "\n".join(lines)
