"""Long-term memory stores."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import json


@dataclass
class MemoryEntry:
    """Base memory entry."""
    id: str
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    importance: str = "medium"  # low, medium, high, critical
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class BaseMemoryStore(ABC):
    """Abstract base for memory stores."""
    
    @abstractmethod
    def store(self, entry: MemoryEntry) -> str:
        pass
    
    @abstractmethod
    def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        pass
    
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> list[MemoryEntry]:
        pass
    
    @abstractmethod
    def update(self, entry_id: str, **kwargs) -> Optional[MemoryEntry]:
        pass
    
    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        pass


class UserMemoryStore(BaseMemoryStore):
    """Stores user preferences and personalization data."""
    
    def __init__(self, store_path: str = "memory_context/data/user_memory.json"):
        self.store_path = store_path
        self._entries: dict[str, MemoryEntry] = {}
        self._load()
    
    def _load(self):
        # TODO: Load from file
        pass
    
    def _save(self):
        # TODO: Save to file
        pass
    
    def store(self, entry: MemoryEntry) -> str:
        self._entries[entry.id] = entry
        self._save()
        return entry.id
    
    def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        return self._entries.get(entry_id)
    
    def search(self, query: str, limit: int = 10) -> list[MemoryEntry]:
        results = []
        for entry in self._entries.values():
            if query.lower() in entry.content.lower():
                results.append(entry)
        return results[:limit]
    
    def update(self, entry_id: str, **kwargs) -> Optional[MemoryEntry]:
        if entry_id not in self._entries:
            return None
        entry = self._entries[entry_id]
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        entry.updated_at = datetime.now()
        self._save()
        return entry
    
    def delete(self, entry_id: str) -> bool:
        if entry_id in self._entries:
            del self._entries[entry_id]
            self._save()
            return True
        return False
    
    def get_preference(self, key: str) -> Optional[Any]:
        """Get a specific user preference."""
        for entry in self._entries.values():
            if entry.metadata.get("preference_key") == key:
                return entry.content
        return None
    
    def set_preference(self, key: str, value: str, importance: str = "medium") -> str:
        """Set a user preference."""
        entry_id = f"pref_{key}"
        entry = MemoryEntry(
            id=entry_id,
            content=value,
            importance=importance,
            metadata={"preference_key": key}
        )
        return self.store(entry)


class ProjectMemoryStore(BaseMemoryStore):
    """Stores project history and context."""
    
    def __init__(self, store_path: str = "memory_context/data/project_memory.json"):
        self.store_path = store_path
        self._entries: dict[str, MemoryEntry] = {}
        self._projects: dict[str, list[str]] = {}  # project_id -> entry_ids
    
    def store(self, entry: MemoryEntry, project_id: str = None) -> str:
        self._entries[entry.id] = entry
        if project_id:
            if project_id not in self._projects:
                self._projects[project_id] = []
            self._projects[project_id].append(entry.id)
        return entry.id
    
    def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        return self._entries.get(entry_id)
    
    def search(self, query: str, limit: int = 10) -> list[MemoryEntry]:
        results = []
        for entry in self._entries.values():
            if query.lower() in entry.content.lower():
                results.append(entry)
        return results[:limit]
    
    def get_project_entries(self, project_id: str) -> list[MemoryEntry]:
        entry_ids = self._projects.get(project_id, [])
        return [self._entries[eid] for eid in entry_ids if eid in self._entries]
    
    def update(self, entry_id: str, **kwargs) -> Optional[MemoryEntry]:
        if entry_id not in self._entries:
            return None
        entry = self._entries[entry_id]
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        entry.updated_at = datetime.now()
        return entry
    
    def delete(self, entry_id: str) -> bool:
        if entry_id in self._entries:
            del self._entries[entry_id]
            # Remove from project mappings
            for project_id, entry_ids in self._projects.items():
                if entry_id in entry_ids:
                    entry_ids.remove(entry_id)
            return True
        return False


class DecisionLogStore(BaseMemoryStore):
    """Stores architectural and design decisions."""
    
    def __init__(self, store_path: str = "memory_context/data/decision_log.json"):
        self.store_path = store_path
        self._entries: dict[str, MemoryEntry] = {}
    
    def store(self, entry: MemoryEntry) -> str:
        self._entries[entry.id] = entry
        return entry.id
    
    def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        return self._entries.get(entry_id)
    
    def search(self, query: str, limit: int = 10) -> list[MemoryEntry]:
        results = []
        for entry in self._entries.values():
            if query.lower() in entry.content.lower():
                results.append(entry)
        return results[:limit]
    
    def log_decision(
        self,
        decision_id: str,
        title: str,
        context: str,
        decision: str,
        rationale: str,
        alternatives: list[str] = None,
        consequences: list[str] = None
    ) -> str:
        """Log a structured decision."""
        content = f"# {title}\n\n## Context\n{context}\n\n## Decision\n{decision}\n\n## Rationale\n{rationale}"
        if alternatives:
            content += f"\n\n## Alternatives\n" + "\n".join(f"- {a}" for a in alternatives)
        if consequences:
            content += f"\n\n## Consequences\n" + "\n".join(f"- {c}" for c in consequences)
        
        entry = MemoryEntry(
            id=decision_id,
            content=content,
            importance="high",
            tags=["decision", "architecture"],
            metadata={
                "title": title,
                "alternatives": alternatives or [],
                "consequences": consequences or []
            }
        )
        return self.store(entry)
    
    def update(self, entry_id: str, **kwargs) -> Optional[MemoryEntry]:
        if entry_id not in self._entries:
            return None
        entry = self._entries[entry_id]
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        entry.updated_at = datetime.now()
        return entry
    
    def delete(self, entry_id: str) -> bool:
        if entry_id in self._entries:
            del self._entries[entry_id]
            return True
        return False
