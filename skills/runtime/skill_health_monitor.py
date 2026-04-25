"""
Skill Health Monitor
技能健康监控器
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import threading
from pathlib import Path


class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthMetric:
    """健康指标"""
    skill_id: str
    status: HealthStatus
    score: float
    last_check: str
    error_count: int = 0
    success_count: int = 0
    avg_duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class SkillHealthMonitor:
    """技能健康监控器"""
    
    def __init__(self):
        self._metrics: Dict[str, HealthMetric] = {}
        self._history: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = threading.RLock()
    
    def record_execution(self, skill_id: str, success: bool, 
                         duration_ms: float = 0, error: Optional[str] = None):
        """记录执行结果"""
        with self._lock:
            if skill_id not in self._metrics:
                self._metrics[skill_id] = HealthMetric(
                    skill_id=skill_id,
                    status=HealthStatus.UNKNOWN,
                    score=1.0,
                    last_check=datetime.now().isoformat()
                )
            
            metric = self._metrics[skill_id]
            
            if success:
                metric.success_count += 1
            else:
                metric.error_count += 1
            
            # 更新平均执行时间
            total = metric.success_count + metric.error_count
            metric.avg_duration_ms = (
                (metric.avg_duration_ms * (total - 1) + duration_ms) / total
            )
            
            # 计算健康分数
            if total > 0:
                metric.score = metric.success_count / total
            
            # 更新状态
            if metric.score >= 0.9:
                metric.status = HealthStatus.HEALTHY
            elif metric.score >= 0.7:
                metric.status = HealthStatus.DEGRADED
            else:
                metric.status = HealthStatus.UNHEALTHY
            
            metric.last_check = datetime.now().isoformat()
            
            # 记录历史
            if skill_id not in self._history:
                self._history[skill_id] = []
            
            self._history[skill_id].append({
                "timestamp": datetime.now().isoformat(),
                "success": success,
                "duration_ms": duration_ms,
                "error": error
            })
    
    def get_health(self, skill_id: str) -> Optional[HealthMetric]:
        """获取健康指标"""
        return self._metrics.get(skill_id)
    
    def get_status(self, skill_id: str) -> HealthStatus:
        """获取健康状态"""
        metric = self._metrics.get(skill_id)
        return metric.status if metric else HealthStatus.UNKNOWN
    
    def get_score(self, skill_id: str) -> float:
        """获取健康分数"""
        metric = self._metrics.get(skill_id)
        return metric.score if metric else 0.0
    
    def is_healthy(self, skill_id: str) -> bool:
        """检查是否健康"""
        status = self.get_status(skill_id)
        return status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
    
    def list_unhealthy(self) -> List[str]:
        """列出不健康的技能"""
        return [
            skill_id for skill_id, metric in self._metrics.items()
            if metric.status == HealthStatus.UNHEALTHY
        ]
    
    def get_history(self, skill_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取执行历史"""
        history = self._history.get(skill_id, [])
        return history[-limit:]
    
    def reset(self, skill_id: str):
        """重置健康指标"""
        with self._lock:
            if skill_id in self._metrics:
                del self._metrics[skill_id]
            if skill_id in self._history:
                del self._history[skill_id]
