"""
Lifecycle Manager
生命周期管理器
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import threading
from pathlib import Path


def _get_project_root() -> Path:
    """动态获取项目根目录"""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "core").exists() and (parent / "infrastructure").exists():
            return parent
    return current.parents[4]


class LifecycleState(Enum):
    """生命周期状态"""
    REGISTERED = "registered"
    INSTALLED = "installed"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    REMOVED = "removed"


@dataclass
class LifecycleRecord:
    """生命周期记录"""
    skill_id: str
    state: LifecycleState
    version: str
    installed_at: Optional[str] = None
    last_used: Optional[str] = None
    use_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class LifecycleManager:
    """生命周期管理器"""
    
    def __init__(self, data_path: Optional[Path] = None):
        if data_path is None:
            project_root = _get_project_root()
            data_path = project_root / "data" / "lifecycle.json"
        
        self.data_path = Path(data_path)
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._records: Dict[str, LifecycleRecord] = {}
        self._lock = threading.RLock()
        self._load()
    
    def _load(self):
        """从文件加载"""
        if self.data_path.exists():
            try:
                import json
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for skill_id, record_data in data.get("records", {}).items():
                        self._records[skill_id] = LifecycleRecord(
                            skill_id=skill_id,
                            state=LifecycleState(record_data.get("state", "registered")),
                            version=record_data.get("version", "1.0.0"),
                            installed_at=record_data.get("installed_at"),
                            last_used=record_data.get("last_used"),
                            use_count=record_data.get("use_count", 0),
                            metadata=record_data.get("metadata", {})
                        )
            except Exception:
                pass
    
    def _save(self):
        """保存到文件"""
        import json
        with self._lock:
            data = {
                "records": {
                    skill_id: {
                        "state": record.state.value,
                        "version": record.version,
                        "installed_at": record.installed_at,
                        "last_used": record.last_used,
                        "use_count": record.use_count,
                        "metadata": record.metadata
                    }
                    for skill_id, record in self._records.items()
                }
            }
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def register(self, skill_id: str, version: str = "1.0.0") -> LifecycleRecord:
        """注册技能"""
        with self._lock:
            record = LifecycleRecord(
                skill_id=skill_id,
                state=LifecycleState.REGISTERED,
                version=version
            )
            self._records[skill_id] = record
            self._save()
            return record
    
    def install(self, skill_id: str, version: str = "1.0.0") -> LifecycleRecord:
        """安装技能"""
        with self._lock:
            record = self._records.get(skill_id)
            if not record:
                record = LifecycleRecord(
                    skill_id=skill_id,
                    state=LifecycleState.INSTALLED,
                    version=version,
                    installed_at=datetime.now().isoformat()
                )
            else:
                record.state = LifecycleState.INSTALLED
                record.version = version
                record.installed_at = datetime.now().isoformat()
            
            self._records[skill_id] = record
            self._save()
            return record
    
    def activate(self, skill_id: str) -> Optional[LifecycleRecord]:
        """激活技能"""
        with self._lock:
            record = self._records.get(skill_id)
            if record:
                record.state = LifecycleState.ACTIVE
                self._save()
                return record
            return None
    
    def deprecate(self, skill_id: str) -> Optional[LifecycleRecord]:
        """弃用技能"""
        with self._lock:
            record = self._records.get(skill_id)
            if record:
                record.state = LifecycleState.DEPRECATED
                self._save()
                return record
            return None
    
    def remove(self, skill_id: str) -> bool:
        """移除技能"""
        with self._lock:
            if skill_id in self._records:
                self._records[skill_id].state = LifecycleState.REMOVED
                self._save()
                return True
            return False
    
    def record_usage(self, skill_id: str):
        """记录使用"""
        with self._lock:
            record = self._records.get(skill_id)
            if record:
                record.last_used = datetime.now().isoformat()
                record.use_count += 1
                self._save()
    
    def get(self, skill_id: str) -> Optional[LifecycleRecord]:
        """获取记录"""
        return self._records.get(skill_id)
    
    def get_state(self, skill_id: str) -> Optional[LifecycleState]:
        """获取状态"""
        record = self._records.get(skill_id)
        return record.state if record else None
    
    def list_by_state(self, state: LifecycleState) -> List[LifecycleRecord]:
        """按状态列出"""
        return [r for r in self._records.values() if r.state == state]


# 单例
_manager: Optional[LifecycleManager] = None
_manager_lock = threading.Lock()


def get_lifecycle_manager() -> LifecycleManager:
    """获取生命周期管理器单例"""
    global _manager
    if _manager is None:
        with _manager_lock:
            if _manager is None:
                _manager = LifecycleManager()
    return _manager
