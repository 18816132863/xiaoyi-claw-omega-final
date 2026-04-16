"""Token Budget Manager - Token 预算管理"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from enum import Enum
import json
import os


class BudgetPeriod(Enum):
    PER_REQUEST = "per_request"
    HOURLY = "hourly"
    DAILY = "daily"


@dataclass
class TokenBudget:
    """Token 预算"""
    profile: str
    limit: int
    used: int = 0
    period: BudgetPeriod = BudgetPeriod.PER_REQUEST
    reset_at: Optional[datetime] = None
    
    def remaining(self) -> int:
        return max(0, self.limit - self.used)
    
    def is_exceeded(self) -> bool:
        return self.used >= self.limit
    
    def use(self, amount: int) -> bool:
        if self.used + amount > self.limit:
            return False
        self.used += amount
        return True


class TokenBudgetManager:
    """
    Token 预算管理器
    
    职责：
    - 按 profile 分配预算
    - 追踪使用量
    - 支持周期重置
    """
    
    def __init__(self, store_path: str = "governance/budget/token_budgets.json"):
        self.store_path = store_path
        self._budgets: Dict[str, TokenBudget] = {}
        self._profile_limits = {
            "admin": 32000,
            "developer": 16000,
            "default": 8000,
            "operator": 4000,
            "auditor": 2000,
            "restricted": 1000
        }
        self._load()
    
    def _load(self):
        """加载预算"""
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, 'r') as f:
                    data = json.load(f)
                    for profile, budget_data in data.get("budgets", {}).items():
                        self._budgets[profile] = TokenBudget(
                            profile=profile,
                            limit=budget_data.get("limit", 8000),
                            used=budget_data.get("used", 0),
                            period=BudgetPeriod(budget_data.get("period", "per_request"))
                        )
            except:
                pass
    
    def _save(self):
        """保存预算"""
        os.makedirs(os.path.dirname(self.store_path) or ".", exist_ok=True)
        data = {
            "budgets": {
                profile: {
                    "limit": budget.limit,
                    "used": budget.used,
                    "period": budget.period.value
                }
                for profile, budget in self._budgets.items()
            }
        }
        with open(self.store_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_budget(self, profile: str) -> TokenBudget:
        """获取预算"""
        if profile not in self._budgets:
            limit = self._profile_limits.get(profile, 8000)
            self._budgets[profile] = TokenBudget(
                profile=profile,
                limit=limit,
                period=BudgetPeriod.PER_REQUEST
            )
        return self._budgets[profile]
    
    def allocate(self, profile: str, limit: int = None) -> TokenBudget:
        """分配预算"""
        limit = limit or self._profile_limits.get(profile, 8000)
        budget = TokenBudget(
            profile=profile,
            limit=limit,
            period=BudgetPeriod.PER_REQUEST
        )
        self._budgets[profile] = budget
        self._save()
        return budget
    
    def use_tokens(self, profile: str, amount: int) -> tuple[bool, int]:
        """使用 Token"""
        budget = self.get_budget(profile)
        success = budget.use(amount)
        self._save()
        return success, budget.remaining()
    
    def check_budget(self, profile: str, required: int = 0) -> tuple[bool, int]:
        """检查预算"""
        budget = self.get_budget(profile)
        remaining = budget.remaining()
        return remaining >= required, remaining
    
    def reset(self, profile: str):
        """重置预算"""
        if profile in self._budgets:
            self._budgets[profile].used = 0
            self._save()
    
    def set_profile_limit(self, profile: str, limit: int):
        """设置 profile 限制"""
        self._profile_limits[profile] = limit
        if profile in self._budgets:
            self._budgets[profile].limit = limit
            self._save()
    
    def get_decision_budget(self, profile: str) -> Dict:
        """获取决策预算信息"""
        budget = self.get_budget(profile)
        return {
            "limit": budget.limit,
            "used": budget.used,
            "remaining": budget.remaining(),
            "is_exceeded": budget.is_exceeded()
        }
