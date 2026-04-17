"""
Memory Version Store - 记忆版本存储
记录记忆的变更历史
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
import uuid


@dataclass
class MemoryVersion:
    """记忆版本"""
    version_id: str
    memory_id: str
    version_number: int
    content: str
    change_type: str  # create, update, delete
    change_reason: str
    source_task_id: str
    previous_version_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_id": self.version_id,
            "memory_id": self.memory_id,
            "version_number": self.version_number,
            "content": self.content,
            "change_type": self.change_type,
            "change_reason": self.change_reason,
            "source_task_id": self.source_task_id,
            "previous_version_id": self.previous_version_id,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


@dataclass
class MemoryHistory:
    """记忆历史"""
    memory_id: str
    versions: List[MemoryVersion] = field(default_factory=list)
    current_version: int = 0
    created_at: str = ""
    last_modified: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "versions": [v.to_dict() for v in self.versions],
            "current_version": self.current_version,
            "created_at": self.created_at,
            "last_modified": self.last_modified
        }


class MemoryVersionStore:
    """
    记忆版本存储

    职责：
    - 记录记忆变更版本
    - 记录更新时间
    - 记录变更原因
    - 记录来源任务
    - 支持版本回滚
    """

    def __init__(
        self,
        store_path: str = "memory_context/long_term/memory_versions.json"
    ):
        self.store_path = store_path
        self._histories: Dict[str, MemoryHistory] = {}
        self._ensure_dir()
        self._load()

    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)

    def _load(self):
        """加载版本历史"""
        if not os.path.exists(self.store_path):
            return

        try:
            with open(self.store_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for memory_id, history_data in data.items():
                versions = [
                    MemoryVersion(**v) for v in history_data.get("versions", [])
                ]
                self._histories[memory_id] = MemoryHistory(
                    memory_id=memory_id,
                    versions=versions,
                    current_version=history_data.get("current_version", 0),
                    created_at=history_data.get("created_at", ""),
                    last_modified=history_data.get("last_modified", "")
                )
        except Exception:
            pass

    def _save(self):
        """保存版本历史"""
        data = {
            memory_id: history.to_dict()
            for memory_id, history in self._histories.items()
        }
        with open(self.store_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_version(
        self,
        memory_id: str,
        content: str,
        change_type: str,
        change_reason: str,
        source_task_id: str,
        metadata: Dict[str, Any] = None
    ) -> MemoryVersion:
        """
        创建新版本

        Args:
            memory_id: 记忆 ID
            content: 内容
            change_type: 变更类型 (create, update, delete)
            change_reason: 变更原因
            source_task_id: 来源任务 ID
            metadata: 元数据

        Returns:
            MemoryVersion
        """
        metadata = metadata or {}

        # 获取或创建历史
        if memory_id not in self._histories:
            self._histories[memory_id] = MemoryHistory(
                memory_id=memory_id,
                created_at=datetime.now().isoformat()
            )

        history = self._histories[memory_id]

        # 创建版本
        version_id = f"ver_{uuid.uuid4().hex[:8]}"
        version_number = len(history.versions) + 1
        previous_version_id = history.versions[-1].version_id if history.versions else None

        version = MemoryVersion(
            version_id=version_id,
            memory_id=memory_id,
            version_number=version_number,
            content=content,
            change_type=change_type,
            change_reason=change_reason,
            source_task_id=source_task_id,
            previous_version_id=previous_version_id,
            metadata=metadata
        )

        # 更新历史
        history.versions.append(version)
        history.current_version = version_number
        history.last_modified = datetime.now().isoformat()

        self._save()

        return version

    def get_version(self, memory_id: str, version_number: int = None) -> Optional[MemoryVersion]:
        """
        获取版本

        Args:
            memory_id: 记忆 ID
            version_number: 版本号（None 表示当前版本）

        Returns:
            MemoryVersion or None
        """
        history = self._histories.get(memory_id)
        if not history:
            return None

        if version_number is None:
            version_number = history.current_version

        for version in history.versions:
            if version.version_number == version_number:
                return version

        return None

    def get_history(self, memory_id: str) -> Optional[MemoryHistory]:
        """获取记忆历史"""
        return self._histories.get(memory_id)

    def get_all_versions(self, memory_id: str) -> List[MemoryVersion]:
        """获取所有版本"""
        history = self._histories.get(memory_id)
        if not history:
            return []
        return list(history.versions)

    def rollback(self, memory_id: str, target_version: int, reason: str) -> Optional[MemoryVersion]:
        """
        回滚到指定版本

        Args:
            memory_id: 记忆 ID
            target_version: 目标版本号
            reason: 回滚原因

        Returns:
            MemoryVersion or None
        """
        target = self.get_version(memory_id, target_version)
        if not target:
            return None

        # 创建回滚版本
        return self.create_version(
            memory_id=memory_id,
            content=target.content,
            change_type="rollback",
            change_reason=f"Rollback to v{target_version}: {reason}",
            source_task_id="system",
            metadata={"rollback_from_version": target_version}
        )

    def get_changes_since(self, memory_id: str, since_version: int) -> List[MemoryVersion]:
        """获取指定版本后的所有变更"""
        history = self._histories.get(memory_id)
        if not history:
            return []

        return [
            v for v in history.versions
            if v.version_number > since_version
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_memories = len(self._histories)
        total_versions = sum(len(h.versions) for h in self._histories.values())

        by_change_type: Dict[str, int] = {}
        for history in self._histories.values():
            for version in history.versions:
                by_change_type[version.change_type] = by_change_type.get(version.change_type, 0) + 1

        return {
            "total_memories": total_memories,
            "total_versions": total_versions,
            "avg_versions_per_memory": total_versions / total_memories if total_memories > 0 else 0,
            "by_change_type": by_change_type
        }


# 全局单例
_memory_version_store = None


def get_memory_version_store() -> MemoryVersionStore:
    """获取记忆版本存储单例"""
    global _memory_version_store
    if _memory_version_store is None:
        _memory_version_store = MemoryVersionStore()
    return _memory_version_store
