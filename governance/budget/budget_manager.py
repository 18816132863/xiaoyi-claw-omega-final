"""Budget manager - resource budget tracking and enforcement."""

from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os


class ResourceType(Enum):
    TOKENS = "tokens"
    API_CALLS = "api_calls"
    EXECUTION_TIME = "execution_time"
    STORAGE = "storage"
    SKILL_CALLS = "skill_calls"


class BudgetPeriod(Enum):
    PER_REQUEST = "per_request"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class Budget:
    """Resource budget definition."""
    budget_id: str
    resource_type: ResourceType
    period: BudgetPeriod
    limit: int
    current_usage: int = 0
    reset_at: datetime = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if self.reset_at is None:
            self.reset_at = self._calculate_reset()
    
    def _calculate_reset(self) -> datetime:
        """Calculate next reset time."""
        now = datetime.now()
        
        if self.period == BudgetPeriod.PER_REQUEST:
            return now
        elif self.period == BudgetPeriod.HOURLY:
            return (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))
        elif self.period == BudgetPeriod.DAILY:
            return (now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1))
        elif self.period == BudgetPeriod.WEEKLY:
            days_until_monday = (7 - now.weekday()) % 7
            return (now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday))
        elif self.period == BudgetPeriod.MONTHLY:
            next_month = now.replace(day=1) + timedelta(days=32)
            return next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        return now
    
    def remaining(self) -> int:
        """Get remaining budget."""
        if datetime.now() >= self.reset_at:
            return self.limit
        return max(0, self.limit - self.current_usage)
    
    def is_exceeded(self) -> bool:
        """Check if budget is exceeded."""
        if datetime.now() >= self.reset_at:
            return False
        return self.current_usage >= self.limit
    
    def use(self, amount: int) -> bool:
        """Use budget. Returns True if successful."""
        if datetime.now() >= self.reset_at:
            self.current_usage = 0
            self.reset_at = self._calculate_reset()
        
        if self.current_usage + amount > self.limit:
            return False
        
        self.current_usage += amount
        return True
    
    def reset(self):
        """Reset budget."""
        self.current_usage = 0
        self.reset_at = self._calculate_reset()


@dataclass
class UsageRecord:
    """Record of resource usage."""
    resource_type: ResourceType
    amount: int
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


class BudgetManager:
    """
    Manages resource budgets across the system.
    
    Tracks and enforces limits for:
    - Token usage
    - API calls
    - Execution time
    - Storage
    - Skill calls
    """
    
    def __init__(self, store_path: str = "governance/budget/budgets.json"):
        self.store_path = store_path
        self._budgets: Dict[str, Budget] = {}
        self._usage_history: List[UsageRecord] = []
        self._load()
    
    def _load(self):
        """Load budgets from file."""
        if os.path.exists(self.store_path):
            try:
                with open(self.store_path, 'r') as f:
                    data = json.load(f)
                    for budget_data in data.get("budgets", []):
                        budget = Budget(
                            budget_id=budget_data["budget_id"],
                            resource_type=ResourceType(budget_data["resource_type"]),
                            period=BudgetPeriod(budget_data["period"]),
                            limit=budget_data["limit"],
                            current_usage=budget_data.get("current_usage", 0),
                            reset_at=datetime.fromisoformat(budget_data["reset_at"]) if budget_data.get("reset_at") else None
                        )
                        self._budgets[budget.budget_id] = budget
            except Exception as e:
                print(f"Warning: Failed to load budgets: {e}")
    
    def _save(self):
        """Save budgets to file."""
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        data = {
            "budgets": [
                {
                    "budget_id": b.budget_id,
                    "resource_type": b.resource_type.value,
                    "period": b.period.value,
                    "limit": b.limit,
                    "current_usage": b.current_usage,
                    "reset_at": b.reset_at.isoformat() if b.reset_at else None
                }
                for b in self._budgets.values()
            ]
        }
        with open(self.store_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_budget(
        self,
        budget_id: str,
        resource_type: ResourceType,
        period: BudgetPeriod,
        limit: int
    ) -> Budget:
        """Create a new budget."""
        budget = Budget(
            budget_id=budget_id,
            resource_type=resource_type,
            period=period,
            limit=limit
        )
        self._budgets[budget_id] = budget
        self._save()
        return budget
    
    def get_budget(self, budget_id: str) -> Optional[Budget]:
        """Get a budget by ID."""
        return self._budgets.get(budget_id)
    
    def check_budget(self, budget_id: str, amount: int = 1) -> tuple[bool, int]:
        """
        Check if budget allows usage.
        
        Returns:
            Tuple of (allowed, remaining)
        """
        budget = self._budgets.get(budget_id)
        if not budget:
            return True, -1  # No budget = unlimited
        
        remaining = budget.remaining()
        return remaining >= amount, remaining
    
    def use_budget(
        self,
        budget_id: str,
        amount: int,
        source: str = "",
        metadata: Dict = None
    ) -> tuple[bool, int]:
        """
        Use budget.
        
        Returns:
            Tuple of (success, remaining)
        """
        budget = self._budgets.get(budget_id)
        if not budget:
            return True, -1
        
        success = budget.use(amount)
        
        # Record usage
        self._usage_history.append(UsageRecord(
            resource_type=budget.resource_type,
            amount=amount,
            source=source,
            metadata=metadata
        ))
        
        if success:
            self._save()
        
        return success, budget.remaining()
    
    def get_usage_stats(
        self,
        resource_type: ResourceType = None,
        since: datetime = None
    ) -> Dict:
        """Get usage statistics."""
        records = self._usage_history
        
        if resource_type:
            records = [r for r in records if r.resource_type == resource_type]
        
        if since:
            records = [r for r in records if r.timestamp >= since]
        
        total = sum(r.amount for r in records)
        
        return {
            "total_usage": total,
            "record_count": len(records),
            "by_source": self._aggregate_by_source(records)
        }
    
    def _aggregate_by_source(self, records: List[UsageRecord]) -> Dict[str, int]:
        """Aggregate usage by source."""
        result = {}
        for record in records:
            source = record.source or "unknown"
            result[source] = result.get(source, 0) + record.amount
        return result
    
    def reset_budget(self, budget_id: str) -> bool:
        """Reset a budget."""
        budget = self._budgets.get(budget_id)
        if budget:
            budget.reset()
            self._save()
            return True
        return False
    
    def list_budgets(self) -> List[Budget]:
        """List all budgets."""
        return list(self._budgets.values())
    
    def get_exceeded_budgets(self) -> List[str]:
        """Get IDs of exceeded budgets."""
        return [bid for bid, b in self._budgets.items() if b.is_exceeded()]
    
    def get_low_budgets(self, threshold: float = 0.1) -> List[Dict]:
        """Get budgets below threshold."""
        low = []
        for bid, b in self._budgets.items():
            remaining_pct = b.remaining() / b.limit if b.limit > 0 else 1.0
            if remaining_pct < threshold:
                low.append({
                    "budget_id": bid,
                    "remaining": b.remaining(),
                    "limit": b.limit,
                    "percentage": remaining_pct
                })
        return low
