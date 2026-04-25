"""
Checkpoint Store
检查点存储

管理工作流执行检查点，支持中断恢复
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import threading
from pathlib import Path


def _get_project_root() -> Path:
    """动态获取项目根目录"""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "core").exists() and (parent / "infrastructure").exists():
            return parent
    return current.parents[3]


@dataclass
class Checkpoint:
    """检查点"""
    checkpoint_id: str
    instance_id: str
    step_id: str
    timestamp: str
    state_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "instance_id": self.instance_id,
            "step_id": self.step_id,
            "timestamp": self.timestamp,
            "state_data": self.state_data,
            "context": self.context,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checkpoint':
        return cls(
            checkpoint_id=data["checkpoint_id"],
            instance_id=data["instance_id"],
            step_id=data["step_id"],
            timestamp=data["timestamp"],
            state_data=data.get("state_data", {}),
            context=data.get("context", {}),
            metadata=data.get("metadata", {})
        )


class CheckpointStore:
    """检查点存储"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            project_root = _get_project_root()
            storage_path = project_root / "data" / "checkpoints.json"
        
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._checkpoints: Dict[str, Checkpoint] = {}
        self._lock = threading.RLock()
        self._load()
    
    def _load(self):
        """从文件加载检查点"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get("checkpoints", []):
                        checkpoint = Checkpoint.from_dict(item)
                        self._checkpoints[checkpoint.checkpoint_id] = checkpoint
            except Exception:
                self._checkpoints = {}
    
    def _save(self):
        """保存检查点到文件"""
        with self._lock:
            data = {
                "checkpoints": [cp.to_dict() for cp in self._checkpoints.values()]
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def save(self, instance_id: str, step_id: str,
             state_data: Optional[Dict[str, Any]] = None,
             context: Optional[Dict[str, Any]] = None,
             metadata: Optional[Dict[str, Any]] = None) -> Checkpoint:
        """保存检查点"""
        checkpoint_id = f"{instance_id}_{step_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            instance_id=instance_id,
            step_id=step_id,
            timestamp=datetime.now().isoformat(),
            state_data=state_data or {},
            context=context or {},
            metadata=metadata or {}
        )
        
        with self._lock:
            self._checkpoints[checkpoint_id] = checkpoint
            self._save()
        
        return checkpoint
    
    def get(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """获取检查点"""
        return self._checkpoints.get(checkpoint_id)
    
    def get_latest(self, instance_id: str) -> Optional[Checkpoint]:
        """获取实例的最新检查点"""
        checkpoints = [cp for cp in self._checkpoints.values() 
                       if cp.instance_id == instance_id]
        if not checkpoints:
            return None
        return max(checkpoints, key=lambda cp: cp.timestamp)
    
    def get_latest_for_step(self, instance_id: str, step_id: str) -> Optional[Checkpoint]:
        """获取指定步骤的最新检查点"""
        checkpoints = [cp for cp in self._checkpoints.values() 
                       if cp.instance_id == instance_id and cp.step_id == step_id]
        if not checkpoints:
            return None
        return max(checkpoints, key=lambda cp: cp.timestamp)
    
    def list_by_instance(self, instance_id: str) -> List[Checkpoint]:
        """按实例列出检查点"""
        return [cp for cp in self._checkpoints.values() 
                if cp.instance_id == instance_id]
    
    def restore(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """恢复检查点"""
        checkpoint = self._checkpoints.get(checkpoint_id)
        if not checkpoint:
            return None
        
        return {
            "checkpoint_id": checkpoint.checkpoint_id,
            "step_id": checkpoint.step_id,
            "state_data": checkpoint.state_data,
            "context": checkpoint.context
        }
    
    def delete(self, checkpoint_id: str) -> bool:
        """删除检查点"""
        with self._lock:
            if checkpoint_id in self._checkpoints:
                del self._checkpoints[checkpoint_id]
                self._save()
                return True
            return False
    
    def delete_for_instance(self, instance_id: str):
        """删除实例的所有检查点"""
        with self._lock:
            to_remove = [cp_id for cp_id, cp in self._checkpoints.items() 
                         if cp.instance_id == instance_id]
            for cp_id in to_remove:
                del self._checkpoints[cp_id]
            if to_remove:
                self._save()
    
    def cleanup_old(self, keep_count: int = 10):
        """清理旧检查点，每个实例只保留最新的N个"""
        with self._lock:
            # 按实例分组
            by_instance: Dict[str, List[Checkpoint]] = {}
            for cp in self._checkpoints.values():
                if cp.instance_id not in by_instance:
                    by_instance[cp.instance_id] = []
                by_instance[cp.instance_id].append(cp)
            
            # 对每个实例，只保留最新的N个
            to_remove = []
            for instance_id, checkpoints in by_instance.items():
                if len(checkpoints) > keep_count:
                    sorted_cps = sorted(checkpoints, key=lambda cp: cp.timestamp)
                    to_remove.extend([cp.checkpoint_id for cp in sorted_cps[:-keep_count]])
            
            for cp_id in to_remove:
                del self._checkpoints[cp_id]
            
            if to_remove:
                self._save()
    
    def persist(self) -> bool:
        """持久化所有检查点到文件"""
        try:
            self._save()
            return True
        except Exception as e:
            print(f"保存检查点失败: {e}")
            return False
    
    def reload(self) -> bool:
        """从文件重新加载检查点"""
        try:
            self._load()
            return True
        except Exception as e:
            print(f"加载检查点失败: {e}")
            return False


# 单例实例
_checkpoint_store: Optional[CheckpointStore] = None
_store_lock = threading.Lock()


def get_checkpoint_store() -> CheckpointStore:
    """获取检查点存储单例"""
    global _checkpoint_store
    if _checkpoint_store is None:
        with _store_lock:
            if _checkpoint_store is None:
                _checkpoint_store = CheckpointStore()
    return _checkpoint_store
