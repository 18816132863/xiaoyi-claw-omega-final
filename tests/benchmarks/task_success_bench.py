"""Task Success Benchmark - 任务成功率基准测试"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    success: bool
    duration_ms: int
    error: str = None
    timestamp: str = ""


@dataclass
class TaskMetrics:
    """任务指标"""
    total: int
    passed: int
    failed: int
    success_rate: float
    avg_duration_ms: float
    timestamp: str
    details: Dict[str, Any] = field(default_factory=dict)


class TaskSuccessBench:
    """
    任务成功率基准测试
    
    职责：
    - 统计任务成功率
    - 计算平均耗时
    - 生成指标报告
    """
    
    def __init__(self, metrics_dir: str = "reports/metrics"):
        self.metrics_dir = metrics_dir
        self._results: List[TaskResult] = []
        self._ensure_dir()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(self.metrics_dir, exist_ok=True)
    
    def record(
        self,
        task_id: str,
        success: bool,
        duration_ms: int,
        error: str = None
    ):
        """
        记录任务结果
        
        Args:
            task_id: 任务 ID
            success: 是否成功
            duration_ms: 耗时（毫秒）
            error: 错误信息
        """
        result = TaskResult(
            task_id=task_id,
            success=success,
            duration_ms=duration_ms,
            error=error,
            timestamp=datetime.now().isoformat()
        )
        self._results.append(result)
    
    def compute(self) -> TaskMetrics:
        """
        计算指标
        
        Returns:
            TaskMetrics
        """
        total = len(self._results)
        passed = sum(1 for r in self._results if r.success)
        failed = total - passed
        success_rate = passed / total if total > 0 else 0.0
        
        durations = [r.duration_ms for r in self._results]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        # 按错误类型统计
        error_types = {}
        for r in self._results:
            if not r.success and r.error:
                error_types[r.error] = error_types.get(r.error, 0) + 1
        
        metrics = TaskMetrics(
            total=total,
            passed=passed,
            failed=failed,
            success_rate=success_rate,
            avg_duration_ms=avg_duration,
            timestamp=datetime.now().isoformat(),
            details={
                "error_types": error_types,
                "min_duration_ms": min(durations) if durations else 0,
                "max_duration_ms": max(durations) if durations else 0
            }
        )
        
        return metrics
    
    def save(self, metrics: TaskMetrics = None) -> str:
        """
        保存指标
        
        Args:
            metrics: 指标对象
        
        Returns:
            文件路径
        """
        if metrics is None:
            metrics = self.compute()
        
        path = os.path.join(self.metrics_dir, "task_metrics.json")
        data = {
            "total": metrics.total,
            "passed": metrics.passed,
            "failed": metrics.failed,
            "success_rate": metrics.success_rate,
            "avg_duration_ms": metrics.avg_duration_ms,
            "timestamp": metrics.timestamp,
            "details": metrics.details
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return path
    
    def run_benchmark(self, test_tasks: List[Dict[str, Any]]) -> TaskMetrics:
        """
        运行基准测试
        
        Args:
            test_tasks: 测试任务列表
        
        Returns:
            TaskMetrics
        """
        for task in test_tasks:
            self.record(
                task_id=task.get("task_id", "unknown"),
                success=task.get("success", False),
                duration_ms=task.get("duration_ms", 0),
                error=task.get("error")
            )
        
        metrics = self.compute()
        self.save(metrics)
        
        return metrics
    
    def load(self) -> Optional[Dict[str, Any]]:
        """加载已保存的指标"""
        path = os.path.join(self.metrics_dir, "task_metrics.json")
        if not os.path.exists(path):
            return None
        
        with open(path, 'r') as f:
            return json.load(f)
    
    def clear(self):
        """清空结果"""
        self._results.clear()
