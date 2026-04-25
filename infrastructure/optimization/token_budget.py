"""Token 预算管理器 - V1.0.0"""

from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class LayerBudget:
    """层级预算"""
    name: str
    budget: int
    used: int = 0

class TokenBudgetManager:
    """Token 预算管理器"""
    
    LAYER_BUDGETS = {
        "L1_core": 3000,
        "L2_memory_context": 2000,
        "L3_orchestration": 1500,
        "L4_execution": 1500,
        "L5_governance": 800,
        "L6_infrastructure": 700
    }
    
    def __init__(self, total_budget: int = 10000):
        self.total_budget = total_budget
        self.layer_budgets: Dict[str, LayerBudget] = {}
        self._init_budgets()
    
    def _init_budgets(self):
        """初始化预算"""
        for layer, budget in self.LAYER_BUDGETS.items():
            self.layer_budgets[layer] = LayerBudget(
                name=layer,
                budget=budget
            )
    
    def allocate(self, layer: str, tokens: int) -> bool:
        """分配 token"""
        if layer not in self.layer_budgets:
            return False
        
        layer_budget = self.layer_budgets[layer]
        if layer_budget.used + tokens > layer_budget.budget:
            return False
        
        layer_budget.used += tokens
        return True
    
    def can_allocate(self, layer: str, tokens: int) -> bool:
        """检查是否可以分配"""
        if layer not in self.layer_budgets:
            return False
        
        layer_budget = self.layer_budgets[layer]
        return layer_budget.used + tokens <= layer_budget.budget
    
    def get_remaining(self, layer: str) -> int:
        """获取剩余预算"""
        if layer not in self.layer_budgets:
            return 0
        return self.layer_budgets[layer].budget - self.layer_budgets[layer].used
    
    def get_total_used(self) -> int:
        """获取总使用量"""
        return sum(lb.used for lb in self.layer_budgets.values())
    
    def get_total_remaining(self) -> int:
        """获取总剩余量"""
        return self.total_budget - self.get_total_used()
    
    def get_summary(self) -> Dict:
        """获取预算摘要"""
        return {
            "total_budget": self.total_budget,
            "total_used": self.get_total_used(),
            "total_remaining": self.get_total_remaining(),
            "layers": {
                layer: {
                    "budget": lb.budget,
                    "used": lb.used,
                    "remaining": lb.budget - lb.used,
                    "usage_rate": lb.used / lb.budget if lb.budget > 0 else 0
                }
                for layer, lb in self.layer_budgets.items()
            }
        }
    
    def reset(self):
        """重置预算"""
        for layer_budget in self.layer_budgets.values():
            layer_budget.used = 0
