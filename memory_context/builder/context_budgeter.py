"""Context Budgeter - Token 预算管理"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass


@dataclass
class BudgetAllocation:
    """预算分配"""
    source_type: str
    allocated_tokens: int
    used_tokens: int
    remaining_tokens: int


class ContextBudgeter:
    """
    Token 预算管理器
    
    职责：
    - 分配 Token 预算给不同源类型
    - 裁剪超出预算的内容
    - 优化预算使用
    """
    
    def __init__(
        self,
        default_budget: int = 8000,
        reserve_for_response: int = 2000,
        min_source_tokens: int = 100
    ):
        self.default_budget = default_budget
        self.reserve_for_response = reserve_for_response
        self.min_source_tokens = min_source_tokens
        
        # 源类型预算分配比例
        self.source_ratios = {
            "rule": 0.25,
            "memory": 0.20,
            "document": 0.20,
            "session": 0.15,
            "skill": 0.10,
            "report": 0.05,
            "additional": 0.05
        }
    
    def apply(
        self,
        sources: List[Dict[str, Any]],
        token_budget: int = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        应用 Token 预算
        
        Args:
            sources: 源列表
            token_budget: 总 Token 预算
        
        Returns:
            Tuple of (budgeted_sources, actual_token_count)
        """
        budget = token_budget or self.default_budget
        available = budget - self.reserve_for_response
        
        # 按源类型分组
        grouped = self._group_by_type(sources)
        
        # 分配预算
        allocations = self._allocate_budget(grouped, available)
        
        # 应用预算
        budgeted = []
        total_tokens = 0
        
        for source_type, sources_in_type in grouped.items():
            type_budget = allocations.get(source_type, 0)
            type_budgeted, type_tokens = self._apply_to_type(
                sources_in_type,
                type_budget
            )
            budgeted.extend(type_budgeted)
            total_tokens += type_tokens
        
        return budgeted, total_tokens
    
    def _group_by_type(
        self,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """按类型分组"""
        grouped = {}
        
        for source in sources:
            source_type = source.get("type", "document")
            if source_type not in grouped:
                grouped[source_type] = []
            grouped[source_type].append(source)
        
        return grouped
    
    def _allocate_budget(
        self,
        grouped: Dict[str, List[Dict[str, Any]]],
        total_budget: int
    ) -> Dict[str, int]:
        """分配预算"""
        allocations = {}
        
        for source_type, sources in grouped.items():
            ratio = self.source_ratios.get(source_type, 0.1)
            allocation = int(total_budget * ratio)
            
            # 确保最小预算
            if sources:
                allocation = max(allocation, self.min_source_tokens)
            
            allocations[source_type] = allocation
        
        return allocations
    
    def _apply_to_type(
        self,
        sources: List[Dict[str, Any]],
        budget: int
    ) -> Tuple[List[Dict[str, Any]], int]:
        """对单个类型应用预算"""
        budgeted = []
        current_tokens = 0
        
        # 按相关性排序
        sorted_sources = sorted(
            sources,
            key=lambda s: s.get("relevance", 0),
            reverse=True
        )
        
        for source in sorted_sources:
            content = source.get("content", "")
            estimated_tokens = max(len(content) // 4, self.min_source_tokens)
            
            if current_tokens + estimated_tokens <= budget:
                budgeted.append(source)
                current_tokens += estimated_tokens
            else:
                # 尝试截断
                remaining = budget - current_tokens
                if remaining >= self.min_source_tokens:
                    truncated_content = content[:remaining * 4]
                    source_copy = source.copy()
                    source_copy["content"] = truncated_content
                    source_copy["truncated"] = True
                    budgeted.append(source_copy)
                    current_tokens += remaining
                break
        
        return budgeted, current_tokens
    
    def estimate_tokens(self, text: str) -> int:
        """估算 Token 数量"""
        return len(text) // 4
    
    def set_source_ratio(self, source_type: str, ratio: float):
        """设置源类型预算比例"""
        self.source_ratios[source_type] = ratio
        
        # 归一化
        total = sum(self.source_ratios.values())
        if total > 0:
            for st in self.source_ratios:
                self.source_ratios[st] /= total
    
    def get_budget_report(
        self,
        sources: List[Dict[str, Any]],
        token_budget: int = None
    ) -> Dict[str, Any]:
        """获取预算报告"""
        budgeted, used = self.apply(sources, token_budget)
        budget = token_budget or self.default_budget
        
        return {
            "total_budget": budget,
            "used_tokens": used,
            "remaining_tokens": budget - used,
            "reserve_for_response": self.reserve_for_response,
            "source_count": len(sources),
            "budgeted_count": len(budgeted),
            "truncated_count": sum(1 for s in budgeted if s.get("truncated"))
        }
