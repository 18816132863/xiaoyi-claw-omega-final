"""经销商-团长数据模型"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from datetime import datetime

class LeaderLevel(Enum):
    """团长等级"""
    BRONZE = "青铜"
    SILVER = "白银"
    GOLD = "黄金"
    DIAMOND = "钻石"

class SettlementCycle(Enum):
    """结算周期"""
    WEEKLY = "周结"
    BIWEEKLY = "双周结"
    MONTHLY = "月结"

@dataclass
class Leader:
    """团长信息"""
    leader_id: str
    name: str
    region: str
    category: str
    followers: int = 0
    monthly_sales: float = 0.0
    rating: float = 5.0
    level: LeaderLevel = LeaderLevel.BRONZE
    contact: Optional[str] = None
    wechat: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def calculate_level(self) -> LeaderLevel:
        """根据销量计算等级"""
        if self.monthly_sales >= 100000:
            return LeaderLevel.DIAMOND
        elif self.monthly_sales >= 50000:
            return LeaderLevel.GOLD
        elif self.monthly_sales >= 10000:
            return LeaderLevel.SILVER
        return LeaderLevel.BRONZE

@dataclass
class CommissionScheme:
    """佣金方案"""
    scheme_id: str
    category: str
    base_rate: float  # 基础佣金率
    tiered_rates: dict = field(default_factory=dict)  # 阶梯佣金
    promotion_rates: dict = field(default_factory=dict)  # 促销佣金
    settlement_cycle: SettlementCycle = SettlementCycle.MONTHLY
    
    def get_commission(self, leader: Leader, is_promotion: bool = False) -> float:
        """计算佣金率"""
        level = leader.calculate_level()
        rate = self.tiered_rates.get(level.value, self.base_rate)
        if is_promotion:
            rate += self.promotion_rates.get("default", 0)
        return rate

@dataclass
class Cooperation:
    """合作关系"""
    cooperation_id: str
    dealer_id: str
    leader_id: str
    commission_scheme: str
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str = "active"
    total_sales: float = 0.0
    total_commission: float = 0.0

@dataclass
class Order:
    """订单"""
    order_id: str
    cooperation_id: str
    leader_id: str
    product_name: str
    quantity: int
    unit_price: float
    total_amount: float
    commission_rate: float
    commission_amount: float
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Settlement:
    """结算单"""
    settlement_id: str
    leader_id: str
    period_start: datetime
    period_end: datetime
    total_sales: float
    total_commission: float
    orders: List[str] = field(default_factory=list)
    status: str = "pending"
    paid_at: Optional[datetime] = None
