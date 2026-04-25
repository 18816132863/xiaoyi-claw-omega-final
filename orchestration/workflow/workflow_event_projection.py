"""
Workflow Event Projection - Workflow 事件投影
从事件存储生成视图和统计
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from orchestration.state.workflow_event_store import (
    get_workflow_event_store,
    EventType
)


@dataclass
class StepProjection:
    """步骤投影"""
    step_id: str
    step_name: str
    action: str
    status: str
    started_at: Optional[str]
    completed_at: Optional[str]
    duration_ms: Optional[int]
    error: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "step_name": self.step_name,
            "action": self.action,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
            "error": self.error
        }


@dataclass
class WorkflowProjection:
    """Workflow 投影"""
    instance_id: str
    workflow_id: str
    status: str
    started_at: str
    completed_at: Optional[str]
    total_steps: int
    completed_steps: int
    failed_steps: int
    steps: List[StepProjection]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "workflow_id": self.workflow_id,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "failed_steps": self.failed_steps,
            "steps": [s.to_dict() for s in self.steps]
        }


class WorkflowEventProjection:
    """
    Workflow 事件投影
    
    从事件存储生成视图和统计：
    - 生成 step timeline
    - 汇总 step 状态
    - 计算执行统计
    """
    
    def __init__(self):
        self._event_store = get_workflow_event_store()
    
    def project(self, instance_id: str) -> Optional[WorkflowProjection]:
        """
        生成 workflow 投影
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            Workflow 投影
        """
        events = self._event_store.get_by_instance(instance_id)
        if not events:
            return None
        
        events.sort(key=lambda e: e.timestamp)
        
        # 提取 workflow 信息
        workflow_id = ""
        status = "unknown"
        started_at = ""
        completed_at = None
        
        for event in events:
            if event.event_type == WorkflowEventType.WORKFLOW_STARTED:
                workflow_id = event.data.get("workflow_id", "")
                started_at = event.timestamp
                status = "running"
            elif event.event_type == WorkflowEventType.WORKFLOW_COMPLETED:
                completed_at = event.timestamp
                status = event.data.get("status", "completed")
        
        # 构建步骤投影
        steps = self._project_steps(events)
        
        # 统计
        total_steps = len(steps)
        completed_steps = sum(1 for s in steps if s.status == "completed")
        failed_steps = sum(1 for s in steps if s.status == "failed")
        
        return WorkflowProjection(
            instance_id=instance_id,
            workflow_id=workflow_id,
            status=status,
            started_at=started_at,
            completed_at=completed_at,
            total_steps=total_steps,
            completed_steps=completed_steps,
            failed_steps=failed_steps,
            steps=steps
        )
    
    def _project_steps(self, events: List[Any]) -> List[StepProjection]:
        """
        投影步骤
        
        Args:
            events: 事件列表
            
        Returns:
            步骤投影列表
        """
        # 按步骤分组
        step_data: Dict[str, Dict[str, Any]] = {}
        
        for event in events:
            if not event.step_id:
                continue
            
            if event.step_id not in step_data:
                step_data[event.step_id] = {
                    "step_id": event.step_id,
                    "step_name": "",
                    "action": "",
                    "status": "pending",
                    "started_at": None,
                    "completed_at": None,
                    "duration_ms": None,
                    "error": None
                }
            
            if event.event_type == WorkflowEventType.STEP_STARTED:
                step_data[event.step_id]["step_name"] = event.data.get("step_name", "")
                step_data[event.step_id]["action"] = event.data.get("action", "")
                step_data[event.step_id]["started_at"] = event.timestamp
                step_data[event.step_id]["status"] = "running"
            elif event.event_type == WorkflowEventType.STEP_COMPLETED:
                step_data[event.step_id]["completed_at"] = event.timestamp
                step_data[event.step_id]["duration_ms"] = event.data.get("duration_ms")
                step_data[event.step_id]["status"] = "completed"
            elif event.event_type == WorkflowEventType.STEP_FAILED:
                step_data[event.step_id]["completed_at"] = event.timestamp
                step_data[event.step_id]["error"] = event.data.get("error_message", "")
                step_data[event.step_id]["status"] = "failed"
        
        # 转换为投影对象
        projections = []
        for step_id, data in step_data.items():
            projections.append(StepProjection(
                step_id=data["step_id"],
                step_name=data["step_name"],
                action=data["action"],
                status=data["status"],
                started_at=data["started_at"],
                completed_at=data["completed_at"],
                duration_ms=data["duration_ms"],
                error=data["error"]
            ))
        
        # 按开始时间排序
        projections.sort(key=lambda s: s.started_at or "")
        
        return projections
    
    def get_step_timeline(self, instance_id: str) -> List[Dict[str, Any]]:
        """
        获取步骤时间线
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            步骤时间线
        """
        projection = self.project(instance_id)
        if projection:
            return [s.to_dict() for s in projection.steps]
        return []
    
    def get_statistics(self, instance_id: str) -> Dict[str, Any]:
        """
        获取执行统计
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            统计信息
        """
        projection = self.project(instance_id)
        if not projection:
            return {}
        
        # 计算总时长
        total_duration_ms = 0
        if projection.completed_at and projection.started_at:
            start = datetime.fromisoformat(projection.started_at)
            end = datetime.fromisoformat(projection.completed_at)
            total_duration_ms = int((end - start).total_seconds() * 1000)
        
        # 计算步骤时长
        step_durations = [
            s.duration_ms for s in projection.steps
            if s.duration_ms is not None
        ]
        avg_step_duration = sum(step_durations) / len(step_durations) if step_durations else 0
        
        return {
            "instance_id": instance_id,
            "workflow_id": projection.workflow_id,
            "status": projection.status,
            "total_steps": projection.total_steps,
            "completed_steps": projection.completed_steps,
            "failed_steps": projection.failed_steps,
            "success_rate": projection.completed_steps / projection.total_steps if projection.total_steps > 0 else 0,
            "total_duration_ms": total_duration_ms,
            "avg_step_duration_ms": avg_step_duration
        }


# 全局单例
_workflow_event_projection = None

def get_workflow_event_projection() -> WorkflowEventProjection:
    """获取事件投影器单例"""
    global _workflow_event_projection
    if _workflow_event_projection is None:
        _workflow_event_projection = WorkflowEventProjection()
    return _workflow_event_projection
