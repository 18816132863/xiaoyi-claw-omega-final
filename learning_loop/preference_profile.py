"""用户偏好档案"""

from typing import Dict, Any, List
from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class PreferenceProfile:
    """用户偏好档案"""
    user_id: str = "default"
    
    # 确认偏好
    l0_auto: bool = True
    l1_auto: bool = True
    l2_confirm_batch: bool = True
    l3_confirm: bool = True
    l4_strong_confirm: bool = True
    
    # 能力偏好
    preferred_capabilities: List[str] = field(default_factory=list)
    avoided_capabilities: List[str] = field(default_factory=list)
    
    # 技能偏好
    preferred_skills: List[str] = field(default_factory=list)
    avoided_skills: List[str] = field(default_factory=list)
    
    # 执行偏好
    prefer_speed: bool = False  # 优先速度
    prefer_safety: bool = True  # 优先安全
    prefer_less_questions: bool = True  # 减少追问
    
    # 时间偏好
    quiet_hours: List[int] = field(default_factory=lambda: [23, 0, 1, 2, 3, 4, 5, 6])
    
    storage_path: str = "data/preference_profile.json"
    
    def save(self):
        """保存偏好"""
        Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump({
                "user_id": self.user_id,
                "l0_auto": self.l0_auto,
                "l1_auto": self.l1_auto,
                "l2_confirm_batch": self.l2_confirm_batch,
                "l3_confirm": self.l3_confirm,
                "l4_strong_confirm": self.l4_strong_confirm,
                "preferred_capabilities": self.preferred_capabilities,
                "avoided_capabilities": self.avoided_capabilities,
                "preferred_skills": self.preferred_skills,
                "avoided_skills": self.avoided_skills,
                "prefer_speed": self.prefer_speed,
                "prefer_safety": self.prefer_safety,
                "prefer_less_questions": self.prefer_less_questions,
                "quiet_hours": self.quiet_hours,
            }, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load(cls, user_id: str = "default", storage_path: str = "data/preference_profile.json") -> "PreferenceProfile":
        """加载偏好"""
        path = Path(storage_path)
        if path.exists():
            with open(path, "r") as f:
                data = json.load(f)
                return cls(
                    user_id=data.get("user_id", user_id),
                    l0_auto=data.get("l0_auto", True),
                    l1_auto=data.get("l1_auto", True),
                    l2_confirm_batch=data.get("l2_confirm_batch", True),
                    l3_confirm=data.get("l3_confirm", True),
                    l4_strong_confirm=data.get("l4_strong_confirm", True),
                    preferred_capabilities=data.get("preferred_capabilities", []),
                    avoided_capabilities=data.get("avoided_capabilities", []),
                    preferred_skills=data.get("preferred_skills", []),
                    avoided_skills=data.get("avoided_skills", []),
                    prefer_speed=data.get("prefer_speed", False),
                    prefer_safety=data.get("prefer_safety", True),
                    prefer_less_questions=data.get("prefer_less_questions", True),
                    quiet_hours=data.get("quiet_hours", [23, 0, 1, 2, 3, 4, 5, 6]),
                    storage_path=storage_path,
                )
        return cls(user_id=user_id, storage_path=storage_path)
    
    def update_from_execution(self, execution_record: Dict[str, Any]):
        """从执行记录更新偏好"""
        # 如果用户满意，增加偏好
        if execution_record.get("user_satisfied"):
            for cap in execution_record.get("capabilities_used", []):
                if cap not in self.preferred_capabilities:
                    self.preferred_capabilities.append(cap)
            for skill in execution_record.get("skills_used", []):
                if skill not in self.preferred_skills:
                    self.preferred_skills.append(skill)
        
        # 如果失败，增加避免
        if execution_record.get("final_result") == "failed":
            for cap in execution_record.get("capabilities_used", []):
                if cap not in self.avoided_capabilities:
                    self.avoided_capabilities.append(cap)
        
        self.save()
