"""
Recovery Store - 恢复记录存储
记录 workflow 执行过程中的恢复动作
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json
import os


class ErrorType(Enum):
    """错误类型"""
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    VALIDATION_ERROR = "validation_error"
    CAPABILITY_BLOCKED = "capability_blocked"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    DEPENDENCY_FAILED = "dependency_failed"
    UNKNOWN = "unknown"


class RecoveryAction(Enum):
    """恢复动作"""
    RETRY = "retry"
    FALLBACK = "fallback"
    ROLLBACK = "rollback"
    SKIP = "skip"
    ABORT = "abort"
    CHECKPOINT = "checkpoint"


@dataclass
class RecoveryRecord:
    """恢复记录"""
    record_id: str
    instance_id: str
    step_id: str
    error_type: ErrorType
    recovery_action: RecoveryAction
    timestamp: str
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    fallback_used: bool = False
    fallback_skill: Optional[str] = None
    rollback_used: bool = False
    rollback_to_step: Optional[str] = None
    checkpoint_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "instance_id": self.instance_id,
            "step_id": self.step_id,
            "error_type": self.error_type.value,
            "recovery_action": self.recovery_action.value,
            "timestamp": self.timestamp,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "fallback_used": self.fallback_used,
            "fallback_skill": self.fallback_skill,
            "rollback_used": self.rollback_used,
            "rollback_to_step": self.rollback_to_step,
            "checkpoint_id": self.checkpoint_id,
            "metadata": self.metadata
        }


class RecoveryStore:
    """
    恢复记录存储
    
    记录 workflow 执行过程中的恢复动作：
    - instance_id
    - step_id
    - error_type
    - recovery_action
    - retry_count
    - fallback_used
    - rollback_used
    - checkpoint_id
    - timestamp
    """
    
    def __init__(self, store_dir: str = "reports/workflow/recovery"):
        self._records: Dict[str, RecoveryRecord] = {}
        self._instance_index: Dict[str, List[str]] = {}  # instance_id -> record_ids
        self._step_index: Dict[str, List[str]] = {}  # step_id -> record_ids
        self._action_index: Dict[str, List[str]] = {a.value: [] for a in RecoveryAction}
        self._store_dir = store_dir
        self._ensure_dir()
    
    def record(
        self,
        instance_id: str,
        step_id: str,
        error_type: ErrorType,
        recovery_action: RecoveryAction,
        error_message: Optional[str] = None,
        retry_count: int = 0,
        max_retries: int = 3,
        fallback_skill: Optional[str] = None,
        rollback_to_step: Optional[str] = None,
        checkpoint_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RecoveryRecord:
        """
        记录恢复动作
        
        Args:
            instance_id: 实例 ID
            step_id: 步骤 ID
            error_type: 错误类型
            recovery_action: 恢复动作
            error_message: 错误消息
            retry_count: 重试次数
            max_retries: 最大重试次数
            fallback_skill: Fallback 技能
            rollback_to_step: 回滚到的步骤
            checkpoint_id: 检查点 ID
            metadata: 元数据
            
        Returns:
            恢复记录
        """
        import uuid
        record_id = f"rec_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now().isoformat()
        
        record = RecoveryRecord(
            record_id=record_id,
            instance_id=instance_id,
            step_id=step_id,
            error_type=error_type,
            recovery_action=recovery_action,
            timestamp=timestamp,
            error_message=error_message,
            retry_count=retry_count,
            max_retries=max_retries,
            fallback_used=fallback_skill is not None,
            fallback_skill=fallback_skill,
            rollback_used=rollback_to_step is not None,
            rollback_to_step=rollback_to_step,
            checkpoint_id=checkpoint_id,
            metadata=metadata or {}
        )
        
        # 存储
        self._records[record_id] = record
        
        # 更新索引
        if instance_id not in self._instance_index:
            self._instance_index[instance_id] = []
        self._instance_index[instance_id].append(record_id)
        
        if step_id not in self._step_index:
            self._step_index[step_id] = []
        self._step_index[step_id].append(record_id)
        
        self._action_index[recovery_action.value].append(record_id)
        
        # 持久化
        self._persist(record)
        
        return record
    
    def record_retry(
        self,
        instance_id: str,
        step_id: str,
        error_type: ErrorType,
        error_message: str,
        retry_count: int,
        max_retries: int
    ) -> RecoveryRecord:
        """记录重试"""
        return self.record(
            instance_id=instance_id,
            step_id=step_id,
            error_type=error_type,
            recovery_action=RecoveryAction.RETRY,
            error_message=error_message,
            retry_count=retry_count,
            max_retries=max_retries
        )
    
    def record_fallback(
        self,
        instance_id: str,
        step_id: str,
        error_type: ErrorType,
        error_message: str,
        fallback_skill: str
    ) -> RecoveryRecord:
        """记录 fallback"""
        return self.record(
            instance_id=instance_id,
            step_id=step_id,
            error_type=error_type,
            recovery_action=RecoveryAction.FALLBACK,
            error_message=error_message,
            fallback_skill=fallback_skill
        )
    
    def record_rollback(
        self,
        instance_id: str,
        step_id: str,
        error_type: ErrorType,
        error_message: str,
        rollback_to_step: str
    ) -> RecoveryRecord:
        """记录 rollback"""
        return self.record(
            instance_id=instance_id,
            step_id=step_id,
            error_type=error_type,
            recovery_action=RecoveryAction.ROLLBACK,
            error_message=error_message,
            rollback_to_step=rollback_to_step
        )
    
    def record_checkpoint(
        self,
        instance_id: str,
        step_id: str,
        checkpoint_id: str
    ) -> RecoveryRecord:
        """记录检查点"""
        return self.record(
            instance_id=instance_id,
            step_id=step_id,
            error_type=ErrorType.UNKNOWN,
            recovery_action=RecoveryAction.CHECKPOINT,
            checkpoint_id=checkpoint_id
        )
    
    def get(self, record_id: str) -> Optional[RecoveryRecord]:
        """
        获取记录
        
        Args:
            record_id: 记录 ID
            
        Returns:
            恢复记录
        """
        return self._records.get(record_id)
    
    def get_by_instance(self, instance_id: str) -> List[RecoveryRecord]:
        """
        按实例获取记录
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            记录列表
        """
        record_ids = self._instance_index.get(instance_id, [])
        return [self._records[rid] for rid in record_ids if rid in self._records]
    
    def get_by_step(self, step_id: str) -> List[RecoveryRecord]:
        """
        按步骤获取记录
        
        Args:
            step_id: 步骤 ID
            
        Returns:
            记录列表
        """
        record_ids = self._step_index.get(step_id, [])
        return [self._records[rid] for rid in record_ids if rid in self._records]
    
    def get_summary(self, instance_id: str) -> Dict[str, Any]:
        """
        获取恢复摘要
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            恢复摘要
        """
        records = self.get_by_instance(instance_id)
        
        retry_count = sum(1 for r in records if r.recovery_action == RecoveryAction.RETRY)
        fallback_count = sum(1 for r in records if r.recovery_action == RecoveryAction.FALLBACK)
        rollback_count = sum(1 for r in records if r.recovery_action == RecoveryAction.ROLLBACK)
        checkpoint_count = sum(1 for r in records if r.recovery_action == RecoveryAction.CHECKPOINT)
        
        return {
            "instance_id": instance_id,
            "total_records": len(records),
            "retry_count": retry_count,
            "fallback_count": fallback_count,
            "rollback_count": rollback_count,
            "checkpoint_count": checkpoint_count,
            "records": [r.to_dict() for r in records]
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息
        """
        return {
            "total": len(self._records),
            "by_action": {
                action: len(ids)
                for action, ids in self._action_index.items()
            },
            "instances": len(self._instance_index)
        }
    
    def _ensure_dir(self):
        """确保目录存在"""
        if self._store_dir:
            os.makedirs(self._store_dir, exist_ok=True)
    
    def _persist(self, record: RecoveryRecord):
        """
        持久化记录
        
        Args:
            record: 记录
        """
        if not self._store_dir:
            return
        
        try:
            file_path = os.path.join(self._store_dir, f"{record.record_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(record.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception:
            pass


# 全局单例
_recovery_store = None

def get_recovery_store() -> RecoveryStore:
    """获取恢复存储单例"""
    global _recovery_store
    if _recovery_store is None:
        _recovery_store = RecoveryStore()
    return _recovery_store
