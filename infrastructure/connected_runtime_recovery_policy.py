"""
Connected Runtime Recovery Policy - 连接运行时恢复策略

遇到联系人/日历/备忘录/位置 timeout，自动执行恢复策略：
1. retry - 重试
2. limited_scope_probe - 有限范围探测
3. cache_fallback - 缓存降级
4. pending_queue - 待处理队列
5. permission_diagnosis - 权限诊断
6. human_action_required - 人工干预（最后手段）

L0 成功率低于 80% 时自动调整：
normal_probe → fast_probe → limited_scope_probe → cache_fallback → permission_diagnosis
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import json
import asyncio


class RecoveryStrategy(Enum):
    """恢复策略"""
    RETRY = "retry"
    LIMITED_SCOPE_PROBE = "limited_scope_probe"
    CACHE_FALLBACK = "cache_fallback"
    PENDING_QUEUE = "pending_queue"
    PERMISSION_DIAGNOSIS = "permission_diagnosis"
    HUMAN_ACTION_REQUIRED = "human_action_required"


class ProbeMode(Enum):
    """探测模式"""
    NORMAL_PROBE = "normal_probe"
    FAST_PROBE = "fast_probe"
    LIMITED_SCOPE_PROBE = "limited_scope_probe"
    CACHE_FALLBACK = "cache_fallback"
    PERMISSION_DIAGNOSIS = "permission_diagnosis"


class FailureType(Enum):
    """失败类型"""
    CONTACT_SERVICE_TIMEOUT = "contact_service_timeout"
    CALENDAR_SERVICE_TIMEOUT = "calendar_service_timeout"
    NOTE_SERVICE_TIMEOUT = "note_service_timeout"
    LOCATION_SERVICE_TIMEOUT = "location_service_timeout"
    MESSAGE_SERVICE_TIMEOUT = "message_service_timeout"
    PERMISSION_REQUIRED = "permission_required"
    RUNTIME_BRIDGE_UNAVAILABLE = "runtime_bridge_unavailable"
    SESSION_DISCONNECTED = "session_disconnected"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class RecoveryStep:
    """恢复步骤"""
    strategy: RecoveryStrategy
    description: str
    max_attempts: int = 3
    timeout_seconds: float = 30.0
    backoff_multiplier: float = 1.5
    current_attempt: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None


@dataclass
class RecoveryPlan:
    """恢复计划"""
    failure_type: FailureType
    steps: List[RecoveryStep] = field(default_factory=list)
    current_step_index: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    completed: bool = False
    final_result: Optional[str] = None


@dataclass
class L0AutoAdjustment:
    """L0 自动调整"""
    current_mode: ProbeMode = ProbeMode.NORMAL_PROBE
    success_rate: float = 1.0
    adjustment_history: List[Dict[str, Any]] = field(default_factory=list)
    last_adjustment: Optional[datetime] = None
    
    def record_result(self, success: bool):
        """记录结果并计算成功率"""
        self.adjustment_history.append({
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "mode": self.current_mode.value
        })
        
        # 计算最近 10 次的成功率
        recent = self.adjustment_history[-10:]
        successes = sum(1 for r in recent if r["success"])
        self.success_rate = successes / len(recent) if recent else 1.0
    
    def should_downgrade(self) -> bool:
        """判断是否需要降级"""
        return self.success_rate < 0.8 and len(self.adjustment_history) >= 5
    
    def downgrade(self) -> Optional[ProbeMode]:
        """执行降级"""
        downgrade_order = [
            ProbeMode.NORMAL_PROBE,
            ProbeMode.FAST_PROBE,
            ProbeMode.LIMITED_SCOPE_PROBE,
            ProbeMode.CACHE_FALLBACK,
            ProbeMode.PERMISSION_DIAGNOSIS
        ]
        
        current_idx = downgrade_order.index(self.current_mode)
        if current_idx < len(downgrade_order) - 1:
            new_mode = downgrade_order[current_idx + 1]
            self.current_mode = new_mode
            self.last_adjustment = datetime.now()
            return new_mode
        
        return None


class ConnectedRuntimeRecoveryPolicy:
    """连接运行时恢复策略"""
    
    # 各失败类型对应的恢复策略序列
    RECOVERY_STRATEGIES = {
        FailureType.CONTACT_SERVICE_TIMEOUT: [
            RecoveryStrategy.RETRY,
            RecoveryStrategy.LIMITED_SCOPE_PROBE,
            RecoveryStrategy.CACHE_FALLBACK,
            RecoveryStrategy.PENDING_QUEUE,
            RecoveryStrategy.PERMISSION_DIAGNOSIS,
            RecoveryStrategy.HUMAN_ACTION_REQUIRED
        ],
        FailureType.CALENDAR_SERVICE_TIMEOUT: [
            RecoveryStrategy.RETRY,
            RecoveryStrategy.LIMITED_SCOPE_PROBE,
            RecoveryStrategy.CACHE_FALLBACK,
            RecoveryStrategy.PENDING_QUEUE,
            RecoveryStrategy.PERMISSION_DIAGNOSIS,
            RecoveryStrategy.HUMAN_ACTION_REQUIRED
        ],
        FailureType.NOTE_SERVICE_TIMEOUT: [
            RecoveryStrategy.RETRY,
            RecoveryStrategy.LIMITED_SCOPE_PROBE,
            RecoveryStrategy.CACHE_FALLBACK,
            RecoveryStrategy.PENDING_QUEUE,
            RecoveryStrategy.PERMISSION_DIAGNOSIS,
            RecoveryStrategy.HUMAN_ACTION_REQUIRED
        ],
        FailureType.LOCATION_SERVICE_TIMEOUT: [
            RecoveryStrategy.RETRY,
            RecoveryStrategy.LIMITED_SCOPE_PROBE,
            RecoveryStrategy.CACHE_FALLBACK,
            RecoveryStrategy.PENDING_QUEUE,
            RecoveryStrategy.PERMISSION_DIAGNOSIS,
            RecoveryStrategy.HUMAN_ACTION_REQUIRED
        ],
        FailureType.MESSAGE_SERVICE_TIMEOUT: [
            RecoveryStrategy.RETRY,
            RecoveryStrategy.LIMITED_SCOPE_PROBE,
            RecoveryStrategy.CACHE_FALLBACK,
            RecoveryStrategy.PENDING_QUEUE,
            RecoveryStrategy.HUMAN_ACTION_REQUIRED
        ],
        FailureType.PERMISSION_REQUIRED: [
            RecoveryStrategy.PERMISSION_DIAGNOSIS,
            RecoveryStrategy.HUMAN_ACTION_REQUIRED
        ],
        FailureType.RUNTIME_BRIDGE_UNAVAILABLE: [
            RecoveryStrategy.RETRY,
            RecoveryStrategy.LIMITED_SCOPE_PROBE,
            RecoveryStrategy.HUMAN_ACTION_REQUIRED
        ],
        FailureType.SESSION_DISCONNECTED: [
            RecoveryStrategy.RETRY,
            RecoveryStrategy.HUMAN_ACTION_REQUIRED
        ],
        FailureType.UNKNOWN_ERROR: [
            RecoveryStrategy.RETRY,
            RecoveryStrategy.PERMISSION_DIAGNOSIS,
            RecoveryStrategy.HUMAN_ACTION_REQUIRED
        ]
    }
    
    def __init__(self):
        self.l0_adjustment = L0AutoAdjustment()
        self.active_plans: Dict[str, RecoveryPlan] = {}
        self.recovery_history: List[Dict[str, Any]] = []
    
    def classify_failure(self, error_message: str, capability_name: str = None) -> FailureType:
        """分类失败类型"""
        error_lower = error_message.lower()
        
        if "timeout" in error_lower:
            if capability_name:
                if "contact" in capability_name.lower():
                    return FailureType.CONTACT_SERVICE_TIMEOUT
                elif "calendar" in capability_name.lower():
                    return FailureType.CALENDAR_SERVICE_TIMEOUT
                elif "note" in capability_name.lower():
                    return FailureType.NOTE_SERVICE_TIMEOUT
                elif "location" in capability_name.lower():
                    return FailureType.LOCATION_SERVICE_TIMEOUT
                elif "message" in capability_name.lower():
                    return FailureType.MESSAGE_SERVICE_TIMEOUT
            return FailureType.UNKNOWN_ERROR
        
        if "permission" in error_lower or "denied" in error_lower:
            return FailureType.PERMISSION_REQUIRED
        
        if "bridge" in error_lower or "adapter" in error_lower:
            return FailureType.RUNTIME_BRIDGE_UNAVAILABLE
        
        if "session" in error_lower or "disconnected" in error_lower:
            return FailureType.SESSION_DISCONNECTED
        
        return FailureType.UNKNOWN_ERROR
    
    def create_recovery_plan(self, failure_type: FailureType) -> RecoveryPlan:
        """创建恢复计划"""
        strategies = self.RECOVERY_STRATEGIES.get(failure_type, [RecoveryStrategy.HUMAN_ACTION_REQUIRED])
        
        steps = []
        for i, strategy in enumerate(strategies):
            step = RecoveryStep(
                strategy=strategy,
                description=self._get_strategy_description(strategy),
                max_attempts=3 if strategy == RecoveryStrategy.RETRY else 1,
                timeout_seconds=self._get_strategy_timeout(strategy),
                backoff_multiplier=1.5 if strategy == RecoveryStrategy.RETRY else 1.0
            )
            steps.append(step)
        
        plan = RecoveryPlan(failure_type=failure_type, steps=steps)
        return plan
    
    def _get_strategy_description(self, strategy: RecoveryStrategy) -> str:
        """获取策略描述"""
        descriptions = {
            RecoveryStrategy.RETRY: "重试操作，使用指数退避",
            RecoveryStrategy.LIMITED_SCOPE_PROBE: "有限范围探测，减少请求量",
            RecoveryStrategy.CACHE_FALLBACK: "使用缓存数据降级",
            RecoveryStrategy.PENDING_QUEUE: "加入待处理队列，稍后重试",
            RecoveryStrategy.PERMISSION_DIAGNOSIS: "诊断权限问题",
            RecoveryStrategy.HUMAN_ACTION_REQUIRED: "需要人工干预"
        }
        return descriptions.get(strategy, "未知策略")
    
    def _get_strategy_timeout(self, strategy: RecoveryStrategy) -> float:
        """获取策略超时时间"""
        timeouts = {
            RecoveryStrategy.RETRY: 30.0,
            RecoveryStrategy.LIMITED_SCOPE_PROBE: 20.0,
            RecoveryStrategy.CACHE_FALLBACK: 5.0,
            RecoveryStrategy.PENDING_QUEUE: 10.0,
            RecoveryStrategy.PERMISSION_DIAGNOSIS: 15.0,
            RecoveryStrategy.HUMAN_ACTION_REQUIRED: 0.0  # 无超时，等待人工
        }
        return timeouts.get(strategy, 30.0)
    
    async def execute_recovery(self, plan: RecoveryPlan, executor: Callable = None) -> bool:
        """执行恢复计划"""
        for i, step in enumerate(plan.steps):
            plan.current_step_index = i
            step.started_at = datetime.now()
            step.current_attempt = 0
            
            for attempt in range(step.max_attempts):
                step.current_attempt = attempt + 1
                
                try:
                    # 执行恢复策略
                    if executor:
                        result = await asyncio.wait_for(
                            executor(step.strategy, plan.failure_type),
                            timeout=step.timeout_seconds
                        )
                    else:
                        result = await self._execute_strategy(step.strategy, plan.failure_type)
                    
                    if result:
                        step.success = True
                        step.completed_at = datetime.now()
                        plan.completed = True
                        plan.final_result = f"recovered_via_{step.strategy.value}"
                        
                        # 记录成功
                        self.l0_adjustment.record_result(True)
                        self._record_recovery(plan, step, True)
                        return True
                
                except asyncio.TimeoutError:
                    step.error_message = f"timeout after {step.timeout_seconds}s"
                except Exception as e:
                    step.error_message = str(e)
                
                # 指数退避
                if attempt < step.max_attempts - 1:
                    await asyncio.sleep(step.timeout_seconds * (step.backoff_multiplier ** attempt))
            
            step.success = False
            step.completed_at = datetime.now()
        
        # 所有策略都失败
        plan.completed = True
        plan.final_result = "recovery_failed"
        
        # 记录失败
        self.l0_adjustment.record_result(False)
        self._record_recovery(plan, plan.steps[-1], False)
        return False
    
    async def _execute_strategy(self, strategy: RecoveryStrategy, failure_type: FailureType) -> bool:
        """执行单个恢复策略（默认实现）"""
        # 这里是默认实现，实际应该由调用方提供 executor
        if strategy == RecoveryStrategy.RETRY:
            # 重试逻辑
            return False  # 默认返回 False，需要实际执行
        
        if strategy == RecoveryStrategy.LIMITED_SCOPE_PROBE:
            # 有限范围探测
            return False
        
        if strategy == RecoveryStrategy.CACHE_FALLBACK:
            # 缓存降级
            return False
        
        if strategy == RecoveryStrategy.PENDING_QUEUE:
            # 加入待处理队列
            return True  # 排队成功就算成功
        
        if strategy == RecoveryStrategy.PERMISSION_DIAGNOSIS:
            # 权限诊断
            return False
        
        if strategy == RecoveryStrategy.HUMAN_ACTION_REQUIRED:
            # 需要人工干预
            return False
        
        return False
    
    def _record_recovery(self, plan: RecoveryPlan, step: RecoveryStep, success: bool):
        """记录恢复历史"""
        self.recovery_history.append({
            "timestamp": datetime.now().isoformat(),
            "failure_type": plan.failure_type.value,
            "strategy": step.strategy.value,
            "attempt": step.current_attempt,
            "success": success,
            "duration_ms": (step.completed_at - step.started_at).total_seconds() * 1000 if step.completed_at and step.started_at else 0,
            "error_message": step.error_message
        })
    
    def check_and_adjust_probe_mode(self) -> Optional[ProbeMode]:
        """检查并调整探测模式"""
        if self.l0_adjustment.should_downgrade():
            new_mode = self.l0_adjustment.downgrade()
            if new_mode:
                return new_mode
        return None
    
    def get_current_probe_mode(self) -> ProbeMode:
        """获取当前探测模式"""
        return self.l0_adjustment.current_mode
    
    def get_success_rate(self) -> float:
        """获取当前成功率"""
        return self.l0_adjustment.success_rate


class TaskProgressTracker:
    """任务进度追踪器"""
    
    def __init__(self, task_id: str, timeout_seconds: float = 180.0):
        self.task_id = task_id
        self.timeout_seconds = timeout_seconds
        self.start_time = datetime.now()
        self.last_progress_time = datetime.now()
        self.progress_stages: List[Dict[str, Any]] = []
        self.current_stage: Optional[str] = None
    
    def update_progress(self, stage: str, details: str = ""):
        """更新进度"""
        now = datetime.now()
        self.current_stage = stage
        self.last_progress_time = now
        
        self.progress_stages.append({
            "timestamp": now.isoformat(),
            "stage": stage,
            "details": details,
            "elapsed_seconds": (now - self.start_time).total_seconds()
        })
    
    def check_timeout(self) -> Dict[str, Any]:
        """检查超时状态"""
        now = datetime.now()
        elapsed = (now - self.start_time).total_seconds()
        since_last_progress = (now - self.last_progress_time).total_seconds()
        
        result = {
            "elapsed_seconds": elapsed,
            "since_last_progress_seconds": since_last_progress,
            "should_degrade": False,
            "should_stop_probe": False,
            "should_output_partial": False,
            "action": "continue"
        }
        
        # 超过 60 秒自动降级
        if since_last_progress > 60:
            result["should_degrade"] = True
            result["action"] = "degrade"
        
        # 超过 120 秒停止当前 probe
        if since_last_progress > 120:
            result["should_stop_probe"] = True
            result["action"] = "stop_probe"
        
        # 超过 180 秒输出部分结果
        if elapsed > self.timeout_seconds:
            result["should_output_partial"] = True
            result["action"] = "output_partial"
        
        return result
    
    def get_progress_report(self) -> str:
        """获取进度报告"""
        lines = []
        lines.append(f"Task: {self.task_id}")
        lines.append(f"Started: {self.start_time.isoformat()}")
        lines.append(f"Current Stage: {self.current_stage}")
        lines.append(f"Elapsed: {(datetime.now() - self.start_time).total_seconds():.1f}s")
        lines.append("")
        lines.append("Progress Stages:")
        for stage in self.progress_stages[-10:]:  # 最近 10 个阶段
            lines.append(f"  [{stage['elapsed_seconds']:.1f}s] {stage['stage']}: {stage['details']}")
        
        return "\n".join(lines)


def format_recovery_report(policy: ConnectedRuntimeRecoveryPolicy) -> str:
    """格式化恢复报告"""
    lines = []
    lines.append("=" * 60)
    lines.append("CONNECTED RUNTIME RECOVERY REPORT")
    lines.append("=" * 60)
    lines.append("")
    
    # L0 自动调整状态
    lines.append("[L0 Auto Adjustment]")
    lines.append(f"  current_mode: {policy.l0_adjustment.current_mode.value}")
    lines.append(f"  success_rate: {policy.l0_adjustment.success_rate:.1%}")
    if policy.l0_adjustment.last_adjustment:
        lines.append(f"  last_adjustment: {policy.l0_adjustment.last_adjustment.isoformat()}")
    lines.append("")
    
    # 恢复历史
    lines.append("[Recovery History]")
    recent = policy.recovery_history[-20:]  # 最近 20 条
    for record in recent:
        status = "✓" if record["success"] else "✗"
        lines.append(f"  {status} [{record['failure_type']}] {record['strategy']} (attempt {record['attempt']})")
        if record["error_message"]:
            lines.append(f"      Error: {record['error_message']}")
    lines.append("")
    
    # 统计
    lines.append("[Statistics]")
    total = len(policy.recovery_history)
    successes = sum(1 for r in policy.recovery_history if r["success"])
    lines.append(f"  total_recoveries: {total}")
    lines.append(f"  successful: {successes}")
    lines.append(f"  failed: {total - successes}")
    if total > 0:
        lines.append(f"  success_rate: {successes / total:.1%}")
    lines.append("")
    
    return "\n".join(lines)
