#!/usr/bin/env python3
"""
GitHub Summary 通道适配器 - V1.0.0

职责：
1. 读取 latest_alerts.json
2. 生成 GitHub Actions Summary Markdown
3. 供 workflow 调用，不再散写大段解析逻辑
"""

import json
from pathlib import Path
from typing import Dict, Optional

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent

def load_alerts() -> Optional[Dict]:
    """加载最新告警"""
    root = get_project_root()
    alerts_path = root / "reports/alerts/latest_alerts.json"
    if not alerts_path.exists():
        return None
    try:
        return json.load(open(alerts_path, encoding='utf-8'))
    except:
        return None

def load_incident_summary() -> Optional[Dict]:
    """加载 incident 摘要"""
    root = get_project_root()
    summary_path = root / "reports/alerts/incident_summary.json"
    if not summary_path.exists():
        return None
    try:
        return json.load(open(summary_path, encoding='utf-8'))
    except:
        return None

def generate_summary_markdown() -> str:
    """生成 GitHub Summary Markdown"""
    alerts = load_alerts()
    incident_summary = load_incident_summary()
    
    lines = []
    lines.append("## 📋 Alerts Summary")
    lines.append("")
    
    if not alerts:
        lines.append("⚠️ 未找到告警报告")
        return "\n".join(lines)
    
    # 总体状态
    if alerts.get("has_blocking_alerts"):
        lines.append("### 🚨 存在阻塞级告警")
    else:
        lines.append("### ✅ 无阻塞级告警")
    lines.append("")
    
    # 统计
    lines.append("| 指标 | 值 |")
    lines.append("|------|-----|")
    lines.append(f"| 总告警数 | {alerts.get('total_alerts', 0)} |")
    lines.append(f"| 阻塞级 | {alerts.get('blocking_count', 0)} |")
    lines.append(f"| 警告级 | {alerts.get('warning_count', 0)} |")
    lines.append(f"| 来源 | {alerts.get('source_workflow', 'unknown')} |")
    lines.append(f"| Profile | {alerts.get('profile', 'unknown')} |")
    lines.append("")
    
    # 告警详情
    if alerts.get("alerts"):
        lines.append("### 告警详情")
        lines.append("")
        for alert in alerts["alerts"]:
            icon = "🚨" if alert["severity"] == "blocking" else "⚠️"
            lines.append(f"{icon} **{alert['alert_type']}**: {alert['message']}")
        lines.append("")
    
    # 阻塞原因
    if alerts.get("blocked_reasons"):
        lines.append("### 阻塞原因")
        lines.append("")
        for reason in alerts["blocked_reasons"]:
            lines.append(f"- {reason}")
        lines.append("")
    
    # 强回归
    if alerts.get("strong_regressions"):
        lines.append("### 🚨 强回归")
        lines.append("")
        for reg in alerts["strong_regressions"]:
            if isinstance(reg, dict):
                change = reg.get("change", {})
                lines.append(f"- {change.get('field', '?')}: {change.get('from', '?')} → {change.get('to', '?')}")
            else:
                lines.append(f"- {reg}")
        lines.append("")
    
    # 弱回归
    if alerts.get("weak_regressions"):
        lines.append("### ⚠️ 弱回归")
        lines.append("")
        for reg in alerts["weak_regressions"]:
            if isinstance(reg, dict):
                change = reg.get("change", {})
                lines.append(f"- {change.get('field', '?')}: {change.get('from', '?')} → {change.get('to', '?')}")
            else:
                lines.append(f"- {reg}")
        lines.append("")
    
    # 跳过的外部技能
    skipped = alerts.get("skipped_external", [])
    if skipped:
        lines.append(f"### 📋 Skipped External ({len(skipped)})")
        lines.append("")
        for s in skipped[:5]:
            if isinstance(s, dict):
                lines.append(f"- {s.get('skill', '?')}: {s.get('reason', '')}")
            else:
                lines.append(f"- {s}")
        if len(skipped) > 5:
            lines.append(f"- ... 还有 {len(skipped) - 5} 个")
        lines.append("")
    
    # 建议操作
    if alerts.get("recommended_actions"):
        lines.append("### 💡 建议操作")
        lines.append("")
        for action in alerts["recommended_actions"]:
            lines.append(f"- {action}")
        lines.append("")
    
    # Incident 状态
    summary = alerts.get("incident_status_summary", {}) or incident_summary
    if summary:
        lines.append("### 📊 Incident 状态")
        lines.append("")
        lines.append(f"- Open: {summary.get('open_incidents', 0)}")
        lines.append(f"- Resolved: {summary.get('resolved_incidents', 0)}")
        if alerts.get("incident_created"):
            lines.append("- ✅ 已创建新 incident")
        if alerts.get("incident_resolved"):
            lines.append("- ✅ 已自动关闭 incident")
        lines.append("")
    
    return "\n".join(lines)

def print_summary():
    """打印 Summary"""
    print(generate_summary_markdown())

if __name__ == "__main__":
    print_summary()
