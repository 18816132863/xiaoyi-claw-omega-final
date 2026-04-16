"""Evaluation aggregator - aggregates metrics and detects regressions."""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os


class MetricType(Enum):
    TASK_SUCCESS_RATE = "task_success_rate"
    SKILL_LATENCY = "skill_latency"
    MEMORY_HIT_RATE = "memory_hit_rate"
    WORKFLOW_STABILITY = "workflow_stability"
    GOVERNANCE_COMPLIANCE = "governance_compliance"


@dataclass
class Metric:
    """A single metric measurement."""
    metric_type: MetricType
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "metric_type": self.metric_type.value,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata
        }


@dataclass
class RegressionAlert:
    """Alert for detected regression."""
    metric_type: MetricType
    metric_name: str
    current_value: float
    baseline_value: float
    change_pct: float
    severity: str  # low, medium, high, critical
    detected_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


class EvaluationAggregator:
    """
    Aggregates metrics from all system components.
    
    Collects metrics from:
    - Task execution
    - Skill performance
    - Memory system
    - Workflow engine
    - Governance policies
    """
    
    def __init__(self, metrics_path: str = "reports/metrics"):
        self.metrics_path = metrics_path
        self._metrics: List[Metric] = []
        self._baselines: Dict[str, float] = {}
        self._thresholds: Dict[str, Dict] = {}
        self._alerts: List[RegressionAlert] = []
        self._load()
    
    def _load(self):
        """Load metrics and baselines."""
        # Load baselines
        baseline_path = os.path.join(self.metrics_path, "baselines.json")
        if os.path.exists(baseline_path):
            try:
                with open(baseline_path, 'r') as f:
                    self._baselines = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load baselines: {e}")
        
        # Load thresholds
        threshold_path = os.path.join(self.metrics_path, "thresholds.json")
        if os.path.exists(threshold_path):
            try:
                with open(threshold_path, 'r') as f:
                    self._thresholds = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load thresholds: {e}")
    
    def _save(self):
        """Save metrics."""
        os.makedirs(self.metrics_path, exist_ok=True)
        
        # Save latest metrics
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"metrics_{timestamp}.json"
        filepath = os.path.join(self.metrics_path, filename)
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": [m.to_dict() for m in self._metrics[-1000:]]  # Keep last 1000
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record(self, metric: Metric):
        """Record a metric."""
        self._metrics.append(metric)
        
        # Check for regression
        self._check_regression(metric)
    
    def record_batch(self, metrics: List[Metric]):
        """Record multiple metrics."""
        for metric in metrics:
            self.record(metric)
        
        self._save()
    
    def _check_regression(self, metric: Metric):
        """Check if metric indicates regression."""
        metric_key = f"{metric.metric_type.value}.{metric.name}"
        baseline = self._baselines.get(metric_key)
        threshold_config = self._thresholds.get(metric_key, {})
        
        if baseline is None:
            return
        
        # Calculate change
        if baseline != 0:
            change_pct = ((metric.value - baseline) / baseline) * 100
        else:
            change_pct = 0 if metric.value == 0 else float('inf')
        
        # Check threshold
        regression_threshold = threshold_config.get("regression_threshold", 10)
        direction = threshold_config.get("direction", "higher_is_better")
        
        is_regression = False
        if direction == "higher_is_better":
            is_regression = change_pct < -regression_threshold
        else:
            is_regression = change_pct > regression_threshold
        
        if is_regression:
            # Determine severity
            abs_change = abs(change_pct)
            if abs_change > 50:
                severity = "critical"
            elif abs_change > 30:
                severity = "high"
            elif abs_change > 15:
                severity = "medium"
            else:
                severity = "low"
            
            alert = RegressionAlert(
                metric_type=metric.metric_type,
                metric_name=metric.name,
                current_value=metric.value,
                baseline_value=baseline,
                change_pct=change_pct,
                severity=severity,
                metadata={"metric_key": metric_key}
            )
            
            self._alerts.append(alert)
    
    def set_baseline(self, metric_type: MetricType, name: str, value: float):
        """Set baseline for a metric."""
        metric_key = f"{metric_type.value}.{name}"
        self._baselines[metric_key] = value
        
        # Save baselines
        os.makedirs(self.metrics_path, exist_ok=True)
        baseline_path = os.path.join(self.metrics_path, "baselines.json")
        with open(baseline_path, 'w') as f:
            json.dump(self._baselines, f, indent=2)
    
    def set_threshold(
        self,
        metric_type: MetricType,
        name: str,
        regression_threshold: float = 10,
        direction: str = "higher_is_better"
    ):
        """Set regression threshold for a metric."""
        metric_key = f"{metric_type.value}.{name}"
        self._thresholds[metric_key] = {
            "regression_threshold": regression_threshold,
            "direction": direction
        }
        
        # Save thresholds
        os.makedirs(self.metrics_path, exist_ok=True)
        threshold_path = os.path.join(self.metrics_path, "thresholds.json")
        with open(threshold_path, 'w') as f:
            json.dump(self._thresholds, f, indent=2)
    
    def get_metrics(
        self,
        metric_type: MetricType = None,
        name: str = None,
        since: datetime = None,
        limit: int = 100
    ) -> List[Metric]:
        """Get metrics with optional filters."""
        metrics = self._metrics
        
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]
        
        if name:
            metrics = [m for m in metrics if m.name == name]
        
        if since:
            metrics = [m for m in metrics if m.timestamp >= since]
        
        return metrics[-limit:]
    
    def get_aggregated(self, metric_type: MetricType, name: str, period: str = "day") -> Dict:
        """Get aggregated metrics for a period."""
        metrics = [m for m in self._metrics if m.metric_type == metric_type and m.name == name]
        
        if not metrics:
            return {"count": 0}
        
        # Filter by period
        now = datetime.now()
        if period == "hour":
            cutoff = now - timedelta(hours=1)
        elif period == "day":
            cutoff = now - timedelta(days=1)
        elif period == "week":
            cutoff = now - timedelta(weeks=1)
        else:
            cutoff = now - timedelta(days=30)
        
        filtered = [m for m in metrics if m.timestamp >= cutoff]
        
        if not filtered:
            return {"count": 0}
        
        values = [m.value for m in filtered]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "latest": values[-1]
        }
    
    def get_alerts(self, severity: str = None, limit: int = 100) -> List[RegressionAlert]:
        """Get regression alerts."""
        alerts = self._alerts
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return alerts[-limit:]
    
    def clear_alerts(self):
        """Clear all alerts."""
        self._alerts.clear()
    
    def get_summary(self) -> Dict:
        """Get overall metrics summary."""
        summary = {
            "total_metrics": len(self._metrics),
            "total_alerts": len(self._alerts),
            "by_type": {},
            "recent_alerts": []
        }
        
        # Count by type
        for metric_type in MetricType:
            count = len([m for m in self._metrics if m.metric_type == metric_type])
            summary["by_type"][metric_type.value] = count
        
        # Recent alerts
        summary["recent_alerts"] = [
            {
                "metric": a.metric_name,
                "severity": a.severity,
                "change_pct": a.change_pct
            }
            for a in self._alerts[-5:]
        ]
        
        return summary


class RegressionDetector:
    """Detects regressions from metrics trends."""
    
    def __init__(self, aggregator: EvaluationAggregator):
        self.aggregator = aggregator
    
    def detect(self, metric_type: MetricType, name: str, window: int = 10) -> Optional[RegressionAlert]:
        """Detect regression in a metric."""
        metrics = self.aggregator.get_metrics(metric_type, name, limit=window)
        
        if len(metrics) < window // 2:
            return None
        
        values = [m.value for m in metrics]
        
        # Split into two halves
        mid = len(values) // 2
        first_half = values[:mid]
        second_half = values[mid:]
        
        first_mean = sum(first_half) / len(first_half)
        second_mean = sum(second_half) / len(second_half)
        
        if first_mean == 0:
            return None
        
        change_pct = ((second_mean - first_mean) / first_mean) * 100
        
        # Check if significant regression
        if abs(change_pct) > 20:
            severity = "critical" if abs(change_pct) > 50 else "high"
            
            return RegressionAlert(
                metric_type=metric_type,
                metric_name=name,
                current_value=second_mean,
                baseline_value=first_mean,
                change_pct=change_pct,
                severity=severity
            )
        
        return None


class PromotionRecommender:
    """Recommends promotion of skills/workflows based on metrics."""
    
    def __init__(self, aggregator: EvaluationAggregator):
        self.aggregator = aggregator
    
    def recommend_skill_promotion(self, skill_id: str) -> Dict:
        """Recommend if a skill should be promoted."""
        # Get skill metrics
        metrics = self.aggregator.get_metrics(
            metric_type=MetricType.SKILL_LATENCY,
            name=f"skill_{skill_id}",
            limit=100
        )
        
        if len(metrics) < 10:
            return {"recommend": False, "reason": "insufficient_data"}
        
        # Calculate success rate
        success_metrics = self.aggregator.get_metrics(
            metric_type=MetricType.TASK_SUCCESS_RATE,
            name=f"skill_{skill_id}_success",
            limit=100
        )
        
        if success_metrics:
            success_rate = sum(m.value for m in success_metrics) / len(success_metrics)
        else:
            success_rate = 0
        
        # Calculate average latency
        latency_values = [m.value for m in metrics]
        avg_latency = sum(latency_values) / len(latency_values)
        
        # Recommendation criteria
        if success_rate >= 0.95 and avg_latency < 1000:
            return {
                "recommend": True,
                "reason": "High success rate and low latency",
                "success_rate": success_rate,
                "avg_latency": avg_latency
            }
        elif success_rate >= 0.90:
            return {
                "recommend": "conditional",
                "reason": "Good success rate, consider monitoring",
                "success_rate": success_rate,
                "avg_latency": avg_latency
            }
        else:
            return {
                "recommend": False,
                "reason": "Success rate below threshold",
                "success_rate": success_rate,
                "avg_latency": avg_latency
            }
