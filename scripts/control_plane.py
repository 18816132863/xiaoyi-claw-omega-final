#!/usr/bin/env python3
"""
控制平面状态聚合器 - V1.0.0

聚合所有运维状态到统一视图
"""

import os
import sys
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
    if not path.exists():
        return None
    try:
        return json.load(open(path, encoding='utf-8'))
    except:
        return None

def save_json(path: Path, data: Dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class ControlPlaneAggregator:
    """控制平面聚合器"""

    def __init__(self, root: Path):
        self.root = root
        self.reports_dir = root / "reports"
        self.governance_dir = root / "governance"

    def aggregate(self) -> Dict:
        """聚合所有状态"""
        state = {
            "generated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "overview": self._build_overview(),
            "gates": self._build_gates(),
            "alerts": self._build_alerts(),
            "incidents": self._build_incidents(),
            "remediation": self._build_remediation(),
            "approvals": self._build_approvals(),
            "notifications": self._build_notifications(),
            "dashboard": self._build_dashboard(),
            "trends": self._build_trends(),
            "audit": self._build_audit_summary()
        }
        return state

    def _build_overview(self) -> Dict:
        """构建概览"""
        runtime = load_json(self.reports_dir / "runtime_integrity.json") or {}
        quality = load_json(self.reports_dir / "quality_gate.json") or {}
        release = load_json(self.reports_dir / "release_gate.json") or {}

        return {
            "runtime_passed": runtime.get("overall_passed", False),
            "quality_passed": quality.get("overall_passed", False),
            "can_release": release.get("can_release", False),
            "p0_count": runtime.get("p0_count", 0),
            "p1_count": runtime.get("p1_count", 0),
            "p2_count": runtime.get("p2_count", 0),
            "last_verified": runtime.get("verified_at", datetime.now().isoformat())
        }

    def _build_gates(self) -> Dict:
        """构建门禁状态"""
        runtime = load_json(self.reports_dir / "runtime_integrity.json") or {}
        quality = load_json(self.reports_dir / "quality_gate.json") or {}
        release = load_json(self.reports_dir / "release_gate.json") or {}

        return {
            "runtime": {
                "passed": runtime.get("overall_passed", False),
                "profile": runtime.get("profile", "unknown"),
                "local_status": runtime.get("local_status", "unknown"),
                "integration_status": runtime.get("integration_status", "unknown")
            },
            "quality": {
                "passed": quality.get("overall_passed", False),
                "protected_files": quality.get("protected_files", {}).get("status", "unknown"),
                "skill_registry": quality.get("skill_registry", {}).get("status", "unknown")
            },
            "release": {
                "can_release": release.get("can_release", False),
                "runtime_gate": release.get("runtime_gate", {}).get("passed", False),
                "quality_gate": release.get("quality_gate", {}).get("passed", False)
            }
        }

    def _build_alerts(self) -> Dict:
        """构建告警状态"""
        alerts = load_json(self.reports_dir / "alerts" / "latest_alerts.json") or {}

        return {
            "blocking_count": alerts.get("blocking_count", 0),
            "warning_count": alerts.get("warning_count", 0),
            "info_count": alerts.get("info_count", 0),
            "strong_regressions": alerts.get("strong_regressions", []),
            "generated_at": alerts.get("generated_at", datetime.now().isoformat())
        }

    def _build_incidents(self) -> Dict:
        """构建 incident 状态"""
        incidents = load_json(self.governance_dir / "ops" / "incident_tracker.json") or []
        summary = load_json(self.reports_dir / "alerts" / "incident_summary.json") or {}

        open_count = len([i for i in incidents if i.get("status") == "open"])
        resolved_count = len([i for i in incidents if i.get("status") == "resolved"])

        return {
            "total": len(incidents),
            "open": open_count,
            "resolved": resolved_count,
            "p0_open": summary.get("p0_open", 0),
            "p1_open": summary.get("p1_open", 0),
            "latest_incidents": incidents[:5] if incidents else []
        }

    def _build_remediation(self) -> Dict:
        """构建处置状态"""
        latest = load_json(self.reports_dir / "remediation" / "latest_remediation.json") or {}
        summary = load_json(self.reports_dir / "remediation" / "remediation_summary.json") or {}
        auto_audit = load_json(self.reports_dir / "remediation" / "auto_execute_audit.json") or {}

        return {
            "latest_action": latest.get("action_type", "none"),
            "latest_success": latest.get("success", False),
            "latest_action_id": latest.get("action_id", "none"),
            "pending_actions": summary.get("pending_safe_actions", []),
            "auto_execute_enabled": auto_audit.get("auto_execute_enabled", False),
            "latest_executed": auto_audit.get("action_executed", []),
            "latest_denied": auto_audit.get("action_denied", [])
        }

    def _build_notifications(self) -> Dict:
        """构建通知状态"""
        result = load_json(self.reports_dir / "alerts" / "notification_result.json") or {}

        return {
            "total_sent": result.get("total_sent", 0),
            "total_failed": result.get("total_failed", 0),
            "channels": result.get("channels", []),
            "sent_at": result.get("sent_at", datetime.now().isoformat())
        }

    def _build_approvals(self) -> Dict:
        """构建审批状态"""
        queue = load_json(self.reports_dir / "remediation" / "approval_queue.json") or {}
        history = load_json(self.reports_dir / "remediation" / "approval_history.json") or {}

        pending = [i for i in queue.get("pending", []) if i.get("status") == "pending"]
        approvals = history.get("approvals", [])

        granted = [a for a in approvals if a.get("status") == "approved"]
        denied = [a for a in approvals if a.get("status") == "denied"]
        executed = [a for a in approvals if a.get("execute_record_id")]

        return {
            "pending_count": len(pending),
            "approved_recent_count": len(granted),
            "denied_recent_count": len(denied),
            "executed_count": len(executed),
            "last_approval_id": approvals[-1].get("approval_id") if approvals else None,
            "last_approval_status": approvals[-1].get("status") if approvals else None,
            "latest_execute_record_id": approvals[-1].get("execute_record_id") if approvals else None
        }

    def _build_dashboard(self) -> Dict:
        """构建 dashboard 状态"""
        dashboard = load_json(self.reports_dir / "dashboard" / "ops_dashboard.json") or {}

        return {
            "runtime_status": dashboard.get("runtime_status", "unknown"),
            "quality_status": dashboard.get("quality_status", "unknown"),
            "release_status": dashboard.get("release_status", "unknown"),
            "blocking_alerts": dashboard.get("blocking_alerts", 0),
            "open_incidents": dashboard.get("open_incidents", 0),
            "generated_at": dashboard.get("generated_at", datetime.now().isoformat())
        }

    def _build_trends(self) -> Dict:
        """构建趋势状态"""
        trend = load_json(self.reports_dir / "trends" / "gate_trend.json") or {}

        # trend 可能是 list 或 dict
        if isinstance(trend, list):
            return {
                "runtime_pass_rate": 0,
                "quality_pass_rate": 0,
                "release_pass_rate": 0,
                "last_7_days": trend
            }

        return {
            "runtime_pass_rate": trend.get("runtime_pass_rate", 0),
            "quality_pass_rate": trend.get("quality_pass_rate", 0),
            "release_pass_rate": trend.get("release_pass_rate", 0),
            "last_7_days": trend.get("last_7_days", [])
        }

    def _build_audit_summary(self) -> Dict:
        """构建审计摘要"""
        return {
            "last_runtime_check": datetime.now().isoformat(),
            "last_quality_check": datetime.now().isoformat(),
            "last_release_check": datetime.now().isoformat(),
            "audit_trail": []
        }

def build_control_plane_state(root: Path = None) -> Dict:
    """构建控制平面状态"""
    root = root or get_project_root()
    aggregator = ControlPlaneAggregator(root)
    return aggregator.aggregate()

def main():
    root = get_project_root()
    state = build_control_plane_state(root)

    # 保存
    output_path = root / "reports" / "ops" / "control_plane_state.json"
    save_json(output_path, state)

    print("✅ 控制平面状态已生成")
    print(f"   路径: {output_path}")
    print()
    print(f"【概览】")
    print(f"  Runtime: {'✅' if state['overview']['runtime_passed'] else '❌'}")
    print(f"  Quality: {'✅' if state['overview']['quality_passed'] else '❌'}")
    print(f"  Release: {'✅' if state['overview']['can_release'] else '❌'}")
    print(f"  P0/P1/P2: {state['overview']['p0_count']}/{state['overview']['p1_count']}/{state['overview']['p2_count']}")

if __name__ == "__main__":
    main()
