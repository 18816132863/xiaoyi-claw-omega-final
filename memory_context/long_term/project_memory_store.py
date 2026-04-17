"""
Project Memory Store - 项目记忆持久化存储
Phase3 Group4 已接入 version 和 GC
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import os


@dataclass
class ProjectMemory:
    """项目记忆条目"""
    memory_id: str
    project_id: str
    memory_type: str  # decision, context, artifact, issue
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    importance: float = 0.5  # 0.0 - 1.0
    importance_level: str = "medium"  # low, medium, high, critical
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    
    def to_dict(self) -> dict:
        return {
            "memory_id": self.memory_id,
            "project_id": self.project_id,
            "memory_type": self.memory_type,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "importance": self.importance,
            "importance_level": self.importance_level,
            "tags": self.tags,
            "metadata": self.metadata,
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProjectMemory":
        return cls(
            memory_id=data["memory_id"],
            project_id=data["project_id"],
            memory_type=data.get("memory_type", "context"),
            content=data.get("content", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
            last_accessed=datetime.fromisoformat(data.get("last_accessed", data.get("updated_at", ""))) if data.get("last_accessed") or data.get("updated_at") else datetime.now(),
            importance=data.get("importance", 0.5),
            importance_level=data.get("importance_level", "medium"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            version=data.get("version", 1)
        )


class ProjectMemoryStore:
    """
    项目记忆持久化存储
    
    支持：
    - 按项目 ID 组织
    - 按类型过滤
    - 持久化到文件
    - 重要性排序
    - 版本记录（接入 MemoryVersionStore）
    - GC 支持（接入 MemoryGC）
    """
    
    def __init__(self, store_path: str = "memory_context/data/project_memory.json"):
        self.store_path = store_path
        self._memories: Dict[str, ProjectMemory] = {}
        self._project_index: Dict[str, List[str]] = {}  # project_id -> memory_ids
        self._type_index: Dict[str, List[str]] = {}  # memory_type -> memory_ids
        
        # Group4 模块
        self._version_store = None
        self._gc = None
        
        self._load()
    
    @property
    def version_store(self):
        """延迟加载 version_store"""
        if self._version_store is None:
            from memory_context.long_term.memory_version_store import get_memory_version_store
            self._version_store = get_memory_version_store()
        return self._version_store
    
    @property
    def gc(self):
        """延迟加载 gc"""
        if self._gc is None:
            from memory_context.long_term.memory_gc import get_memory_gc
            self._gc = get_memory_gc()
        return self._gc
    
    def _load(self):
        """从文件加载"""
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, 'r') as f:
                    data = json.load(f)
                    for mem_data in data.get("memories", []):
                        memory = ProjectMemory.from_dict(mem_data)
                        self._memories[memory.memory_id] = memory
                        self._update_indexes(memory)
            except Exception as e:
                print(f"Warning: Failed to load project memory: {e}")
    
    def _save(self):
        """保存到文件"""
        os.makedirs(os.path.dirname(self.store_path) or ".", exist_ok=True)
        data = {
            "version": "1.0",
            "memories": [m.to_dict() for m in self._memories.values()]
        }
        with open(self.store_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _update_indexes(self, memory: ProjectMemory):
        """更新索引"""
        # 项目索引
        if memory.project_id not in self._project_index:
            self._project_index[memory.project_id] = []
        if memory.memory_id not in self._project_index[memory.project_id]:
            self._project_index[memory.project_id].append(memory.memory_id)
        
        # 类型索引
        if memory.memory_type not in self._type_index:
            self._type_index[memory.memory_type] = []
        if memory.memory_id not in self._type_index[memory.memory_type]:
            self._type_index[memory.memory_type].append(memory.memory_id)
    
    def _remove_from_indexes(self, memory: ProjectMemory):
        """从索引移除"""
        if memory.project_id in self._project_index:
            if memory.memory_id in self._project_index[memory.project_id]:
                self._project_index[memory.project_id].remove(memory.memory_id)
        
        if memory.memory_type in self._type_index:
            if memory.memory_id in self._type_index[memory.memory_type]:
                self._type_index[memory.memory_type].remove(memory.memory_id)
    
    def store(self, memory: ProjectMemory, source_task_id: str = "unknown", reason: str = "创建记忆") -> str:
        """存储记忆（接入 version store）"""
        self._memories[memory.memory_id] = memory
        self._update_indexes(memory)
        self._save()
        
        # 记录版本
        self.version_store.create_version(
            memory_id=memory.memory_id,
            content=memory.content,
            change_type="create",
            change_reason=reason,
            source_task_id=source_task_id
        )
        
        return memory.memory_id
    
    def retrieve(self, memory_id: str) -> Optional[ProjectMemory]:
        """获取记忆"""
        return self._memories.get(memory_id)
    
    def get_by_project(self, project_id: str) -> List[ProjectMemory]:
        """按项目获取"""
        memory_ids = self._project_index.get(project_id, [])
        return [self._memories[mid] for mid in memory_ids if mid in self._memories]
    
    def get_by_type(self, memory_type: str) -> List[ProjectMemory]:
        """按类型获取"""
        memory_ids = self._type_index.get(memory_type, [])
        return [self._memories[mid] for mid in memory_ids if mid in self._memories]
    
    def search(self, query: str, project_id: str = None) -> List[ProjectMemory]:
        """搜索记忆"""
        query_lower = query.lower()
        results = []
        
        for memory in self._memories.values():
            if project_id and memory.project_id != project_id:
                continue
            
            if query_lower in memory.content.lower():
                results.append(memory)
        
        # 按重要性排序
        importance_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        results.sort(key=lambda m: importance_order.get(m.importance, 2))
        
        return results
    
    def update(self, memory_id: str, source_task_id: str = "unknown", reason: str = "更新记忆", **kwargs) -> Optional[ProjectMemory]:
        """更新记忆（接入 version store）"""
        memory = self._memories.get(memory_id)
        if not memory:
            return None
        
        old_content = memory.content
        
        for key, value in kwargs.items():
            if hasattr(memory, key):
                setattr(memory, key, value)
        
        memory.updated_at = datetime.now()
        memory.last_accessed = datetime.now()
        memory.version += 1
        self._save()
        
        # 记录版本
        self.version_store.create_version(
            memory_id=memory_id,
            content=memory.content,
            change_type="update",
            change_reason=reason,
            source_task_id=source_task_id
        )
        
        return memory
    
    def delete(self, memory_id: str, source_task_id: str = "unknown", reason: str = "删除记忆") -> bool:
        """删除记忆（接入 version store）"""
        if memory_id not in self._memories:
            return False
        
        memory = self._memories[memory_id]
        
        # 记录版本（删除操作）
        self.version_store.create_version(
            memory_id=memory_id,
            content="",
            change_type="delete",
            change_reason=reason,
            source_task_id=source_task_id
        )
        
        self._remove_from_indexes(memory)
        del self._memories[memory_id]
        self._save()
        return True
    
    def run_gc(self, dry_run: bool = False):
        """运行 GC（正式入口）"""
        # 更新 GC 的存储路径
        self.gc.memory_store_path = self.store_path
        return self.gc.run_gc(dry_run=dry_run)
    
    def get_recent(self, project_id: str = None, limit: int = 10) -> List[ProjectMemory]:
        """获取最近记忆"""
        memories = list(self._memories.values())
        
        if project_id:
            memories = [m for m in memories if m.project_id == project_id]
        
        memories.sort(key=lambda m: m.created_at, reverse=True)
        return memories[:limit]
    
    def count(self, project_id: str = None) -> int:
        """统计数量"""
        if project_id:
            return len(self._project_index.get(project_id, []))
        return len(self._memories)
