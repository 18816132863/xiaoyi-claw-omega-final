"""Cost Budget Manager - 成本预算管理"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from enum import Enum
import json
import os


class CostType(Enum):
    API_CALL = "api_call"
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"


@dataclass
class CostBudget:
    """成本预算"""
    profile: str
    cost_type: CostType
    limit: float  # 成本限制（单位：元或其他）
    used: float = 0.0
    period: str = "daily"  # daily, weekly, monthly
    
    def remaining(self) -> float:
        return max(0.0, self.limit - self.used)
    
    def is_exceeded(self) -> bool:
        return self.used >= self.limit
    
    def use(self, amount: float) -> bool:
        if self.used + amount > self.limit:
            return False
        self.used += amount
        return True


class CostBudgetManager:
    """
    成本预算管理器
    
    职责：
    - 按 profile 和成本类型分配预算
    - 追踪成本使用
    - 支持多维度成本控制
    """
    
    def __init__(self, store_path: str = "governance/budget/cost_budgets.json"):
        self.store_path = store_path
        self._budgets: Dict[str, CostBudget] = {}
        self._default_limits = {
            ("admin", CostType.API_CALL): 100.0,
            ("admin", CostType.COMPUTE): 50.0,
            ("developer", CostType.API_CALL): 50.0,
            ("developer", CostType.COMPUTE): 20.0,
            ("default", CostType.API_CALL): 20.0,
            ("default", CostType.COMPUTE): 10.0,
            ("operator", CostType.API_CALL): 10.0,
            ("auditor", CostType.API_CALL): 5.0,
            ("restricted", CostType.API_CALL): 1.0,
        }
        self._load()
    
    def _load(self):
        """加载预算"""
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, 'r') as f:
                    data = json.load(f)
                    for key, budget_data in data.get("budgets", {}).items():
                        self._budgets[key] = CostBudget(
                            profile=budget_data.get("profile", "default"),
                            cost_type=CostType(budget_data.get("cost_type", "api_call")),
                            limit=budget_data.get("limit", 10.0),
                            used=budget_data.get("used", 0.0),
                            period=budget_data.get("period", "daily")
                        )
            except:
                pass
    
    def _save(self):
        """保存预算"""
        os.makedirs(os.path.dirname(self.store_path) or ".", exist_ok=True)
        data = {
            "budgets": {
                key: {
                    "profile": budget.profile,
                    "cost_type": budget.cost_type.value,
                    "limit": budget.limit,
                    "used": budget.used,
                    "period": budget.period
                }
                for key, budget in self._budgets.items()
            }
        }
        with open(self.store_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _make_key(self, profile: str, cost_type: CostType) -> str:
        return f"{profile}_{cost_type.value}"
    
    def get_budget(self, profile: str, cost_type: CostType) -> CostBudget:
        """获取预算"""
        key = self._make_key(profile, cost_type)
        
        if key not in self._budgets:
            limit = self._default_limits.get((profile, cost_type), 10.0)
            self._budgets[key] = CostBudget(
                profile=profile,
                cost_type=cost_type,
                limit=limit
            )
        
        return self._budgets[key]
    
    def use_cost(
        self,
        profile: str,
        cost_type: CostType,
        amount: float
    ) -> tuple[bool, float]:
        """使用成本"""
        budget = self.get_budget(profile, cost_type)
        success = budget.use(amount)
        self._save()
        return success, budget.remaining()
    
    def check_budget(
        self,
        profile: str,
        cost_type: CostType,
        required: float = 0
    ) -> tuple[bool, float]:
        """检查预算"""
        budget = self.get_budget(profile, cost_type)
        remaining = budget.remaining()
        return remaining >= required, remaining
    
    def get_decision_budget(self, profile: str) -> Dict:
        """获取决策预算信息"""
        api_budget = self.get_budget(profile, CostType.API_CALL)
        compute_budget = self.get_budget(profile, CostType.COMPUTE)
        
        return {
            "api_call": {
                "limit": api_budget.limit,
                "used": api_budget.used,
                "remaining": api_budget.remaining(),
                "is_exceeded": api_budget.is_exceeded()
            },
            "compute": {
                "limit": compute_budget.limit,
                "used": compute_budget.used,
                "remaining": compute_budget.remaining(),
                "is_exceeded": compute_budget.is_exceeded()
            }
        }
    
    def reset(self, profile: str, cost_type: CostType = None):
        """重置预算"""
        if cost_type:
            key = self._make_key(profile, cost_type)
            if key in self._budgets:
                self._budgets[key].used = 0.0
        else:
            for key in list(self._budgets.keys()):
                if key.startswith(f"{profile}_"):
                    self._budgets[key].used = 0.0
        self._save()
