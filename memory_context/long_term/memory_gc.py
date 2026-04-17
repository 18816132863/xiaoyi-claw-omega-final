"""
Memory GC - 记忆垃圾回收
清理过期和废弃的记忆
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import json
import os


class GCAction(Enum):
    """GC 动作"""
    DECAY = "decay"
    ARCHIVE = "archive"
    REMOVE = "remove"
    KEEP = "keep"


@dataclass
class GCResult:
    """GC 结果"""
    action: GCAction
    memory_id: str
    reason: str
    original_score: float
    new_score: float = 0.0
    archived_to: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.value,
            "memory_id": self.memory_id,
            "reason": self.reason,
            "original_score": self.original_score,
            "new_score": self.new_score,
            "archived_to": self.archived_to,
            "timestamp": self.timestamp
        }


@dataclass
class GCReport:
    """GC 报告"""
    total_processed: int = 0
    decayed: int = 0
    archived: int = 0
    removed: int = 0
    kept: int = 0
    results: List[GCResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_processed": self.total_processed,
            "decayed": self.decayed,
            "archived": self.archived,
            "removed": self.removed,
            "kept": self.kept,
            "results": [r.to_dict() for r in self.results],
            "timestamp": self.timestamp
        }


class MemoryGC:
    """
    记忆垃圾回收

    职责：
    - 衰减旧记忆的重要性
    - 归档不活跃记忆
    - 删除废弃记忆
    - 保留关键记忆
    """

    def __init__(
        self,
        memory_store_path: str = "memory_context/long_term/memory_store.json",
        archive_path: str = "memory_context/long_term/memory_archive.json"
    ):
        self.memory_store_path = memory_store_path
        self.archive_path = archive_path

        # GC 配置
        self._config = {
            "decay_threshold_days": 30,
            "archive_threshold_days": 90,
            "remove_threshold_days": 365,
            "decay_factor": 0.9,
            "min_importance": 0.1,
            "preserve_tags": ["critical", "permanent", "user_marked"]
        }

        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.memory_store_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.archive_path), exist_ok=True)

    def run_gc(self, dry_run: bool = False) -> GCReport:
        """
        运行 GC

        Args:
            dry_run: 是否只模拟不实际执行

        Returns:
            GCReport
        """
        report = GCReport()

        # 加载记忆
        memories = self._load_memories()
        report.total_processed = len(memories)

        to_decay = []
        to_archive = []
        to_remove = []
        to_keep = []

        for memory in memories:
            result = self._evaluate_memory(memory)
            report.results.append(result)

            if result.action == GCAction.DECAY:
                to_decay.append(memory)
                report.decayed += 1
            elif result.action == GCAction.ARCHIVE:
                to_archive.append(memory)
                report.archived += 1
            elif result.action == GCAction.REMOVE:
                to_remove.append(memory)
                report.removed += 1
            else:
                to_keep.append(memory)
                report.kept += 1

        if not dry_run:
            # 执行衰减
            for memory in to_decay:
                self._apply_decay(memory)

            # 执行归档
            for memory in to_archive:
                self._archive_memory(memory)

            # 执行删除
            remaining = [m for m in memories if m not in to_remove and m not in to_archive]
            self._save_memories(remaining)

        return report

    def _evaluate_memory(self, memory: Dict[str, Any]) -> GCResult:
        """评估记忆"""
        memory_id = memory.get("memory_id", "")
        importance = memory.get("importance", 0.5)
        tags = memory.get("tags", [])
        last_accessed = memory.get("last_accessed", "")
        created_at = memory.get("created_at", "")

        # 检查是否需要保留
        for tag in self._config["preserve_tags"]:
            if tag in tags:
                return GCResult(
                    action=GCAction.KEEP,
                    memory_id=memory_id,
                    reason=f"Preserved by tag: {tag}",
                    original_score=importance
                )

        # 计算年龄
        try:
            created = datetime.fromisoformat(created_at) if created_at else datetime.now()
            age_days = (datetime.now() - created).days
        except Exception:
            age_days = 0

        # 检查最后访问时间
        try:
            last_acc = datetime.fromisoformat(last_accessed) if last_accessed else created
            inactive_days = (datetime.now() - last_acc).days
        except Exception:
            inactive_days = age_days

        # 决定动作
        if inactive_days >= self._config["remove_threshold_days"]:
            return GCResult(
                action=GCAction.REMOVE,
                memory_id=memory_id,
                reason=f"Inactive for {inactive_days} days",
                original_score=importance
            )

        if inactive_days >= self._config["archive_threshold_days"]:
            return GCResult(
                action=GCAction.ARCHIVE,
                memory_id=memory_id,
                reason=f"Inactive for {inactive_days} days",
                original_score=importance
            )

        if inactive_days >= self._config["decay_threshold_days"]:
            new_score = importance * self._config["decay_factor"]
            return GCResult(
                action=GCAction.DECAY,
                memory_id=memory_id,
                reason=f"Inactive for {inactive_days} days",
                original_score=importance,
                new_score=new_score
            )

        return GCResult(
            action=GCAction.KEEP,
            memory_id=memory_id,
            reason="Active memory",
            original_score=importance
        )

    def _apply_decay(self, memory: Dict[str, Any]):
        """应用衰减"""
        importance = memory.get("importance", 0.5)
        memory["importance"] = importance * self._config["decay_factor"]
        memory["last_decayed"] = datetime.now().isoformat()

    def _archive_memory(self, memory: Dict[str, Any]):
        """归档记忆"""
        archive = self._load_archive()
        memory["archived_at"] = datetime.now().isoformat()
        archive.append(memory)
        self._save_archive(archive)

    def _load_memories(self) -> List[Dict[str, Any]]:
        """加载记忆"""
        if not os.path.exists(self.memory_store_path):
            return []
        try:
            with open(self.memory_store_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_memories(self, memories: List[Dict[str, Any]]):
        """保存记忆"""
        with open(self.memory_store_path, 'w', encoding='utf-8') as f:
            json.dump(memories, f, indent=2, ensure_ascii=False)

    def _load_archive(self) -> List[Dict[str, Any]]:
        """加载归档"""
        if not os.path.exists(self.archive_path):
            return []
        try:
            with open(self.archive_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_archive(self, archive: List[Dict[str, Any]]):
        """保存归档"""
        with open(self.archive_path, 'w', encoding='utf-8') as f:
            json.dump(archive, f, indent=2, ensure_ascii=False)

    def set_config(self, key: str, value: Any):
        """设置配置"""
        self._config[key] = value

    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return dict(self._config)


# 全局单例
_memory_gc = None


def get_memory_gc() -> MemoryGC:
    """获取记忆 GC 单例"""
    global _memory_gc
    if _memory_gc is None:
        _memory_gc = MemoryGC()
    return _memory_gc
