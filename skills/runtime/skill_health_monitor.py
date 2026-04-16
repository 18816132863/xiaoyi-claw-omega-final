"""
Skill Health Monitor - 技能健康监控器
负责监控技能执行健康状态
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import os


@dataclass
class HealthMetrics:
    """健康指标"""
    skill_id: str
    version: str
    total_executions: int = 0
    success_count: int = 0
    failure_count: int = 0
    timeout_count: int = 0
    total_latency_ms: int = 0
    recent_errors: List[Dict[str, Any]] = field(default_factory=list)
    last_success_at: Optional[str] = None
    last_failure_at: Optional[str] = None
    health_status: str = "unknown"
    health_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "version": self.version,
            "total_executions": self.total_executions,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "timeout_count": self.timeout_count,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,
            "avg_latency_ms": self.avg_latency_ms,
            "recent_errors": self.recent_errors[-10:],  # 最近 10 个错误
            "last_success_at": self.last_success_at,
            "last_failure_at": self.last_failure_at,
            "health_status": self.health_status,
            "health_score": self.health_score
        }

    @property
    def success_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.success_count / self.total_executions

    @property
    def failure_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.failure_count / self.total_executions

    @property
    def avg_latency_ms(self) -> float:
        if self.success_count == 0:
            return 0.0
        return self.total_latency_ms / self.success_count


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    skill_id: str
    version: str
    health_status: str
    health_score: float
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "version": self.version,
            "health_status": self.health_status,
            "health_score": self.health_score,
            "issues": self.issues,
            "recommendations": self.recommendations
        }


class SkillHealthMonitor:
    """
    技能健康监控器

    职责：
    - 记录执行结果
    - 计算健康指标
    - 判断健康状态
    - 生成健康报告
    """

    def __init__(self, index_path: str = "skills/registry/skill_health_index.json"):
        self.index_path = index_path
        self._metrics: Dict[str, HealthMetrics] = {}
        self._health_index: Dict[str, Dict[str, Any]] = {}
        self._ensure_dir()

    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

    def record_execution(
        self,
        skill_id: str,
        version: str,
        success: bool,
        latency_ms: int = 0,
        error: str = None,
        error_type: str = None
    ):
        """
        记录执行结果

        Args:
            skill_id: 技能 ID
            version: 版本
            success: 是否成功
            latency_ms: 延迟（毫秒）
            error: 错误信息
            error_type: 错误类型
        """
        cache_key = f"{skill_id}@{version}"

        if cache_key not in self._metrics:
            self._metrics[cache_key] = HealthMetrics(
                skill_id=skill_id,
                version=version
            )

        metrics = self._metrics[cache_key]
        metrics.total_executions += 1
        now = datetime.now().isoformat()

        if success:
            metrics.success_count += 1
            metrics.total_latency_ms += latency_ms
            metrics.last_success_at = now
        else:
            metrics.failure_count += 1
            metrics.last_failure_at = now

            # 记录错误
            if error:
                error_record = {
                    "timestamp": now,
                    "error": error,
                    "error_type": error_type or "unknown"
                }
                metrics.recent_errors.append(error_record)

                # 只保留最近 100 个错误
                if len(metrics.recent_errors) > 100:
                    metrics.recent_errors = metrics.recent_errors[-100:]

        # 更新健康状态
        self._update_health_status(metrics)

        # 持久化
        self._persist_metrics(metrics)

    def _update_health_status(self, metrics: HealthMetrics):
        """更新健康状态"""
        if metrics.total_executions < 5:
            # 样本太少，状态未知
            metrics.health_status = "unknown"
            metrics.health_score = 0.5
            return

        # 计算健康分数
        success_rate = metrics.success_rate
        avg_latency = metrics.avg_latency_ms

        # 健康分数 = 成功率 * 0.7 + 延迟分数 * 0.3
        latency_score = 1.0
        if avg_latency > 10000:  # > 10s
            latency_score = 0.3
        elif avg_latency > 5000:  # > 5s
            latency_score = 0.5
        elif avg_latency > 2000:  # > 2s
            latency_score = 0.7
        elif avg_latency > 1000:  # > 1s
            latency_score = 0.9

        metrics.health_score = success_rate * 0.7 + latency_score * 0.3

        # 判断健康状态
        if metrics.health_score >= 0.9:
            metrics.health_status = "healthy"
        elif metrics.health_score >= 0.7:
            metrics.health_status = "degraded"
        else:
            metrics.health_status = "unhealthy"

    def _persist_metrics(self, metrics: HealthMetrics):
        """持久化指标"""
        self._health_index[f"{metrics.skill_id}@{metrics.version}"] = metrics.to_dict()

        try:
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(self._health_index, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def check_health(
        self,
        skill_id: str,
        version: str = None
    ) -> HealthCheckResult:
        """
        检查健康状态

        Args:
            skill_id: 技能 ID
            version: 版本（可选）

        Returns:
            HealthCheckResult
        """
        if version:
            cache_key = f"{skill_id}@{version}"
            metrics = self._metrics.get(cache_key)
        else:
            # 获取最新版本的指标
            matching = [
                m for k, m in self._metrics.items()
                if m.skill_id == skill_id
            ]
            if not matching:
                metrics = None
            else:
                # 选择执行次数最多的版本
                metrics = max(matching, key=lambda m: m.total_executions)

        if not metrics:
            return HealthCheckResult(
                skill_id=skill_id,
                version=version or "unknown",
                health_status="unknown",
                health_score=0.0,
                issues=["No execution data available"]
            )

        issues = []
        recommendations = []

        # 检查成功率
        if metrics.success_rate < 0.5:
            issues.append(f"Low success rate: {metrics.success_rate:.1%}")
            recommendations.append("Investigate recent errors and consider fallback")

        # 检查延迟
        if metrics.avg_latency_ms > 5000:
            issues.append(f"High latency: {metrics.avg_latency_ms:.0f}ms")
            recommendations.append("Consider optimization or timeout adjustment")

        # 检查错误频率
        recent_error_count = len([
            e for e in metrics.recent_errors
            if datetime.fromisoformat(e["timestamp"]) > datetime.now() - timedelta(hours=1)
        ])
        if recent_error_count > 10:
            issues.append(f"High error frequency: {recent_error_count} errors in last hour")
            recommendations.append("Consider disabling or degrading the skill")

        return HealthCheckResult(
            skill_id=skill_id,
            version=metrics.version,
            health_status=metrics.health_status,
            health_score=metrics.health_score,
            issues=issues,
            recommendations=recommendations
        )

    def get_metrics(self, skill_id: str, version: str = None) -> Optional[HealthMetrics]:
        """获取健康指标"""
        if version:
            return self._metrics.get(f"{skill_id}@{version}")

        matching = [
            m for k, m in self._metrics.items()
            if m.skill_id == skill_id
        ]
        if not matching:
            return None

        return max(matching, key=lambda m: m.total_executions)

    def get_health_index(self) -> Dict[str, Any]:
        """获取健康索引"""
        return {
            "updated_at": datetime.now().isoformat(),
            "skills": {
                k: {
                    "health_status": v.get("health_status", "unknown"),
                    "health_score": v.get("health_score", 0.0),
                    "success_rate": v.get("success_rate", 0.0),
                    "avg_latency_ms": v.get("avg_latency_ms", 0)
                }
                for k, v in self._health_index.items()
            }
        }

    def get_degraded_skills(self) -> List[str]:
        """获取降级技能列表"""
        return [
            k for k, v in self._health_index.items()
            if v.get("health_status") in ["degraded", "unhealthy"]
        ]

    def reset_metrics(self, skill_id: str, version: str = None):
        """重置指标"""
        if version:
            cache_key = f"{skill_id}@{version}"
            if cache_key in self._metrics:
                del self._metrics[cache_key]
            if cache_key in self._health_index:
                del self._health_index[cache_key]
        else:
            # 删除所有版本
            keys_to_delete = [
                k for k in self._metrics.keys()
                if k.startswith(f"{skill_id}@")
            ]
            for k in keys_to_delete:
                del self._metrics[k]
                if k in self._health_index:
                    del self._health_index[k]


# 全局单例
_skill_health_monitor = None


def get_skill_health_monitor() -> SkillHealthMonitor:
    """获取健康监控器单例"""
    global _skill_health_monitor
    if _skill_health_monitor is None:
        _skill_health_monitor = SkillHealthMonitor()
    return _skill_health_monitor
