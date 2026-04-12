#!/usr/bin/env python3
"""渲染 release summary"""

import json
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent

    print("## 🚀 Release Gate Summary")
    print()

    # Release gate
    release_path = root / "reports/release_gate.json"
    if release_path.exists():
        try:
            data = json.load(open(release_path, encoding='utf-8'))
            can_release = data.get("can_release", False)
            status = "✅ 可以发布" if can_release else "❌ 不可发布"
            print(f"**Release Decision**: {status}")
            print()

            runtime = data.get("runtime_gate", {})
            quality = data.get("quality_gate", {})

            if runtime:
                rt_passed = runtime.get("passed", False)
                print(f"- Runtime Gate: {'✅' if rt_passed else '❌'}")

            if quality:
                q_passed = quality.get("passed", False)
                print(f"- Quality Gate: {'✅' if q_passed else '❌'}")

            print()
        except:
            print("**Release Gate**: ⚠️ 无法读取")
            print()

    # Remediation
    remediation_path = root / "reports/remediation/auto_execute_summary.json"
    if remediation_path.exists():
        try:
            data = json.load(open(remediation_path, encoding='utf-8'))
            enabled = data.get("auto_execute_enabled", False)
            executed = data.get("latest_executed_actions", [])
            denied = data.get("latest_denied_actions", [])
            print(f"**Auto Execute**: {'✅ enabled' if enabled else '❌ disabled'}")
            if executed:
                print(f"- Executed: {executed}")
            if denied:
                print(f"- Denied: {denied}")
            print()
        except:
            pass

    # Approval Summary
    approval_history_path = root / "reports/remediation/approval_history.json"
    if approval_history_path.exists():
        try:
            data = json.load(open(approval_history_path, encoding='utf-8'))
            approvals = data.get("approvals", [])

            pending = [a for a in approvals if a.get("status") == "pending"]
            executed = [a for a in approvals if a.get("status") == "executed"]
            denied = [a for a in approvals if a.get("status") == "denied"]

            print(f"**Approval Summary**:")
            print(f"- Pending: {len(pending)}")
            print(f"- Executed: {len(executed)}")
            print(f"- Denied: {len(denied)}")

            if approvals:
                latest = approvals[-1]
                print(f"- Latest: {latest.get('approval_id', 'N/A')} ({latest.get('status', 'N/A')})")
                if latest.get("execute_record_id"):
                    print(f"- Latest execute_record_id: {latest.get('execute_record_id')}")
            print()
        except:
            pass

if __name__ == "__main__":
    main()
