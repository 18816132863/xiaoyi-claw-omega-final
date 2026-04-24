#!/usr/bin/env python3
"""
运维看板构建器 - V1.0.0

职责：
1. 读取所有 latest 报告
2. 读取 history 快照
3. 生成统一 dashboard 输出 (json/md/html)
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent

def load_json(path: Path) -> Optional[Dict]:
    """加载 JSON 文件"""
    if not path.exists():
        return None
    try:
        return json.load(open(path, encoding='utf-8'))
    except:
        return None

def load_latest_reports(root: Path) -> Dict[str, Any]:
    """加载所有 latest 报告"""
    return {
        "runtime": load_json(root / "reports/runtime_integrity.json"),
        "quality": load_json(root / "reports/quality_gate.json"),
        "release": load_json(root / "reports/release_gate.json"),
        "nightly": load_json(root / "reports/nightly_audit.json"),
        "alerts": load_json(root / "reports/alerts/latest_alerts.json"),
        "incident_summary": load_json(root / "reports/alerts/incident_summary.json"),
        "trends": load_json(root / "reports/trends/gate_trend.json"),
    }

def load_history_snapshots(root: Path, limit: int = 10) -> Dict[str, List]:
    """加载历史快照"""
    history = {
        "runtime": [],
        "quality": [],
        "release": [],
        "alerts": []
    }
    
    # Runtime history
    runtime_dir = root / "reports/history/runtime"
    if runtime_dir.exists():
        files = sorted(runtime_dir.glob("*.json"), reverse=True)[:limit]
        for f in files:
            data = load_json(f)
            if data:
                history["runtime"].append(data)
    
    # Quality history
    quality_dir = root / "reports/history/quality"
    if quality_dir.exists():
        files = sorted(quality_dir.glob("*.json"), reverse=True)[:limit]
        for f in files:
            data = load_json(f)
            if data:
                history["quality"].append(data)
    
    # Release history
    release_dir = root / "reports/history/release"
    if release_dir.exists():
        files = sorted(release_dir.glob("*.json"), reverse=True)[:limit]
        for f in files:
            data = load_json(f)
            if data:
                history["release"].append(data)
    
    # Alerts history
    alerts_dir = root / "reports/alerts/history"
    if alerts_dir.exists():
        files = sorted(alerts_dir.glob("*.json"), reverse=True)[:limit]
        for f in files:
            data = load_json(f)
            if data:
                history["alerts"].append(data)
    
    return history

def build_overview_section(latest: Dict) -> Dict:
    """构建总览区"""
    runtime = latest.get("runtime") or {}
    quality = latest.get("quality") or {}
    release = latest.get("release") or {}
    alerts = latest.get("alerts") or {}
    incident_summary = latest.get("incident_summary") or {}
    
    return {
        "generated_at": datetime.now().isoformat(),
        "runtime_status": runtime.get("overall_passed", False),
        "quality_status": quality.get("overall_passed", False),
        "release_status": release.get("can_release", False),
        "blocking_alerts": alerts.get("blocking_count", 0),
        "warning_alerts": alerts.get("warning_count", 0),
        "open_incidents": incident_summary.get("open_incidents", 0),
        "resolved_incidents": incident_summary.get("resolved_incidents", 0),
        "can_release": release.get("can_release", False),
        "profile": runtime.get("profile", "unknown")
    }

def build_runtime_section(latest: Dict) -> Dict:
    """构建运行时区"""
    runtime = latest.get("runtime") or {}
    
    return {
        "verified_at": runtime.get("verified_at"),
        "profile": runtime.get("profile"),
        "overall_passed": runtime.get("overall_passed", False),
        "p0_count": runtime.get("p0_count", 0),
        "p1_count": runtime.get("p1_count", 0),
        "p2_count": runtime.get("p2_count", 0),
        "local_status": runtime.get("local_status", "unknown"),
        "integration_status": runtime.get("integration_status", "unknown"),
        "external_status": runtime.get("external_status", "unknown"),
        "skipped_count": runtime.get("skipped_count", 0),
        "failure_reasons": runtime.get("failure_reasons", []),
        "skill_total": runtime.get("skill_total", 0),
        "callable_total": runtime.get("callable_total", 0)
    }

def build_quality_section(latest: Dict) -> Dict:
    """构建质量区"""
    quality = latest.get("quality") or {}
    
    checks = quality.get("checks", {})
    checks_summary = []
    for name, check in checks.items():
        checks_summary.append({
            "name": name,
            "status": check.get("status", "unknown"),
            "message": check.get("message", "")
        })
    
    return {
        "verified_at": quality.get("verified_at"),
        "overall_passed": quality.get("overall_passed", False),
        "checks": checks_summary
    }

def build_release_section(latest: Dict) -> Dict:
    """构建发布区"""
    release = latest.get("release") or {}
    
    return {
        "checked_at": release.get("checked_at"),
        "can_release": release.get("can_release", False),
        "blocked_reasons": release.get("blocked_reasons", []),
        "skipped_external": release.get("skipped_external", [])
    }

def build_alerts_section(latest: Dict) -> Dict:
    """构建告警区"""
    alerts = latest.get("alerts") or {}
    
    return {
        "generated_at": alerts.get("generated_at"),
        "source_workflow": alerts.get("source_workflow"),
        "profile": alerts.get("profile"),
        "has_blocking_alerts": alerts.get("has_blocking_alerts", False),
        "has_warning_alerts": alerts.get("has_warning_alerts", False),
        "total_alerts": alerts.get("total_alerts", 0),
        "blocking_count": alerts.get("blocking_count", 0),
        "warning_count": alerts.get("warning_count", 0),
        "alerts": alerts.get("alerts", []),
        "blocked_reasons": alerts.get("blocked_reasons", []),
        "strong_regressions": alerts.get("strong_regressions", []),
        "weak_regressions": alerts.get("weak_regressions", []),
        "recommended_actions": alerts.get("recommended_actions", [])
    }

def build_incidents_section(latest: Dict) -> Dict:
    """构建 Incident 区"""
    incident_summary = latest.get("incident_summary") or {}
    alerts = latest.get("alerts") or {}
    incident_status = alerts.get("incident_status_summary", {})
    
    return {
        "total_incidents": incident_summary.get("total_incidents", 0),
        "open_incidents": incident_summary.get("open_incidents", 0),
        "resolved_incidents": incident_summary.get("resolved_incidents", 0),
        "latest_opened_at": incident_summary.get("latest_opened_at"),
        "latest_resolved_at": incident_summary.get("latest_resolved_at"),
        "incident_created": alerts.get("incident_created", False),
        "incident_resolved": alerts.get("incident_resolved", False)
    }

def build_trends_section(latest: Dict, history: Dict) -> Dict:
    """构建趋势区"""
    trends = latest.get("trends") or []
    
    # 最近 N 次结果
    recent_trends = trends[-10:] if trends else []
    
    return {
        "total_records": len(trends),
        "recent_trends": recent_trends,
        "latest": recent_trends[-1] if recent_trends else None,
        "previous": recent_trends[-2] if len(recent_trends) > 1 else None
    }

def build_recent_changes_section(latest: Dict, history: Dict) -> Dict:
    """构建最近变化区"""
    changes = {
        "last_blocked_reason": None,
        "last_resolved_incident": None,
        "last_strong_regression": None,
        "last_can_release_false": None,
        "nightly_diff": None
    }
    
    # 从 alerts history 找最近变化
    alerts_history = history.get("alerts", [])
    if len(alerts_history) >= 2:
        curr = alerts_history[0]
        prev = alerts_history[1]
        
        diff = {
            "blocking_count_change": curr.get("blocking_count", 0) - prev.get("blocking_count", 0),
            "warning_count_change": curr.get("warning_count", 0) - prev.get("warning_count", 0),
            "has_new_blocking": curr.get("has_blocking_alerts", False) and not prev.get("has_blocking_alerts", False),
            "has_resolved_blocking": not curr.get("has_blocking_alerts", False) and prev.get("has_blocking_alerts", False)
        }
        changes["nightly_diff"] = diff
    
    # 找最近 blocked
    for alert in alerts_history:
        if alert.get("blocked_reasons"):
            changes["last_blocked_reason"] = {
                "at": alert.get("generated_at"),
                "reasons": alert.get("blocked_reasons", [])[:3]
            }
            break
    
    # 找最近 strong regression
    for alert in alerts_history:
        if alert.get("strong_regressions"):
            changes["last_strong_regression"] = {
                "at": alert.get("generated_at"),
                "count": len(alert.get("strong_regressions", []))
            }
            break
    
    # 找最近 can_release=false
    release_history = history.get("release", [])
    for rel in release_history:
        if not rel.get("can_release", True):
            changes["last_can_release_false"] = {
                "at": rel.get("checked_at"),
                "reasons": rel.get("blocked_reasons", [])[:3]
            }
            break
    
    return changes

def build_dashboard() -> Dict:
    """构建完整看板"""
    root = get_project_root()
    
    # 加载数据
    latest = load_latest_reports(root)
    history = load_history_snapshots(root)
    
    # 构建各 section
    dashboard = {
        "generated_at": datetime.now().isoformat(),
        "version": "1.0.0",
        
        # 各区数据
        "overview": build_overview_section(latest),
        "runtime": build_runtime_section(latest),
        "quality": build_quality_section(latest),
        "release": build_release_section(latest),
        "alerts": build_alerts_section(latest),
        "incidents": build_incidents_section(latest),
        "trends": build_trends_section(latest, history),
        "recent_changes": build_recent_changes_section(latest, history),
        
        # 原始数据引用
        "history": {
            "runtime_count": len(history.get("runtime", [])),
            "quality_count": len(history.get("quality", [])),
            "release_count": len(history.get("release", [])),
            "alerts_count": len(history.get("alerts", []))
        }
    }
    
    return dashboard

def generate_markdown(dashboard: Dict) -> str:
    """生成 Markdown 看板"""
    lines = []
    
    # 标题
    lines.append("# 📊 运维观测看板")
    lines.append("")
    lines.append(f"**生成时间**: {dashboard['generated_at']}")
    lines.append("")
    
    # 总览
    overview = dashboard.get("overview", {})
    lines.append("## 🎯 总览")
    lines.append("")
    lines.append("| 指标 | 状态 |")
    lines.append("|------|------|")
    lines.append(f"| Runtime | {'✅' if overview.get('runtime_status') else '❌'} |")
    lines.append(f"| Quality | {'✅' if overview.get('quality_status') else '❌'} |")
    lines.append(f"| Release | {'✅' if overview.get('release_status') else '❌'} |")
    lines.append(f"| Can Release | {'✅' if overview.get('can_release') else '❌'} |")
    lines.append(f"| Blocking Alerts | {overview.get('blocking_alerts', 0)} |")
    lines.append(f"| Open Incidents | {overview.get('open_incidents', 0)} |")
    lines.append("")
    
    # Runtime
    runtime = dashboard.get("runtime", {})
    lines.append("## 🔧 Runtime")
    lines.append("")
    lines.append(f"- **P0/P1/P2**: {runtime.get('p0_count', 0)} / {runtime.get('p1_count', 0)} / {runtime.get('p2_count', 0)}")
    lines.append(f"- **Local**: {runtime.get('local_status', 'unknown')}")
    lines.append(f"- **Integration**: {runtime.get('integration_status', 'unknown')}")
    lines.append(f"- **External**: {runtime.get('external_status', 'unknown')}")
    lines.append(f"- **Skills**: {runtime.get('skill_total', 0)} total, {runtime.get('callable_total', 0)} callable")
    if runtime.get("failure_reasons"):
        lines.append(f"- **Blocked**: {', '.join(runtime['failure_reasons'][:3])}")
    lines.append("")
    
    # Alerts
    alerts = dashboard.get("alerts", {})
    lines.append("## 🚨 Alerts")
    lines.append("")
    if alerts.get("has_blocking_alerts"):
        lines.append("### ⚠️ 存在阻塞级告警")
    else:
        lines.append("### ✅ 无阻塞级告警")
    lines.append("")
    lines.append(f"- Total: {alerts.get('total_alerts', 0)}")
    lines.append(f"- Blocking: {alerts.get('blocking_count', 0)}")
    lines.append(f"- Warning: {alerts.get('warning_count', 0)}")
    if alerts.get("alerts"):
        lines.append("")
        lines.append("#### 告警详情")
        for alert in alerts["alerts"]:
            icon = "🚨" if alert.get("severity") == "blocking" else "⚠️"
            lines.append(f"- {icon} **{alert.get('alert_type')}**: {alert.get('message')}")
    if alerts.get("recommended_actions"):
        lines.append("")
        lines.append("#### 建议操作")
        for action in alerts["recommended_actions"]:
            lines.append(f"- {action}")
    lines.append("")
    
    # Incidents
    incidents = dashboard.get("incidents", {})
    lines.append("## 📋 Incidents")
    lines.append("")
    lines.append(f"- Open: {incidents.get('open_incidents', 0)}")
    lines.append(f"- Resolved: {incidents.get('resolved_incidents', 0)}")
    if incidents.get("latest_opened_at"):
        lines.append(f"- Latest Opened: {incidents.get('latest_opened_at')}")
    if incidents.get("latest_resolved_at"):
        lines.append(f"- Latest Resolved: {incidents.get('latest_resolved_at')}")
    lines.append("")
    
    # Trends
    trends = dashboard.get("trends", {})
    lines.append("## 📈 Trends")
    lines.append("")
    lines.append(f"- Total Records: {trends.get('total_records', 0)}")
    recent = trends.get("recent_trends", [])
    if recent:
        lines.append("")
        lines.append("| Date | P0 | P1 | P2 | Can Release |")
        lines.append("|------|-----|-----|-----|-------------|")
        for t in recent[-5:]:
            lines.append(f"| {t.get('date', '?')[:19]} | {t.get('p0_count', 0)} | {t.get('p1_count', 0)} | {t.get('p2_count', 0)} | {'✅' if t.get('can_release') else '❌'} |")
    lines.append("")
    
    # Recent Changes
    changes = dashboard.get("recent_changes", {})
    lines.append("## 🔄 Recent Changes")
    lines.append("")
    if changes.get("nightly_diff"):
        diff = changes["nightly_diff"]
        lines.append(f"- Blocking Change: {diff.get('blocking_count_change', 0):+d}")
        lines.append(f"- Warning Change: {diff.get('warning_count_change', 0):+d}")
        if diff.get("has_new_blocking"):
            lines.append("- 🚨 **New Blocking Alert**")
        if diff.get("has_resolved_blocking"):
            lines.append("- ✅ **Blocking Resolved**")
    if changes.get("last_blocked_reason"):
        lines.append(f"- Last Blocked: {changes['last_blocked_reason'].get('at', '?')[:19]}")
    if changes.get("last_strong_regression"):
        lines.append(f"- Last Strong Regression: {changes['last_strong_regression'].get('at', '?')[:19]}")
    lines.append("")
    
    return "\n".join(lines)

def generate_html(dashboard: Dict) -> str:
    """生成 HTML 看板"""
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>运维观测看板</title>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
.container { max-width: 1200px; margin: 0 auto; }
h1 { color: #333; }
h2 { color: #444; border-bottom: 2px solid #ddd; padding-bottom: 10px; }
.card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
.stat { text-align: center; padding: 15px; }
.stat-value { font-size: 32px; font-weight: bold; }
.stat-label { color: #666; margin-top: 5px; }
.status-pass { color: #22c55e; }
.status-fail { color: #ef4444; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; }
th, td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; }
th { background: #f9f9f9; }
.alert-blocking { background: #fef2f2; border-left: 4px solid #ef4444; padding: 10px; margin: 5px 0; }
.alert-warning { background: #fffbeb; border-left: 4px solid #f59e0b; padding: 10px; margin: 5px 0; }
</style>
</head>
<body>
<div class="container">
<h1>📊 运维观测看板</h1>
<p>生成时间: """ + dashboard.get("generated_at", "") + """</p>
"""
    
    # 总览卡片
    overview = dashboard.get("overview", {})
    html += """
<div class="card">
<h2>🎯 总览</h2>
<div class="grid">
<div class="stat">
<div class="stat-value """ + ("status-pass" if overview.get("runtime_status") else "status-fail") + """">""" + ("✅" if overview.get("runtime_status") else "❌") + """</div>
<div class="stat-label">Runtime</div>
</div>
<div class="stat">
<div class="stat-value """ + ("status-pass" if overview.get("quality_status") else "status-fail") + """">""" + ("✅" if overview.get("quality_status") else "❌") + """</div>
<div class="stat-label">Quality</div>
</div>
<div class="stat">
<div class="stat-value """ + ("status-pass" if overview.get("can_release") else "status-fail") + """">""" + ("✅" if overview.get("can_release") else "❌") + """</div>
<div class="stat-label">Can Release</div>
</div>
<div class="stat">
<div class="stat-value">""" + str(overview.get("blocking_alerts", 0)) + """</div>
<div class="stat-label">Blocking Alerts</div>
</div>
<div class="stat">
<div class="stat-value">""" + str(overview.get("open_incidents", 0)) + """</div>
<div class="stat-label">Open Incidents</div>
</div>
</div>
</div>
"""
    
    # Runtime
    runtime = dashboard.get("runtime", {})
    html += """
<div class="card">
<h2>🔧 Runtime</h2>
<p><strong>P0/P1/P2</strong>: """ + str(runtime.get("p0_count", 0)) + """ / """ + str(runtime.get("p1_count", 0)) + """ / """ + str(runtime.get("p2_count", 0)) + """</p>
<p><strong>Local</strong>: """ + str(runtime.get("local_status", "unknown")) + """ | <strong>Integration</strong>: """ + str(runtime.get("integration_status", "unknown")) + """ | <strong>External</strong>: """ + str(runtime.get("external_status", "unknown")) + """</p>
<p><strong>Skills</strong>: """ + str(runtime.get("skill_total", 0)) + """ total, """ + str(runtime.get("callable_total", 0)) + """ callable</p>
</div>
"""
    
    # Alerts
    alerts = dashboard.get("alerts", {})
    html += """
<div class="card">
<h2>🚨 Alerts</h2>
<p>Total: """ + str(alerts.get("total_alerts", 0)) + """ | Blocking: """ + str(alerts.get("blocking_count", 0)) + """ | Warning: """ + str(alerts.get("warning_count", 0)) + """</p>
"""
    for alert in alerts.get("alerts", []):
        css_class = "alert-blocking" if alert.get("severity") == "blocking" else "alert-warning"
        html += """<div class=\"""" + css_class + """\">""" + alert.get("alert_type", "") + """: """ + alert.get("message", "") + """</div>\n"""
    html += """</div>
"""
    
    # Incidents
    incidents = dashboard.get("incidents", {})
    html += """
<div class="card">
<h2>📋 Incidents</h2>
<p>Open: """ + str(incidents.get("open_incidents", 0)) + """ | Resolved: """ + str(incidents.get("resolved_incidents", 0)) + """</p>
</div>
"""
    
    # Trends
    trends = dashboard.get("trends", {})
    recent = trends.get("recent_trends", [])
    html += """
<div class="card">
<h2>📈 Trends (Last 5)</h2>
<table>
<tr><th>Date</th><th>P0</th><th>P1</th><th>P2</th><th>Can Release</th></tr>
"""
    for t in recent[-5:]:
        html += """<tr>
<td>""" + str(t.get("date", "?")[:19]) + """</td>
<td>""" + str(t.get("p0_count", 0)) + """</td>
<td>""" + str(t.get("p1_count", 0)) + """</td>
<td>""" + str(t.get("p2_count", 0)) + """</td>
<td>""" + ("✅" if t.get("can_release") else "❌") + """</td>
</tr>\n"""
    html += """</table>
</div>
"""
    
    html += """
</div>
</body>
</html>
"""
    return html

def save_dashboard(dashboard: Dict):
    """保存看板"""
    root = get_project_root()
    dashboard_dir = root / "reports/dashboard"
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存 JSON
    json_path = dashboard_dir / "ops_dashboard.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(dashboard, f, ensure_ascii=False, indent=2)
    
    # 保存 Markdown
    md_path = dashboard_dir / "ops_dashboard.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(generate_markdown(dashboard))
    
    # 保存 HTML
    html_path = dashboard_dir / "ops_dashboard.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(generate_html(dashboard))
    
    print(f"✅ Dashboard 已保存:")
    print(f"  - {json_path}")
    print(f"  - {md_path}")
    print(f"  - {html_path}")

def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║              运维看板构建器 V1.0                ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    dashboard = build_dashboard()
    save_dashboard(dashboard)
    
    print()
    print("【总览】")
    overview = dashboard.get("overview", {})
    print(f"  Runtime: {'✅' if overview.get('runtime_status') else '❌'}")
    print(f"  Quality: {'✅' if overview.get('quality_status') else '❌'}")
    print(f"  Can Release: {'✅' if overview.get('can_release') else '❌'}")
    print(f"  Blocking Alerts: {overview.get('blocking_alerts', 0)}")
    print(f"  Open Incidents: {overview.get('open_incidents', 0)}")

if __name__ == "__main__":
    main()
