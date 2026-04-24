"""
Skill Abuse Guard - 技能滥用防护 V2.0.0

防止技能被滥用：
- 内存泄漏攻击
- DDoS 攻击
- 资源耗尽攻击
- 递归炸弹
- 无限循环
- 恶意调用链
- CPU 炸弹
- IO 炸弹
- 网络攻击
- 数据泄露

V2.0.0 新增：
- 多维度检测（CPU/IO/网络/数据）
- 自适应限流
- 智能熔断
- 攻击模式学习
- 实时告警
- 审计日志
"""

import time
import threading
import json
import os
import psutil
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
from pathlib import Path
import weakref


class AbuseType(Enum):
    """滥用类型"""
    # 原有
    MEMORY_LEAK = "memory_leak"
    DDOS = "ddos"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    RECURSION_BOMB = "recursion_bomb"
    INFINITE_LOOP = "infinite_loop"
    MALICIOUS_CHAIN = "malicious_chain"
    RAPID_FIRE = "rapid_fire"
    PAYLOAD_BOMB = "payload_bomb"
    # V2.0.0 新增
    CPU_BOMB = "cpu_bomb"                 # CPU 炸弹
    IO_BOMB = "io_bomb"                   # IO 炸弹
    NETWORK_ABUSE = "network_abuse"       # 网络滥用
    DATA_EXFILTRATION = "data_exfiltration"  # 数据泄露
    SUSPICIOUS_PATTERN = "suspicious_pattern"  # 可疑模式
    QUOTA_EXCEEDED = "quota_exceeded"     # 配额超限
    CONCURRENT_OVERFLOW = "concurrent_overflow"  # 并发溢出


class AbuseSeverity(Enum):
    """滥用严重程度"""
    INFO = "info"           # 信息，仅记录
    LOW = "low"             # 轻微，警告
    MEDIUM = "medium"       # 中等，限流
    HIGH = "high"           # 严重，暂停
    CRITICAL = "critical"   # 危急，封禁
    EMERGENCY = "emergency" # 紧急，全局熔断


class GuardAction(Enum):
    """守卫动作"""
    ALLOW = "allow"           # 允许
    WARN = "warn"             # 警告
    THROTTLE = "throttle"     # 限流
    DELAY = "delay"           # 延迟
    QUEUE = "queue"           # 排队
    REJECT = "reject"         # 拒绝
    BAN = "ban"               # 封禁
    CIRCUIT_OPEN = "circuit_open"  # 熔断


@dataclass
class AbuseDetection:
    """滥用检测结果"""
    abuse_type: AbuseType
    severity: AbuseSeverity
    skill_id: str
    evidence: Dict[str, Any]
    timestamp: datetime
    action_taken: GuardAction
    message: str
    recommended_action: str = ""


@dataclass
class SkillUsageRecord:
    """技能使用记录 V2.0"""
    skill_id: str
    
    # 调用统计
    call_count: int = 0
    error_count: int = 0
    success_count: int = 0
    
    # 时间统计
    total_duration_ms: float = 0.0
    max_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    avg_duration_ms: float = 0.0
    
    # 内存统计
    total_memory_mb: float = 0.0
    max_memory_mb: float = 0.0
    memory_samples: deque = field(default_factory=lambda: deque(maxlen=100))
    
    # CPU 统计
    total_cpu_time_ms: float = 0.0
    max_cpu_percent: float = 0.0
    cpu_samples: deque = field(default_factory=lambda: deque(maxlen=100))
    
    # IO 统计
    total_io_read_mb: float = 0.0
    total_io_write_mb: float = 0.0
    max_io_rate_mbps: float = 0.0
    
    # 网络统计
    total_network_sent_mb: float = 0.0
    total_network_recv_mb: float = 0.0
    
    # 载荷统计
    total_payload_in_kb: float = 0.0
    total_payload_out_kb: float = 0.0
    max_payload_kb: float = 0.0
    
    # 时间戳
    last_call_time: datetime = None
    first_call_time: datetime = None
    
    # 调用间隔
    call_intervals: deque = field(default_factory=lambda: deque(maxlen=100))
    
    # 错误模式
    error_types: Dict[str, int] = field(default_factory=dict)
    consecutive_errors: int = 0
    max_consecutive_errors: int = 0
    
    # 警告统计
    warning_count: int = 0
    ban_count: int = 0


@dataclass
class AbusePolicy:
    """滥用防护策略 V2.0"""
    # 调用频率限制
    max_calls_per_second: int = 10
    max_calls_per_minute: int = 100
    max_calls_per_hour: int = 1000
    max_calls_per_day: int = 10000
    
    # 并发限制
    max_concurrent_calls: int = 5
    max_concurrent_per_skill: int = 3
    
    # 执行时间限制
    max_execution_time_ms: int = 30000
    max_total_time_per_hour_ms: int = 300000
    
    # 内存限制
    max_memory_mb: int = 500
    max_memory_growth_rate: float = 0.5
    max_total_memory_per_hour_mb: int = 5000
    
    # CPU 限制
    max_cpu_percent: float = 80.0
    max_cpu_time_per_call_ms: int = 10000
    max_total_cpu_time_per_hour_ms: int = 300000
    
    # IO 限制
    max_io_read_mb: int = 1000
    max_io_write_mb: int = 500
    max_io_rate_mbps: float = 100.0
    
    # 网络限制
    max_network_sent_mb: int = 500
    max_network_recv_mb: int = 1000
    
    # 递归深度限制
    max_recursion_depth: int = 10
    max_call_chain_length: int = 20
    
    # 载荷大小限制
    max_payload_in_kb: int = 1024
    max_payload_out_kb: int = 2048
    max_total_payload_per_minute_kb: int = 10240
    
    # 错误率限制
    max_error_rate: float = 0.5
    max_consecutive_errors: int = 5
    
    # 配额限制
    max_total_calls_per_day: int = 50000
    max_total_memory_per_day_mb: int = 50000
    
    # 自适应限流
    adaptive_throttle_enabled: bool = True
    throttle_recovery_rate: float = 0.1  # 每秒恢复10%
    
    # 熔断配置
    circuit_breaker_enabled: bool = True
    circuit_failure_threshold: int = 10
    circuit_recovery_timeout_ms: int = 60000
    circuit_half_open_requests: int = 3


@dataclass
class CircuitBreakerState:
    """熔断器状态"""
    skill_id: str
    state: str = "closed"  # closed, open, half_open
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: datetime = None
    last_state_change: datetime = None
    open_until: datetime = None


@dataclass
class ThrottleState:
    """限流状态"""
    skill_id: str
    current_rate: float = 1.0  # 0.0 - 1.0
    tokens: float = 100.0
    last_refill: datetime = None
    is_throttled: bool = False


class SkillAbuseGuard:
    """
    技能滥用防护守卫 V2.0.0
    
    职责：
    - 多维度检测（CPU/内存/IO/网络/数据）
    - 自适应限流
    - 智能熔断
    - 攻击模式学习
    - 实时告警
    - 审计日志
    """
    
    def __init__(
        self,
        policy: AbusePolicy = None,
        audit_log_path: str = "reports/audit/abuse_audit.jsonl"
    ):
        self.policy = policy or AbusePolicy()
        self.audit_log_path = audit_log_path
        
        # 技能使用记录
        self._usage_records: Dict[str, SkillUsageRecord] = {}
        
        # 调用链追踪
        self._call_chains: Dict[str, List[str]] = {}
        
        # 当前执行中的技能
        self._active_executions: Dict[str, Dict] = {}
        
        # 封禁列表
        self._banned_skills: Dict[str, datetime] = {}
        
        # 熔断器状态
        self._circuit_breakers: Dict[str, CircuitBreakerState] = {}
        
        # 限流状态
        self._throttle_states: Dict[str, ThrottleState] = {}
        
        # 警告计数
        self._warning_counts: Dict[str, int] = defaultdict(int)
        
        # 检测器注册
        self._detectors: List[Callable] = []
        
        # 告警回调
        self._alert_callbacks: List[Callable] = []
        
        # 锁
        self._lock = threading.RLock()
        
        # 系统资源监控
        self._system_monitor = SystemResourceMonitor()
        
        # 攻击模式学习
        self._attack_patterns: Dict[str, int] = defaultdict(int)
        
        # 注册内置检测器
        self._register_builtin_detectors()
        
        # 启动后台清理
        self._start_cleanup_thread()
    
    def _register_builtin_detectors(self):
        """注册内置检测器"""
        self._detectors = [
            # 频率检测
            self._detect_rapid_fire,
            self._detect_rate_limit_violation,
            self._detect_concurrent_overflow,
            
            # 资源检测
            self._detect_memory_leak,
            self._detect_cpu_bomb,
            self._detect_io_bomb,
            self._detect_resource_exhaustion,
            
            # 执行检测
            self._detect_infinite_loop,
            self._detect_recursion_bomb,
            self._detect_malicious_chain,
            
            # 数据检测
            self._detect_payload_bomb,
            self._detect_data_exfiltration,
            self._detect_network_abuse,
            
            # 错误检测
            self._detect_high_error_rate,
            self._detect_error_pattern,
            
            # 配额检测
            self._detect_quota_exceeded,
            
            # 模式检测
            self._detect_suspicious_pattern,
        ]
    
    # ==================== 调用前检查 ====================
    
    def check_before_call(
        self,
        skill_id: str,
        payload_size: int = 0,
        call_chain: List[str] = None,
        context: Dict[str, Any] = None
    ) -> Tuple[bool, Optional[AbuseDetection]]:
        """
        调用前检查 V2.0
        
        Args:
            skill_id: 技能ID
            payload_size: 载荷大小（字节）
            call_chain: 调用链
            context: 执行上下文
        
        Returns:
            Tuple of (allowed, detection)
        """
        with self._lock:
            context = context or {}
            now = datetime.now()
            
            # 1. 检查是否被封禁
            if skill_id in self._banned_skills:
                ban_time = self._banned_skills[skill_id]
                if now < ban_time:
                    return False, AbuseDetection(
                        abuse_type=AbuseType.DDOS,
                        severity=AbuseSeverity.CRITICAL,
                        skill_id=skill_id,
                        evidence={"ban_until": ban_time.isoformat()},
                        timestamp=now,
                        action_taken=GuardAction.BAN,
                        message=f"Skill {skill_id} is banned until {ban_time}",
                        recommended_action="Wait for ban to expire or contact admin"
                    )
                else:
                    del self._banned_skills[skill_id]
            
            # 2. 检查熔断器
            circuit = self._get_or_create_circuit_breaker(skill_id)
            if circuit.state == "open":
                if now < circuit.open_until:
                    return False, AbuseDetection(
                        abuse_type=AbuseType.RESOURCE_EXHAUSTION,
                        severity=AbuseSeverity.HIGH,
                        skill_id=skill_id,
                        evidence={
                            "circuit_state": "open",
                            "open_until": circuit.open_until.isoformat()
                        },
                        timestamp=now,
                        action_taken=GuardAction.CIRCUIT_OPEN,
                        message=f"Circuit breaker open for {skill_id}",
                        recommended_action="Wait for circuit to close"
                    )
                else:
                    # 进入半开状态
                    circuit.state = "half_open"
                    circuit.last_state_change = now
            
            # 3. 检查限流
            throttle = self._get_or_create_throttle(skill_id)
            if not self._check_throttle(throttle):
                return False, AbuseDetection(
                    abuse_type=AbuseType.RATE_LIMIT_VIOLATION,
                    severity=AbuseSeverity.MEDIUM,
                    skill_id=skill_id,
                    evidence={
                        "current_rate": throttle.current_rate,
                        "tokens": throttle.tokens
                    },
                    timestamp=now,
                    action_taken=GuardAction.THROTTLE,
                    message=f"Skill {skill_id} is throttled",
                    recommended_action="Reduce call frequency"
                )
            
            # 4. 检查并发
            active_count = len([e for e in self._active_executions.values() 
                               if e.get("skill_id") == skill_id])
            if active_count >= self.policy.max_concurrent_per_skill:
                return False, AbuseDetection(
                    abuse_type=AbuseType.CONCURRENT_OVERFLOW,
                    severity=AbuseSeverity.MEDIUM,
                    skill_id=skill_id,
                    evidence={
                        "active_count": active_count,
                        "limit": self.policy.max_concurrent_per_skill
                    },
                    timestamp=now,
                    action_taken=GuardAction.QUEUE,
                    message=f"Too many concurrent calls for {skill_id}",
                    recommended_action="Wait for existing calls to complete"
                )
            
            # 5. 检查全局并发
            total_active = len(self._active_executions)
            if total_active >= self.policy.max_concurrent_calls:
                return False, AbuseDetection(
                    abuse_type=AbuseType.CONCURRENT_OVERFLOW,
                    severity=AbuseSeverity.HIGH,
                    skill_id=skill_id,
                    evidence={
                        "total_active": total_active,
                        "limit": self.policy.max_concurrent_calls
                    },
                    timestamp=now,
                    action_taken=GuardAction.QUEUE,
                    message="System at max concurrent capacity",
                    recommended_action="Wait for system load to decrease"
                )
            
            # 6. 检查载荷大小
            if payload_size > self.policy.max_payload_in_kb * 1024:
                return False, AbuseDetection(
                    abuse_type=AbuseType.PAYLOAD_BOMB,
                    severity=AbuseSeverity.HIGH,
                    skill_id=skill_id,
                    evidence={"payload_size_kb": payload_size / 1024},
                    timestamp=now,
                    action_taken=GuardAction.REJECT,
                    message=f"Payload size exceeds limit: {payload_size / 1024:.1f}KB",
                    recommended_action="Reduce payload size"
                )
            
            # 7. 检查调用链深度
            if call_chain and len(call_chain) > self.policy.max_call_chain_length:
                return False, AbuseDetection(
                    abuse_type=AbuseType.MALICIOUS_CHAIN,
                    severity=AbuseSeverity.HIGH,
                    skill_id=skill_id,
                    evidence={"chain_length": len(call_chain)},
                    timestamp=now,
                    action_taken=GuardAction.REJECT,
                    message=f"Call chain too long: {len(call_chain)}",
                    recommended_action="Simplify call chain"
                )
            
            # 8. 检查递归
            if call_chain:
                recursion_count = call_chain.count(skill_id)
                if recursion_count >= self.policy.max_recursion_depth:
                    return False, AbuseDetection(
                        abuse_type=AbuseType.RECURSION_BOMB,
                        severity=AbuseSeverity.CRITICAL,
                        skill_id=skill_id,
                        evidence={"recursion_depth": recursion_count},
                        timestamp=now,
                        action_taken=GuardAction.REJECT,
                        message=f"Recursion depth exceeded: {recursion_count}",
                        recommended_action="Avoid recursive skill calls"
                    )
            
            # 9. 检查系统资源
            system_status = self._system_monitor.get_status()
            if system_status["cpu_percent"] > self.policy.max_cpu_percent * 1.5:
                return False, AbuseDetection(
                    abuse_type=AbuseType.CPU_BOMB,
                    severity=AbuseSeverity.EMERGENCY,
                    skill_id=skill_id,
                    evidence=system_status,
                    timestamp=now,
                    action_taken=GuardAction.REJECT,
                    message="System CPU overloaded",
                    recommended_action="Wait for system to recover"
                )
            
            if system_status["memory_percent"] > 90:
                return False, AbuseDetection(
                    abuse_type=AbuseType.MEMORY_LEAK,
                    severity=AbuseSeverity.EMERGENCY,
                    skill_id=skill_id,
                    evidence=system_status,
                    timestamp=now,
                    action_taken=GuardAction.REJECT,
                    message="System memory critical",
                    recommended_action="Wait for system to recover"
                )
            
            # 消耗令牌
            self._consume_token(throttle)
            
            return True, None
    
    # ==================== 调用记录 ====================
    
    def record_call_start(
        self,
        skill_id: str,
        context: Dict[str, Any] = None
    ) -> str:
        """
        记录调用开始
        
        Returns:
            execution_id
        """
        with self._lock:
            execution_id = f"{skill_id}_{time.time_ns()}"
            now = datetime.now()
            
            # 记录活跃执行
            self._active_executions[execution_id] = {
                "skill_id": skill_id,
                "start_time": now,
                "context": context or {}
            }
            
            # 更新使用记录
            record = self._get_or_create_record(skill_id)
            record.call_count += 1
            if record.first_call_time is None:
                record.first_call_time = now
            record.last_call_time = now
            
            return execution_id
    
    def record_call_end(
        self,
        skill_id: str,
        execution_id: str,
        duration_ms: float,
        memory_mb: float = 0,
        cpu_percent: float = 0,
        io_read_mb: float = 0,
        io_write_mb: float = 0,
        network_sent_mb: float = 0,
        network_recv_mb: float = 0,
        payload_in_kb: float = 0,
        payload_out_kb: float = 0,
        success: bool = True,
        error: str = None
    ) -> Optional[AbuseDetection]:
        """
        记录调用结束 V2.0
        
        Returns:
            AbuseDetection if abuse detected
        """
        with self._lock:
            now = datetime.now()
            
            # 移除活跃执行
            execution = self._active_executions.pop(execution_id, None)
            
            record = self._get_or_create_record(skill_id)
            
            # 更新基础统计
            if success:
                record.success_count += 1
                record.consecutive_errors = 0
            else:
                record.error_count += 1
                record.consecutive_errors += 1
                record.max_consecutive_errors = max(
                    record.max_consecutive_errors,
                    record.consecutive_errors
                )
                if error:
                    record.error_types[error] = record.error_types.get(error, 0) + 1
            
            # 更新时间统计
            record.total_duration_ms += duration_ms
            record.max_duration_ms = max(record.max_duration_ms, duration_ms)
            record.min_duration_ms = min(record.min_duration_ms, duration_ms)
            record.avg_duration_ms = record.total_duration_ms / record.call_count
            
            # 更新内存统计
            record.total_memory_mb += memory_mb
            record.max_memory_mb = max(record.max_memory_mb, memory_mb)
            record.memory_samples.append(memory_mb)
            
            # 更新CPU统计
            cpu_time_ms = duration_ms * (cpu_percent / 100)
            record.total_cpu_time_ms += cpu_time_ms
            record.max_cpu_percent = max(record.max_cpu_percent, cpu_percent)
            record.cpu_samples.append(cpu_percent)
            
            # 更新IO统计
            record.total_io_read_mb += io_read_mb
            record.total_io_write_mb += io_write_mb
            io_rate = (io_read_mb + io_write_mb) / max(duration_ms / 1000, 0.001)
            record.max_io_rate_mbps = max(record.max_io_rate_mbps, io_rate)
            
            # 更新网络统计
            record.total_network_sent_mb += network_sent_mb
            record.total_network_recv_mb += network_recv_mb
            
            # 更新载荷统计
            record.total_payload_in_kb += payload_in_kb
            record.total_payload_out_kb += payload_out_kb
            record.max_payload_kb = max(record.max_payload_kb, payload_in_kb, payload_out_kb)
            
            # 更新熔断器
            circuit = self._get_or_create_circuit_breaker(skill_id)
            if success:
                circuit.success_count += 1
                circuit.failure_count = max(0, circuit.failure_count - 1)
                
                # 半开状态下成功，关闭熔断器
                if circuit.state == "half_open":
                    if circuit.success_count >= self.policy.circuit_half_open_requests:
                        circuit.state = "closed"
                        circuit.last_state_change = now
                        circuit.failure_count = 0
            else:
                circuit.failure_count += 1
                circuit.last_failure_time = now
                
                # 检查是否需要打开熔断器
                if circuit.failure_count >= self.policy.circuit_failure_threshold:
                    circuit.state = "open"
                    circuit.last_state_change = now
                    circuit.open_until = now + timedelta(
                        milliseconds=self.policy.circuit_recovery_timeout_ms
                    )
            
            # 运行检测器
            for detector in self._detectors:
                detection = detector(skill_id, record, execution)
                if detection:
                    self._handle_detection(detection)
                    self._log_audit(detection)
                    self._send_alert(detection)
                    return detection
            
            return None
    
    # ==================== 检测器 ====================
    
    def _detect_rapid_fire(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测快速连发"""
        if len(record.call_intervals) < 10:
            return None
        
        recent = list(record.call_intervals)[-10:]
        avg_interval = sum(recent) / len(recent)
        
        if avg_interval < 0.05:
            return AbuseDetection(
                abuse_type=AbuseType.RAPID_FIRE,
                severity=AbuseSeverity.HIGH,
                skill_id=skill_id,
                evidence={
                    "avg_interval_ms": avg_interval * 1000,
                    "recent_calls": len(recent)
                },
                timestamp=datetime.now(),
                action_taken=GuardAction.THROTTLE,
                message=f"Rapid fire detected: avg interval {avg_interval*1000:.1f}ms",
                recommended_action="Reduce call frequency"
            )
        return None
    
    def _detect_rate_limit_violation(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测速率限制违规"""
        now = datetime.now()
        
        # 检查每分钟限制
        if record.first_call_time:
            elapsed_minutes = (now - record.first_call_time).total_seconds() / 60
            if elapsed_minutes > 0:
                calls_per_minute = record.call_count / elapsed_minutes
                if calls_per_minute > self.policy.max_calls_per_minute:
                    return AbuseDetection(
                        abuse_type=AbuseType.DDOS,
                        severity=AbuseSeverity.MEDIUM,
                        skill_id=skill_id,
                        evidence={
                            "calls_per_minute": calls_per_minute,
                            "limit": self.policy.max_calls_per_minute
                        },
                        timestamp=now,
                        action_taken=GuardAction.THROTTLE,
                        message=f"Rate limit exceeded: {calls_per_minute:.1f} calls/min",
                        recommended_action="Reduce call frequency"
                    )
        return None
    
    def _detect_concurrent_overflow(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测并发溢出"""
        active = len([e for e in self._active_executions.values() 
                     if e.get("skill_id") == skill_id])
        if active > self.policy.max_concurrent_per_skill:
            return AbuseDetection(
                abuse_type=AbuseType.CONCURRENT_OVERFLOW,
                severity=AbuseSeverity.MEDIUM,
                skill_id=skill_id,
                evidence={"active": active},
                timestamp=datetime.now(),
                action_taken=GuardAction.QUEUE,
                message=f"Concurrent overflow: {active} active calls",
                recommended_action="Wait for existing calls to complete"
            )
        return None
    
    def _detect_memory_leak(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测内存泄漏"""
        if record.call_count < 5:
            return None
        
        # 检查内存增长趋势
        if len(record.memory_samples) >= 10:
            recent = list(record.memory_samples)[-10:]
            if all(recent[i] < recent[i+1] for i in range(len(recent)-1)):
                # 持续增长
                growth_rate = (recent[-1] - recent[0]) / max(recent[0], 0.1)
                if growth_rate > self.policy.max_memory_growth_rate:
                    return AbuseDetection(
                        abuse_type=AbuseType.MEMORY_LEAK,
                        severity=AbuseSeverity.HIGH,
                        skill_id=skill_id,
                        evidence={
                            "growth_rate": growth_rate,
                            "recent_samples": recent
                        },
                        timestamp=datetime.now(),
                        action_taken=GuardAction.WARN,
                        message=f"Memory leak suspected: {growth_rate*100:.1f}% growth",
                        recommended_action="Check for memory leaks in skill"
                    )
        
        if record.total_memory_mb > self.policy.max_total_memory_per_hour_mb:
            return AbuseDetection(
                abuse_type=AbuseType.MEMORY_LEAK,
                severity=AbuseSeverity.HIGH,
                skill_id=skill_id,
                evidence={"total_memory_mb": record.total_memory_mb},
                timestamp=datetime.now(),
                action_taken=GuardAction.THROTTLE,
                message=f"Total memory exceeds limit: {record.total_memory_mb:.1f}MB",
                recommended_action="Reduce memory usage"
            )
        return None
    
    def _detect_cpu_bomb(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测CPU炸弹"""
        if record.max_cpu_percent > self.policy.max_cpu_percent:
            return AbuseDetection(
                abuse_type=AbuseType.CPU_BOMB,
                severity=AbuseSeverity.HIGH,
                skill_id=skill_id,
                evidence={
                    "max_cpu_percent": record.max_cpu_percent,
                    "limit": self.policy.max_cpu_percent
                },
                timestamp=datetime.now(),
                action_taken=GuardAction.THROTTLE,
                message=f"CPU usage exceeds limit: {record.max_cpu_percent:.1f}%",
                recommended_action="Optimize CPU-intensive operations"
            )
        
        if record.total_cpu_time_ms > self.policy.max_total_cpu_time_per_hour_ms:
            return AbuseDetection(
                abuse_type=AbuseType.CPU_BOMB,
                severity=AbuseSeverity.MEDIUM,
                skill_id=skill_id,
                evidence={"total_cpu_time_ms": record.total_cpu_time_ms},
                timestamp=datetime.now(),
                action_taken=GuardAction.THROTTLE,
                message="Total CPU time exceeds limit",
                recommended_action="Reduce CPU-intensive operations"
            )
        return None
    
    def _detect_io_bomb(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测IO炸弹"""
        if record.max_io_rate_mbps > self.policy.max_io_rate_mbps:
            return AbuseDetection(
                abuse_type=AbuseType.IO_BOMB,
                severity=AbuseSeverity.MEDIUM,
                skill_id=skill_id,
                evidence={
                    "max_io_rate_mbps": record.max_io_rate_mbps,
                    "limit": self.policy.max_io_rate_mbps
                },
                timestamp=datetime.now(),
                action_taken=GuardAction.THROTTLE,
                message=f"IO rate exceeds limit: {record.max_io_rate_mbps:.1f}MB/s",
                recommended_action="Reduce IO operations"
            )
        
        if record.total_io_read_mb > self.policy.max_io_read_mb:
            return AbuseDetection(
                abuse_type=AbuseType.IO_BOMB,
                severity=AbuseSeverity.MEDIUM,
                skill_id=skill_id,
                evidence={"total_io_read_mb": record.total_io_read_mb},
                timestamp=datetime.now(),
                action_taken=GuardAction.THROTTLE,
                message=f"Total IO read exceeds limit: {record.total_io_read_mb:.1f}MB",
                recommended_action="Reduce IO operations"
            )
        return None
    
    def _detect_resource_exhaustion(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测资源耗尽"""
        if record.total_duration_ms > self.policy.max_total_time_per_hour_ms:
            return AbuseDetection(
                abuse_type=AbuseType.RESOURCE_EXHAUSTION,
                severity=AbuseSeverity.MEDIUM,
                skill_id=skill_id,
                evidence={
                    "total_time_ms": record.total_duration_ms,
                    "limit_ms": self.policy.max_total_time_per_hour_ms
                },
                timestamp=datetime.now(),
                action_taken=GuardAction.THROTTLE,
                message="Total execution time exceeds limit",
                recommended_action="Reduce execution time"
            )
        return None
    
    def _detect_infinite_loop(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测无限循环"""
        if record.max_duration_ms > self.policy.max_execution_time_ms:
            return AbuseDetection(
                abuse_type=AbuseType.INFINITE_LOOP,
                severity=AbuseSeverity.HIGH,
                skill_id=skill_id,
                evidence={
                    "max_duration_ms": record.max_duration_ms,
                    "limit_ms": self.policy.max_execution_time_ms
                },
                timestamp=datetime.now(),
                action_taken=GuardAction.REJECT,
                message=f"Execution time exceeded: {record.max_duration_ms:.0f}ms",
                recommended_action="Optimize long-running operations"
            )
        return None
    
    def _detect_recursion_bomb(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测递归炸弹"""
        # 在 check_before_call 中处理
        return None
    
    def _detect_malicious_chain(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测恶意调用链"""
        # 在 check_before_call 中处理
        return None
    
    def _detect_payload_bomb(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测载荷炸弹"""
        if record.total_payload_in_kb > self.policy.max_total_payload_per_minute_kb:
            return AbuseDetection(
                abuse_type=AbuseType.PAYLOAD_BOMB,
                severity=AbuseSeverity.MEDIUM,
                skill_id=skill_id,
                evidence={
                    "total_payload_kb": record.total_payload_in_kb,
                    "limit_kb": self.policy.max_total_payload_per_minute_kb
                },
                timestamp=datetime.now(),
                action_taken=GuardAction.THROTTLE,
                message=f"Total payload exceeds limit: {record.total_payload_in_kb:.1f}KB",
                recommended_action="Reduce payload size"
            )
        return None
    
    def _detect_data_exfiltration(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测数据泄露"""
        # 检查出站数据量
        if record.total_payload_out_kb > self.policy.max_payload_out_kb * 10:
            return AbuseDetection(
                abuse_type=AbuseType.DATA_EXFILTRATION,
                severity=AbuseSeverity.CRITICAL,
                skill_id=skill_id,
                evidence={
                    "total_out_kb": record.total_payload_out_kb,
                    "threshold_kb": self.policy.max_payload_out_kb * 10
                },
                timestamp=datetime.now(),
                action_taken=GuardAction.BAN,
                message=f"Potential data exfiltration: {record.total_payload_out_kb:.1f}KB sent",
                recommended_action="Review skill behavior immediately"
            )
        return None
    
    def _detect_network_abuse(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测网络滥用"""
        if record.total_network_sent_mb > self.policy.max_network_sent_mb:
            return AbuseDetection(
                abuse_type=AbuseType.NETWORK_ABUSE,
                severity=AbuseSeverity.MEDIUM,
                skill_id=skill_id,
                evidence={
                    "total_sent_mb": record.total_network_sent_mb,
                    "limit_mb": self.policy.max_network_sent_mb
                },
                timestamp=datetime.now(),
                action_taken=GuardAction.THROTTLE,
                message=f"Network sent exceeds limit: {record.total_network_sent_mb:.1f}MB",
                recommended_action="Reduce network operations"
            )
        return None
    
    def _detect_high_error_rate(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测高错误率"""
        if record.call_count < 5:
            return None
        
        error_rate = record.error_count / record.call_count
        
        if error_rate > self.policy.max_error_rate:
            return AbuseDetection(
                abuse_type=AbuseType.RESOURCE_EXHAUSTION,
                severity=AbuseSeverity.MEDIUM,
                skill_id=skill_id,
                evidence={
                    "error_rate": error_rate,
                    "error_count": record.error_count,
                    "call_count": record.call_count
                },
                timestamp=datetime.now(),
                action_taken=GuardAction.WARN,
                message=f"High error rate: {error_rate*100:.1f}%",
                recommended_action="Investigate and fix errors"
            )
        return None
    
    def _detect_error_pattern(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测错误模式"""
        if record.consecutive_errors >= self.policy.max_consecutive_errors:
            return AbuseDetection(
                abuse_type=AbuseType.RESOURCE_EXHAUSTION,
                severity=AbuseSeverity.HIGH,
                skill_id=skill_id,
                evidence={
                    "consecutive_errors": record.consecutive_errors,
                    "error_types": record.error_types
                },
                timestamp=datetime.now(),
                action_taken=GuardAction.CIRCUIT_OPEN,
                message=f"Consecutive errors: {record.consecutive_errors}",
                recommended_action="Fix underlying issue before retrying"
            )
        return None
    
    def _detect_quota_exceeded(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测配额超限"""
        if record.call_count > self.policy.max_total_calls_per_day:
            return AbuseDetection(
                abuse_type=AbuseType.QUOTA_EXCEEDED,
                severity=AbuseSeverity.MEDIUM,
                skill_id=skill_id,
                evidence={
                    "total_calls": record.call_count,
                    "limit": self.policy.max_total_calls_per_day
                },
                timestamp=datetime.now(),
                action_taken=GuardAction.REJECT,
                message=f"Daily call quota exceeded: {record.call_count}",
                recommended_action="Wait for quota reset"
            )
        return None
    
    def _detect_suspicious_pattern(
        self,
        skill_id: str,
        record: SkillUsageRecord,
        execution: Dict = None
    ) -> Optional[AbuseDetection]:
        """检测可疑模式"""
        # 检查是否有攻击模式特征
        patterns = []
        
        # 模式1: 高频调用 + 高错误率
        if (len(record.call_intervals) > 10 and 
            record.error_count / max(record.call_count, 1) > 0.3):
            patterns.append("high_freq_high_error")
        
        # 模式2: 持续增长内存 + 长时间执行
        if (len(record.memory_samples) > 5 and 
            record.max_duration_ms > 10000):
            patterns.append("memory_growth_long_exec")
        
        # 模式3: 大量出站数据
        if record.total_payload_out_kb > record.total_payload_in_kb * 5:
            patterns.append("excessive_outbound")
        
        if patterns:
            return AbuseDetection(
                abuse_type=AbuseType.SUSPICIOUS_PATTERN,
                severity=AbuseSeverity.MEDIUM,
                skill_id=skill_id,
                evidence={"patterns": patterns},
                timestamp=datetime.now(),
                action_taken=GuardAction.WARN,
                message=f"Suspicious patterns detected: {patterns}",
                recommended_action="Review skill behavior"
            )
        return None
    
    # ==================== 辅助方法 ====================
    
    def _get_or_create_record(self, skill_id: str) -> SkillUsageRecord:
        """获取或创建使用记录"""
        if skill_id not in self._usage_records:
            self._usage_records[skill_id] = SkillUsageRecord(skill_id=skill_id)
        return self._usage_records[skill_id]
    
    def _get_or_create_circuit_breaker(self, skill_id: str) -> CircuitBreakerState:
        """获取或创建熔断器"""
        if skill_id not in self._circuit_breakers:
            self._circuit_breakers[skill_id] = CircuitBreakerState(skill_id=skill_id)
        return self._circuit_breakers[skill_id]
    
    def _get_or_create_throttle(self, skill_id: str) -> ThrottleState:
        """获取或创建限流器"""
        if skill_id not in self._throttle_states:
            self._throttle_states[skill_id] = ThrottleState(skill_id=skill_id)
        return self._throttle_states[skill_id]
    
    def _check_throttle(self, throttle: ThrottleState) -> bool:
        """检查限流"""
        if not self.policy.adaptive_throttle_enabled:
            return True
        
        # 补充令牌
        now = datetime.now()
        if throttle.last_refill:
            elapsed = (now - throttle.last_refill).total_seconds()
            refill = elapsed * self.policy.throttle_recovery_rate * 100
            throttle.tokens = min(100, throttle.tokens + refill)
        
        throttle.last_refill = now
        
        return throttle.tokens > 0
    
    def _consume_token(self, throttle: ThrottleState):
        """消耗令牌"""
        throttle.tokens = max(0, throttle.tokens - 10)
        throttle.is_throttled = throttle.tokens < 50
    
    def _handle_detection(self, detection: AbuseDetection):
        """处理检测结果"""
        skill_id = detection.skill_id
        
        # 增加警告计数
        self._warning_counts[skill_id] += 1
        
        # 记录攻击模式
        pattern_key = f"{detection.abuse_type.value}:{skill_id}"
        self._attack_patterns[pattern_key] += 1
        
        # 根据严重程度采取措施
        if detection.severity == AbuseSeverity.EMERGENCY:
            # 全局熔断
            for cb in self._circuit_breakers.values():
                cb.state = "open"
                cb.open_until = datetime.now() + timedelta(minutes=5)
        
        elif detection.severity == AbuseSeverity.CRITICAL:
            # 封禁1小时
            self._banned_skills[skill_id] = datetime.now() + timedelta(hours=1)
        
        elif detection.severity == AbuseSeverity.HIGH:
            # 警告3次后封禁
            if self._warning_counts[skill_id] >= 3:
                self._banned_skills[skill_id] = datetime.now() + timedelta(minutes=30)
    
    def _log_audit(self, detection: AbuseDetection):
        """记录审计日志"""
        try:
            log_path = Path(self.audit_log_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            log_entry = {
                "timestamp": detection.timestamp.isoformat(),
                "abuse_type": detection.abuse_type.value,
                "severity": detection.severity.value,
                "skill_id": detection.skill_id,
                "action_taken": detection.action_taken.value,
                "evidence": detection.evidence,
                "message": detection.message
            }
            
            with open(log_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass
    
    def _send_alert(self, detection: AbuseDetection):
        """发送告警"""
        for callback in self._alert_callbacks:
            try:
                callback(detection)
            except Exception:
                pass
    
    def _start_cleanup_thread(self):
        """启动后台清理线程"""
        def cleanup():
            while True:
                time.sleep(60)
                self._cleanup_old_records()
        
        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()
    
    def _cleanup_old_records(self):
        """清理旧记录"""
        with self._lock:
            now = datetime.now()
            
            # 清理过期的封禁
            expired_bans = [
                k for k, v in self._banned_skills.items()
                if now > v
            ]
            for k in expired_bans:
                del self._banned_skills[k]
            
            # 清理旧的活跃执行（超过1小时）
            expired_executions = [
                k for k, v in self._active_executions.items()
                if (now - v["start_time"]).total_seconds() > 3600
            ]
            for k in expired_executions:
                del self._active_executions[k]
    
    # ==================== 公共API ====================
    
    def register_alert_callback(self, callback: Callable):
        """注册告警回调"""
        self._alert_callbacks.append(callback)
    
    def ban_skill(self, skill_id: str, duration_minutes: int = 60, reason: str = ""):
        """手动封禁技能"""
        with self._lock:
            self._banned_skills[skill_id] = datetime.now() + timedelta(minutes=duration_minutes)
            self._log_audit(AbuseDetection(
                abuse_type=AbuseType.DDOS,
                severity=AbuseSeverity.CRITICAL,
                skill_id=skill_id,
                evidence={"manual_ban": True, "reason": reason},
                timestamp=datetime.now(),
                action_taken=GuardAction.BAN,
                message=f"Manually banned: {reason}"
            ))
    
    def unban_skill(self, skill_id: str):
        """解封技能"""
        with self._lock:
            if skill_id in self._banned_skills:
                del self._banned_skills[skill_id]
    
    def get_usage_stats(self, skill_id: str = None) -> Dict[str, Any]:
        """获取使用统计"""
        with self._lock:
            if skill_id:
                record = self._usage_records.get(skill_id)
                if record:
                    return {
                        "skill_id": skill_id,
                        "call_count": record.call_count,
                        "success_count": record.success_count,
                        "error_count": record.error_count,
                        "error_rate": record.error_count / max(record.call_count, 1),
                        "total_duration_ms": record.total_duration_ms,
                        "avg_duration_ms": record.avg_duration_ms,
                        "max_duration_ms": record.max_duration_ms,
                        "total_memory_mb": record.total_memory_mb,
                        "max_memory_mb": record.max_memory_mb,
                        "total_cpu_time_ms": record.total_cpu_time_ms,
                        "max_cpu_percent": record.max_cpu_percent,
                        "total_io_read_mb": record.total_io_read_mb,
                        "total_io_write_mb": record.total_io_write_mb,
                        "total_network_sent_mb": record.total_network_sent_mb,
                        "total_network_recv_mb": record.total_network_recv_mb,
                        "is_banned": skill_id in self._banned_skills,
                        "warning_count": self._warning_counts.get(skill_id, 0),
                        "circuit_state": self._circuit_breakers.get(skill_id, CircuitBreakerState(skill_id)).state,
                        "throttle_tokens": self._throttle_states.get(skill_id, ThrottleState(skill_id)).tokens
                    }
                return {}
            
            # 返回所有统计
            return {
                "total_skills": len(self._usage_records),
                "banned_skills": list(self._banned_skills.keys()),
                "active_executions": len(self._active_executions),
                "top_callers": sorted(
                    [(k, v.call_count) for k, v in self._usage_records.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
                "top_memory_users": sorted(
                    [(k, v.total_memory_mb) for k, v in self._usage_records.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:10],
                "attack_patterns": dict(self._attack_patterns),
                "system_status": self._system_monitor.get_status()
            }
    
    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """获取熔断器状态"""
        with self._lock:
            return {
                skill_id: {
                    "state": cb.state,
                    "failure_count": cb.failure_count,
                    "success_count": cb.success_count,
                    "open_until": cb.open_until.isoformat() if cb.open_until else None
                }
                for skill_id, cb in self._circuit_breakers.items()
            }
    
    def reset_stats(self, skill_id: str = None):
        """重置统计"""
        with self._lock:
            if skill_id:
                if skill_id in self._usage_records:
                    del self._usage_records[skill_id]
                if skill_id in self._warning_counts:
                    del self._warning_counts[skill_id]
                if skill_id in self._circuit_breakers:
                    self._circuit_breakers[skill_id] = CircuitBreakerState(skill_id=skill_id)
                if skill_id in self._throttle_states:
                    self._throttle_states[skill_id] = ThrottleState(skill_id=skill_id)
            else:
                self._usage_records.clear()
                self._warning_counts.clear()
                self._circuit_breakers.clear()
                self._throttle_states.clear()
                self._attack_patterns.clear()


class SystemResourceMonitor:
    """系统资源监控器"""
    
    def __init__(self):
        self._process = psutil.Process()
        self._last_check = None
        self._last_cpu = 0.0
        self._last_io = None
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 进程级统计
            process_cpu = self._process.cpu_percent()
            process_memory = self._process.memory_info()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / 1024 / 1024,
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024,
                "process_cpu_percent": process_cpu,
                "process_memory_mb": process_memory.rss / 1024 / 1024
            }
        except Exception:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "memory_available_mb": 0,
                "disk_percent": 0,
                "disk_free_gb": 0,
                "process_cpu_percent": 0,
                "process_memory_mb": 0
            }


# 全局单例
_abuse_guard: Optional[SkillAbuseGuard] = None


def get_abuse_guard() -> SkillAbuseGuard:
    """获取全局滥用防护守卫"""
    global _abuse_guard
    if _abuse_guard is None:
        _abuse_guard = SkillAbuseGuard()
    return _abuse_guard
