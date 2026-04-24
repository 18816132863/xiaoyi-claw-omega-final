"""
Token Budget Manager - Token 预算管理器
管理不同 profile 的 token 预算
"""

from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime


@dataclass
class TokenBudget:
    """Token 预算"""
    profile: str
    total: int
    used: int
    available: int
    reset_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "profile": self.profile,
            "total": self.total,
            "used": self.used,
            "available": self.available,
            "reset_at": self.reset_at
        }


class TokenBudgetManager:
    """
    Token 预算管理器
    
    管理不同 profile 的 token 预算
    """
    
    # Profile 预算配置
    PROFILE_BUDGETS = {
        "development": 500000,
        "performance": 200000,
        "default": 100000,
        "production": 80000,
        "safe": 50000,
        "restricted": 10000
    }
    
    def __init__(self):
        self._budgets: Dict[str, TokenBudget] = {}
        self._custom_budgets: Dict[str, int] = {}
        self._init_budgets()
    
    def _init_budgets(self):
        """初始化预算"""
        for profile, total in self.PROFILE_BUDGETS.items():
            self._budgets[profile] = TokenBudget(
                profile=profile,
                total=total,
                used=0,
                available=total,
                reset_at=self._get_reset_time()
            )
    
    def get_budget(self, profile: str) -> int:
        """
        获取预算
        
        Args:
            profile: 配置文件名
            
        Returns:
            预算值
        """
        if profile in self._custom_budgets:
            return self._custom_budgets[profile]
        return self.PROFILE_BUDGETS.get(profile, 100000)
    
    def get_available(self, profile: str) -> int:
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
        return self.get_available(profile) > 0
    
    def consume(self, profile: str, amount: int) -> bool:
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
        self._budgets[profile] = TokenBudget(
            profile=profile,
            total=total,
            used=0,
            available=total,
            reset_at=self._get_reset_time()
        )
    
    def set_budget(self, profile: str, total: int):
        """
        设置预算
        
        Args:
            profile: 配置文件名
            total: 总预算
        """
        self._custom_budgets[profile] = total
        self._budgets[profile] = TokenBudget(
            profile=profile,
            total=total,
            used=0,
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
        return {"profile": profile, "total": 0, "used": 0, "available": 0}
    
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
_token_budget_manager = None

def get_token_budget_manager() -> TokenBudgetManager:
    """获取 Token 预算管理器单例"""
    global _token_budget_manager
    if _token_budget_manager is None:
        _token_budget_manager = TokenBudgetManager()
    return _token_budget_manager
