"""Token budget manager for context construction."""

from typing import List, Dict, Tuple


class ContextBudgeter:
    """Manages token budget allocation for context."""
    
    def __init__(
        self,
        default_budget: int = 8000,
        reserve_for_response: int = 2000,
        min_source_tokens: int = 100
    ):
        self.default_budget = default_budget
        self.reserve_for_response = reserve_for_response
        self.min_source_tokens = min_source_tokens
    
    def apply(
        self,
        sources: List[Dict],
        token_budget: int = None
    ) -> Tuple[List[Dict], int]:
        """
        Apply token budget to sources.
        
        Returns:
            Tuple of (budgeted_sources, actual_token_count)
        """
        budget = token_budget or self.default_budget
        available = budget - self.reserve_for_response
        
        budgeted = []
        total_tokens = 0
        
        for source in sources:
            content = source.get("content", "")
            # Estimate tokens (rough: 4 chars per token)
            estimated_tokens = max(len(content) // 4, self.min_source_tokens)
            
            if total_tokens + estimated_tokens <= available:
                budgeted.append(source)
                total_tokens += estimated_tokens
            else:
                # Try to truncate if possible
                remaining = available - total_tokens
                if remaining >= self.min_source_tokens:
                    truncated_content = content[:remaining * 4]
                    source_copy = source.copy()
                    source_copy["content"] = truncated_content
                    source_copy["truncated"] = True
                    budgeted.append(source_copy)
                    total_tokens += remaining
                break
        
        return budgeted, total_tokens
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def allocate_budget(
        self,
        total_budget: int,
        source_priorities: Dict[str, float]
    ) -> Dict[str, int]:
        """
        Allocate budget across source types based on priorities.
        
        Args:
            total_budget: Total token budget
            source_priorities: Dict of source_type -> priority (0-1)
        
        Returns:
            Dict of source_type -> allocated_tokens
        """
        available = total_budget - self.reserve_for_response
        
        # Normalize priorities
        total_priority = sum(source_priorities.values())
        if total_priority == 0:
            # Equal allocation
            count = len(source_priorities)
            return {k: available // count for k in source_priorities}
        
        allocations = {}
        for source_type, priority in source_priorities.items():
            allocation = int(available * (priority / total_priority))
            allocations[source_type] = max(allocation, self.min_source_tokens)
        
        return allocations
