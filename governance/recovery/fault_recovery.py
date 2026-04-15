#!/usr/bin/env python3
"""
故障恢复模块 - V1.0.0

处理系统故障的检测和恢复。
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import traceback


class FaultType(Enum):
    """故障类型"""
    SKILL_FAILURE = "skill_failure"
    TOOL_FAILURE = "tool_failure"
    NETWORK_ERROR = "network_error"
    FILE_ERROR = "file_error"
    MEMORY_ERROR = "memory_error"
    TIMEOUT = "timeout"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    UNKNOWN = "unknown"


class FaultSeverity(Enum):
    """故障严重程度"""
    LOW = "low"          # 轻微，可忽略
    MEDIUM = "medium"    # 中等，需要处理
    HIGH = "high"        # 严重，需要立即处理
    CRITICAL = "critical"  # 致命，需要紧急处理


@dataclass
class Fault:
    """故障记录"""
    id: str
    type: FaultType
    severity: FaultSeverity
    message: str
    context: Dict[str, Any]
    stack_trace: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution: Optional[str] = None


@dataclass
class RecoveryStrategy:
    """恢复策略"""
    name: str
    fault_types: List[FaultType]
    handler: Callable
    priority: int = 0
    max_retries: int = 3
    backoff_seconds: float = 1.0


class FaultRecovery:
    """故障恢复管理器"""
    
    def __init__(self):
        self.faults: List[Fault] = []
        self.strategies: List[RecoveryStrategy] = []
        self.fault_counter = 0
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """注册默认恢复策略"""
        self.register_strategy(RecoveryStrategy(
            name="retry",
            fault_types=[FaultType.NETWORK_ERROR, FaultType.TIMEOUT],
            handler=self._retry_handler,
            priority=10,
            max_retries=3,
            backoff_seconds=2.0
        ))
        
        self.register_strategy(RecoveryStrategy(
            name="fallback",
            fault_types=[FaultType.SKILL_FAILURE, FaultType.TOOL_FAILURE],
            handler=self._fallback_handler,
            priority=5
        ))
        
        self.register_strategy(RecoveryStrategy(
            name="graceful_degradation",
            fault_types=[FaultType.RESOURCE_EXHAUSTED],
            handler=self._degradation_handler,
            priority=3
        ))
    
    def register_strategy(self, strategy: RecoveryStrategy):
        """注册恢复策略"""
        self.strategies.append(strategy)
        self.strategies.sort(key=lambda s: -s.priority)
    
    def report_fault(self,
                     fault_type: FaultType,
                     severity: FaultSeverity,
                     message: str,
                     context: Dict = None,
                     exception: Exception = None) -> Fault:
        """报告故障"""
        fault = Fault(
            id=f"fault_{self.fault_counter}",
            type=fault_type,
            severity=severity,
            message=message,
            context=context or {},
            stack_trace=traceback.format_exc() if exception else None
        )
        
        self.faults.append(fault)
        self.fault_counter += 1
        
        return fault
    
    def recover(self, fault: Fault, context: Dict = None) -> Dict[str, Any]:
        """尝试恢复"""
        result = {
            "fault_id": fault.id,
            "recovered": False,
            "strategy": None,
            "attempts": 0,
            "error": None
        }
        
        # 找到适用的策略
        applicable_strategies = [
            s for s in self.strategies
            if fault.type in s.fault_types
        ]
        
        if not applicable_strategies:
            result["error"] = "没有适用的恢复策略"
            return result
        
        # 尝试每个策略
        for strategy in applicable_strategies:
            result["strategy"] = strategy.name
            
            for attempt in range(strategy.max_retries):
                result["attempts"] += 1
                
                try:
                    recovery_result = strategy.handler(fault, context or {})
                    
                    if recovery_result.get("success"):
                        fault.resolved = True
                        fault.resolution = f"使用策略 {strategy.name} 恢复"
                        result["recovered"] = True
                        return result
                    
                except Exception as e:
                    result["error"] = str(e)
                
                # 等待后重试
                if attempt < strategy.max_retries - 1:
                    import time
                    time.sleep(strategy.backoff_seconds * (attempt + 1))
        
        return result
    
    def _retry_handler(self, fault: Fault, context: Dict) -> Dict:
        """重试处理器"""
        original_action = context.get("action")
        if not original_action:
            return {"success": False, "error": "没有可重试的操作"}
        
        try:
            if callable(original_action):
                result = original_action()
                return {"success": True, "result": result}
            return {"success": False, "error": "操作不可调用"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _fallback_handler(self, fault: Fault, context: Dict) -> Dict:
        """降级处理器"""
        fallback = context.get("fallback")
        if not fallback:
            return {"success": False, "error": "没有降级方案"}
        
        try:
            if callable(fallback):
                result = fallback()
                return {"success": True, "result": result, "fallback": True}
            return {"success": True, "result": fallback, "fallback": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _degradation_handler(self, fault: Fault, context: Dict) -> Dict:
        """优雅降级处理器"""
        # 减少资源使用
        return {
            "success": True,
            "result": "已启用降级模式",
            "degraded": True
        }
    
    def get_fault_statistics(self) -> Dict[str, Any]:
        """获取故障统计"""
        if not self.faults:
            return {"total": 0}
        
        by_type = {}
        by_severity = {}
        resolved = 0
        
        for fault in self.faults:
            by_type[fault.type.value] = by_type.get(fault.type.value, 0) + 1
            by_severity[fault.severity.value] = by_severity.get(fault.severity.value, 0) + 1
            if fault.resolved:
                resolved += 1
        
        return {
            "total": len(self.faults),
            "resolved": resolved,
            "unresolved": len(self.faults) - resolved,
            "by_type": by_type,
            "by_severity": by_severity,
            "resolution_rate": resolved / len(self.faults)
        }
    
    def get_unresolved_faults(self, severity: FaultSeverity = None) -> List[Fault]:
        """获取未解决的故障"""
        faults = [f for f in self.faults if not f.resolved]
        
        if severity:
            faults = [f for f in faults if f.severity == severity]
        
        # 按严重程度排序
        severity_order = {
            FaultSeverity.CRITICAL: 0,
            FaultSeverity.HIGH: 1,
            FaultSeverity.MEDIUM: 2,
            FaultSeverity.LOW: 3
        }
        faults.sort(key=lambda f: severity_order.get(f.severity, 99))
        
        return faults


# 全局故障恢复器
_fault_recovery: Optional[FaultRecovery] = None


def get_fault_recovery() -> FaultRecovery:
    """获取全局故障恢复器"""
    global _fault_recovery
    if _fault_recovery is None:
        _fault_recovery = FaultRecovery()
    return _fault_recovery
