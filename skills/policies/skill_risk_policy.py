"""
技能风险策略

定义技能的风险等级和控制策略
"""

from enum import Enum
from typing import Dict, List, Optional, Set


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SkillRiskPolicy:
    """技能风险策略"""
    
    # 默认风险等级映射
    DEFAULT_RISK_MAP = {
        "xiaoyi-gui-agent": RiskLevel.HIGH,
        "send_message": RiskLevel.MEDIUM,
        "make_call": RiskLevel.HIGH,
        "delete_file": RiskLevel.HIGH,
        "delete_photo": RiskLevel.HIGH,
        "web_search": RiskLevel.LOW,
        "create_note": RiskLevel.LOW,
        "query_calendar": RiskLevel.LOW,
    }
    
    # 高风险操作关键词
    HIGH_RISK_KEYWORDS = [
        "delete", "remove", "drop", "truncate",
        "send", "publish", "post", "broadcast",
        "call", "dial", "execute", "run",
        "payment", "purchase", "transfer",
    ]
    
    def __init__(self):
        self.risk_map: Dict[str, RiskLevel] = dict(self.DEFAULT_RISK_MAP)
        self.overrides: Dict[str, RiskLevel] = {}
    
    def get_risk_level(self, skill_id: str) -> RiskLevel:
        """获取技能风险等级"""
        # 检查覆盖
        if skill_id in self.overrides:
            return self.overrides[skill_id]
        
        # 检查预设
        if skill_id in self.risk_map:
            return self.risk_map[skill_id]
        
        # 根据关键词推断
        skill_lower = skill_id.lower()
        for keyword in self.HIGH_RISK_KEYWORDS:
            if keyword in skill_lower:
                return RiskLevel.HIGH
        
        return RiskLevel.MEDIUM
    
    def set_risk_level(self, skill_id: str, level: RiskLevel):
        """设置技能风险等级"""
        self.overrides[skill_id] = level
    
    def is_high_risk(self, skill_id: str) -> bool:
        """检查是否高风险"""
        level = self.get_risk_level(skill_id)
        return level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    def requires_confirmation(self, skill_id: str) -> bool:
        """检查是否需要确认"""
        level = self.get_risk_level(skill_id)
        return level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    def requires_strong_confirmation(self, skill_id: str) -> bool:
        """检查是否需要强确认"""
        level = self.get_risk_level(skill_id)
        return level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    def get_skills_by_risk_level(self, level: RiskLevel) -> List[str]:
        """获取指定风险等级的技能"""
        return [
            skill_id for skill_id in self.risk_map
            if self.get_risk_level(skill_id) == level
        ]


__all__ = ["SkillRiskPolicy", "RiskLevel"]
