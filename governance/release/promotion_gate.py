"""
Promotion Gate - 晋升门禁
Phase3 Group6 核心模块
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import os
import subprocess


class GateStatus(Enum):
    """门禁状态"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


@dataclass
class GateCheck:
    """门禁检查项"""
    name: str
    passed: bool
    required: bool = True
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "required": self.required,
            "error": self.error,
            "details": self.details
        }


@dataclass
class GateResult:
    """门禁结果"""
    baseline_id: str
    version: str
    status: GateStatus
    checks: List[GateCheck] = field(default_factory=list)
    passed_count: int = 0
    failed_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseline_id": self.baseline_id,
            "version": self.version,
            "status": self.status.value,
            "checks": [c.to_dict() for c in self.checks],
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "timestamp": self.timestamp
        }
    
    @property
    def all_passed(self) -> bool:
        return all(c.passed for c in self.checks if c.required)


class PromotionGate:
    """
    晋升门禁
    
    检查项：
    1. Phase1 baseline
    2. Integration tests
    3. Benchmarks
    4. Metrics health
    5. Regression guard
    """
    
    def __init__(self):
        self._checks_config = [
            {"name": "phase1_baseline", "required": True, "command": "python tests/integration/test_minimum_loop.py"},
            {"name": "demo_minimum_loop", "required": True, "command": "python scripts/demo_minimum_loop.py"},
            {"name": "group2_tests", "required": True, "command": "python tests/integration/test_phase3_group2_final.py"},
            {"name": "group3_tests", "required": True, "command": "python tests/integration/test_skill_platform_main_chain.py"},
            {"name": "group4_tests", "required": True, "command": "python tests/integration/test_memory_context_kernel.py"},
        ]
    
    def check(self, baseline_id: str, version: str) -> GateResult:
        """
        执行门禁检查
        
        Args:
            baseline_id: 基线 ID
            version: 版本
        
        Returns:
            GateResult
        """
        result = GateResult(
            baseline_id=baseline_id,
            version=version,
            status=GateStatus.PENDING
        )
        
        # 1. Phase1 baseline
        check = self._run_check("phase1_baseline", "python tests/integration/test_minimum_loop.py", True)
        result.checks.append(check)
        
        # 2. Demo
        check = self._run_check("demo_minimum_loop", "python scripts/demo_minimum_loop.py", True)
        result.checks.append(check)
        
        # 3. Integration tests
        check = self._run_check("group2_tests", "python tests/integration/test_phase3_group2_final.py", True)
        result.checks.append(check)
        
        check = self._run_check("group3_tests", "python tests/integration/test_skill_platform_main_chain.py", True)
        result.checks.append(check)
        
        check = self._run_check("group4_tests", "python tests/integration/test_memory_context_kernel.py", True)
        result.checks.append(check)
        
        # 4. Benchmarks (可选)
        check = self._run_check("task_success_bench", "python tests/benchmarks/task_success_bench.py", False)
        result.checks.append(check)
        
        check = self._run_check("skill_latency_bench", "python tests/benchmarks/skill_latency_bench.py", False)
        result.checks.append(check)
        
        check = self._run_check("memory_retrieval_bench", "python tests/benchmarks/memory_retrieval_bench.py", False)
        result.checks.append(check)
        
        # 5. Metrics health
        check = self._check_metrics_health()
        result.checks.append(check)
        
        # 6. Regression guard
        check = self._check_regression_guard()
        result.checks.append(check)
        
        # 统计
        result.passed_count = sum(1 for c in result.checks if c.passed)
        result.failed_count = sum(1 for c in result.checks if not c.passed)
        
        # 判断状态
        if result.all_passed:
            result.status = GateStatus.PASSED
        else:
            result.status = GateStatus.FAILED
        
        return result
    
    def _run_check(self, name: str, command: str, required: bool) -> GateCheck:
        """运行检查"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120,
                cwd="/home/sandbox/.openclaw/workspace"
            )
            
            passed = result.returncode == 0
            
            return GateCheck(
                name=name,
                passed=passed,
                required=required,
                error=result.stderr[:500] if not passed else None,
                details={"returncode": result.returncode}
            )
        except subprocess.TimeoutExpired:
            return GateCheck(
                name=name,
                passed=False,
                required=required,
                error="Timeout"
            )
        except Exception as e:
            return GateCheck(
                name=name,
                passed=False,
                required=required,
                error=str(e)
            )
    
    def _check_metrics_health(self) -> GateCheck:
        """检查 metrics 健康"""
        metrics_path = "reports/metrics/aggregated_metrics.json"
        
        if not os.path.exists(metrics_path):
            return GateCheck(
                name="metrics_health",
                passed=True,  # 如果没有 metrics 文件，跳过
                required=False,
                details={"note": "No metrics file, skipped"}
            )
        
        try:
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
            
            # 检查关键指标
            task_success_rate = metrics.get("task_success_rate", 1.0)
            skill_failure_rate = metrics.get("skill_failure_rate", 0.0)
            
            passed = task_success_rate >= 0.8 and skill_failure_rate <= 0.2
            
            return GateCheck(
                name="metrics_health",
                passed=passed,
                required=True,
                details={
                    "task_success_rate": task_success_rate,
                    "skill_failure_rate": skill_failure_rate
                }
            )
        except Exception as e:
            return GateCheck(
                name="metrics_health",
                passed=False,
                required=True,
                error=str(e)
            )
    
    def _check_regression_guard(self) -> GateCheck:
        """检查回归防护"""
        # 参考 task_success_rate, skill_failure_rate, memory_hit_rate, rollback_rate, degradation_rate
        metrics_path = "reports/metrics/aggregated_metrics.json"
        
        if not os.path.exists(metrics_path):
            return GateCheck(
                name="regression_guard",
                passed=True,
                required=False,
                details={"note": "No metrics file, skipped"}
            )
        
        try:
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
            
            # 回归阈值
            thresholds = {
                "task_success_rate": 0.8,
                "skill_failure_rate": 0.2,
                "memory_hit_rate": 0.5,
                "rollback_rate": 0.1,
                "degradation_rate": 0.2
            }
            
            violations = []
            
            for metric, threshold in thresholds.items():
                value = metrics.get(metric)
                if value is not None:
                    if metric in ["task_success_rate", "memory_hit_rate"]:
                        if value < threshold:
                            violations.append(f"{metric}: {value:.2f} < {threshold}")
                    else:
                        if value > threshold:
                            violations.append(f"{metric}: {value:.2f} > {threshold}")
            
            passed = len(violations) == 0
            
            return GateCheck(
                name="regression_guard",
                passed=passed,
                required=True,
                error="; ".join(violations) if violations else None,
                details=metrics
            )
        except Exception as e:
            return GateCheck(
                name="regression_guard",
                passed=False,
                required=True,
                error=str(e)
            )


# 全局单例
_promotion_gate = None


def get_promotion_gate() -> PromotionGate:
    """获取晋升门禁单例"""
    global _promotion_gate
    if _promotion_gate is None:
        _promotion_gate = PromotionGate()
    return _promotion_gate
