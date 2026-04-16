"""Skill Latency Benchmark - 技能延迟基准测试"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os


@dataclass
class SkillExecution:
    """技能执行记录"""
    skill_id: str
    success: bool
    duration_ms: int
    error: str = None
    timestamp: str = ""


@dataclass
class SkillMetrics:
    """技能指标"""
    skill_id: str
    total_calls: int
    successful_calls: int
    failed_calls: int
    avg_latency_ms: float
    max_latency_ms: int
    min_latency_ms: int
    failure_rate: float
    timestamp: str
    details: Dict[str, Any] = field(default_factory=dict)


class SkillLatencyBench:
    """
    技能延迟基准测试
    
    职责：
    - 统计技能调用耗时
    - 计算失败率
    - 生成指标报告
    """
    
    def __init__(self, metrics_dir: str = "reports/metrics"):
        self.metrics_dir = metrics_dir
        self._executions: List[SkillExecution] = []
        self._ensure_dir()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(self.metrics_dir, exist_ok=True)
    
    def record(
        self,
        skill_id: str,
        success: bool,
        duration_ms: int,
        error: str = None
    ):
        """
        记录技能执行
        
        Args:
            skill_id: 技能 ID
            success: 是否成功
            duration_ms: 耗时（毫秒）
            error: 错误信息
        """
        execution = SkillExecution(
            skill_id=skill_id,
            success=success,
            duration_ms=duration_ms,
            error=error,
            timestamp=datetime.now().isoformat()
        )
        self._executions.append(execution)
    
    def compute(self) -> Dict[str, SkillMetrics]:
        """
        计算指标
        
        Returns:
            Dict of skill_id -> SkillMetrics
        """
        # 按技能分组
        by_skill: Dict[str, List[SkillExecution]] = {}
        for exec in self._executions:
            if exec.skill_id not in by_skill:
                by_skill[exec.skill_id] = []
            by_skill[exec.skill_id].append(exec)
        
        metrics = {}
        for skill_id, executions in by_skill.items():
            total = len(executions)
            successful = sum(1 for e in executions if e.success)
            failed = total - successful
            failure_rate = failed / total if total > 0 else 0.0
            
            durations = [e.duration_ms for e in executions]
            avg_latency = sum(durations) / len(durations) if durations else 0.0
            
            metrics[skill_id] = SkillMetrics(
                skill_id=skill_id,
                total_calls=total,
                successful_calls=successful,
                failed_calls=failed,
                avg_latency_ms=avg_latency,
                max_latency_ms=max(durations) if durations else 0,
                min_latency_ms=min(durations) if durations else 0,
                failure_rate=failure_rate,
                timestamp=datetime.now().isoformat()
            )
        
        return metrics
    
    def compute_aggregate(self) -> SkillMetrics:
        """
        计算聚合指标
        
        Returns:
            SkillMetrics (aggregate)
        """
        total = len(self._executions)
        successful = sum(1 for e in self._executions if e.success)
        failed = total - successful
        failure_rate = failed / total if total > 0 else 0.0
        
        durations = [e.duration_ms for e in self._executions]
        avg_latency = sum(durations) / len(durations) if durations else 0.0
        
        # 按错误类型统计
        error_types = {}
        for e in self._executions:
            if not e.success and e.error:
                error_types[e.error] = error_types.get(e.error, 0) + 1
        
        return SkillMetrics(
            skill_id="_aggregate",
            total_calls=total,
            successful_calls=successful,
            failed_calls=failed,
            avg_latency_ms=avg_latency,
            max_latency_ms=max(durations) if durations else 0,
            min_latency_ms=min(durations) if durations else 0,
            failure_rate=failure_rate,
            timestamp=datetime.now().isoformat(),
            details={
                "error_types": error_types,
                "unique_skills": len(set(e.skill_id for e in self._executions))
            }
        )
    
    def save(self, metrics: Dict[str, SkillMetrics] = None) -> str:
        """
        保存指标
        
        Args:
            metrics: 指标字典
        
        Returns:
            文件路径
        """
        if metrics is None:
            metrics = self.compute()
        
        # 添加聚合指标
        aggregate = self.compute_aggregate()
        
        path = os.path.join(self.metrics_dir, "skill_metrics.json")
        data = {
            "aggregate": {
                "total_calls": aggregate.total_calls,
                "avg_latency_ms": aggregate.avg_latency_ms,
                "max_latency_ms": aggregate.max_latency_ms,
                "failure_rate": aggregate.failure_rate,
                "timestamp": aggregate.timestamp,
                "details": aggregate.details
            },
            "by_skill": {
                skill_id: {
                    "total_calls": m.total_calls,
                    "avg_latency_ms": m.avg_latency_ms,
                    "max_latency_ms": m.max_latency_ms,
                    "failure_rate": m.failure_rate
                }
                for skill_id, m in metrics.items()
            }
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return path
    
    def run_benchmark(self, test_executions: List[Dict[str, Any]]) -> Dict[str, SkillMetrics]:
        """
        运行基准测试
        
        Args:
            test_executions: 测试执行列表
        
        Returns:
            Dict of skill_id -> SkillMetrics
        """
        for exec in test_executions:
            self.record(
                skill_id=exec.get("skill_id", "unknown"),
                success=exec.get("success", False),
                duration_ms=exec.get("duration_ms", 0),
                error=exec.get("error")
            )
        
        metrics = self.compute()
        self.save(metrics)
        
        return metrics
    
    def load(self) -> Optional[Dict[str, Any]]:
        """加载已保存的指标"""
        path = os.path.join(self.metrics_dir, "skill_metrics.json")
        if not os.path.exists(path):
            return None
        
        with open(path, 'r') as f:
            return json.load(f)
    
    def clear(self):
        """清空执行记录"""
        self._executions.clear()
