"""
Timeline Generator - 时间线生成器
从正式事件流投影生成 timeline
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import os


@dataclass
class TimelineEvent:
    """时间线事件"""
    event_type: str
    timestamp: str
    summary: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowTimeline:
    """Workflow 时间线"""
    workflow_instance_id: str
    workflow_id: str
    version: str
    profile: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    step_timeline: List[Dict[str, Any]] = field(default_factory=list)
    retry_events: List[Dict[str, Any]] = field(default_factory=list)
    fallback_events: List[Dict[str, Any]] = field(default_factory=list)
    rollback_events: List[Dict[str, Any]] = field(default_factory=list)
    checkpoint_events: List[Dict[str, Any]] = field(default_factory=list)
    total_duration_ms: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_instance_id": self.workflow_instance_id,
            "workflow_id": self.workflow_id,
            "version": self.version,
            "profile": self.profile,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "step_timeline": self.step_timeline,
            "retry_events": self.retry_events,
            "fallback_events": self.fallback_events,
            "rollback_events": self.rollback_events,
            "checkpoint_events": self.checkpoint_events,
            "total_duration_ms": self.total_duration_ms
        }


@dataclass
class SkillTimeline:
    """Skill 时间线"""
    skill_id: str
    version: str
    task_id: str
    selected_at: Optional[str] = None
    executed_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: str = "unknown"
    latency_ms: int = 0
    confidence: float = 0.0
    selection_chain: List[str] = field(default_factory=list)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "version": self.version,
            "task_id": self.task_id,
            "selected_at": self.selected_at,
            "executed_at": self.executed_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "confidence": self.confidence,
            "selection_chain": self.selection_chain,
            "error": self.error
        }


@dataclass
class PolicyTimeline:
    """Policy 时间线"""
    decision_id: str
    task_id: str
    decision: str
    risk_level: str
    degradation_mode: bool
    allowed_capabilities: List[str] = field(default_factory=list)
    blocked_capabilities: List[str] = field(default_factory=list)
    timestamp: str = ""
    profile: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "task_id": self.task_id,
            "decision": self.decision,
            "risk_level": self.risk_level,
            "degradation_mode": self.degradation_mode,
            "allowed_capabilities": self.allowed_capabilities,
            "blocked_capabilities": self.blocked_capabilities,
            "timestamp": self.timestamp,
            "profile": self.profile
        }


class TimelineGenerator:
    """
    时间线生成器
    
    从正式事件流投影生成 timeline
    """
    
    def __init__(self, events_path: str = "reports/observability/events.jsonl"):
        self.events_path = events_path
        self._events: List[Dict[str, Any]] = []
        self._load_events()
    
    def _load_events(self):
        """加载事件流"""
        if not os.path.exists(self.events_path):
            return
        
        try:
            with open(self.events_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            self._events.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception:
            pass
    
    def generate_workflow_timeline(self, instance_id: str = None) -> List[WorkflowTimeline]:
        """生成 Workflow 时间线"""
        timelines = []
        
        # 按 workflow_instance_id 分组
        workflow_events: Dict[str, List[Dict]] = {}
        for event in self._events:
            wid = event.get("workflow_instance_id")
            if wid:
                if wid not in workflow_events:
                    workflow_events[wid] = []
                workflow_events[wid].append(event)
        
        # 如果指定了 instance_id，只处理那个
        if instance_id:
            workflow_events = {k: v for k, v in workflow_events.items() if k == instance_id}
        
        for wid, events in workflow_events.items():
            timeline = self._build_workflow_timeline(wid, events)
            timelines.append(timeline)
        
        return timelines
    
    def _build_workflow_timeline(self, instance_id: str, events: List[Dict]) -> WorkflowTimeline:
        """构建单个 workflow 时间线"""
        timeline = WorkflowTimeline(
            workflow_instance_id=instance_id,
            workflow_id="",
            version="",
            profile="",
            status="unknown",
            started_at=""
        )
        
        for event in events:
            event_type = event.get("event_type", "")
            payload = event.get("payload", {})
            timestamp = event.get("timestamp", "")
            
            if event_type == "workflow_started":
                timeline.workflow_id = payload.get("workflow_id", "")
                timeline.version = payload.get("version", "")
                timeline.profile = payload.get("profile", "")
                timeline.started_at = timestamp
                timeline.status = "running"
            
            elif event_type == "step_started":
                timeline.step_timeline.append({
                    "step_id": payload.get("step_id"),
                    "step_name": payload.get("step_name"),
                    "action": payload.get("action"),
                    "status": "started",
                    "timestamp": timestamp
                })
            
            elif event_type == "step_completed":
                for step in timeline.step_timeline:
                    if step.get("step_id") == payload.get("step_id"):
                        step["status"] = "completed"
                        step["completed_at"] = timestamp
                        step["duration_ms"] = payload.get("duration_ms", 0)
            
            elif event_type == "step_failed":
                for step in timeline.step_timeline:
                    if step.get("step_id") == payload.get("step_id"):
                        step["status"] = "failed"
                        step["error"] = payload.get("error_message", "")
                timeline.status = "failed"
            
            elif event_type == "retry_triggered":
                timeline.retry_events.append({
                    "step_id": payload.get("step_id"),
                    "retry_count": payload.get("retry_count"),
                    "timestamp": timestamp
                })
            
            elif event_type == "fallback_triggered":
                timeline.fallback_events.append({
                    "step_id": payload.get("step_id"),
                    "fallback_skill": payload.get("fallback_skill"),
                    "timestamp": timestamp
                })
            
            elif event_type == "rollback_triggered":
                timeline.rollback_events.append({
                    "step_id": payload.get("step_id"),
                    "rollback_point_id": payload.get("rollback_point_id"),
                    "timestamp": timestamp
                })
            
            elif event_type == "checkpoint_saved":
                timeline.checkpoint_events.append({
                    "checkpoint_id": payload.get("checkpoint_id"),
                    "step_id": payload.get("step_id"),
                    "timestamp": timestamp
                })
            
            elif event_type == "workflow_completed":
                timeline.status = payload.get("status", "completed")
                timeline.completed_at = timestamp
                timeline.total_duration_ms = payload.get("total_duration_ms", 0)
        
        return timeline
    
    def generate_skill_timeline(self, skill_id: str = None) -> List[SkillTimeline]:
        """生成 Skill 时间线"""
        timelines = []
        
        # 按 skill_id 分组
        skill_events: Dict[str, List[Dict]] = {}
        for event in self._events:
            sid = event.get("skill_id")
            if sid:
                if sid not in skill_events:
                    skill_events[sid] = []
                skill_events[sid].append(event)
        
        if skill_id:
            skill_events = {k: v for k, v in skill_events.items() if k == skill_id}
        
        for sid, events in skill_events.items():
            timeline = self._build_skill_timeline(sid, events)
            timelines.append(timeline)
        
        return timelines
    
    def _build_skill_timeline(self, skill_id: str, events: List[Dict]) -> SkillTimeline:
        """构建单个 skill 时间线"""
        timeline = SkillTimeline(
            skill_id=skill_id,
            version="",
            task_id=""
        )
        
        for event in events:
            event_type = event.get("event_type", "")
            payload = event.get("payload", {})
            timestamp = event.get("timestamp", "")
            
            if event_type == "skill_selected":
                timeline.version = payload.get("version", "")
                timeline.task_id = event.get("task_id", "")
                timeline.selected_at = timestamp
                timeline.confidence = payload.get("confidence", 0.0)
                timeline.selection_chain = payload.get("selection_chain", [])
                timeline.status = "selected"
            
            elif event_type == "skill_executed":
                timeline.executed_at = timestamp
                timeline.status = payload.get("status", "executed")
                timeline.latency_ms = payload.get("latency_ms", 0)
            
            elif event_type == "skill_failed":
                timeline.status = "failed"
                timeline.error = payload.get("error_message", "")
                timeline.completed_at = timestamp
        
        return timeline
    
    def generate_policy_timeline(self, decision_id: str = None) -> List[PolicyTimeline]:
        """生成 Policy 时间线"""
        timelines = []
        
        policy_events = [
            e for e in self._events
            if e.get("event_type") == "policy_decided"
        ]
        
        if decision_id:
            policy_events = [
                e for e in policy_events
                if e.get("decision_id") == decision_id
            ]
        
        for event in policy_events:
            payload = event.get("payload", {})
            timeline = PolicyTimeline(
                decision_id=event.get("decision_id", ""),
                task_id=event.get("task_id", ""),
                decision=payload.get("decision", ""),
                risk_level=payload.get("risk_level", "low"),
                degradation_mode=payload.get("degradation_mode", False),
                allowed_capabilities=payload.get("allowed_capabilities", []),
                blocked_capabilities=payload.get("blocked_capabilities", []),
                timestamp=event.get("timestamp", ""),
                profile=payload.get("profile", "")
            )
            timelines.append(timeline)
        
        return timelines
    
    def save_all_timelines(self, output_dir: str = "reports/observability"):
        """保存所有时间线"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Workflow timeline
        workflow_timelines = self.generate_workflow_timeline()
        workflow_data = [t.to_dict() for t in workflow_timelines]
        with open(os.path.join(output_dir, "workflow_timeline.json"), 'w', encoding='utf-8') as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "total_workflows": len(workflow_timelines),
                "timelines": workflow_data
            }, f, indent=2, ensure_ascii=False)
        
        # Skill timeline
        skill_timelines = self.generate_skill_timeline()
        skill_data = [t.to_dict() for t in skill_timelines]
        with open(os.path.join(output_dir, "skill_timeline.json"), 'w', encoding='utf-8') as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "total_skills": len(skill_timelines),
                "timelines": skill_data
            }, f, indent=2, ensure_ascii=False)
        
        # Policy timeline
        policy_timelines = self.generate_policy_timeline()
        policy_data = [t.to_dict() for t in policy_timelines]
        with open(os.path.join(output_dir, "policy_timeline.json"), 'w', encoding='utf-8') as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "total_decisions": len(policy_timelines),
                "timelines": policy_data
            }, f, indent=2, ensure_ascii=False)
        
        return {
            "workflow_count": len(workflow_timelines),
            "skill_count": len(skill_timelines),
            "policy_count": len(policy_timelines)
        }


def generate_timelines():
    """生成所有时间线"""
    generator = TimelineGenerator()
    return generator.save_all_timelines()


if __name__ == "__main__":
    result = generate_timelines()
    print(json.dumps(result, indent=2))
