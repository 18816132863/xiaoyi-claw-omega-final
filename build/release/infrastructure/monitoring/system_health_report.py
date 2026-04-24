"""
System Health Report - 系统健康报告
Phase3 Group5 核心模块
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import os


@dataclass
class HealthMetric:
    """健康指标"""
    name: str
    value: float
    threshold: float
    status: str  # healthy, warning, critical
    trend: str = "stable"  # up, down, stable
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "threshold": self.threshold,
            "status": self.status,
            "trend": self.trend
        }


@dataclass
class SystemHealthReport:
    """系统健康报告"""
    report_id: str
    timestamp: str
    overall_health: str  # healthy, degraded, critical
    overall_score: float
    metrics: List[HealthMetric] = field(default_factory=list)
    alerts: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp,
            "overall_health": self.overall_health,
            "overall_score": self.overall_score,
            "metrics": [m.to_dict() for m in self.metrics],
            "alerts": self.alerts,
            "recommendations": self.recommendations
        }


class SystemHealthReporter:
    """
    系统健康报告生成器
    
    职责：
    - 读取聚合指标
    - 计算健康分数
    - 生成健康报告
    - 提供改进建议
    """
    
    def __init__(self, metrics_path: str = "reports/metrics/aggregated_metrics.json"):
        self.metrics_path = metrics_path
        self._thresholds = {
            "task_success_rate": {"warning": 0.9, "critical": 0.8},
            "skill_failure_rate": {"warning": 0.1, "critical": 0.2},
            "memory_hit_rate": {"warning": 0.7, "critical": 0.5},
            "rollback_rate": {"warning": 0.05, "critical": 0.1},
            "degradation_rate": {"warning": 0.1, "critical": 0.2},
            "avg_latency_ms": {"warning": 5000, "critical": 10000}
        }
    
    def generate_report(self) -> SystemHealthReport:
        """生成健康报告"""
        import uuid
        
        # 读取指标
        metrics_data = self._load_metrics()
        
        # 计算各项指标
        metrics = []
        
        # Task success rate
        task_success = metrics_data.get("task_success_rate", 1.0)
        metrics.append(self._create_metric(
            "task_success_rate",
            task_success,
            self._thresholds["task_success_rate"],
            higher_is_better=True
        ))
        
        # Skill failure rate
        skill_failure = metrics_data.get("skill_failure_rate", 0.0)
        metrics.append(self._create_metric(
            "skill_failure_rate",
            skill_failure,
            self._thresholds["skill_failure_rate"],
            higher_is_better=False
        ))
        
        # Memory hit rate
        memory_hit = metrics_data.get("memory_hit_rate", 1.0)
        metrics.append(self._create_metric(
            "memory_hit_rate",
            memory_hit,
            self._thresholds["memory_hit_rate"],
            higher_is_better=True
        ))
        
        # Rollback rate
        rollback_rate = metrics_data.get("rollback_rate", 0.0)
        metrics.append(self._create_metric(
            "rollback_rate",
            rollback_rate,
            self._thresholds["rollback_rate"],
            higher_is_better=False
        ))
        
        # Degradation rate
        degradation_rate = metrics_data.get("degradation_rate", 0.0)
        metrics.append(self._create_metric(
            "degradation_rate",
            degradation_rate,
            self._thresholds["degradation_rate"],
            higher_is_better=False
        ))
        
        # 计算总体健康分数
        overall_score = self._calculate_overall_score(metrics)
        overall_health = self._determine_overall_health(overall_score)
        
        # 生成建议
        recommendations = self._generate_recommendations(metrics)
        
        report = SystemHealthReport(
            report_id=f"health_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now().isoformat(),
            overall_health=overall_health,
            overall_score=overall_score,
            metrics=metrics,
            recommendations=recommendations
        )
        
        # 保存报告
        self._save_report(report)
        
        return report
    
    def _load_metrics(self) -> Dict[str, Any]:
        """加载指标"""
        if not os.path.exists(self.metrics_path):
            return {}
        
        try:
            with open(self.metrics_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _create_metric(
        self,
        name: str,
        value: float,
        thresholds: Dict[str, float],
        higher_is_better: bool
    ) -> HealthMetric:
        """创建指标"""
        if higher_is_better:
            if value >= thresholds["warning"]:
                status = "healthy"
            elif value >= thresholds["critical"]:
                status = "warning"
            else:
                status = "critical"
        else:
            if value <= thresholds["warning"]:
                status = "healthy"
            elif value <= thresholds["critical"]:
                status = "warning"
            else:
                status = "critical"
        
        return HealthMetric(
            name=name,
            value=value,
            threshold=thresholds["warning"],
            status=status
        )
    
    def _calculate_overall_score(self, metrics: List[HealthMetric]) -> float:
        """计算总体分数"""
        if not metrics:
            return 1.0
        
        scores = []
        for m in metrics:
            if m.status == "healthy":
                scores.append(1.0)
            elif m.status == "warning":
                scores.append(0.7)
            else:
                scores.append(0.3)
        
        return sum(scores) / len(scores)
    
    def _determine_overall_health(self, score: float) -> str:
        """确定总体健康状态"""
        if score >= 0.9:
            return "healthy"
        elif score >= 0.7:
            return "degraded"
        else:
            return "critical"
    
    def _generate_recommendations(self, metrics: List[HealthMetric]) -> List[str]:
        """生成建议"""
        recommendations = []
        
        for m in metrics:
            if m.status == "critical":
                if m.name == "task_success_rate":
                    recommendations.append("Task success rate is critical. Review recent failures and consider fallback strategies.")
                elif m.name == "skill_failure_rate":
                    recommendations.append("Skill failure rate is high. Check skill health and consider version rollback.")
                elif m.name == "memory_hit_rate":
                    recommendations.append("Memory hit rate is low. Review retrieval configuration and indexing.")
                elif m.name == "rollback_rate":
                    recommendations.append("Rollback rate is high. Review workflow stability and error handling.")
                elif m.name == "degradation_rate":
                    recommendations.append("Degradation is frequent. Review policy thresholds and capability restrictions.")
            elif m.status == "warning":
                if m.name == "task_success_rate":
                    recommendations.append("Monitor task success rate trend.")
                elif m.name == "skill_failure_rate":
                    recommendations.append("Monitor skill failure rate.")
        
        if not recommendations:
            recommendations.append("System is healthy. Continue monitoring.")
        
        return recommendations
    
    def _save_report(self, report: SystemHealthReport):
        """保存报告"""
        report_path = "reports/observability/system_health_report.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)


# 全局单例
_system_health_reporter = None


def get_system_health_reporter() -> SystemHealthReporter:
    """获取系统健康报告生成器单例"""
    global _system_health_reporter
    if _system_health_reporter is None:
        _system_health_reporter = SystemHealthReporter()
    return _system_health_reporter
