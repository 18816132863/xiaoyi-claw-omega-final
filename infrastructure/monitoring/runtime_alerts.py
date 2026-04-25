"""
Runtime Alerts - 运行时告警
Phase3 Group5 核心模块
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import os
import uuid


class AlertSeverity(Enum):
    """告警严重程度"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(Enum):
    """告警类型"""
    HEALTH_DEGRADED = "health_degraded"
    SKILL_FAILURE_HIGH = "skill_failure_high"
    WORKFLOW_ROLLBACK_FREQUENT = "workflow_rollback_frequent"
    MEMORY_HIT_LOW = "memory_hit_low"
    DEGRADATION_EXCESSIVE = "degradation_excessive"
    LATENCY_HIGH = "latency_high"


@dataclass
class Alert:
    """告警"""
    alert_id: str
    severity: AlertSeverity
    alert_type: AlertType
    reason: str
    related_metric: str
    metric_value: float
    threshold: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    acknowledged: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "severity": self.severity.value,
            "alert_type": self.alert_type.value,
            "reason": self.reason,
            "related_metric": self.related_metric,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "timestamp": self.timestamp,
            "acknowledged": self.acknowledged,
            "metadata": self.metadata
        }


class RuntimeAlerts:
    """
    运行时告警系统
    
    职责：
    - 监控指标变化
    - 生成告警
    - 管理告警状态
    - 持久化告警
    """
    
    def __init__(self, alerts_path: str = "reports/alerts/latest_alerts.json"):
        self.alerts_path = alerts_path
        self._alerts: List[Alert] = []
        self._rules = self._create_default_rules()
        self._ensure_dir()
        self._load_alerts()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.alerts_path), exist_ok=True)
    
    def _create_default_rules(self) -> List[Dict[str, Any]]:
        """创建默认告警规则"""
        return [
            {
                "alert_type": AlertType.HEALTH_DEGRADED,
                "metric": "overall_health_score",
                "condition": "below",
                "warning_threshold": 0.9,
                "critical_threshold": 0.7,
                "reason_template": "Overall health score dropped to {value:.2f}"
            },
            {
                "alert_type": AlertType.SKILL_FAILURE_HIGH,
                "metric": "skill_failure_rate",
                "condition": "above",
                "warning_threshold": 0.1,
                "critical_threshold": 0.2,
                "reason_template": "Skill failure rate elevated to {value:.1%}"
            },
            {
                "alert_type": AlertType.WORKFLOW_ROLLBACK_FREQUENT,
                "metric": "rollback_rate",
                "condition": "above",
                "warning_threshold": 0.05,
                "critical_threshold": 0.1,
                "reason_template": "Rollback rate is {value:.1%}"
            },
            {
                "alert_type": AlertType.MEMORY_HIT_LOW,
                "metric": "memory_hit_rate",
                "condition": "below",
                "warning_threshold": 0.7,
                "critical_threshold": 0.5,
                "reason_template": "Memory hit rate dropped to {value:.1%}"
            },
            {
                "alert_type": AlertType.DEGREDATION_EXCESSIVE,
                "metric": "degradation_rate",
                "condition": "above",
                "warning_threshold": 0.1,
                "critical_threshold": 0.2,
                "reason_template": "Degradation rate is {value:.1%}"
            }
        ]
    
    def _load_alerts(self):
        """加载已有告警"""
        if not os.path.exists(self.alerts_path):
            return
        
        try:
            with open(self.alerts_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for alert_data in data.get("alerts", []):
                    alert = Alert(
                        alert_id=alert_data.get("alert_id", ""),
                        severity=AlertSeverity(alert_data.get("severity", "info")),
                        alert_type=AlertType(alert_data.get("alert_type", "health_degraded")),
                        reason=alert_data.get("reason", ""),
                        related_metric=alert_data.get("related_metric", ""),
                        metric_value=alert_data.get("metric_value", 0),
                        threshold=alert_data.get("threshold", 0),
                        timestamp=alert_data.get("timestamp", ""),
                        acknowledged=alert_data.get("acknowledged", False),
                        metadata=alert_data.get("metadata", {})
                    )
                    self._alerts.append(alert)
        except Exception:
            pass
    
    def check_and_alert(self, metrics: Dict[str, float]) -> List[Alert]:
        """
        检查指标并生成告警
        
        Args:
            metrics: 指标字典
        
        Returns:
            List[Alert]
        """
        new_alerts = []
        
        for rule in self._rules:
            metric_name = rule["metric"]
            if metric_name not in metrics:
                continue
            
            value = metrics[metric_name]
            condition = rule["condition"]
            
            # 检查是否触发告警
            severity = None
            threshold = None
            
            if condition == "below":
                if value < rule["critical_threshold"]:
                    severity = AlertSeverity.CRITICAL
                    threshold = rule["critical_threshold"]
                elif value < rule["warning_threshold"]:
                    severity = AlertSeverity.WARNING
                    threshold = rule["warning_threshold"]
            else:  # above
                if value > rule["critical_threshold"]:
                    severity = AlertSeverity.CRITICAL
                    threshold = rule["critical_threshold"]
                elif value > rule["warning_threshold"]:
                    severity = AlertSeverity.WARNING
                    threshold = rule["warning_threshold"]
            
            if severity:
                alert = Alert(
                    alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                    severity=severity,
                    alert_type=rule["alert_type"],
                    reason=rule["reason_template"].format(value=value),
                    related_metric=metric_name,
                    metric_value=value,
                    threshold=threshold
                )
                new_alerts.append(alert)
                self._alerts.append(alert)
        
        # 保存告警
        if new_alerts:
            self._save_alerts()
        
        return new_alerts
    
    def _save_alerts(self):
        """保存告警"""
        data = {
            "updated_at": datetime.now().isoformat(),
            "total_alerts": len(self._alerts),
            "unacknowledged": len([a for a in self._alerts if not a.acknowledged]),
            "alerts": [a.to_dict() for a in self._alerts[-100:]]  # 保留最近 100 条
        }
        
        with open(self.alerts_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def acknowledge(self, alert_id: str) -> bool:
        """确认告警"""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                self._save_alerts()
                return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """获取未确认的告警"""
        return [a for a in self._alerts if not a.acknowledged]
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """按严重程度获取告警"""
        return [a for a in self._alerts if a.severity == severity]
    
    def clear_acknowledged(self):
        """清理已确认的告警"""
        self._alerts = [a for a in self._alerts if not a.acknowledged]
        self._save_alerts()


# 全局单例
_runtime_alerts = None


def get_runtime_alerts() -> RuntimeAlerts:
    """获取运行时告警单例"""
    global _runtime_alerts
    if _runtime_alerts is None:
        _runtime_alerts = RuntimeAlerts()
    return _runtime_alerts
