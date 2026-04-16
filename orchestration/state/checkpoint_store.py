"""Checkpoint Store - 检查点存储"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os


@dataclass
class Checkpoint:
    """检查点"""
    checkpoint_id: str
    workflow_id: str
    step_id: str
    timestamp: str
    state: Dict[str, Any]
    completed_steps: List[str]
    pending_steps: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class CheckpointStore:
    """
    检查点存储
    
    职责：
    - 保存 workflow 执行状态
    - 支持从检查点恢复
    - 管理检查点生命周期
    """
    
    def __init__(self, store_dir: str = "orchestration/state/checkpoints"):
        self.store_dir = store_dir
        self._checkpoints: Dict[str, Checkpoint] = {}
        self._ensure_dir()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(self.store_dir, exist_ok=True)
    
    def save(
        self,
        workflow_id: str,
        step_id: str,
        state: Dict[str, Any],
        completed_steps: List[str],
        pending_steps: List[str],
        metadata: Dict[str, Any] = None
    ) -> Checkpoint:
        """
        保存检查点
        
        Args:
            workflow_id: 工作流 ID
            step_id: 当前步骤 ID
            state: 当前状态
            completed_steps: 已完成步骤
            pending_steps: 待执行步骤
            metadata: 元数据
        
        Returns:
            Checkpoint
        """
        import uuid
        
        checkpoint_id = f"cp_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            workflow_id=workflow_id,
            step_id=step_id,
            timestamp=timestamp,
            state=state,
            completed_steps=completed_steps,
            pending_steps=pending_steps,
            metadata=metadata or {}
        )
        
        self._checkpoints[checkpoint_id] = checkpoint
        self._save_checkpoint(checkpoint)
        
        return checkpoint
    
    def _save_checkpoint(self, checkpoint: Checkpoint):
        """保存检查点到文件"""
        path = self._get_path(checkpoint.checkpoint_id)
        data = {
            "checkpoint_id": checkpoint.checkpoint_id,
            "workflow_id": checkpoint.workflow_id,
            "step_id": checkpoint.step_id,
            "timestamp": checkpoint.timestamp,
            "state": checkpoint.state,
            "completed_steps": checkpoint.completed_steps,
            "pending_steps": checkpoint.pending_steps,
            "metadata": checkpoint.metadata
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _get_path(self, checkpoint_id: str) -> str:
        """获取检查点文件路径"""
        return os.path.join(self.store_dir, f"{checkpoint_id}.json")
    
    def load(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        加载检查点
        
        Args:
            checkpoint_id: 检查点 ID
        
        Returns:
            Checkpoint or None
        """
        if checkpoint_id in self._checkpoints:
            return self._checkpoints[checkpoint_id]
        
        path = self._get_path(checkpoint_id)
        if not os.path.exists(path):
            return None
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        checkpoint = Checkpoint(
            checkpoint_id=data["checkpoint_id"],
            workflow_id=data["workflow_id"],
            step_id=data["step_id"],
            timestamp=data["timestamp"],
            state=data["state"],
            completed_steps=data["completed_steps"],
            pending_steps=data["pending_steps"],
            metadata=data.get("metadata", {})
        )
        
        self._checkpoints[checkpoint_id] = checkpoint
        return checkpoint
    
    def load_latest(self, workflow_id: str) -> Optional[Checkpoint]:
        """
        加载最新的检查点
        
        Args:
            workflow_id: 工作流 ID
        
        Returns:
            Checkpoint or None
        """
        checkpoints = self.list_by_workflow(workflow_id)
        if not checkpoints:
            return None
        
        return max(checkpoints, key=lambda c: c.timestamp)
    
    def list_by_workflow(self, workflow_id: str) -> List[Checkpoint]:
        """
        列出工作流的所有检查点
        
        Args:
            workflow_id: 工作流 ID
        
        Returns:
            List of Checkpoint
        """
        checkpoints = []
        
        # 从内存获取
        for cp in self._checkpoints.values():
            if cp.workflow_id == workflow_id:
                checkpoints.append(cp)
        
        # 从文件加载
        for filename in os.listdir(self.store_dir):
            if filename.endswith(".json"):
                cp = self.load(filename[:-5])
                if cp and cp.workflow_id == workflow_id:
                    if cp not in checkpoints:
                        checkpoints.append(cp)
        
        return sorted(checkpoints, key=lambda c: c.timestamp)
    
    def delete(self, checkpoint_id: str) -> bool:
        """
        删除检查点
        
        Args:
            checkpoint_id: 检查点 ID
        
        Returns:
            bool
        """
        if checkpoint_id in self._checkpoints:
            del self._checkpoints[checkpoint_id]
        
        path = self._get_path(checkpoint_id)
        if os.path.exists(path):
            os.remove(path)
            return True
        
        return False
    
    def clear_workflow(self, workflow_id: str):
        """
        清除工作流的所有检查点
        
        Args:
            workflow_id: 工作流 ID
        """
        checkpoints = self.list_by_workflow(workflow_id)
        for cp in checkpoints:
            self.delete(cp.checkpoint_id)
    
    def get_resume_info(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        获取恢复信息
        
        Args:
            checkpoint_id: 检查点 ID
        
        Returns:
            Dict with resume info
        """
        checkpoint = self.load(checkpoint_id)
        if not checkpoint:
            return {
                "success": False,
                "error": "checkpoint_not_found"
            }
        
        return {
            "success": True,
            "checkpoint_id": checkpoint.checkpoint_id,
            "workflow_id": checkpoint.workflow_id,
            "resume_from_step": checkpoint.step_id,
            "completed_steps": checkpoint.completed_steps,
            "pending_steps": checkpoint.pending_steps,
            "state": checkpoint.state,
            "timestamp": checkpoint.timestamp
        }
