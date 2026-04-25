"""
Workflow Replay - Workflow 回放
从事件存储重建 workflow 执行过程
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from orchestration.state.workflow_instance_store import (
    get_workflow_instance_store,
    InstanceStatus
)
from orchestration.state.workflow_event_store import (
    get_workflow_event_store,
    EventType
)
from orchestration.state.recovery_store import get_recovery_store


@dataclass
class StepTimeline:
    """步骤时间线"""
    step_id: str
    step_name: str
    action: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: str = "pending"
    duration_ms: Optional[int] = None
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    retries: int = 0
    fallback_used: bool = False
    rollback_used: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "step_name": self.step_name,
            "action": self.action,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "output": self.output,
            "error": self.error,
            "retries": self.retries,
            "fallback_used": self.fallback_used,
            "rollback_used": self.rollback_used
        }


@dataclass
class ReplayResult:
    """回放结果"""
    instance_id: str
    workflow_id: str
    version: str
    status: str
    started_at: str
    completed_at: Optional[str]
    duration_ms: Optional[int]
    step_timeline: List[StepTimeline]
    failed_step_id: Optional[str]
    retry_summary: Dict[str, Any]
    fallback_summary: Dict[str, Any]
    rollback_summary: Dict[str, Any]
    checkpoint_summary: Dict[str, Any]
    control_decision_id: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "workflow_id": self.workflow_id,
            "version": self.version,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
            "step_timeline": [s.to_dict() for s in self.step_timeline],
            "failed_step_id": self.failed_step_id,
            "retry_summary": self.retry_summary,
            "fallback_summary": self.fallback_summary,
            "rollback_summary": self.rollback_summary,
            "checkpoint_summary": self.checkpoint_summary,
            "control_decision_id": self.control_decision_id
        }


class WorkflowReplay:
    """
    Workflow 回放
    
    从事件存储重建 workflow 执行过程：
    - replay(instance_id) -> replay_result
    - 生成 step timeline
    - 汇总恢复动作
    """
    
    def __init__(self):
        self._instance_store = get_workflow_instance_store()
        self._event_store = get_workflow_event_store()
        self._recovery_store = get_recovery_store()
    
    def replay(self, instance_id: str) -> Optional[ReplayResult]:
        """
        回放 workflow 执行过程
        
        Args:
            instance_id: 实例 ID
            
        Returns:
            回放结果
        """
        # 获取实例
        instance = self._instance_store.get(instance_id)
        if not instance:
            return None
        
        # 获取事件
        events = self._event_store.get_by_instance(instance_id)
        events.sort(key=lambda e: e.timestamp)
        
        # 获取恢复记录
        recovery_records = self._recovery_store.get_by_instance(instance_id)
        
        # 构建步骤时间线
        step_timeline = self._build_step_timeline(events, recovery_records)
        
        # 计算时长
        duration_ms = None
        if instance.completed_at and instance.started_at:
            start = datetime.fromisoformat(instance.started_at)
            end = datetime.fromisoformat(instance.completed_at)
            duration_ms = int((end - start).total_seconds() * 1000)
        
        # 汇总恢复动作
        retry_summary = self._summarize_retries(recovery_records)
        fallback_summary = self._summarize_fallbacks(recovery_records)
        rollback_summary = self._summarize_rollbacks(recovery_records)
        checkpoint_summary = self._summarize_checkpoints(recovery_records)
        
        return ReplayResult(
            instance_id=instance_id,
            workflow_id=instance.workflow_id,
            version=instance.version,
            status=instance.status.value,
            started_at=instance.started_at,
            completed_at=instance.completed_at,
            duration_ms=duration_ms,
            step_timeline=step_timeline,
            failed_step_id=instance.failed_step_id,
            retry_summary=retry_summary,
            fallback_summary=fallback_summary,
            rollback_summary=rollback_summary,
            checkpoint_summary=checkpoint_summary,
            control_decision_id=instance.control_decision_id
        )
    
    def _build_step_timeline(
        self,
        events: List[Any],
        recovery_records: List[Any]
    ) -> List[StepTimeline]:
        """
        构建步骤时间线
        
        Args:
            events: 事件列表
            recovery_records: 恢复记录列表
            
        Returns:
            步骤时间线
        """
        # 按步骤分组事件
        step_events: Dict[str, Dict[str, Any]] = {}
        
        for event in events:
            if event.step_id:
                if event.step_id not in step_events:
                    step_events[event.step_id] = {
                        "step_id": event.step_id,
                        "events": []
                    }
                step_events[event.step_id]["events"].append(event)
        
        # 构建时间线
        timeline = []
        
        for step_id, data in step_events.items():
            step_events_list = data["events"]
            
            # 提取步骤信息
            step_name = ""
            action = ""
            started_at = None
            completed_at = None
            status = "pending"
            output = {}
            error = None
            duration_ms = None
            
            for event in step_events_list:
                if event.event_type == WorkflowEventType.STEP_STARTED:
                    started_at = event.timestamp
                    step_name = event.data.get("step_name", "")
                    action = event.data.get("action", "")
                    status = "running"
                elif event.event_type == WorkflowEventType.STEP_COMPLETED:
                    completed_at = event.timestamp
                    output = event.data.get("output", {})
                    duration_ms = event.data.get("duration_ms")
                    status = "completed"
                elif event.event_type == WorkflowEventType.STEP_FAILED:
                    completed_at = event.timestamp
                    error = event.data.get("error_message", "")
                    status = "failed"
            
            # 计算重试次数
            retries = sum(
                1 for r in recovery_records
                if r.step_id == step_id and r.recovery_action.value == "retry"
            )
            
            # 检查 fallback/rollback
            fallback_used = any(
                r.step_id == step_id and r.recovery_action.value == "fallback"
                for r in recovery_records
            )
            rollback_used = any(
                r.step_id == step_id and r.recovery_action.value == "rollback"
                for r in recovery_records
            )
            
            timeline.append(StepTimeline(
                step_id=step_id,
                step_name=step_name,
                action=action,
                started_at=started_at,
                completed_at=completed_at,
                status=status,
                duration_ms=duration_ms,
                output=output,
                error=error,
                retries=retries,
                fallback_used=fallback_used,
                rollback_used=rollback_used
            ))
        
        # 按开始时间排序
        timeline.sort(key=lambda s: s.started_at or "")
        
        return timeline
    
    def _summarize_retries(self, records: List[Any]) -> Dict[str, Any]:
        """汇总重试"""
        retry_records = [r for r in records if r.recovery_action.value == "retry"]
        return {
            "total": len(retry_records),
            "by_step": {
                step_id: sum(1 for r in retry_records if r.step_id == step_id)
                for step_id in set(r.step_id for r in retry_records)
            }
        }
    
    def _summarize_fallbacks(self, records: List[Any]) -> Dict[str, Any]:
        """汇总 fallback"""
        fallback_records = [r for r in records if r.recovery_action.value == "fallback"]
        return {
            "total": len(fallback_records),
            "by_step": [
                {
                    "step_id": r.step_id,
                    "fallback_skill": r.fallback_skill
                }
                for r in fallback_records
            ]
        }
    
    def _summarize_rollbacks(self, records: List[Any]) -> Dict[str, Any]:
        """汇总 rollback"""
        rollback_records = [r for r in records if r.recovery_action.value == "rollback"]
        return {
            "total": len(rollback_records),
            "by_step": [
                {
                    "step_id": r.step_id,
                    "rollback_to_step": r.rollback_to_step
                }
                for r in rollback_records
            ]
        }
    
    def _summarize_checkpoints(self, records: List[Any]) -> Dict[str, Any]:
        """汇总 checkpoint"""
        checkpoint_records = [r for r in records if r.recovery_action.value == "checkpoint"]
        return {
            "total": len(checkpoint_records),
            "checkpoints": [
                {
                    "step_id": r.step_id,
                    "checkpoint_id": r.checkpoint_id,
                    "timestamp": r.timestamp
                }
                for r in checkpoint_records
            ]
        }


# 全局单例
_workflow_replay = None

def get_workflow_replay() -> WorkflowReplay:
    """获取回放器单例"""
    global _workflow_replay
    if _workflow_replay is None:
        _workflow_replay = WorkflowReplay()
    return _workflow_replay
