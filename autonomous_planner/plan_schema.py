"""计划模式"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PlanStep:
    """计划步骤"""
    step_id: int
    capability: str
    params: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    risk_level: str = "L0"
    status: str = "pending"  # pending, running, completed, failed, skipped
    result: Optional[Dict[str, Any]] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class Plan:
    """执行计划"""
    goal: str
    intent: str
    steps: List[PlanStep] = field(default_factory=list)
    estimated_time: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "draft"  # draft, previewing, confirmed, executing, completed, failed
    current_step: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "intent": self.intent,
            "steps": [
                {
                    "step_id": s.step_id,
                    "capability": s.capability,
                    "params": s.params,
                    "description": s.description,
                    "risk_level": s.risk_level,
                    "status": s.status,
                }
                for s in self.steps
            ],
            "estimated_time": self.estimated_time,
            "created_at": self.created_at,
            "status": self.status,
            "current_step": self.current_step,
        }
    
    def get_high_risk_steps(self) -> List[PlanStep]:
        """获取高风险步骤"""
        return [s for s in self.steps if s.risk_level in ["L3", "L4"]]
    
    def get_preview(self) -> str:
        """获取预览"""
        lines = [f"目标: {self.goal}", "", "执行计划:"]
        for step in self.steps:
            risk_icon = {"L0": "✅", "L1": "✅", "L2": "⚠️", "L3": "🔴", "L4": "⛔"}.get(step.risk_level, "❓")
            lines.append(f"  {step.step_id}. {risk_icon} {step.description}")
            if step.params:
                for k, v in step.params.items():
                    lines.append(f"     - {k}: {v}")
        return "\n".join(lines)
