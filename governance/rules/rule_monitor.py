#!/usr/bin/env python3
"""
规则监控模块 - V1.0.0

监控规则执行状态和效果。
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict


class AlertType(Enum):
    """告警类型"""
    HIGH_HIT_RATE = "high_hit_rate"
    LOW_HIT_RATE = "low_hit_rate"
    ERROR_RATE = "error_rate"
    CONFLICT = "conflict"
    DEPRECATED = "deprecated"


@dataclass
class RuleMetric:
    """规则指标"""
    rule_id: str
    hit_count: int
    deny_count: int
    warn_count: int
    error_count: int
    last_hit: Optional[datetime]
    avg_execution_time_ms: float


@dataclass
class RuleAlert:
    """规则告警"""
    id: str
    rule_id: str
    type: AlertType
    message: str
    severity: str
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False


class RuleMonitor:
    """规则监控器"""
    
    def __init__(self):
        self.metrics: Dict[str, RuleMetric] = {}
        self.alerts: List[RuleAlert] = []
        self.alert_counter = 0
        self.monitoring_start = datetime.now()
    
    def record_execution(self,
                         rule_id: str,
                         matched: bool,
                         action: str,
                         execution_time_ms: float,
                         error: bool = False):
        """记录规则执行"""
        if rule_id not in self.metrics:
            self.metrics[rule_id] = RuleMetric(
                rule_id=rule_id,
                hit_count=0,
                deny_count=0,
                warn_count=0,
                error_count=0,
                last_hit=None,
                avg_execution_time_ms=0
            )
        
        metric = self.metrics[rule_id]
        
        if matched:
            metric.hit_count += 1
            metric.last_hit = datetime.now()
            
            if action == "deny":
                metric.deny_count += 1
            elif action == "warn":
                metric.warn_count += 1
        
        if error:
            metric.error_count += 1
        
        # 更新平均执行时间
        total_executions = metric.hit_count + metric.error_count
        if total_executions > 0:
            metric.avg_execution_time_ms = (
                (metric.avg_execution_time_ms * (total_executions - 1) + execution_time_ms)
                / total_executions
            )
        
        # 检查告警条件
        self._check_alerts(rule_id, metric)
    
    def _check_alerts(self, rule_id: str, metric: RuleMetric):
        """检查告警条件"""
        # 高命中率告警
        total = metric.hit_count + metric.deny_count + metric.warn_count
        if total > 100:
            deny_rate = metric.deny_count / total
            if deny_rate > 0.5:
                self._create_alert(
                    rule_id,
                    AlertType.HIGH_HIT_RATE,
                    f"规则 {rule_id} 拒绝率过高: {deny_rate:.1%}",
                    "warning"
                )
        
        # 错误率告警
        if metric.error_count > 10:
            error_rate = metric.error_count / (metric.hit_count + metric.error_count)
            if error_rate > 0.1:
                self._create_alert(
                    rule_id,
                    AlertType.ERROR_RATE,
                    f"规则 {rule_id} 错误率过高: {error_rate:.1%}",
                    "error"
                )
    
    def _create_alert(self, rule_id: str, alert_type: AlertType, message: str, severity: str):
        """创建告警"""
        # 检查是否已存在相同告警
        for alert in self.alerts:
            if (alert.rule_id == rule_id and 
                alert.type == alert_type and 
                not alert.acknowledged):
                return
        
        alert = RuleAlert(
            id=f"alert_{self.alert_counter}",
            rule_id=rule_id,
            type=alert_type,
            message=message,
            severity=severity
        )
        
        self.alerts.append(alert)
        self.alert_counter += 1
    
    def get_rule_health(self, rule_id: str) -> Dict:
        """获取规则健康状态"""
        metric = self.metrics.get(rule_id)
        if not metric:
            return {"status": "unknown", "message": "无执行记录"}
        
        # 计算健康分数
        score = 100
        
        # 错误率扣分
        total = metric.hit_count + metric.error_count
        if total > 0:
            error_rate = metric.error_count / total
            score -= error_rate * 50
        
        # 执行时间扣分
        if metric.avg_execution_time_ms > 100:
            score -= 10
        
        # 确定状态
        if score >= 80:
            status = "healthy"
        elif score >= 50:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "score": score,
            "hit_count": metric.hit_count,
            "error_count": metric.error_count,
            "avg_execution_time_ms": metric.avg_execution_time_ms
        }
    
    def get_summary(self) -> Dict:
        """获取监控摘要"""
        total_hits = sum(m.hit_count for m in self.metrics.values())
        total_denies = sum(m.deny_count for m in self.metrics.values())
        total_warns = sum(m.warn_count for m in self.metrics.values())
        total_errors = sum(m.error_count for m in self.metrics.values())
        
        unacknowledged_alerts = sum(1 for a in self.alerts if not a.acknowledged)
        
        return {
            "monitoring_duration": str(datetime.now() - self.monitoring_start),
            "total_rules_monitored": len(self.metrics),
            "total_hits": total_hits,
            "total_denies": total_denies,
            "total_warns": total_warns,
            "total_errors": total_errors,
            "unacknowledged_alerts": unacknowledged_alerts,
            "top_rules": sorted(
                [(r, m.hit_count) for r, m in self.metrics.items()],
                key=lambda x: -x[1]
            )[:5]
        }
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """确认告警"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False


# 全局规则监控器
_rule_monitor: Optional[RuleMonitor] = None


def get_rule_monitor() -> RuleMonitor:
    """获取全局规则监控器"""
    global _rule_monitor
    if _rule_monitor is None:
        _rule_monitor = RuleMonitor()
    return _rule_monitor
