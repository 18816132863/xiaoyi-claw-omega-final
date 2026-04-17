"""
Event Replay - 事件回放
Phase3 Group5 核心模块
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import json


@dataclass
class ReplayStep:
    """回放步骤"""
    step_index: int
    event_type: str
    timestamp: str
    summary: str
    state_before: Optional[str] = None
    state_after: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReplayResult:
    """回放结果"""
    task_id: Optional[str] = None
    workflow_instance_id: Optional[str] = None
    timeline: List[ReplayStep] = field(default_factory=list)
    state_transitions: List[Dict[str, Any]] = field(default_factory=list)
    failure_points: List[Dict[str, Any]] = field(default_factory=list)
    recovery_actions: List[Dict[str, Any]] = field(default_factory=list)
    skill_selection_chain: List[Dict[str, Any]] = field(default_factory=list)
    policy_decision_chain: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "workflow_instance_id": self.workflow_instance_id,
            "timeline": [
                {
                    "step_index": s.step_index,
                    "event_type": s.event_type,
                    "timestamp": s.timestamp,
                    "summary": s.summary,
                    "state_before": s.state_before,
                    "state_after": s.state_after,
                    "details": s.details
                }
                for s in self.timeline
            ],
            "state_transitions": self.state_transitions,
            "failure_points": self.failure_points,
            "recovery_actions": self.recovery_actions,
            "skill_selection_chain": self.skill_selection_chain,
            "policy_decision_chain": self.policy_decision_chain,
            "summary": self.summary
        }


class EventReplay:
    """
    事件回放
    
    职责：
    - 回放任务事件流
    - 回放 workflow 实例事件流
    - 生成状态转移
    - 识别失败点
    - 识别恢复动作
    """
    
    def __init__(self, event_persistence=None):
        self._persistence = event_persistence
    
    @property
    def persistence(self):
        """延迟加载 persistence"""
        if self._persistence is None:
            from core.events.event_persistence import get_event_persistence
            self._persistence = get_event_persistence()
        return self._persistence
    
    def replay_task(self, task_id: str) -> ReplayResult:
        """
        回放任务
        
        Args:
            task_id: 任务 ID
        
        Returns:
            ReplayResult
        """
        events = self.persistence.list(task_id=task_id)
        return self._build_replay(events, task_id=task_id)
    
    def replay_workflow_instance(self, instance_id: str) -> ReplayResult:
        """
        回放 workflow 实例
        
        Args:
            instance_id: Workflow 实例 ID
        
        Returns:
            ReplayResult
        """
        events = self.persistence.list(workflow_instance_id=instance_id)
        return self._build_replay(events, workflow_instance_id=instance_id)
    
    def _build_replay(
        self,
        events: List,
        task_id: str = None,
        workflow_instance_id: str = None
    ) -> ReplayResult:
        """构建回放结果"""
        result = ReplayResult(
            task_id=task_id,
            workflow_instance_id=workflow_instance_id
        )
        
        current_state = "init"
        
        for i, event in enumerate(events):
            step = ReplayStep(
                step_index=i,
                event_type=event.event_type,
                timestamp=event.timestamp,
                summary=self._summarize_event(event),
                state_before=current_state,
                details=event.payload
            )
            
            # 状态转移
            new_state = self._get_state_from_event(event.event_type, current_state)
            step.state_after = new_state
            
            if new_state != current_state:
                result.state_transitions.append({
                    "from": current_state,
                    "to": new_state,
                    "event_type": event.event_type,
                    "timestamp": event.timestamp
                })
                current_state = new_state
            
            # 失败点
            if event.event_type in ["step_failed", "skill_failed"]:
                result.failure_points.append({
                    "event_type": event.event_type,
                    "timestamp": event.timestamp,
                    "error_type": event.payload.get("error_type", "unknown"),
                    "error_message": event.payload.get("error_message", ""),
                    "details": event.payload
                })
            
            # 恢复动作
            if event.event_type in ["retry_triggered", "fallback_triggered", "rollback_triggered"]:
                result.recovery_actions.append({
                    "action": event.event_type,
                    "timestamp": event.timestamp,
                    "details": event.payload
                })
            
            # 技能选择链
            if event.event_type == "skill_selected":
                result.skill_selection_chain.append({
                    "skill_id": event.payload.get("skill_id"),
                    "version": event.payload.get("version"),
                    "confidence": event.payload.get("confidence"),
                    "timestamp": event.timestamp
                })
            
            # 策略决策链
            if event.event_type == "policy_decided":
                result.policy_decision_chain.append({
                    "decision": event.payload.get("decision"),
                    "risk_level": event.payload.get("risk_level"),
                    "degradation_mode": event.payload.get("degradation_mode"),
                    "timestamp": event.timestamp
                })
            
            result.timeline.append(step)
        
        # 生成总结
        result.summary = self._generate_summary(result)
        
        return result
    
    def _summarize_event(self, event) -> str:
        """总结事件"""
        summaries = {
            "task_created": f"Task created",
            "policy_decided": f"Policy: {event.payload.get('decision', 'unknown')}",
            "context_built": f"Context: {event.payload.get('token_count', 0)} tokens",
            "workflow_started": f"Workflow started",
            "step_started": f"Step: {event.payload.get('step_id', 'unknown')}",
            "step_completed": f"Step completed",
            "step_failed": f"Step failed: {event.payload.get('error_type', 'unknown')}",
            "retry_triggered": f"Retry #{event.payload.get('retry_count', 0)}",
            "fallback_triggered": f"Fallback: {event.payload.get('fallback_skill', 'unknown')}",
            "rollback_triggered": f"Rollback",
            "checkpoint_saved": f"Checkpoint saved",
            "workflow_completed": f"Workflow: {event.payload.get('status', 'unknown')}",
            "skill_selected": f"Skill: {event.payload.get('skill_id', 'unknown')}",
            "skill_executed": f"Skill executed",
            "skill_failed": f"Skill failed",
        }
        return summaries.get(event.event_type, event.event_type)
    
    def _get_state_from_event(self, event_type: str, current_state: str) -> str:
        """从事件获取状态"""
        state_map = {
            "task_created": "created",
            "policy_decided": "policy_decided",
            "context_built": "context_ready",
            "workflow_started": "workflow_running",
            "step_started": "step_running",
            "step_completed": "step_completed",
            "step_failed": "step_failed",
            "retry_triggered": "retrying",
            "fallback_triggered": "fallback",
            "rollback_triggered": "rollback",
            "workflow_completed": "completed",
            "skill_selected": "skill_selected",
            "skill_executed": "skill_executed",
            "skill_failed": "skill_failed",
        }
        return state_map.get(event_type, current_state)
    
    def _generate_summary(self, result: ReplayResult) -> str:
        """生成总结"""
        parts = []
        
        if result.task_id:
            parts.append(f"Task: {result.task_id}")
        
        if result.workflow_instance_id:
            parts.append(f"Workflow: {result.workflow_instance_id}")
        
        parts.append(f"Events: {len(result.timeline)}")
        parts.append(f"State transitions: {len(result.state_transitions)}")
        
        if result.failure_points:
            parts.append(f"Failures: {len(result.failure_points)}")
        
        if result.recovery_actions:
            parts.append(f"Recoveries: {len(result.recovery_actions)}")
        
        if result.skill_selection_chain:
            parts.append(f"Skills: {len(result.skill_selection_chain)}")
        
        if result.policy_decision_chain:
            parts.append(f"Decisions: {len(result.policy_decision_chain)}")
        
        return " | ".join(parts)


# 全局单例
_event_replay = None


def get_event_replay() -> EventReplay:
    """获取事件回放单例"""
    global _event_replay
    if _event_replay is None:
        _event_replay = EventReplay()
    return _event_replay
