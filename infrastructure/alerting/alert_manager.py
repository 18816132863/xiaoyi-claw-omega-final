#!/usr/bin/env python3
"""
告警管理器 - V2.0.0

职责：
1. 读取各类门禁报告
2. 生成统一告警对象
3. 保存 latest + history（结构一致）
4. 管理 incident 闭环
5. 生成 incident_summary.json
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class AlertSeverity(Enum):
    BLOCKING = "blocking"      # 阻塞级
    WARNING = "warning"        # 警告级
    INFO = "info"              # 信息级

class AlertType(Enum):
    P0_BLOCKED = "P0_BLOCKED"
    STRONG_REGRESSION = "STRONG_REGRESSION"
    RELEASE_BLOCKED = "RELEASE_BLOCKED"
    WEAK_REGRESSION = "WEAK_REGRESSION"

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent

def load_report(report_path: str) -> Optional[Dict]:
    """加载报告"""
    root = get_project_root()
    path = root / report_path
    if not path.exists():
        return None
    try:
        return json.load(open(path, encoding='utf-8'))
    except:
        return None

def check_p0_blocked(runtime: Dict) -> Optional[Dict]:
    """检查 P0 阻塞"""
    if not runtime:
        return None
    
    p0_count = runtime.get("p0_count", 0)
    if p0_count > 0:
        return {
            "alert_type": AlertType.P0_BLOCKED.value,
            "severity": AlertSeverity.BLOCKING.value,
            "message": f"P0 硬编码路径: {p0_count} 处",
            "details": {"p0_count": p0_count}
        }
    return None

def check_strong_regression(nightly_audit: Dict) -> Optional[Dict]:
    """检查强回归"""
    if not nightly_audit:
        return None
    
    strong = nightly_audit.get("strong_regressions", [])
    if strong:
        return {
            "alert_type": AlertType.STRONG_REGRESSION.value,
            "severity": AlertSeverity.BLOCKING.value,
            "message": f"检测到 {len(strong)} 个强回归",
            "details": {"regressions": strong}
        }
    return None

def check_release_blocked(release_gate: Dict) -> Optional[Dict]:
    """检查发布阻塞"""
    if not release_gate:
        return None
    
    if not release_gate.get("can_release", True):
        blocked = release_gate.get("blocked_reasons", [])
        return {
            "alert_type": AlertType.RELEASE_BLOCKED.value,
            "severity": AlertSeverity.BLOCKING.value,
            "message": "发布门禁未通过",
            "details": {"blocked_reasons": blocked}
        }
    return None

def check_weak_regression(nightly_audit: Dict) -> Optional[Dict]:
    """检查弱回归"""
    if not nightly_audit:
        return None
    
    weak = nightly_audit.get("weak_regressions", [])
    if weak:
        return {
            "alert_type": AlertType.WEAK_REGRESSION.value,
            "severity": AlertSeverity.WARNING.value,
            "message": f"检测到 {len(weak)} 个弱回归",
            "details": {"regressions": weak}
        }
    return None

def generate_alerts(source_workflow: str = "manual", profile: str = "unknown") -> Dict:
    """生成统一告警对象"""
    root = get_project_root()
    timestamp = datetime.now()
    
    # 加载报告
    runtime = load_report("reports/runtime_integrity.json")
    quality = load_report("reports/quality_gate.json")
    release = load_report("reports/release_gate.json")
    nightly = load_report("reports/nightly_audit.json")
    
    # 检查告警
    alerts = []
    
    # P0 阻塞
    alert = check_p0_blocked(runtime)
    if alert:
        alerts.append(alert)
    
    # 强回归
    alert = check_strong_regression(nightly)
    if alert:
        alerts.append(alert)
    
    # 发布阻塞
    alert = check_release_blocked(release)
    if alert:
        alerts.append(alert)
    
    # 弱回归
    alert = check_weak_regression(nightly)
    if alert:
        alerts.append(alert)
    
    # 构建统一告警对象
    has_blocking = any(a["severity"] == AlertSeverity.BLOCKING.value for a in alerts)
    has_warning = any(a["severity"] == AlertSeverity.WARNING.value for a in alerts)
    
    # 提取 blocked_reasons
    blocked_reasons = []
    for alert in alerts:
        if alert["severity"] == AlertSeverity.BLOCKING.value:
            blocked_reasons.extend(alert.get("details", {}).get("blocked_reasons", []))
    
    # 提取 strong_regressions
    strong_regressions = []
    for alert in alerts:
        if alert["alert_type"] == AlertType.STRONG_REGRESSION.value:
            strong_regressions.extend(alert.get("details", {}).get("regressions", []))
    
    # 提取 weak_regressions
    weak_regressions = []
    for alert in alerts:
        if alert["alert_type"] == AlertType.WEAK_REGRESSION.value:
            weak_regressions.extend(alert.get("details", {}).get("regressions", []))
    
    # 提取 skipped_external
    skipped_external = []
    if runtime:
        skipped_external = runtime.get("skipped_external", [])
    
    # 生成建议
    recommended_actions = []
    if has_blocking:
        recommended_actions.append("🚨 存在阻塞级告警，建议立即处理")
    for alert in alerts:
        if alert["alert_type"] == AlertType.P0_BLOCKED.value:
            recommended_actions.append("修复 P0 硬编码路径后再合并")
        elif alert["alert_type"] == AlertType.STRONG_REGRESSION.value:
            recommended_actions.append("检查最近提交，定位回归原因")
        elif alert["alert_type"] == AlertType.RELEASE_BLOCKED.value:
            recommended_actions.append("解决阻塞原因后重新运行 release-gate")
    
    # 构建完整报告
    report = {
        "generated_at": timestamp.isoformat(),
        "source_workflow": source_workflow,
        "profile": profile,
        "triggered_at": timestamp.isoformat(),
        
        # 告警状态
        "has_blocking_alerts": has_blocking,
        "has_warning_alerts": has_warning,
        "total_alerts": len(alerts),
        "blocking_count": sum(1 for a in alerts if a["severity"] == AlertSeverity.BLOCKING.value),
        "warning_count": sum(1 for a in alerts if a["severity"] == AlertSeverity.WARNING.value),
        
        # 告警详情
        "alerts": alerts,
        "blocked_reasons": blocked_reasons,
        "strong_regressions": strong_regressions,
        "weak_regressions": weak_regressions,
        "skipped_external": skipped_external,
        
        # 来源报告
        "source_reports": {
            "runtime": runtime.get("verified_at") if runtime else None,
            "quality": quality.get("verified_at") if quality else None,
            "release": release.get("checked_at") if release else None,
            "nightly": nightly.get("audit_at") if nightly else None
        },
        
        # 建议
        "recommended_actions": recommended_actions,
        
        # incident 状态（稍后更新）
        "incident_created": False,
        "incident_resolved": False,
        "incident_status_summary": {
            "total_incidents": 0,
            "open_incidents": 0,
            "resolved_incidents": 0
        }
    }
    
    # 保存 latest
    alerts_dir = root / "reports/alerts"
    alerts_dir.mkdir(parents=True, exist_ok=True)
    
    latest_path = alerts_dir / "latest_alerts.json"
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 保存 history（结构完全一致）
    history_dir = alerts_dir / "history"
    history_dir.mkdir(parents=True, exist_ok=True)
    history_path = history_dir / f"{timestamp.strftime('%Y%m%d_%H%M%S')}_alerts.json"
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report

def manage_incidents(alerts_report: Dict) -> Dict:
    """管理 incident 闭环"""
    root = get_project_root()
    timestamp = datetime.now()
    
    incidents_path = root / "governance/ops/incident_tracker.json"
    incidents_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 加载现有 incidents
    incidents = []
    if incidents_path.exists():
        try:
            incidents = json.load(open(incidents_path, encoding='utf-8'))
        except:
            pass
    
    incident_created = False
    incident_resolved = False
    
    # 检查是否需要创建新 incident
    if alerts_report.get("has_blocking_alerts"):
        # 检查是否已有相同类型的 open incident
        existing_types = set()
        for inc in incidents:
            if inc.get("status") == "open":
                existing_types.add(inc.get("alert_type"))
        
        # 创建新 incident
        for alert in alerts_report.get("alerts", []):
            if alert["severity"] == AlertSeverity.BLOCKING.value:
                if alert["alert_type"] not in existing_types:
                    incident = {
                        "incident_id": f"INC-{timestamp.strftime('%Y%m%d%H%M%S')}",
                        "alert_type": alert["alert_type"],
                        "severity": alert["severity"],
                        "opened_at": timestamp.isoformat(),
                        "status": "open",
                        "owner": None,
                        "source_report": alerts_report.get("source_reports", {}),
                        "blocked_reasons": alert.get("details", {}).get("blocked_reasons", []),
                        "resolution_note": None,
                        "resolved_at": None
                    }
                    incidents.append(incident)
                    incident_created = True
    else:
        # 无阻塞告警，关闭相关 open incidents
        for inc in incidents:
            if inc.get("status") == "open":
                inc["status"] = "resolved"
                inc["resolved_at"] = timestamp.isoformat()
                inc["resolution_note"] = "告警已自动恢复"
                incident_resolved = True
    
    # 保存
    with open(incidents_path, 'w', encoding='utf-8') as f:
        json.dump(incidents, f, ensure_ascii=False, indent=2)
    
    # 统计
    open_count = sum(1 for i in incidents if i.get("status") == "open")
    resolved_count = sum(1 for i in incidents if i.get("status") == "resolved")
    
    # 生成 incident_summary.json
    summary = {
        "generated_at": timestamp.isoformat(),
        "total_incidents": len(incidents),
        "open_incidents": open_count,
        "resolved_incidents": resolved_count,
        "latest_opened_at": None,
        "latest_resolved_at": None
    }
    
    # 找最新的 opened/resolved
    for inc in reversed(incidents):
        if inc.get("status") == "open" and not summary["latest_opened_at"]:
            summary["latest_opened_at"] = inc.get("opened_at")
        if inc.get("status") == "resolved" and not summary["latest_resolved_at"]:
            summary["latest_resolved_at"] = inc.get("resolved_at")
    
    # 保存 incident_summary
    alerts_dir = root / "reports/alerts"
    summary_path = alerts_dir / "incident_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # 更新 alerts_report
    alerts_report["incident_created"] = incident_created
    alerts_report["incident_resolved"] = incident_resolved
    alerts_report["incident_status_summary"] = summary
    
    # 重新保存 latest_alerts.json
    latest_path = alerts_dir / "latest_alerts.json"
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(alerts_report, f, ensure_ascii=False, indent=2)
    
    return {
        "total_incidents": len(incidents),
        "open_incidents": open_count,
        "resolved_incidents": resolved_count,
        "incident_created": incident_created,
        "incident_resolved": incident_resolved,
        "incidents": incidents
    }

def print_alert_summary(report: Dict):
    """打印告警摘要"""
    print("╔══════════════════════════════════════════════════╗")
    print("║              告警摘要 V2.0                      ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    if report["has_blocking_alerts"]:
        print("🚨 存在阻塞级告警")
    else:
        print("✅ 无阻塞级告警")
    
    print()
    print(f"总告警数: {report['total_alerts']}")
    print(f"阻塞级: {report['blocking_count']}")
    print(f"警告级: {report['warning_count']}")
    print()
    
    if report["alerts"]:
        print("【告警详情】")
        for alert in report["alerts"]:
            severity_icon = "🚨" if alert["severity"] == "blocking" else "⚠️"
            print(f"  {severity_icon} [{alert['alert_type']}] {alert['message']}")
        print()
    
    if report.get("blocked_reasons"):
        print("【阻塞原因】")
        for reason in report["blocked_reasons"]:
            print(f"  - {reason}")
        print()
    
    if report.get("strong_regressions"):
        print("【强回归】")
        for reg in report["strong_regressions"]:
            print(f"  - {reg}")
        print()
    
    if report.get("weak_regressions"):
        print("【弱回归】")
        for reg in report["weak_regressions"]:
            print(f"  - {reg}")
        print()
    
    if report.get("recommended_actions"):
        print("【建议操作】")
        for action in report["recommended_actions"]:
            print(f"  - {action}")
    
    # incident 状态
    summary = report.get("incident_status_summary", {})
    if summary:
        print()
        print(f"【Incident 状态】")
        print(f"  Open: {summary.get('open_incidents', 0)}")
        print(f"  Resolved: {summary.get('resolved_incidents', 0)}")
        if report.get("incident_created"):
            print("  ✅ 已创建新 incident")
        if report.get("incident_resolved"):
            print("  ✅ 已自动关闭 incident")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="告警管理器 V2.0")
    parser.add_argument("--generate", action="store_true", help="生成告警")
    parser.add_argument("--incidents", action="store_true", help="管理 incidents")
    parser.add_argument("--workflow", default="manual", help="来源 workflow")
    parser.add_argument("--profile", default="unknown", help="门禁 profile")
    args = parser.parse_args()
    
    if args.generate:
        report = generate_alerts(args.workflow, args.profile)
        print_alert_summary(report)
        
        if args.incidents:
            incidents = manage_incidents(report)
            print()
            print(f"Open incidents: {incidents['open_incidents']}")
        
        sys.exit(1 if report["has_blocking_alerts"] else 0)
    
    # 默认：生成告警 + 管理 incidents
    report = generate_alerts(args.workflow, args.profile)
    incidents = manage_incidents(report)
    print_alert_summary(report)
    
    sys.exit(1 if report["has_blocking_alerts"] else 0)
