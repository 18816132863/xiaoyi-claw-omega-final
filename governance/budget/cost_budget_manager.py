"""
Cost Budget Manager - 成本预算管理器
管理不同 profile 的成本预算
"""

from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime


@dataclass
class CostBudget:
    """成本预算"""
    profile: str
    total: float
    used: float
    available: float
    reset_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile": self.profile,
            "total": self.total,
            "used": self.used,
            "available": self.available,
            "reset_at": self.reset_at
        }


class CostBudgetManager:
    """
    成本预算管理器
    
    管理不同 profile 的成本预算
    """
    
    # Profile 预算配置
    PROFILE_BUDGETS = {
        "development": 50.0,
        "performance": 20.0,
        "default": 10.0,
        "production": 8.0,
        "safe": 5.0,
        "restricted": 1.0
    }
    
    def __init__(self):
        self._budgets: Dict[str, CostBudget] = {}
        self._custom_budgets: Dict[str, float] = {}
        self._init_budgets()
    
    def _init_budgets(self):
        """初始化预算"""
        for profile, total in self.PROFILE_BUDGETS.items():
            self._budgets[profile] = CostBudget(
                profile=profile,
                total=total,
                used=0.0,
                available=total,
                reset_at=self._get_reset_time()
            )
    
    def get_budget(self, profile: str) -> float:
        """
        获取预算
        
        Args:
            profile: 配置文件名
            
        Returns:
            预算值
        """
        if profile in self._custom_budgets:
            return self._custom_budgets[profile]
        return self.PROFILE_BUDGETS.get(profile, 10.0)
    
    def get_available(self, profile: str) -> float:
        """
        获取可用预算
        
        Args:
            profile: 配置文件名
            
        Returns:
            可用预算
        """
        budget = self._budgets.get(profile)
        if budget:
            return budget.available
        return self.get_budget(profile)
    
    def check_available(self, profile: str) -> bool:
        """
        检查是否有可用预算
        
        Args:
            profile: 配置文件名
            
        Returns:
            是否有可用预算
        """
        return self.get_available(profile) > 0.0
    
    def consume(self, profile: str, amount: float) -> bool:
        """
        消耗预算
        
        Args:
            profile: 配置文件名
            amount: 消耗量
            
        Returns:
            是否成功
        """
        budget = self._budgets.get(profile)
        if not budget:
            return False
        
        if budget.available < amount:
            return False
        
        budget.used += amount
        budget.available -= amount
        return True
    
    def reset(self, profile: str):
        """
        重置预算
        
        Args:
            profile: 配置文件名
        """
        total = self.get_budget(profile)
        self._budgets[profile] = CostBudget(
            profile=profile,
            total=total,
            used=0.0,
            available=total,
            reset_at=self._get_reset_time()
        )
    
    def set_budget(self, profile: str, total: float):
        """
        设置预算
        
        Args:
            profile: 配置文件名
            total: 总预算
        """
        self._custom_budgets[profile] = total
        self._budgets[profile] = CostBudget(
            profile=profile,
            total=total,
            used=0.0,
            available=total,
            reset_at=self._get_reset_time()
        )
    
    def get_status(self, profile: str) -> Dict[str, Any]:
        """
        获取预算状态
        
        Args:
            profile: 配置文件名
            
        Returns:
            预算状态
        """
        budget = self._budgets.get(profile)
        if budget:
            return budget.to_dict()
        return {"profile": profile, "total": 0.0, "used": 0.0, "available": 0.0}
    
    def reload(self) -> Dict[str, Any]:
        """
        重新加载
        
        Returns:
            重载结果
        """
        self._init_budgets()
        return {
            "status": "reloaded",
            "profiles": len(self._budgets)
        }
    
    def _get_reset_time(self) -> str:
        """获取重置时间（明天 0 点）"""
        now = datetime.now()
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = tomorrow.replace(day=now.day + 1)
        return tomorrow.isoformat()


# 全局单例
_cost_budget_manager = None

def get_cost_budget_manager() -> CostBudgetManager:
    """获取成本预算管理器单例"""
    global _cost_budget_manager
    if _cost_budget_manager is None:
        _cost_budget_manager = CostBudgetManager()
    return _cost_budget_manager
