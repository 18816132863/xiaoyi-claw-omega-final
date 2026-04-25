"""
Skill Budget Policy
技能预算策略

管理技能调用的资源预算和限制
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
import json
import threading
from pathlib import Path


def _get_project_root() -> Path:
    """动态获取项目根目录"""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "core").exists() and (parent / "infrastructure").exists():
            return parent
    return current.parents[4]


class BudgetType(Enum):
    """预算类型"""
    CALL_COUNT = "call_count"           # 调用次数
    EXECUTION_TIME = "execution_time"   # 执行时间（秒）
    TOKEN_COUNT = "token_count"         # Token 数量
    MEMORY_MB = "memory_mb"             # 内存使用（MB）
    COST = "cost"                       # 成本


@dataclass
class BudgetLimit:
    """预算限制"""
    budget_type: BudgetType
    limit: float
    period_seconds: int = 3600  # 默认1小时
    current_usage: float = 0.0
    last_reset: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "budget_type": self.budget_type.value,
            "limit": self.limit,
            "period_seconds": self.period_seconds,
            "current_usage": self.current_usage,
            "last_reset": self.last_reset
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BudgetLimit':
        return cls(
            budget_type=BudgetType(data["budget_type"]),
            limit=data["limit"],
            period_seconds=data.get("period_seconds", 3600),
            current_usage=data.get("current_usage", 0.0),
            last_reset=data.get("last_reset")
        )
    
    def is_exceeded(self) -> bool:
        """检查是否超出预算"""
        return self.current_usage >= self.limit
    
    def remaining(self) -> float:
        """获取剩余预算"""
        return max(0, self.limit - self.current_usage)
    
    def reset_if_needed(self) -> bool:
        """如果需要则重置"""
        if self.last_reset:
            last = datetime.fromisoformat(self.last_reset)
            if datetime.now() - last > timedelta(seconds=self.period_seconds):
                self.current_usage = 0.0
                self.last_reset = datetime.now().isoformat()
                return True
        else:
            self.last_reset = datetime.now().isoformat()
        return False


class SkillBudgetPolicy:
    """技能预算策略"""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            project_root = _get_project_root()
            config_path = project_root / "config" / "skill_budget.json"
        
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 默认预算限制
        self._budgets: Dict[str, Dict[BudgetType, BudgetLimit]] = {}
        self._global_budgets: Dict[BudgetType, BudgetLimit] = {}
        self._lock = threading.RLock()
        
        self._init_defaults()
        self._load()
    
    def _init_defaults(self):
        """初始化默认预算"""
        # 全局默认预算
        self._global_budgets = {
            BudgetType.CALL_COUNT: BudgetLimit(BudgetType.CALL_COUNT, 1000, 3600),
            BudgetType.EXECUTION_TIME: BudgetLimit(BudgetType.EXECUTION_TIME, 3600, 3600),
            BudgetType.TOKEN_COUNT: BudgetLimit(BudgetType.TOKEN_COUNT, 100000, 3600),
        }
    
    def _load(self):
        """从文件加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 加载全局预算
                    for bt_str, limit_data in data.get("global", {}).items():
                        bt = BudgetType(bt_str)
                        self._global_budgets[bt] = BudgetLimit.from_dict(limit_data)
                    
                    # 加载技能特定预算
                    for skill_id, budgets in data.get("skills", {}).items():
                        self._budgets[skill_id] = {}
                        for bt_str, limit_data in budgets.items():
                            bt = BudgetType(bt_str)
                            self._budgets[skill_id][bt] = BudgetLimit.from_dict(limit_data)
            except Exception:
                pass
    
    def _save(self):
        """保存配置到文件"""
        with self._lock:
            data = {
                "global": {bt.value: limit.to_dict() 
                          for bt, limit in self._global_budgets.items()},
                "skills": {
                    skill_id: {bt.value: limit.to_dict() 
                              for bt, limit in budgets.items()}
                    for skill_id, budgets in self._budgets.items()
                }
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def set_global_limit(self, budget_type: BudgetType, limit: float, 
                         period_seconds: int = 3600):
        """设置全局预算限制"""
        with self._lock:
            self._global_budgets[budget_type] = BudgetLimit(
                budget_type=budget_type,
                limit=limit,
                period_seconds=period_seconds
            )
            self._save()
    
    def set_skill_limit(self, skill_id: str, budget_type: BudgetType, 
                        limit: float, period_seconds: int = 3600):
        """设置技能特定预算限制"""
        with self._lock:
            if skill_id not in self._budgets:
                self._budgets[skill_id] = {}
            self._budgets[skill_id][budget_type] = BudgetLimit(
                budget_type=budget_type,
                limit=limit,
                period_seconds=period_seconds
            )
            self._save()
    
    def get_limit(self, skill_id: str, budget_type: BudgetType) -> BudgetLimit:
        """获取预算限制"""
        # 先检查技能特定预算
        if skill_id in self._budgets and budget_type in self._budgets[skill_id]:
            return self._budgets[skill_id][budget_type]
        # 否则返回全局预算
        return self._global_budgets.get(budget_type, BudgetLimit(budget_type, float('inf')))
    
    def can_execute(self, skill_id: str, 
                    estimated_usage: Optional[Dict[BudgetType, float]] = None) -> bool:
        """检查是否可以执行"""
        with self._lock:
            # 检查所有预算类型
            for budget_type in [BudgetType.CALL_COUNT, BudgetType.EXECUTION_TIME, 
                               BudgetType.TOKEN_COUNT]:
                limit = self.get_limit(skill_id, budget_type)
                limit.reset_if_needed()
                
                if limit.is_exceeded():
                    return False
                
                # 检查预估使用量
                if estimated_usage and budget_type in estimated_usage:
                    if limit.current_usage + estimated_usage[budget_type] > limit.limit:
                        return False
            
            return True
    
    def record_usage(self, skill_id: str, budget_type: BudgetType, amount: float):
        """记录使用量"""
        with self._lock:
            limit = self.get_limit(skill_id, budget_type)
            limit.reset_if_needed()
            limit.current_usage += amount
            self._save()
    
    def get_usage(self, skill_id: str, budget_type: BudgetType) -> float:
        """获取当前使用量"""
        limit = self.get_limit(skill_id, budget_type)
        limit.reset_if_needed()
        return limit.current_usage
    
    def reset(self, skill_id: Optional[str] = None, 
              budget_type: Optional[BudgetType] = None):
        """重置预算"""
        with self._lock:
            if skill_id:
                if skill_id in self._budgets:
                    if budget_type:
                        if budget_type in self._budgets[skill_id]:
                            self._budgets[skill_id][budget_type].current_usage = 0.0
                            self._budgets[skill_id][budget_type].last_reset = datetime.now().isoformat()
                    else:
                        for bt in self._budgets[skill_id]:
                            self._budgets[skill_id][bt].current_usage = 0.0
                            self._budgets[skill_id][bt].last_reset = datetime.now().isoformat()
            else:
                if budget_type and budget_type in self._global_budgets:
                    self._global_budgets[budget_type].current_usage = 0.0
                    self._global_budgets[budget_type].last_reset = datetime.now().isoformat()
                else:
                    for bt in self._global_budgets:
                        self._global_budgets[bt].current_usage = 0.0
                        self._global_budgets[bt].last_reset = datetime.now().isoformat()
            
            self._save()


# 单例实例
_budget_policy: Optional[SkillBudgetPolicy] = None
_policy_lock = threading.Lock()


def get_skill_budget_policy() -> SkillBudgetPolicy:
    """获取技能预算策略单例"""
    global _budget_policy
    if _budget_policy is None:
        with _policy_lock:
            if _budget_policy is None:
                _budget_policy = SkillBudgetPolicy()
    return _budget_policy
