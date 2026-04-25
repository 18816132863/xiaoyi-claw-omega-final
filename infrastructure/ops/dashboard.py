#!/usr/bin/env python3
"""
运营监控面板 - V2.8.0

展示：
- 当前运行中的项目
- 工作流使用频率
- 任务失败分布
- 技能稳定性排行
- 产物输出数量
- 自动化动作统计
- 当前系统健康度
- 最近异常与告警
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
from enum import Enum

from infrastructure.path_resolver import get_project_root

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Alert:
    """告警"""
    alert_id: str
    level: str
    source: str
    message: str
    timestamp: str
    resolved: bool

@dataclass
class SystemHealth:
    """系统健康度"""
    status: str
    score: float
    components: Dict[str, float]
    issues: List[str]

class OpsDashboard:
    """运营监控面板"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.dashboard_path = self.project_root / 'ops' / 'dashboard_data.json'
        
        # 告警列表
        self.alerts: List[Alert] = []
        
        # 统计数据
        self.stats = {
            "total_projects": 0,
            "active_projects": 0,
            "workflow_usage": defaultdict(int),
            "task_failures": defaultdict(int),
            "skill_stability": defaultdict(lambda: {"success": 0, "failure": 0}),
            "product_count": 0,
            "auto_actions": {"total": 0, "success": 0, "failed": 0},
        }
        
        self._load()
    
    def _load(self):
        """加载数据"""
        if self.dashboard_path.exists():
            data = json.loads(self.dashboard_path.read_text(encoding='utf-8'))
            self.alerts = [Alert(**a) for a in data.get("alerts", [])]
            self.stats = data.get("stats", self.stats)
    
    def _save(self):
        """保存数据"""
        self.dashboard_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "alerts": [asdict(a) for a in self.alerts],
            "stats": self.stats,
            "updated": datetime.now().isoformat()
        }
        self.dashboard_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def add_alert(self, level: str, source: str, message: str) -> Alert:
        """添加告警"""
        alert = Alert(
            alert_id=f"alert_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            level=level,
            source=source,
            message=message,
            timestamp=datetime.now().isoformat(),
            resolved=False
        )
        
        self.alerts.append(alert)
        
        # 限制告警数量
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        self._save()
        
        return alert
    
    def resolve_alert(self, alert_id: str):
        """解决告警"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                self._save()
                break
    
    def record_workflow_usage(self, workflow: str):
        """记录工作流使用"""
        self.stats["workflow_usage"][workflow] += 1
        self._save()
    
    def record_task_failure(self, failure_type: str):
        """记录任务失败"""
        self.stats["task_failures"][failure_type] += 1
        self._save()
    
    def record_skill_result(self, skill: str, success: bool):
        """记录技能结果"""
        if success:
            self.stats["skill_stability"][skill]["success"] += 1
        else:
            self.stats["skill_stability"][skill]["failure"] += 1
        self._save()
    
    def update_project_count(self, total: int, active: int):
        """更新项目数量"""
        self.stats["total_projects"] = total
        self.stats["active_projects"] = active
        self._save()
    
    def update_product_count(self, count: int):
        """更新产物数量"""
        self.stats["product_count"] = count
        self._save()
    
    def record_auto_action(self, success: bool):
        """记录自动化动作"""
        self.stats["auto_actions"]["total"] += 1
        if success:
            self.stats["auto_actions"]["success"] += 1
        else:
            self.stats["auto_actions"]["failed"] += 1
        self._save()
    
    def calculate_health(self) -> SystemHealth:
        """计算系统健康度"""
        components = {}
        issues = []
        
        # 工作流健康度
        workflow_usage = self.stats.get("workflow_usage", {})
        if workflow_usage:
            total_usage = sum(workflow_usage.values())
            components["workflows"] = min(1.0, total_usage / 100)  # 100次为满分
        else:
            components["workflows"] = 0.5
            issues.append("无工作流使用记录")
        
        # 技能健康度
        skill_stability = self.stats.get("skill_stability", {})
        if skill_stability:
            total_success = sum(s.get("success", 0) for s in skill_stability.values())
            total_failure = sum(s.get("failure", 0) for s in skill_stability.values())
            total = total_success + total_failure
            components["skills"] = total_success / max(total, 1)
        else:
            components["skills"] = 0.5
        
        # 自动化健康度
        auto_actions = self.stats.get("auto_actions", {})
        total_auto = auto_actions.get("total", 0)
        if total_auto > 0:
            components["automation"] = auto_actions.get("success", 0) / total_auto
        else:
            components["automation"] = 0.5
        
        # 告警健康度
        unresolved = sum(1 for a in self.alerts if not a.resolved)
        critical_alerts = sum(1 for a in self.alerts if a.level == AlertLevel.CRITICAL.value and not a.resolved)
        components["alerts"] = max(0, 1 - unresolved * 0.1 - critical_alerts * 0.3)
        
        # 计算总分
        score = sum(components.values()) / len(components)
        
        # 确定状态
        if score >= 0.9:
            status = HealthStatus.HEALTHY.value
        elif score >= 0.7:
            status = HealthStatus.DEGRADED.value
        elif score >= 0.5:
            status = HealthStatus.UNHEALTHY.value
        else:
            status = HealthStatus.CRITICAL.value
            issues.append("系统健康度严重不足")
        
        return SystemHealth(
            status=status,
            score=score,
            components=components,
            issues=issues
        )
    
    def get_active_projects(self) -> List[Dict]:
        """获取运行中的项目"""
        # 简化实现
        return [
            {"name": f"项目{i}", "status": "active"}
            for i in range(self.stats.get("active_projects", 0))
        ]
    
    def get_workflow_usage_ranking(self, limit: int = 10) -> List[Dict]:
        """获取工作流使用频率排行"""
        usage = self.stats.get("workflow_usage", {})
        sorted_usage = sorted(usage.items(), key=lambda x: x[1], reverse=True)
        return [{"workflow": w, "count": c} for w, c in sorted_usage[:limit]]
    
    def get_task_failure_distribution(self) -> List[Dict]:
        """获取任务失败分布"""
        failures = self.stats.get("task_failures", {})
        return [{"type": t, "count": c} for t, c in failures.items()]
    
    def get_skill_stability_ranking(self, limit: int = 10) -> List[Dict]:
        """获取技能稳定性排行"""
        stability = self.stats.get("skill_stability", {})
        
        rankings = []
        for skill, stats in stability.items():
            total = stats.get("success", 0) + stats.get("failure", 0)
            if total > 0:
                rate = stats.get("success", 0) / total
                rankings.append({"skill": skill, "stability": rate, "total_calls": total})
        
        return sorted(rankings, key=lambda x: x["stability"])[:limit]
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """获取最近告警"""
        unresolved = [a for a in self.alerts if not a.resolved]
        return [asdict(a) for a in unresolved[-limit:]]
    
    def get_dashboard_summary(self) -> Dict:
        """获取面板摘要"""
        health = self.calculate_health()
        
        return {
            "health": {
                "status": health.status,
                "score": health.score,
                "issues": health.issues
            },
            "projects": {
                "total": self.stats.get("total_projects", 0),
                "active": self.stats.get("active_projects", 0)
            },
            "products": {
                "count": self.stats.get("product_count", 0)
            },
            "automation": self.stats.get("auto_actions", {}),
            "alerts": {
                "total": len(self.alerts),
                "unresolved": sum(1 for a in self.alerts if not a.resolved)
            }
        }
    
    def get_full_report(self) -> str:
        """生成完整报告"""
        health = self.calculate_health()
        summary = self.get_dashboard_summary()
        
        status_emoji = {
            HealthStatus.HEALTHY.value: "✅",
            HealthStatus.DEGRADED.value: "⚠️",
            HealthStatus.UNHEALTHY.value: "❌",
            HealthStatus.CRITICAL.value: "💀"
        }
        
        lines = [
            "# 运营监控面板",
            "",
            f"## 系统健康度: {status_emoji.get(health.status, '❓')} {health.status}",
            f"**分数**: {health.score:.2f}",
            "",
            "### 组件健康度",
            ""
        ]
        
        for component, score in health.components.items():
            lines.append(f"- {component}: {score*100:.0f}%")
        
        if health.issues:
            lines.extend(["", "### 问题", ""])
            for issue in health.issues:
                lines.append(f"- ⚠️ {issue}")
        
        lines.extend([
            "",
            "## 项目状态",
            f"- 总项目数: {summary['projects']['total']}",
            f"- 运行中: {summary['projects']['active']}",
            "",
            "## 产物统计",
            f"- 产物数量: {summary['products']['count']}",
            "",
            "## 自动化统计",
            f"- 总动作: {summary['automation'].get('total', 0)}",
            f"- 成功: {summary['automation'].get('success', 0)}",
            f"- 失败: {summary['automation'].get('failed', 0)}",
            "",
            "## 告警",
            f"- 总数: {summary['alerts']['total']}",
            f"- 未解决: {summary['alerts']['unresolved']}",
            "",
            "## 工作流使用 TOP 5",
            ""
        ])
        
        for wf in self.get_workflow_usage_ranking(5):
            lines.append(f"- {wf['workflow']}: {wf['count']}次")
        
        lines.extend([
            "",
            "## 技能稳定性（最低5个）",
            ""
        ])
        
        for skill in self.get_skill_stability_ranking(5):
            lines.append(f"- {skill['skill']}: {skill['stability']*100:.0f}% ({skill['total_calls']}次)")
        
        return "\n".join(lines)

# 全局实例
_ops_dashboard = None

def get_ops_dashboard() -> OpsDashboard:
    global _ops_dashboard
    if _ops_dashboard is None:
        _ops_dashboard = OpsDashboard()
    return _ops_dashboard
