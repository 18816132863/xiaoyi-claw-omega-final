#!/usr/bin/env python3
"""渲染 nightly summary"""

import json
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent

    print("## 🌙 Nightly Audit Summary")
    print()

    # Runtime integrity
    runtime_path = root / "reports/runtime_integrity.json"
    if runtime_path.exists():
        try:
            data = json.load(open(runtime_path, encoding='utf-8'))
            passed = data.get("overall_passed", False)
            status = "✅" if passed else "❌"
            print(f"**Runtime Gate**: {status}")
            print(f"- P0: {data.get('p0_count', 0)}, P1: {data.get('p1_count', 0)}, P2: {data.get('p2_count', 0)}")
            print()
        except:
            pass

    # Quality gate
    quality_path = root / "reports/quality_gate.json"
    if quality_path.exists():
        try:
            data = json.load(open(quality_path, encoding='utf-8'))
            passed = data.get("overall_passed", False)
            status = "✅" if passed else "❌"
            print(f"**Quality Gate**: {status}")
            print()
        except:
            pass

    # Alerts
    alerts_path = root / "reports/alerts/latest_alerts.json"
    if alerts_path.exists():
        try:
            data = json.load(open(alerts_path, encoding='utf-8'))
            blocking = data.get("blocking_count", 0)
            warning = data.get("warning_count", 0)
            print(f"**Alerts**: 🚫 {blocking} blocking, ⚠️ {warning} warning")
            print()
        except:
            pass

    # Remediation
    remediation_path = root / "reports/remediation/remediation_summary.json"
    if remediation_path.exists():
        try:
            data = json.load(open(remediation_path, encoding='utf-8'))
            pending = data.get("pending_safe_actions", [])
            latest = data.get("latest_action_type", "none")
            success = data.get("latest_action_success", "N/A")
            print(f"**Remediation**:")
            print(f"- Pending actions: {pending if pending else 'none'}")
            print(f"- Latest execute: {latest} ({'✅' if success else '❌'})")
            print()
        except:
            pass

if __name__ == "__main__":
    main()
