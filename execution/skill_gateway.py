#!/usr/bin/env python3
"""
技能网关 - V1.0.0

统一技能执行入口，委托给 SkillAdapterGateway。
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from execution.skill_adapter_gateway import execute_skill

@dataclass
class SkillResult:
    """技能执行结果"""
    success: bool
    skill_id: str
    data: Any
    error: Optional[Dict] = None
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class SkillGateway:
    """技能网关"""

    def __init__(self):
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0
        }

    def execute(self, skill_id: str, params: Dict[str, Any]) -> SkillResult:
        """执行技能"""
        self.stats["total"] += 1

        result = execute_skill(skill_id, params)

        if result.get("success"):
            self.stats["success"] += 1
        else:
            self.stats["failed"] += 1

        return SkillResult(
            success=result.get("success", False),
            skill_id=skill_id,
            data=result.get("data"),
            error=result.get("error"),
            timestamp=datetime.now().isoformat()
        )

    def get_stats(self) -> Dict:
        return {
            **self.stats,
            "success_rate": self.stats["success"] / max(1, self.stats["total"])
        }

# 全局实例
_gateway = None

def get_gateway() -> SkillGateway:
    global _gateway
    if _gateway is None:
        _gateway = SkillGateway()
    return _gateway
