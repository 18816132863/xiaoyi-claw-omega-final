"""风险等级定义 - L4 强确认，不默认禁止"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class RiskLevel(Enum):
    """风险等级"""
    L0 = "L0"  # 查询、总结、解释 - 自动执行
    L1 = "L1"  # 轻写入（备忘录、日程） - 自动执行
    L2 = "L2"  # 短信、通知、批量操作 - 策略控制 + 限流
    L3 = "L3"  # 删除、拨电话、重要修改 - 默认确认
    L4 = "L4"  # 支付、金融、账号、隐私、游戏自动化 - 强确认 + 分步执行
    BLOCKED = "BLOCKED"  # 违法、盗号、绕过反作弊、规避风控 - 拒绝


class RiskPolicy(Enum):
    """风险策略"""
    AUTO_EXECUTE = "auto_execute"  # 自动执行
    RATE_LIMITED = "rate_limited"  # 限流执行
    CONFIRM_ONCE = "confirm_once"  # 单次确认
    STRONG_CONFIRM = "strong_confirm"  # 强确认（双重确认 + 预览 + 分步）
    BLOCKED = "blocked"  # 拒绝执行


@dataclass
class RiskAssessment:
    """风险评估结果"""
    risk_level: RiskLevel
    policy: RiskPolicy
    requires_confirmation: bool = False
    requires_preview: bool = False
    requires_stepwise: bool = False
    blocked: bool = False
    reason: Optional[str] = None
    confirmation_prompt: Optional[str] = None
    preview_data: Optional[dict] = None


# 风险等级到策略的映射
RISK_POLICY_MAP = {
    RiskLevel.L0: RiskPolicy.AUTO_EXECUTE,
    RiskLevel.L1: RiskPolicy.AUTO_EXECUTE,
    RiskLevel.L2: RiskPolicy.RATE_LIMITED,
    RiskLevel.L3: RiskPolicy.CONFIRM_ONCE,
    RiskLevel.L4: RiskPolicy.STRONG_CONFIRM,  # 强确认，不默认禁止
    RiskLevel.BLOCKED: RiskPolicy.BLOCKED,
}

# BLOCKED 场景定义
BLOCKED_SCENARIOS = [
    "illegal_activity",  # 违法活动
    "bypass_anti_cheat",  # 绕过反作弊
    "account_theft",  # 盗号
    "unauthorized_payment",  # 未授权支付
    "batch_harassment",  # 批量骚扰
    "bypass_risk_control",  # 规避风控
    "competitive_cheating",  # 竞技作弊
    "resource_farming_bot",  # 脚本挂机刷资源
    "unauthorized_trading",  # 未授权交易
]
