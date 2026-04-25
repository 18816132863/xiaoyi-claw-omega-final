"""Fallback Policy - 回退策略"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum


class FallbackAction(Enum):
    """回退动作"""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ABORT = "abort"


@dataclass
class FallbackDecision:
    """回退决策"""
    action: FallbackAction
    reason: str
    retry_count: int = 0
    max_retries: int = 3
    fallback_skill_id: Optional[str] = None
    skip_allowed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class FallbackPolicy:
    """
    回退策略
    
    职责：
    - 决定 step 失败后的处理方式
    - 支持 retry / fallback / skip / abort
    """
    
    def __init__(self):
        # 默认最大重试次数
        self.default_max_retries = 3

        # 错误类型映射
        self.error_actions = {
            "timeout": FallbackAction.RETRY,
            "network_error": FallbackAction.RETRY,
            "exception": FallbackAction.RETRY,  # 默认异常重试
            "skill_not_found": FallbackAction.FALLBACK,
            "permission_denied": FallbackAction.ABORT,
            "budget_exceeded": FallbackAction.ABORT,
            "validation_error": FallbackAction.SKIP,
            "unknown": FallbackAction.RETRY,  # 未知错误也重试
        }
        
        # 技能回退映射
        self.fallback_map: Dict[str, str] = {}
        
        # 可跳过的步骤
        self.skippable_steps: List[str] = []
    
    def decide(
        self,
        step_id: str,
        error: str,
        error_type: str = None,
        retry_count: int = 0,
        context: Dict[str, Any] = None
    ) -> FallbackDecision:
        """
        决定回退动作
        
        Args:
            step_id: 步骤 ID
            error: 错误信息
            error_type: 错误类型
            retry_count: 当前重试次数
            context: 执行上下文
        
        Returns:
            FallbackDecision
        """
        context = context or {}
        error_type = error_type or self._infer_error_type(error)
        
        # 获取默认动作
        default_action = self.error_actions.get(error_type, FallbackAction.ABORT)
        
        # 检查重试次数
        if default_action == FallbackAction.RETRY:
            if retry_count >= self.default_max_retries:
                # 重试次数用完，尝试回退
                fallback_skill = self.fallback_map.get(step_id)
                if fallback_skill:
                    return FallbackDecision(
                        action=FallbackAction.FALLBACK,
                        reason=f"Max retries ({retry_count}) exceeded, using fallback",
                        retry_count=retry_count,
                        fallback_skill_id=fallback_skill
                    )
                
                # 没有回退，检查是否可跳过
                if step_id in self.skippable_steps:
                    return FallbackDecision(
                        action=FallbackAction.SKIP,
                        reason="Max retries exceeded, step is skippable",
                        retry_count=retry_count,
                        skip_allowed=True
                    )
                
                return FallbackDecision(
                    action=FallbackAction.ABORT,
                    reason=f"Max retries ({retry_count}) exceeded, no fallback available",
                    retry_count=retry_count
                )
            
            return FallbackDecision(
                action=FallbackAction.RETRY,
                reason=f"Retry {retry_count + 1}/{self.default_max_retries}",
                retry_count=retry_count,
                max_retries=self.default_max_retries
            )
        
        # 回退动作
        if default_action == FallbackAction.FALLBACK:
            fallback_skill = self.fallback_map.get(step_id)
            if fallback_skill:
                return FallbackDecision(
                    action=FallbackAction.FALLBACK,
                    reason=f"Using fallback for {step_id}",
                    fallback_skill_id=fallback_skill
                )
            
            # 没有回退，检查是否可跳过
            if step_id in self.skippable_steps:
                return FallbackDecision(
                    action=FallbackAction.SKIP,
                    reason="No fallback, step is skippable",
                    skip_allowed=True
                )
            
            return FallbackDecision(
                action=FallbackAction.ABORT,
                reason="No fallback available"
            )
        
        # 跳过动作
        if default_action == FallbackAction.SKIP:
            if step_id in self.skippable_steps:
                return FallbackDecision(
                    action=FallbackAction.SKIP,
                    reason="Step is skippable",
                    skip_allowed=True
                )
            return FallbackDecision(
                action=FallbackAction.ABORT,
                reason="Step is not skippable"
            )
        
        # 中止动作
        return FallbackDecision(
            action=FallbackAction.ABORT,
            reason=f"Error type {error_type} requires abort"
        )
    
    def _infer_error_type(self, error: str) -> str:
        """推断错误类型"""
        error_lower = error.lower()
        
        # 支持下划线格式
        if "skill_not_found" in error_lower:
            return "skill_not_found"
        if "skill_disabled" in error_lower:
            return "skill_disabled"
        if "skill_deprecated" in error_lower:
            return "skill_deprecated"
        if "budget_exceeded" in error_lower:
            return "budget_exceeded"
        if "permission_denied" in error_lower:
            return "permission_denied"
        
        # 支持空格格式
        if "timeout" in error_lower:
            return "timeout"
        if "network" in error_lower or "connection" in error_lower:
            return "network_error"
        if "not found" in error_lower:
            return "skill_not_found"
        if "permission" in error_lower or "denied" in error_lower:
            return "permission_denied"
        if "budget" in error_lower or "exceeded" in error_lower:
            return "budget_exceeded"
        if "validation" in error_lower or "invalid" in error_lower:
            return "validation_error"
        if "disabled" in error_lower:
            return "skill_disabled"
        if "deprecated" in error_lower:
            return "skill_deprecated"
        
        return "unknown"
    
    def set_fallback(self, step_id: str, fallback_skill_id: str):
        """设置回退技能"""
        self.fallback_map[step_id] = fallback_skill_id
    
    def set_skippable(self, step_id: str, skippable: bool = True):
        """设置可跳过"""
        if skippable:
            if step_id not in self.skippable_steps:
                self.skippable_steps.append(step_id)
        else:
            if step_id in self.skippable_steps:
                self.skippable_steps.remove(step_id)
    
    def set_max_retries(self, max_retries: int):
        """设置最大重试次数"""
        self.default_max_retries = max_retries
    
    def set_error_action(self, error_type: str, action: FallbackAction):
        """设置错误类型动作"""
        self.error_actions[error_type] = action
