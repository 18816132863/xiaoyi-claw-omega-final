"""
Workflow Instance Store - Workflow 实例存储
管理 workflow 实例的生命周期
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json
import os


class InstanceStatus(Enum):
    """实例状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class WorkflowInstance:
    """Workflow 实例"""
    instance_id: str
    workflow_id: str
    version: str
    task_id: str
    profile: str
    status: InstanceStatus
    started_at: str
    completed_at: Optional[str] = None
    failed_step_id: Optional[str] = None
    recovery_summary: Dict[str, Any] = field(default_factory=dict)
    control_decision_id: Optional[str] = None
    input: Dict[str, Any] = field(default_factory=dict)
    output: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "workflow_id": self.workflow_id,
            "version": self.version,
            "task_id": self.task_id,
            "profile": self.profile,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "failed_step_id": self.failed_step_id,
            "recovery_summary": self.recovery_summary,
            "control_decision_id": self.control_decision_id,
            "input": self.input,
            "output": self.output,
            "metadata": self.metadata
        }


class WorkflowInstanceStore:
    """
    Workflow 实例存储
    
    管理 workflow 实例的生命周期：
    - create() - 创建实例
    - update() - 更新实例
    - get() - 获取实例
    - query() - 查询实例
    """
    
    def __init__(self, store_dir: str = "reports/workflow/instances"):
        self._instances: Dict[str, WorkflowInstance] = {}
        self._workflow_index: Dict[str, List[str]] = {}  # workflow_id -> instance_ids
        self._task_index: Dict[str, str] = {}  # task_id -> instance_id
        self._status_index: Dict[str, List[str]] = {s.value: [] for s in InstanceStatus}
        self._store_dir = store_dir
        self._ensure_dir()
    
    def create(
        self,
        workflow_id: str,
        version: str,
        task_id: str,
        profile: str,
        control_decision_id: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> WorkflowInstance:
        """
        创建实例
        
        Args:
            workflow_id: Workflow ID
            version: 版本
            task_id: 任务 ID
            profile: 配置
            control_decision_id: Control Plane 决策 ID
            input_data: 输入数据
            metadata: 元数据
            
        Returns:
            Workflow 实例
        """
        import uuid
        instance_id = f"inst_{uuid.uuid4().hex[:12]}"
        started_at = datetime.now().isoformat()
        
        instance = WorkflowInstance(
            instance_id=instance_id,
            workflow_id=workflow_id,
            version=version,
            task_id=task_id,
            profile=profile,
            status=InstanceStatus.PENDING,
            started_at=started_at,
            control_decision_id=control_decision_id,
            input=input_data or {},
            metadata=metadata or {}
        )
        
        # 存储
        self._instances[instance_id] = instance
        
        # 更新索引
        if workflow_id not in self._workflow_index:
            self._workflow_index[workflow_id] = []
        self._workflow_index[workflow_id].append(instance_id)
        
        self._task_index[task_id] = instance_id
        self._status_index[InstanceStatus.PENDING.value].append(instance_id)
        
        # 持久化
        self._persist(instance)
        
        return instance
    
    def update(
        self,
        instance_id: str,
        status: Optional[InstanceStatus] = None,
        output: Optional[Dict[str, Any]] = None,
        failed_step_id: Optional[str] = None,
        recovery_summary: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新实例
        
        Args:
            instance_id: 实例 ID
            status: 状态
            output: 输出
            failed_step_id: 失败步骤 ID
            recovery_summary: 恢复摘要
            
        Returns:
            是否更新成功
        """
        instance = self._instances.get(instance_id)
        if not instance:
            return False
        
        # 更新状态索引
        if status and status != instance.status:
            old_status = instance.status.value
            new_status = status.value
            
            if instance_id in self._status_index[old_status]:
                self._status_index[old_status].remove(instance_id)
            self._status_index[new_status].append(instance_id)
            
            instance.status = status
        
        # 更新其他字段
        if output is not None:
            instance.output = output
        
        if failed_step_id is not None:
            instance.failed_step_id = failed_step_id
        
        if recovery_summary is not None:
            instance.recovery_summary = recovery_summary
        
        # 完成时间
        if status in [InstanceStatus.COMPLETED, InstanceStatus.FAILED, InstanceStatus.CANCELLED]:
            instance.completed_at = datetime.now().isoformat()
        
        # 持久化
        self._persist(instance)
        
        return True
    
    def get(self, instance_id: str) -> Optional[WorkflowInstance]:
        """
        获取实例
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            Workflow 实例
        """
        return self._instances.get(instance_id)
    
    def get_by_task(self, task_id: str) -> Optional[WorkflowInstance]:
        """
        按任务 ID 获取实例
        
        Args:
            task_id: 任务 ID
            
        Returns:
            Workflow 实例
        """
        instance_id = self._task_index.get(task_id)
        if instance_id:
            return self._instances.get(instance_id)
        return None
    
    def query(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[InstanceStatus] = None,
        limit: int = 100
    ) -> List[WorkflowInstance]:
        """
        查询实例
        
        Args:
            workflow_id: Workflow ID
            status: 状态
            limit: 返回数量限制
            
        Returns:
            实例列表
        """
        results = []
        
        if workflow_id and status:
            # 交集查询
            workflow_instances = set(self._workflow_index.get(workflow_id, []))
            status_instances = set(self._status_index.get(status.value, []))
            instance_ids = workflow_instances & status_instances
            results = [self._instances[iid] for iid in instance_ids if iid in self._instances]
        elif workflow_id:
            instance_ids = self._workflow_index.get(workflow_id, [])
            results = [self._instances[iid] for iid in instance_ids if iid in self._instances]
        elif status:
            instance_ids = self._status_index.get(status.value, [])
            results = [self._instances[iid] for iid in instance_ids if iid in self._instances]
        else:
            results = list(self._instances.values())
        
        # 按时间排序
        results.sort(key=lambda x: x.started_at, reverse=True)
        
        return results[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息
        """
        return {
            "total": len(self._instances),
            "by_status": {
                status: len(ids)
                for status, ids in self._status_index.items()
            },
            "by_workflow": {
                wid: len(ids)
                for wid, ids in self._workflow_index.items()
            }
        }
    
    def _ensure_dir(self):
        """确保目录存在"""
        if self._store_dir:
            os.makedirs(self._store_dir, exist_ok=True)
    
    def _persist(self, instance: WorkflowInstance):
        """
        持久化实例
        
        Args:
            instance: 实例
        """
        if not self._store_dir:
            return
        
        try:
            file_path = os.path.join(self._store_dir, f"{instance.instance_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(instance.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception:
            pass


# 全局单例
_workflow_instance_store = None

def get_workflow_instance_store() -> WorkflowInstanceStore:
    """获取实例存储单例"""
    global _workflow_instance_store
    if _workflow_instance_store is None:
        _workflow_instance_store = WorkflowInstanceStore()
    return _workflow_instance_store
