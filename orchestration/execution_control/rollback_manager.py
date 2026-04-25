"""Rollback Manager - 回滚管理器"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os


@dataclass
class RollbackPoint:
    """回滚点"""
    point_id: str
    step_id: str
    timestamp: str
    state: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RollbackResult:
    """回滚结果"""
    success: bool
    point_id: str
    restored_state: Dict[str, Any]
    message: str
    error: Optional[str] = None


class RollbackManager:
    """
    回滚管理器
    
    职责：
    - 创建回滚点
    - 执行回滚
    - 管理回滚历史
    """
    
    def __init__(self, rollback_dir: str = "orchestration/state/rollback"):
        self.rollback_dir = rollback_dir
        self._points: Dict[str, RollbackPoint] = {}
        self._history: List[Dict[str, Any]] = []
        self._ensure_dir()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(self.rollback_dir, exist_ok=True)
    
    def create_point(
        self,
        step_id: str,
        state: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> RollbackPoint:
        """
        创建回滚点
        
        Args:
            step_id: 步骤 ID
            state: 当前状态
            metadata: 元数据
        
        Returns:
            RollbackPoint
        """
        import uuid
        
        point_id = f"rb_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        point = RollbackPoint(
            point_id=point_id,
            step_id=step_id,
            timestamp=timestamp,
            state=state,
            metadata=metadata or {}
        )
        
        self._points[point_id] = point
        self._save_point(point)
        
        return point
    
    def _save_point(self, point: RollbackPoint):
        """保存回滚点"""
        path = os.path.join(self.rollback_dir, f"{point.point_id}.json")
        data = {
            "point_id": point.point_id,
            "step_id": point.step_id,
            "timestamp": point.timestamp,
            "state": point.state,
            "metadata": point.metadata
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_point(self, point_id: str) -> Optional[RollbackPoint]:
        """加载回滚点"""
        path = os.path.join(self.rollback_dir, f"{point_id}.json")
        if not os.path.exists(path):
            return None
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        return RollbackPoint(
            point_id=data["point_id"],
            step_id=data["step_id"],
            timestamp=data["timestamp"],
            state=data["state"],
            metadata=data.get("metadata", {})
        )
    
    def rollback(self, point_id: str) -> RollbackResult:
        """
        执行回滚
        
        Args:
            point_id: 回滚点 ID
        
        Returns:
            RollbackResult
        """
        # 加载回滚点
        point = self._points.get(point_id) or self._load_point(point_id)
        
        if not point:
            return RollbackResult(
                success=False,
                point_id=point_id,
                restored_state={},
                message=f"Rollback point {point_id} not found",
                error="point_not_found"
            )
        
        # 记录回滚历史
        self._history.append({
            "point_id": point_id,
            "step_id": point.step_id,
            "timestamp": datetime.now().isoformat(),
            "action": "rollback"
        })
        
        return RollbackResult(
            success=True,
            point_id=point_id,
            restored_state=point.state,
            message=f"Rolled back to point {point_id} (step: {point.step_id})"
        )
    
    def rollback_to_step(self, step_id: str) -> RollbackResult:
        """
        回滚到指定步骤
        
        Args:
            step_id: 步骤 ID
        
        Returns:
            RollbackResult
        """
        # 查找该步骤的最近回滚点
        matching_points = [
            p for p in self._points.values()
            if p.step_id == step_id
        ]
        
        if not matching_points:
            # 尝试从文件加载
            for filename in os.listdir(self.rollback_dir):
                if filename.endswith(".json"):
                    point = self._load_point(filename[:-5])
                    if point and point.step_id == step_id:
                        matching_points.append(point)
        
        if not matching_points:
            return RollbackResult(
                success=False,
                point_id="",
                restored_state={},
                message=f"No rollback point for step {step_id}",
                error="no_point_for_step"
            )
        
        # 选择最近的回滚点
        latest = max(matching_points, key=lambda p: p.timestamp)
        return self.rollback(latest.point_id)
    
    def get_point(self, point_id: str) -> Optional[RollbackPoint]:
        """获取回滚点"""
        return self._points.get(point_id) or self._load_point(point_id)
    
    def list_points(self) -> List[RollbackPoint]:
        """列出所有回滚点"""
        points = list(self._points.values())
        
        # 从文件加载
        for filename in os.listdir(self.rollback_dir):
            if filename.endswith(".json"):
                point_id = filename[:-5]
                if point_id not in self._points:
                    point = self._load_point(point_id)
                    if point:
                        points.append(point)
        
        return sorted(points, key=lambda p: p.timestamp, reverse=True)
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取回滚历史"""
        return self._history[-limit:]
    
    def clear_points(self):
        """清空回滚点"""
        self._points.clear()
        for filename in os.listdir(self.rollback_dir):
            if filename.endswith(".json"):
                os.remove(os.path.join(self.rollback_dir, filename))
