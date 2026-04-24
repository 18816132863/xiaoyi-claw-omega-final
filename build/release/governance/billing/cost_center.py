#!/usr/bin/env python3
"""
成本核算与计费中心 - V2.8.0

统计与管理：
- 按任务类型的资源消耗
- 按工作流的平均成本
- 按客户/项目的资源占用
- 按产物类型的生成成本
- 自动化动作的触发成本
- 高消耗能力的限频与限额规则

支持：
- 基础计费规则
- 套餐计费规则
- 限额控制
- 超额提醒
- 成本报表
- 收益/消耗对照
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
from enum import Enum

from infrastructure.path_resolver import get_project_root

class BillingModel(Enum):
    PAY_PER_USE = "pay_per_use"     # 按量计费
    SUBSCRIPTION = "subscription"    # 订阅制
    TIERED = "tiered"               # 阶梯计费
    PACKAGE = "package"             # 套餐计费

class ResourceType(Enum):
    TASK = "task"                   # 任务
    WORKFLOW = "workflow"           # 工作流
    PRODUCT = "product"             # 产物
    STORAGE = "storage"             # 存储
    API_CALL = "api_call"           # API调用
    AUTO_ACTION = "auto_action"     # 自动化动作

@dataclass
class ResourceCost:
    """资源成本"""
    resource_type: str
    resource_name: str
    unit_cost: float          # 单位成本
    unit: str                 # 单位（次、MB、个等）
    overhead_cost: float      # 额外开销

@dataclass
class UsageRecord:
    """使用记录"""
    record_id: str
    tenant_id: str
    workspace_id: str
    resource_type: str
    resource_name: str
    quantity: int
    cost: float
    timestamp: str

@dataclass
class BillingRule:
    """计费规则"""
    rule_id: str
    name: str
    billing_model: str
    base_cost: float
    unit_cost: float
    free_quota: int           # 免费额度
    tiered_rules: List[Dict]  # 阶梯规则
    limits: Dict[str, int]    # 限额

@dataclass
class BillingAccount:
    """计费账户"""
    tenant_id: str
    balance: float
    used_this_month: float
    limits: Dict[str, int]
    alerts: List[str]

class CostBillingCenter:
    """成本核算与计费中心"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.billing_path = self.project_root / 'billing'
        self.config_path = self.billing_path / 'billing_config.json'
        
        # 资源成本定义
        self.resource_costs: Dict[str, ResourceCost] = {}
        
        # 使用记录
        self.usage_records: List[UsageRecord] = []
        
        # 计费规则
        self.billing_rules: Dict[str, BillingRule] = {}
        
        # 计费账户
        self.accounts: Dict[str, BillingAccount] = {}
        
        self._init_defaults()
        self._load()
    
    def _init_defaults(self):
        """初始化默认配置"""
        # 默认资源成本
        default_costs = [
            ResourceCost("task", "basic_task", 0.01, "次", 0.001),
            ResourceCost("task", "complex_task", 0.05, "次", 0.005),
            ResourceCost("workflow", "analysis_workflow", 0.10, "次", 0.01),
            ResourceCost("workflow", "execution_workflow", 0.15, "次", 0.02),
            ResourceCost("product", "report", 0.02, "个", 0.005),
            ResourceCost("product", "table", 0.01, "个", 0.002),
            ResourceCost("storage", "data_storage", 0.001, "MB/天", 0.0),
            ResourceCost("api_call", "external_api", 0.005, "次", 0.001),
            ResourceCost("auto_action", "automation", 0.005, "次", 0.001),
        ]
        
        for cost in default_costs:
            self.resource_costs[f"{cost.resource_type}_{cost.resource_name}"] = cost
        
        # 默认计费规则
        default_rules = [
            BillingRule(
                rule_id="rule_basic",
                name="基础计费",
                billing_model=BillingModel.PAY_PER_USE.value,
                base_cost=0.0,
                unit_cost=1.0,
                free_quota=100,
                tiered_rules=[],
                limits={"daily_tasks": 1000, "monthly_tasks": 30000}
            ),
            BillingRule(
                rule_id="rule_subscription",
                name="订阅制",
                billing_model=BillingModel.SUBSCRIPTION.value,
                base_cost=99.0,
                unit_cost=0.0,
                free_quota=1000,
                tiered_rules=[],
                limits={"daily_tasks": 5000, "monthly_tasks": 150000}
            ),
            BillingRule(
                rule_id="rule_tiered",
                name="阶梯计费",
                billing_model=BillingModel.TIERED.value,
                base_cost=0.0,
                unit_cost=0.01,
                free_quota=50,
                tiered_rules=[
                    {"min": 0, "max": 100, "rate": 0.01},
                    {"min": 100, "max": 500, "rate": 0.008},
                    {"min": 500, "max": 1000, "rate": 0.005},
                    {"min": 1000, "max": -1, "rate": 0.003}
                ],
                limits={}
            )
        ]
        
        for rule in default_rules:
            self.billing_rules[rule.rule_id] = rule
    
    def _load(self):
        """加载配置"""
        if self.config_path.exists():
            data = json.loads(self.config_path.read_text(encoding='utf-8'))
            
            for rid, rdata in data.get("usage_records", {}).items():
                self.usage_records.append(UsageRecord(**rdata))
            
            for tid, adata in data.get("accounts", {}).items():
                self.accounts[tid] = BillingAccount(**adata)
    
    def _save(self):
        """保存配置"""
        self.billing_path.mkdir(parents=True, exist_ok=True)
        data = {
            "usage_records": {r.record_id: asdict(r) for r in self.usage_records[-10000:]},
            "accounts": {tid: asdict(a) for tid, a in self.accounts.items()},
            "updated": datetime.now().isoformat()
        }
        self.config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def record_usage(self, tenant_id: str, workspace_id: str,
                     resource_type: str, resource_name: str,
                     quantity: int) -> UsageRecord:
        """记录使用"""
        # 计算成本
        cost_key = f"{resource_type}_{resource_name}"
        resource_cost = self.resource_costs.get(cost_key)
        
        if resource_cost:
            cost = (resource_cost.unit_cost + resource_cost.overhead_cost) * quantity
        else:
            cost = 0.01 * quantity  # 默认成本
        
        record = UsageRecord(
            record_id=f"usage_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            resource_type=resource_type,
            resource_name=resource_name,
            quantity=quantity,
            cost=cost,
            timestamp=datetime.now().isoformat()
        )
        
        self.usage_records.append(record)
        
        # 更新账户
        if tenant_id not in self.accounts:
            self.accounts[tenant_id] = BillingAccount(
                tenant_id=tenant_id,
                balance=0.0,
                used_this_month=0.0,
                limits={},
                alerts=[]
            )
        
        self.accounts[tenant_id].used_this_month += cost
        self._save()
        
        return record
    
    def calculate_cost(self, tenant_id: str, rule_id: str, usage: Dict) -> float:
        """计算成本"""
        rule = self.billing_rules.get(rule_id)
        if not rule:
            return 0.0
        
        total_usage = sum(usage.values())
        
        if rule.billing_model == BillingModel.PAY_PER_USE.value:
            # 按量计费
            billable = max(0, total_usage - rule.free_quota)
            return billable * rule.unit_cost
        
        elif rule.billing_model == BillingModel.SUBSCRIPTION.value:
            # 订阅制
            return rule.base_cost
        
        elif rule.billing_model == BillingModel.TIERED.value:
            # 阶梯计费
            cost = 0.0
            remaining = total_usage - rule.free_quota
            
            for tier in rule.tiered_rules:
                if remaining <= 0:
                    break
                
                tier_max = tier["max"] if tier["max"] > 0 else remaining
                tier_usage = min(remaining, tier_max - tier["min"])
                cost += tier_usage * tier["rate"]
                remaining -= tier_usage
            
            return cost
        
        return 0.0
    
    def check_limit(self, tenant_id: str, resource_type: str,
                    current_usage: int) -> tuple:
        """检查限额"""
        if tenant_id not in self.accounts:
            return True, "无限制"
        
        account = self.accounts[tenant_id]
        
        # 检查账户限额
        limit_key = f"daily_{resource_type}"
        if limit_key in account.limits:
            limit = account.limits[limit_key]
            if current_usage >= limit:
                return False, f"已达日限额: {limit}"
        
        return True, "限额检查通过"
    
    def add_alert(self, tenant_id: str, message: str):
        """添加超额提醒"""
        if tenant_id in self.accounts:
            self.accounts[tenant_id].alerts.append({
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            self._save()
    
    def get_usage_report(self, tenant_id: str, period: str = "month") -> Dict:
        """获取使用报告"""
        now = datetime.now()
        
        if period == "day":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start = now - timedelta(days=7)
        elif period == "month":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start = now - timedelta(days=30)
        
        # 过滤记录
        records = [
            r for r in self.usage_records
            if r.tenant_id == tenant_id and datetime.fromisoformat(r.timestamp) >= start
        ]
        
        # 按类型统计
        by_type = defaultdict(lambda: {"count": 0, "cost": 0.0})
        for record in records:
            by_type[record.resource_type]["count"] += record.quantity
            by_type[record.resource_type]["cost"] += record.cost
        
        return {
            "tenant_id": tenant_id,
            "period": period,
            "total_records": len(records),
            "total_cost": sum(r.cost for r in records),
            "by_type": dict(by_type)
        }
    
    def get_cost_report(self) -> str:
        """生成成本报告"""
        lines = [
            "# 成本核算报告",
            "",
            "## 资源成本定义",
            ""
        ]
        
        for key, cost in self.resource_costs.items():
            lines.append(f"- **{key}**: {cost.unit_cost}/{cost.unit} (开销: {cost.overhead_cost})")
        
        lines.extend([
            "",
            "## 计费规则",
            ""
        ])
        
        for rule in self.billing_rules.values():
            lines.append(f"- **{rule.name}** ({rule.billing_model}): 基础 {rule.base_cost}, 免费额度 {rule.free_quota}")
        
        lines.extend([
            "",
            "## 账户状态",
            ""
        ])
        
        for account in self.accounts.values():
            lines.append(f"- **{account.tenant_id}**: 本月已用 {account.used_this_month:.2f}")
        
        return "\n".join(lines)

# 全局实例
_cost_center = None

def get_cost_center() -> CostBillingCenter:
    global _cost_center
    if _cost_center is None:
        _cost_center = CostBillingCenter()
    return _cost_center
