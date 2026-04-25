"""
Workflow Instance Store
工作流实例存储

管理工作流实例的生命周期状态
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import json
import threading
from pathlib import Path

# 动态获取项目根目录
def _get_project_root() -> Path:
    """动态获取项目根目录"""
    current = Path(__file__).resolve()
    # 从 orchestration/state/ 向上找到项目根
    for parent in current.parents:
        if (parent / "core").exists() and (parent / "infrastructure").exists():
            return parent
    return current.parents[3]  # 默认向上4级


class InstanceStatus(Enum):
    """工作流实例状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowInstance:
    """工作流实例"""
    instance_id: str
    template_id: str
    status: InstanceStatus
    created_at: str
    updated_at: str
    context: Dict[str, Any] = field(default_factory=dict)
    current_step: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "template_id": self.template_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "context": self.context,
            "current_step": self.current_step,
            "error": self.error,
            "metadata": self.metadata,
            "started_at": self.started_at,
            "completed_at": self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowInstance':
        return cls(
            instance_id=data["instance_id"],
            template_id=data["template_id"],
            status=InstanceStatus(data["status"]),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            context=data.get("context", {}),
            current_step=data.get("current_step"),
            error=data.get("error"),
            metadata=data.get("metadata", {}),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at")
        )


class WorkflowInstanceStore:
    """工作流实例存储"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            project_root = _get_project_root()
            storage_path = project_root / "data" / "workflow_instances.json"
        
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._instances: Dict[str, WorkflowInstance] = {}
        self._lock = threading.RLock()
        self._load()
    
    def _load(self):
        """从文件加载实例"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data.get("instances", []):
                        instance = WorkflowInstance.from_dict(item)
                        self._instances[instance.instance_id] = instance
            except Exception:
                self._instances = {}
    
    def _save(self):
        """保存实例到文件"""
        with self._lock:
            data = {
                "instances": [inst.to_dict() for inst in self._instances.values()]
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def create(self, instance_id: str = None, template_id: str = None, 
               context: Optional[Dict[str, Any]] = None,
               # 新签名参数
               workflow_id: str = None, version: str = None, 
               task_id: str = None, profile: str = None,
               control_decision_id: str = None, input_data: Dict[str, Any] = None,
               **kwargs) -> WorkflowInstance:
        """创建新实例（兼容新旧签名）"""
        now = datetime.now().isoformat()
        
        # 兼容新旧签名
        final_instance_id = instance_id or workflow_id or f"inst_{now}"
        final_template_id = template_id or workflow_id or "default"
        final_context = context or input_data or {}
        
        # 合并额外参数到 metadata
        metadata = {}
        if version:
            metadata["version"] = version
        if task_id:
            metadata["task_id"] = task_id
        if profile:
            metadata["profile"] = profile
        if control_decision_id:
            metadata["control_decision_id"] = control_decision_id
        metadata.update(kwargs.get("metadata", {}))
        
        instance = WorkflowInstance(
            instance_id=final_instance_id,
            template_id=final_template_id,
            status=InstanceStatus.PENDING,
            created_at=now,
            updated_at=now,
            context=final_context,
            metadata=metadata
        )
        
        with self._lock:
            self._instances[final_instance_id] = instance
            self._save()
        
        return instance
    
    def get(self, instance_id: str) -> Optional[WorkflowInstance]:
        """获取实例"""
        return self._instances.get(instance_id)
    
    def update(self, instance_id: str, **kwargs) -> Optional[WorkflowInstance]:
        """更新实例"""
        with self._lock:
            instance = self._instances.get(instance_id)
            if not instance:
                return None
            
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            instance.updated_at = datetime.now().isoformat()
            self._save()
            return instance
    
    def update_status(self, instance_id: str, status: InstanceStatus,
                      error: Optional[str] = None) -> Optional[WorkflowInstance]:
        """更新实例状态"""
        return self.update(instance_id, status=status, error=error)
    
    def set_current_step(self, instance_id: str, step_id: str) -> Optional[WorkflowInstance]:
        """设置当前步骤"""
        return self.update(instance_id, current_step=step_id)
    
    def list_by_status(self, status: InstanceStatus) -> List[WorkflowInstance]:
        """按状态列出实例"""
        return [inst for inst in self._instances.values() if inst.status == status]
    
    def list_by_template(self, template_id: str) -> List[WorkflowInstance]:
        """按模板列出实例"""
        return [inst for inst in self._instances.values() if inst.template_id == template_id]
    
    def delete(self, instance_id: str) -> bool:
        """删除实例"""
        with self._lock:
            if instance_id in self._instances:
                del self._instances[instance_id]
                self._save()
                return True
            return False


# 单例实例
_instance_store: Optional[WorkflowInstanceStore] = None
_store_lock = threading.Lock()


def get_workflow_instance_store() -> WorkflowInstanceStore:
    """获取工作流实例存储单例"""
    global _instance_store
    if _instance_store is None:
        with _store_lock:
            if _instance_store is None:
                _instance_store = WorkflowInstanceStore()
    return _instance_store
