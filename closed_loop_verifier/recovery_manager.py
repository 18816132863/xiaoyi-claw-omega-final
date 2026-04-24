"""恢复管理器"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class RecoveryStrategy(Enum):
    """恢复策略"""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ABORT = "abort"
    ASK_USER = "ask_user"


@dataclass
class RecoveryDecision:
    """恢复决策"""
    strategy: RecoveryStrategy
    reason: str
    max_retries: int = 1
    fallback_capability: Optional[str] = None
    user_message: Optional[str] = None


class RecoveryManager:
    """恢复管理器"""
    
    def decide(self, error: str, context: Dict[str, Any]) -> RecoveryDecision:
        """决定恢复策略"""
        error_lower = error.lower()
        
        # 网络错误 - 重试
        if "network" in error_lower or "timeout" in error_lower:
            return RecoveryDecision(
                strategy=RecoveryStrategy.RETRY,
                reason="网络错误，尝试重试",
                max_retries=3,
            )
        
        # 权限错误 - 询问用户
        if "permission" in error_lower or "auth" in error_lower:
            return RecoveryDecision(
                strategy=RecoveryStrategy.ASK_USER,
                reason="需要授权",
                user_message="该操作需要额外授权，是否继续？",
            )
        
        # 不支持 - 跳过或备用
        if "not supported" in error_lower or "not found" in error_lower:
            fallback = context.get("fallback_capability")
            if fallback:
                return RecoveryDecision(
                    strategy=RecoveryStrategy.FALLBACK,
                    reason="使用备用能力",
                    fallback_capability=fallback,
                )
            else:
                return RecoveryDecision(
                    strategy=RecoveryStrategy.SKIP,
                    reason="能力不可用，跳过",
                )
        
        # 严重错误 - 终止
        if "critical" in error_lower or "fatal" in error_lower:
            return RecoveryDecision(
                strategy=RecoveryStrategy.ABORT,
                reason="严重错误，终止执行",
            )
        
        # 默认 - 询问用户
        return RecoveryDecision(
            strategy=RecoveryStrategy.ASK_USER,
            reason="未知错误",
            user_message=f"执行出错: {error}，如何处理？",
        )
    
    def execute_recovery(self, decision: RecoveryDecision, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行恢复"""
        if decision.strategy == RecoveryStrategy.RETRY:
            return {"action": "retry", "max_retries": decision.max_retries}
        
        elif decision.strategy == RecoveryStrategy.FALLBACK:
            return {"action": "fallback", "capability": decision.fallback_capability}
        
        elif decision.strategy == RecoveryStrategy.SKIP:
            return {"action": "skip", "message": decision.reason}
        
        elif decision.strategy == RecoveryStrategy.ABORT:
            return {"action": "abort", "message": decision.reason}
        
        elif decision.strategy == RecoveryStrategy.ASK_USER:
            return {"action": "ask_user", "message": decision.user_message}
        
        return {"action": "unknown"}
