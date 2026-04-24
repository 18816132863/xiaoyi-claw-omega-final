#!/usr/bin/env python3
"""
控制平面审计聚合器 - V1.0.0

聚合历史审计记录
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

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

def load_json_list(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    try:
        data = json.load(open(path, encoding='utf-8'))
        if isinstance(data, list):
            return data
        return []
    except:
        return []

def save_json(path: Path, data: Dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class ControlPlaneAuditAggregator:
    """控制平面审计聚合器"""

    def __init__(self, root: Path, limit: int = 10):
        self.root = root
        self.reports_dir = root / "reports"
        self.governance_dir = root / "governance"
        self.limit = limit

    def aggregate(self) -> Dict:
        """聚合审计历史"""
        audit = {
            "generated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "release_gates": self._get_release_gates(),
            "nightly_audits": self._get_nightly_audits(),
            "blocking_alerts": self._get_blocking_alerts(),
            "incidents": self._get_incidents(),
            "remediations": self._get_remediations(),
            "approvals": self._get_approvals(),
            "timeline": self._build_timeline()
        }
        return audit

    def _get_release_gates(self) -> List[Dict]:
        """获取最近 release gate 记录"""
        history_dir = self.reports_dir / "history" / "release"
        if not history_dir.exists():
            return []

        files = sorted(history_dir.glob("*.json"), reverse=True)[:self.limit]
        records = []
        for f in files:
            data = load_json(f)
            if data:
                records.append({
                    "timestamp": f.stem.split("_")[0] + "_" + f.stem.split("_")[1],
                    "can_release": data.get("can_release", False),
                    "runtime_passed": data.get("runtime_gate", {}).get("passed", False),
                    "quality_passed": data.get("quality_gate", {}).get("passed", False)
                })
        return records

    def _get_nightly_audits(self) -> List[Dict]:
        """获取最近 nightly audit 记录"""
        history_dir = self.reports_dir / "history" / "runtime"
        if not history_dir.exists():
            return []

        files = sorted(history_dir.glob("*_nightly.json"), reverse=True)[:self.limit]
        records = []
        for f in files:
            data = load_json(f)
            if data:
                records.append({
                    "timestamp": f.stem.split("_")[0] + "_" + f.stem.split("_")[1],
                    "passed": data.get("overall_passed", False),
                    "p0_count": data.get("p0_count", 0),
                    "p1_count": data.get("p1_count", 0)
                })
        return records

    def _get_blocking_alerts(self) -> List[Dict]:
        """获取最近 blocking alerts"""
        alerts = load_json(self.reports_dir / "alerts" / "latest_alerts.json") or {}
        blocking = alerts.get("blocking_alerts", alerts.get("alerts", []))
        return blocking[:self.limit]

    def _get_incidents(self) -> List[Dict]:
        """获取最近 incidents"""
        incidents = load_json_list(self.governance_dir / "ops" / "incident_tracker.json")
        # 按时间排序
        sorted_incidents = sorted(incidents, key=lambda x: x.get("created_at", ""), reverse=True)
        return sorted_incidents[:self.limit]

    def _get_remediations(self) -> List[Dict]:
        """获取最近 remediation 记录"""
        history_dir = self.reports_dir / "remediation" / "history"
        if not history_dir.exists():
            return []

        files = sorted(history_dir.glob("rem_*.json"), reverse=True)[:self.limit]
        records = []
        for f in files:
            data = load_json(f)
            if data:
                records.append({
                    "action_id": data.get("action_id", "unknown"),
                    "action_type": data.get("action_type", "unknown"),
                    "mode": data.get("mode", "unknown"),
                    "success": data.get("success", False),
                    "timestamp": data.get("started_at", "")[:19]
                })
        return records

    def _get_approvals(self) -> Dict:
        """获取审批结构化摘要"""
        history = load_json(self.reports_dir / "remediation" / "approval_history.json") or {}
        approvals = history.get("approvals", [])

        # 按归一后的状态分类
        pending = [a for a in approvals if a.get("status") == "pending"]
        granted = [a for a in approvals if a.get("status") == "approved_legacy"]
        denied = [a for a in approvals if a.get("status") == "denied"]
        executed = [a for a in approvals if a.get("status") == "executed"]
        execute_failed = [a for a in approvals if a.get("status") == "execute_failed"]

        # 获取最新 execute_record_id
        latest_execute_record_id = None
        for a in reversed(approvals):
            if a.get("status") == "executed" and a.get("execute_record_id"):
                latest_execute_record_id = a.get("execute_record_id")
                break

        return {
            "pending": pending[:self.limit],
            "granted": granted[:self.limit],
            "denied": denied[:self.limit],
            "executed": executed[:self.limit],
            "execute_failed": execute_failed[:self.limit],
            "pending_count": len(pending),
            "granted_count": len(granted),
            "denied_count": len(denied),
            "executed_count": len(executed),
            "execute_failed_count": len(execute_failed),
            "latest_execute_record_id": latest_execute_record_id
        }

    def _build_timeline(self) -> List[Dict]:
        """构建时间线"""
        events = []

        # Release gates
        for r in self._get_release_gates():
            events.append({
                "type": "release_gate",
                "timestamp": r.get("timestamp", ""),
                "result": "pass" if r.get("can_release") else "fail"
            })

        # Remediations
        for r in self._get_remediations():
            events.append({
                "type": "remediation",
                "timestamp": r.get("timestamp", ""),
                "action": r.get("action_type", "unknown"),
                "result": "success" if r.get("success") else "fail"
            })

        # 按时间排序
        events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return events[:self.limit * 2]

def build_control_plane_audit(root: Path = None, limit: int = 10) -> Dict:
    """构建控制平面审计"""
    root = root or get_project_root()
    aggregator = ControlPlaneAuditAggregator(root, limit)
    return aggregator.aggregate()

def main():
    root = get_project_root()
    audit = build_control_plane_audit(root)

    # 保存
    output_path = root / "reports" / "ops" / "control_plane_audit.json"
    save_json(output_path, audit)

    print("✅ 控制平面审计已生成")
    print(f"   路径: {output_path}")
    print()
    print(f"【审计摘要】")
    print(f"  Release gates: {len(audit['release_gates'])} 条")
    print(f"  Nightly audits: {len(audit['nightly_audits'])} 条")
    print(f"  Remediations: {len(audit['remediations'])} 条")
    print(f"  Timeline events: {len(audit['timeline'])} 条")

if __name__ == "__main__":
    main()
