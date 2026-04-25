"""技能资产模式"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SkillAsset:
    """技能资产"""
    skill_id: str
    name: str
    category: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    side_effecting: bool = False
    requires_auth: bool = False
    requires_confirmation: bool = False
    can_auto_run: bool = True
    can_schedule: bool = True
    can_compose: bool = True
    success_rate: float = 0.0
    last_used_at: Optional[str] = None
    failure_reason: Optional[str] = None
    fallback_skills: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    location: str = ""
