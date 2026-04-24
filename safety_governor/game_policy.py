"""游戏策略 - 不一刀切禁止"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from .risk_levels import RiskLevel, RiskPolicy, RiskAssessment


class GameActionType(Enum):
    """游戏动作类型"""
    # 允许（L0-L2）
    VISUAL_ASSIST = "visual_assist"  # 视觉辅助
    STRATEGY_SUGGESTION = "strategy_suggestion"  # 策略建议
    PRACTICE_MODE = "practice_mode"  # 练习模式
    SINGLE_PLAYER = "single_player"  # 单机非竞争
    REPLAY_ANALYSIS = "replay_analysis"  # 复盘分析
    PAGE_UNDERSTANDING = "page_understanding"  # 页面理解
    OPERATION_REMINDER = "operation_reminder"  # 操作提醒
    
    # 强确认（L4）
    AUTO_CLICK = "auto_click"  # 自动点击
    LONG_OPERATION = "long_operation"  # 长时间操作
    RESOURCE_OPERATION = "resource_operation"  # 资源操作
    ITEM_OPERATION = "item_operation"  # 道具操作
    GACHA_OPERATION = "gacha_operation"  # 抽卡操作
    
    # 禁止（BLOCKED）
    COMPETITIVE_AUTO_PLAY = "competitive_auto_play"  # 联网竞技自动代打
    BYPASS_ANTI_CHEAT = "bypass_anti_cheat"  # 绕过反作弊
    RESOURCE_FARMING = "resource_farming"  # 挂机刷资源
    ACCOUNT_TRADING = "account_trading"  # 账号交易
    UNAUTHORIZED_PAYMENT = "unauthorized_payment"  # 未授权支付


# 动作类型到风险等级的映射
GAME_ACTION_RISK_MAP = {
    GameActionType.VISUAL_ASSIST: RiskLevel.L0,
    GameActionType.STRATEGY_SUGGESTION: RiskLevel.L0,
    GameActionType.PRACTICE_MODE: RiskLevel.L1,
    GameActionType.SINGLE_PLAYER: RiskLevel.L2,
    GameActionType.REPLAY_ANALYSIS: RiskLevel.L0,
    GameActionType.PAGE_UNDERSTANDING: RiskLevel.L0,
    GameActionType.OPERATION_REMINDER: RiskLevel.L1,
    GameActionType.AUTO_CLICK: RiskLevel.L4,
    GameActionType.LONG_OPERATION: RiskLevel.L4,
    GameActionType.RESOURCE_OPERATION: RiskLevel.L4,
    GameActionType.ITEM_OPERATION: RiskLevel.L4,
    GameActionType.GACHA_OPERATION: RiskLevel.L4,
    GameActionType.COMPETITIVE_AUTO_PLAY: RiskLevel.BLOCKED,
    GameActionType.BYPASS_ANTI_CHEAT: RiskLevel.BLOCKED,
    GameActionType.RESOURCE_FARMING: RiskLevel.BLOCKED,
    GameActionType.ACCOUNT_TRADING: RiskLevel.BLOCKED,
    GameActionType.UNAUTHORIZED_PAYMENT: RiskLevel.BLOCKED,
}


@dataclass
class GamePolicyResult:
    """游戏策略结果"""
    allowed: bool
    action_type: GameActionType
    risk_level: RiskLevel
    policy: RiskPolicy
    message: str
    requires_confirmation: bool = False


class GamePolicy:
    """游戏策略"""
    
    def assess_game_action(
        self,
        action: str,
        game_context: Optional[Dict[str, Any]] = None,
    ) -> GamePolicyResult:
        """评估游戏动作"""
        game_context = game_context or {}
        
        # 确定动作类型
        action_type = self._classify_game_action(action, game_context)
        risk_level = GAME_ACTION_RISK_MAP[action_type]
        
        # BLOCKED
        if risk_level == RiskLevel.BLOCKED:
            return GamePolicyResult(
                allowed=False,
                action_type=action_type,
                risk_level=risk_level,
                policy=RiskPolicy.BLOCKED,
                message=self._get_blocked_message(action_type),
            )
        
        # L4 强确认
        if risk_level == RiskLevel.L4:
            return GamePolicyResult(
                allowed=True,
                action_type=action_type,
                risk_level=risk_level,
                policy=RiskPolicy.STRONG_CONFIRM,
                message=f"游戏操作需要强确认：{action_type.value}",
                requires_confirmation=True,
            )
        
        # L0-L3
        policy = {
            RiskLevel.L0: RiskPolicy.AUTO_EXECUTE,
            RiskLevel.L1: RiskPolicy.AUTO_EXECUTE,
            RiskLevel.L2: RiskPolicy.RATE_LIMITED,
            RiskLevel.L3: RiskPolicy.CONFIRM_ONCE,
        }.get(risk_level, RiskPolicy.AUTO_EXECUTE)
        
        return GamePolicyResult(
            allowed=True,
            action_type=action_type,
            risk_level=risk_level,
            policy=policy,
            message=f"游戏操作允许：{action_type.value}",
            requires_confirmation=policy == RiskPolicy.CONFIRM_ONCE,
        )
    
    def _classify_game_action(self, action: str, context: Dict[str, Any]) -> GameActionType:
        """分类游戏动作"""
        action_lower = action.lower()
        
        # BLOCKED 关键词
        blocked_keywords = {
            "竞技代打": GameActionType.COMPETITIVE_AUTO_PLAY,
            "绕过反作弊": GameActionType.BYPASS_ANTI_CHEAT,
            "挂机刷": GameActionType.RESOURCE_FARMING,
            "账号交易": GameActionType.ACCOUNT_TRADING,
            "未授权支付": GameActionType.UNAUTHORIZED_PAYMENT,
        }
        for kw, at in blocked_keywords.items():
            if kw in action_lower:
                return at
        
        # L4 关键词
        l4_keywords = {
            "自动点击": GameActionType.AUTO_CLICK,
            "长时间": GameActionType.LONG_OPERATION,
            "资源": GameActionType.RESOURCE_OPERATION,
            "道具": GameActionType.ITEM_OPERATION,
            "抽卡": GameActionType.GACHA_OPERATION,
        }
        for kw, at in l4_keywords.items():
            if kw in action_lower:
                return at
        
        # L0-L2 关键词
        low_risk_keywords = {
            "视觉": GameActionType.VISUAL_ASSIST,
            "策略": GameActionType.STRATEGY_SUGGESTION,
            "练习": GameActionType.PRACTICE_MODE,
            "单机": GameActionType.SINGLE_PLAYER,
            "复盘": GameActionType.REPLAY_ANALYSIS,
            "页面": GameActionType.PAGE_UNDERSTANDING,
            "提醒": GameActionType.OPERATION_REMINDER,
        }
        for kw, at in low_risk_keywords.items():
            if kw in action_lower:
                return at
        
        # 默认 L2
        return GameActionType.SINGLE_PLAYER
    
    def _get_blocked_message(self, action_type: GameActionType) -> str:
        """获取 BLOCKED 消息"""
        messages = {
            GameActionType.COMPETITIVE_AUTO_PLAY: "联网竞技自动代打会破坏公平性，不能执行",
            GameActionType.BYPASS_ANTI_CHEAT: "绕过反作弊违反游戏规则，不能执行",
            GameActionType.RESOURCE_FARMING: "挂机刷资源违反游戏规则，不能执行",
            GameActionType.ACCOUNT_TRADING: "账号交易存在安全风险，不能执行",
            GameActionType.UNAUTHORIZED_PAYMENT: "未授权支付操作，不能执行",
        }
        return messages.get(action_type, "该游戏操作被禁止")
