"""Retry Policy - 重试策略"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import time


class RetryStrategy(Enum):
    """重试策略"""
    FIXED = "fixed"  # 固定间隔
    LINEAR = "linear"  # 线性递增
    EXPONENTIAL = "exponential"  # 指数递增


@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    retryable_errors: List[str] = field(default_factory=list)
    on_retry: Optional[Callable] = None


@dataclass
class RetryResult:
    """重试结果"""
    success: bool
    attempts: int
    total_delay_seconds: float
    last_error: Optional[str] = None
    result: Any = None


class RetryPolicy:
    """
    重试策略
    
    支持：
    - 固定间隔重试
    - 线性递增重试
    - 指数退避重试
    - 自定义重试条件
    """
    
    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
    
    def execute(
        self,
        action: Callable,
        *args,
        **kwargs
    ) -> RetryResult:
        """
        执行带重试的动作
        
        Args:
            action: 要执行的动作
            *args, **kwargs: 动作参数
        
        Returns:
            RetryResult
        """
        attempts = 0
        total_delay = 0.0
        last_error = None
        
        while attempts <= self.config.max_retries:
            try:
                result = action(*args, **kwargs)
                return RetryResult(
                    success=True,
                    attempts=attempts + 1,
                    total_delay_seconds=total_delay,
                    result=result
                )
            except Exception as e:
                last_error = str(e)
                attempts += 1
                
                # 检查是否可重试
                if not self._should_retry(e, attempts):
                    break
                
                # 计算延迟
                if attempts <= self.config.max_retries:
                    delay = self._calculate_delay(attempts)
                    total_delay += delay
                    
                    # 回调
                    if self.config.on_retry:
                        try:
                            self.config.on_retry(attempts, e, delay)
                        except:
                            pass
                    
                    time.sleep(delay)
        
        return RetryResult(
            success=False,
            attempts=attempts,
            total_delay_seconds=total_delay,
            last_error=last_error
        )
    
    def _should_retry(self, error: Exception, attempts: int) -> bool:
        """判断是否应该重试"""
        if attempts > self.config.max_retries:
            return False
        
        if not self.config.retryable_errors:
            return True
        
        error_str = str(error)
        error_type = type(error).__name__
        
        return (
            error_type in self.config.retryable_errors or
            any(e in error_str for e in self.config.retryable_errors)
        )
    
    def _calculate_delay(self, attempt: int) -> float:
        """计算延迟时间"""
        if self.config.strategy == RetryStrategy.FIXED:
            delay = self.config.base_delay_seconds
        
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.base_delay_seconds * attempt
        
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.base_delay_seconds * (2 ** (attempt - 1))
        
        else:
            delay = self.config.base_delay_seconds
        
        return min(delay, self.config.max_delay_seconds)
    
    def set_max_retries(self, max_retries: int):
        """设置最大重试次数"""
        self.config.max_retries = max_retries
    
    def set_strategy(self, strategy: RetryStrategy):
        """设置重试策略"""
        self.config.strategy = strategy
    
    def set_retryable_errors(self, errors: List[str]):
        """设置可重试的错误"""
        self.config.retryable_errors = errors


class RetryPolicyBuilder:
    """重试策略构建器"""
    
    def __init__(self):
        self._config = RetryConfig()
    
    def max_retries(self, count: int) -> "RetryPolicyBuilder":
        self._config.max_retries = count
        return self
    
    def fixed_delay(self, seconds: float) -> "RetryPolicyBuilder":
        self._config.strategy = RetryStrategy.FIXED
        self._config.base_delay_seconds = seconds
        return self
    
    def linear_backoff(self, base_seconds: float) -> "RetryPolicyBuilder":
        self._config.strategy = RetryStrategy.LINEAR
        self._config.base_delay_seconds = base_seconds
        return self
    
    def exponential_backoff(
        self,
        base_seconds: float,
        max_seconds: float = 60.0
    ) -> "RetryPolicyBuilder":
        self._config.strategy = RetryStrategy.EXPONENTIAL
        self._config.base_delay_seconds = base_seconds
        self._config.max_delay_seconds = max_seconds
        return self
    
    def retry_on(self, errors: List[str]) -> "RetryPolicyBuilder":
        self._config.retryable_errors = errors
        return self
    
    def on_retry(self, callback: Callable) -> "RetryPolicyBuilder":
        self._config.on_retry = callback
        return self
    
    def build(self) -> RetryPolicy:
        return RetryPolicy(self._config)
