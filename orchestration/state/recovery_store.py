"""
Recovery Store
恢复存储

管理工作流恢复记录和错误处理策略
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
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


class ErrorType(Enum):
    """错误类型"""
    TRANSIENT = "transient"          # 暂时性错误（网络、超时等）
    PERMANENT = "permanent"          # 永久性错误
    RESOURCE = "resource"            # 资源错误
    VALIDATION = "validation"        # 验证错误
    DEPENDENCY = "dependency"        # 依赖错误
    TIMEOUT = "timeout"              # 超时错误
    PERMISSION = "permission"        # 权限错误
    UNKNOWN = "unknown"              # 未知错误
    EXCEPTION = "exception"          # 异常错误


class RecoveryAction(Enum):
    """恢复动作"""
    RETRY = "retry"                  # 重试
    SKIP = "skip"                    # 跳过
    FALLBACK = "fallback"            # 降级
    ABORT = "abort"                  # 终止
    ROLLBACK = "rollback"            # 回滚
    MANUAL = "manual"                # 人工介入


@dataclass
class RecoveryRecord:
    """恢复记录"""
    record_id: str
    instance_id: str
    step_id: str
    error_type: ErrorType
    error_message: str
    recovery_action: RecoveryAction
    timestamp: str
    retry_count: int = 0
    max_retries: int = 3
    resolved: bool = False
    resolved_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "instance_id": self.instance_id,
            "step_id": self.step_id,
            "error_type": self.error_type.value,
            "error_message": self.error_message,
            "recovery_action": self.recovery_action.value,
            "timestamp": self.timestamp,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecoveryRecord':
        return cls(
            record_id=data["record_id"],
            instance_id=data["instance_id"],
            step_id=data["step_id"],
            error_type=ErrorType(data["error_type"]),
            error_message=data["error_message"],
            recovery_action=RecoveryAction(data["recovery_action"]),
            timestamp=data["timestamp"],
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            resolved=data.get("resolved", False),
            resolved_at=data.get("resolved_at"),
            metadata=data.get("metadata", {})
        )


class RecoveryStore:
    """恢复存储"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            project_root = _get_project_root()
            storage_path = project_root / "data" / "recovery_records.json"
        
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._records: Dict[str, RecoveryRecord] = {}
        self._lock = threading.RLock()
        self._load()
    
    def _load(self):
        """从文件加载记录"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get("records", []):
                        record = RecoveryRecord.from_dict(item)
                        self._records[record.record_id] = record
            except Exception:
                self._records = {}
    
    def _save(self):
        """保存记录到文件"""
        with self._lock:
            data = {
                "records": [rec.to_dict() for rec in self._records.values()]
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def record_error(self, instance_id: str, step_id: str,
                     error_type: ErrorType, error_message: str,
                     recovery_action: RecoveryAction,
                     max_retries: int = 3,
                     metadata: Optional[Dict[str, Any]] = None) -> RecoveryRecord:
        """记录错误"""
        record_id = f"{instance_id}_{step_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        record = RecoveryRecord(
            record_id=record_id,
            instance_id=instance_id,
            step_id=step_id,
            error_type=error_type,
            error_message=error_message,
            recovery_action=recovery_action,
            timestamp=datetime.now().isoformat(),
            max_retries=max_retries,
            metadata=metadata or {}
        )
        
        with self._lock:
            self._records[record_id] = record
            self._save()
        
        return record
    
    def get(self, record_id: str) -> Optional[RecoveryRecord]:
        """获取记录"""
        return self._records.get(record_id)
    
    def get_latest(self, instance_id: str, step_id: str) -> Optional[RecoveryRecord]:
        """获取最新的恢复记录"""
        records = [r for r in self._records.values() 
                   if r.instance_id == instance_id and r.step_id == step_id]
        return records[-1] if records else None
    
    def increment_retry(self, record_id: str) -> Optional[RecoveryRecord]:
        """增加重试计数"""
        with self._lock:
            record = self._records.get(record_id)
            if not record:
                return None
            
            record.retry_count += 1
            self._save()
            return record
    
    def mark_resolved(self, record_id: str) -> Optional[RecoveryRecord]:
        """标记为已解决"""
        with self._lock:
            record = self._records.get(record_id)
            if not record:
                return None
            
            record.resolved = True
            record.resolved_at = datetime.now().isoformat()
            self._save()
            return record
    
    def can_retry(self, record_id: str) -> bool:
        """检查是否可以重试"""
        record = self._records.get(record_id)
        if not record:
            return False
        return record.retry_count < record.max_retries
    
    def list_unresolved(self, instance_id: Optional[str] = None) -> List[RecoveryRecord]:
        """列出未解决的记录"""
        records = [r for r in self._records.values() if not r.resolved]
        if instance_id:
            records = [r for r in records if r.instance_id == instance_id]
        return records
    
    def list_by_instance(self, instance_id: str) -> List[RecoveryRecord]:
        """按实例列出记录"""
        return [r for r in self._records.values() if r.instance_id == instance_id]
    
    def clear_resolved(self, older_than_days: int = 7):
        """清除已解决的旧记录"""
        cutoff = datetime.now()
        with self._lock:
            to_remove = []
            for record_id, record in self._records.items():
                if record.resolved and record.resolved_at:
                    resolved_time = datetime.fromisoformat(record.resolved_at)
                    age_days = (cutoff - resolved_time).days
                    if age_days > older_than_days:
                        to_remove.append(record_id)
            
            for record_id in to_remove:
                del self._records[record_id]
            
            if to_remove:
                self._save()


# 单例实例
_recovery_store: Optional[RecoveryStore] = None
_store_lock = threading.Lock()


def get_recovery_store() -> RecoveryStore:
    """获取恢复存储单例"""
    global _recovery_store
    if _recovery_store is None:
        with _store_lock:
            if _recovery_store is None:
                _recovery_store = RecoveryStore()
    return _recovery_store
