"""Evaluation Aggregator - 评估聚合器"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
import json
import os


@dataclass
class AggregatedMetrics:
    """聚合指标"""
    timestamp: str
    task_metrics: Dict[str, Any]
    skill_metrics: Dict[str, Any]
    memory_metrics: Dict[str, Any]
    summary: Dict[str, Any]
    details: Dict[str, Any] = field(default_factory=dict)


class EvaluationAggregator:
    """
    评估聚合器
    
    职责：
    - 汇总三类指标
    - 生成总览对象
    - 保存聚合报告
    """
    
    def __init__(self, metrics_dir: str = "reports/metrics"):
        self.metrics_dir = metrics_dir
        self._ensure_dir()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(self.metrics_dir, exist_ok=True)
    
    def load_task_metrics(self) -> Optional[Dict[str, Any]]:
        """加载任务指标"""
        path = os.path.join(self.metrics_dir, "task_metrics.json")
        if not os.path.exists(path):
            return None
        
        with open(path, 'r') as f:
            return json.load(f)
    
    def load_skill_metrics(self) -> Optional[Dict[str, Any]]:
        """加载技能指标"""
        path = os.path.join(self.metrics_dir, "skill_metrics.json")
        if not os.path.exists(path):
            return None
        
        with open(path, 'r') as f:
            return json.load(f)
    
    def load_memory_metrics(self) -> Optional[Dict[str, Any]]:
        """加载记忆指标"""
        path = os.path.join(self.metrics_dir, "memory_metrics.json")
        if not os.path.exists(path):
            return None
        
        with open(path, 'r') as f:
            return json.load(f)
    
    def aggregate(self) -> AggregatedMetrics:
        """
        聚合所有指标
        
        Returns:
            AggregatedMetrics
        """
        task_metrics = self.load_task_metrics() or {}
        skill_metrics = self.load_skill_metrics() or {}
        memory_metrics = self.load_memory_metrics() or {}
        
        # 生成摘要
        summary = {
            "task_success_rate": task_metrics.get("success_rate", 0.0),
            "skill_failure_rate": skill_metrics.get("aggregate", {}).get("failure_rate", 0.0),
            "memory_hit_rate": memory_metrics.get("hit_rate", 0.0),
            "overall_health": self._compute_health(
                task_metrics.get("success_rate", 0.0),
                skill_metrics.get("aggregate", {}).get("failure_rate", 0.0),
                memory_metrics.get("hit_rate", 0.0)
            )
        }
        
        return AggregatedMetrics(
            timestamp=datetime.now().isoformat(),
            task_metrics=task_metrics,
            skill_metrics=skill_metrics,
            memory_metrics=memory_metrics,
            summary=summary,
            details={
                "task_total": task_metrics.get("total", 0),
                "skill_total_calls": skill_metrics.get("aggregate", {}).get("total_calls", 0),
                "memory_total_queries": memory_metrics.get("total_queries", 0)
            }
        )
    
    def _compute_health(
        self,
        task_success_rate: float,
        skill_failure_rate: float,
        memory_hit_rate: float
    ) -> str:
        """计算健康状态"""
        # 加权评分
        score = (
            task_success_rate * 0.4 +
            (1 - skill_failure_rate) * 0.3 +
            memory_hit_rate * 0.3
        )
        
        if score >= 0.9:
            return "excellent"
        elif score >= 0.7:
            return "good"
        elif score >= 0.5:
            return "fair"
        else:
            return "poor"
    
    def save(self, metrics: AggregatedMetrics = None) -> str:
        """
        保存聚合报告
        
        Args:
            metrics: 聚合指标
        
        Returns:
            文件路径
        """
        if metrics is None:
            metrics = self.aggregate()
        
        path = os.path.join(self.metrics_dir, "aggregated_metrics.json")
        data = {
            "timestamp": metrics.timestamp,
            "summary": metrics.summary,
            "task_metrics": metrics.task_metrics,
            "skill_metrics": metrics.skill_metrics,
            "memory_metrics": metrics.memory_metrics,
            "details": metrics.details
        }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return path
    
    def generate_report(self) -> Dict[str, Any]:
        """
        生成报告
        
        Returns:
            Dict with full report
        """
        metrics = self.aggregate()
        path = self.save(metrics)
        
        return {
            "status": "success",
            "report_path": path,
            "summary": metrics.summary,
            "timestamp": metrics.timestamp
        }
