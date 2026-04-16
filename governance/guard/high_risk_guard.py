"""
High Risk Guard - 高风险守卫
阻止高风险操作
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Set


@dataclass
class GuardResult:
    """守卫检查结果"""
    allowed: bool
    blocked: List[str]
    reasons: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "blocked": self.blocked,
            "reasons": self.reasons
        }


class HighRiskGuard:
    """
    高风险守卫
    
    阻止高风险操作：
    - 高风险能力
    - 高风险任务类型
    - 高风险上下文
    """
    
    # 高风险能力
    HIGH_RISK_CAPABILITIES = {
        "high_risk.write",
        "high_risk.delete",
        "high_risk.execute",
        "system.restart",
        "system.config",
        "skill.remove"
    }
    
    # 高风险任务类型
    HIGH_RISK_TASK_TYPES = {
        "delete",
        "remove",
        "destructive",
        "system"
    }
    
    # 风险等级阻止规则
    RISK_LEVEL_BLOCKS = {
        "critical": True,  # 严重风险直接阻止
        "high": False,     # 高风险需要 review
        "medium": False,
        "low": False
    }
    
    def __init__(self):
        self._custom_blocks: Set[str] = set()
        self._custom_allows: Set[str] = set()
    
    def check(
        self,
        task_meta: Dict[str, Any],
        capabilities: List[str],
        risk_level: Any
    ) -> Dict[str, Any]:
        """
        检查高风险
        
        Args:
            task_meta: 任务元数据
            capabilities: 能力列表
            risk_level: 风险等级
            
        Returns:
            {"allowed": [...], "blocked": [...]}
        """
        blocked = []
        reasons = []
        
        risk_str = risk_level.value if hasattr(risk_level, 'value') else str(risk_level)
        
        # 1. 检查风险等级
        if self.RISK_LEVEL_BLOCKS.get(risk_str, False):
            reasons.append(f"Risk level '{risk_str}' is blocked by guard")
            # 不直接阻止所有，只标记原因
        
        # 2. 检查高风险能力
        for cap in capabilities:
            if cap in self._custom_allows:
                continue
            
            if cap in self.HIGH_RISK_CAPABILITIES or cap in self._custom_blocks:
                blocked.append(cap)
                reasons.append(f"High risk capability blocked: {cap}")
        
        # 3. 检查高风险任务类型
        task_type = task_meta.get("type", "")
        if task_type in self.HIGH_RISK_TASK_TYPES:
            reasons.append(f"High risk task type: {task_type}")
        
        return {
            "blocked": blocked,
            "reasons": reasons
        }
    
    def is_high_risk(self, capability: str) -> bool:
        """
        检查是否是高风险能力
        
        Args:
            capability: 能力名称
            
        Returns:
            是否高风险
        """
        if capability in self._custom_allows:
            return False
        return capability in self.HIGH_RISK_CAPABILITIES or capability in self._custom_blocks
    
    def block(self, capability: str):
        """
        添加阻止能力
        
        Args:
            capability: 能力名称
        """
        self._custom_blocks.add(capability)
        if capability in self._custom_allows:
            self._custom_allows.remove(capability)
    
    def allow(self, capability: str):
        """
        允许能力
        
        Args:
            capability: 能力名称
        """
        self._custom_allows.add(capability)
        if capability in self._custom_blocks:
            self._custom_blocks.remove(capability)
    
    def get_blocked_capabilities(self) -> List[str]:
        """
        获取被阻止的能力列表
        
        Returns:
            被阻止的能力列表
        """
        return list(self.HIGH_RISK_CAPABILITIES | self._custom_blocks)
    
    def reload(self) -> Dict[str, Any]:
        """
        重新加载
        
        Returns:
            重载结果
        """
        return {
            "status": "reloaded",
            "high_risk_capabilities": len(self.HIGH_RISK_CAPABILITIES),
            "custom_blocks": len(self._custom_blocks),
            "custom_allows": len(self._custom_allows)
        }


# 全局单例
_high_risk_guard = None

def get_high_risk_guard() -> HighRiskGuard:
    """获取高风险守卫单例"""
    global _high_risk_guard
    if _high_risk_guard is None:
        _high_risk_guard = HighRiskGuard()
    return _high_risk_guard
