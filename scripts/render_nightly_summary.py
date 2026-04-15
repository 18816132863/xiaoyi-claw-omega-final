#!/usr/bin/env python3
"""渲染 nightly summary - 从统一规则引擎报告读取"""

import json
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent

    print("## 🌙 Nightly Audit Summary")
    print()

    # Rule Engine Report
    rule_report_path = root / "reports/ops/rule_engine_report.json"
    if rule_report_path.exists():
        try:
            data = json.load(open(rule_report_path, encoding='utf-8'))
            print("**Rule Checks**:")
            print(f"- Profile: {data.get('profile', 'N/A')}")
            print(f"- Total Rules: {data.get('total_rules', 0)}")
            print(f"- Passed: {data.get('passed_count', 0)}")
            print(f"- Failed: {data.get('failed_count', 0)}")
            print(f"- Warnings: {data.get('warning_count', 0)}")
            print(f"- Skipped: {data.get('skipped_count', 0)}")
            print(f"- Waived: {data.get('waived_count', 0)}")
            print()
            
            # By Status
            print("**By Status**:")
            print(f"- Active: {len(data.get('active_rules', []))}")
            print(f"- Experimental: {len(data.get('experimental_rules', []))}")
            print(f"- Deprecated: {len(data.get('deprecated_rules', []))}")
            print(f"- Disabled: {len(data.get('disabled_rules', []))}")
            print()
            
            # Exceptions
            if data.get('active_exceptions'):
                print("**Active Exceptions**:")
                for exc in data['active_exceptions']:
                    print(f"  - {exc['exception_id']}: {exc['rule_id']}")
                print()
            
            if data.get('expired_exceptions'):
                print("**Expired Exceptions**:")
                for exc in data['expired_exceptions']:
                    print(f"  - {exc['exception_id']}: {exc['rule_id']}")
                print()
            
            if data.get("blocking_failures"):
                print(f"**Blocking Failures**: {len(data['blocking_failures'])}")
                for bf in data['blocking_failures']:
                    print(f"  - {bf['rule_id']} (owner: {bf['owner']})")
                print()
            
            if data.get("warning_rules"):
                print(f"**Warning Rules**: {', '.join(data['warning_rules'])}")
                print()
            
            if data.get("waived_rules"):
                print(f"**Waived Rules**: {', '.join(data['waived_rules'])}")
                print()
            
            if data.get("skipped_rules"):
                print(f"**Skipped Rules**: {', '.join(data['skipped_rules'])}")
                print()
            
            # Exception Debt
            exception_debt = data.get('exception_debt', {})
            summary = exception_debt.get('summary', {})
            
            # Fallback to rule_exception_debt.json
            if not summary:
                debt_path = root / "reports/ops/rule_exception_debt.json"
                if debt_path.exists():
                    try:
                        debt_data = json.load(open(debt_path, encoding='utf-8'))
                        summary = debt_data.get('summary', {})
                    except:
                        pass
            
            stale_count = summary.get('stale_count', 0)
            overused_count = summary.get('overused_count', 0)
            high_debt_count = summary.get('high_debt_count', 0)
            
            print("**Exception Debt**:")
            print(f"- Stale Exceptions: {stale_count}")
            print(f"- Overused Exceptions: {overused_count}")
            print(f"- High Debt Exceptions: {high_debt_count}")
            print()
            
            # Recent Exception Actions
            history_path = root / "reports/ops/rule_exception_history.json"
            if history_path.exists():
                try:
                    from datetime import datetime, timedelta
                    history = json.load(open(history_path, encoding='utf-8'))
                    
                    now = datetime.now()
                    cutoff = now - timedelta(hours=24)
                    
                    stats = {"create": 0, "renew": 0, "revoke": 0, "expire": 0}
                    for h in history:
                        try:
                            ts = datetime.fromisoformat(h.get("timestamp", ""))
                            if ts >= cutoff:
                                action = h.get("action", "")
                                if action in stats:
                                    stats[action] += 1
                        except:
                            continue
                    
                    print("**Recent Exception Actions** (24h):")
                    print(f"- create: {stats['create']}")
                    print(f"- renew: {stats['renew']}")
                    print(f"- revoke: {stats['revoke']}")
                    print(f"- expire: {stats['expire']}")
                    print()
                except:
                    pass
            
            # Exception Status
            status_path = root / "reports/ops/rule_exception_status.json"
            if status_path.exists():
                try:
                    status = json.load(open(status_path, encoding='utf-8'))
                    print("**Exception Status**:")
                    print(f"- Active Exceptions: {status.get('active_count', 0)}")
                    print(f"- Soon Expiring Exceptions: {status.get('soon_expiring_count', 0)}")
                    print(f"- Expired Exceptions: {status.get('expired_count', 0)}")
                    print(f"- Revoked Exceptions: {status.get('revoked_count', 0)}")
                    print()
                except:
                    pass
        except:
            print("**Rule Checks**: ⚠️ 无法读取")
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

    # Approval Summary
    control_plane_path = root / "reports/ops/control_plane_state.json"
    if control_plane_path.exists():
        try:
            data = json.load(open(control_plane_path, encoding='utf-8'))
            approvals = data.get("approvals", {})

            print(f"**Approval Summary**:")
            print(f"- Pending: {approvals.get('pending_count', 0)}")
            print(f"- Executed: {approvals.get('executed_count', 0)}")
            print(f"- Denied: {approvals.get('denied_recent_count', 0)}")
            print(f"- Execute failed: {approvals.get('execute_failed_count', 0)}")

            latest_id = approvals.get('latest_execute_record_id')
            print(f"- Latest execute record: {latest_id if latest_id else 'N/A'}")
            print()
        except:
            pass

if __name__ == "__main__":
    main()

# Exception Quota
quota_path = root / "reports/ops/rule_exception_quota.json"
if quota_path.exists():
    try:
        quota = json.load(open(quota_path, encoding='utf-8'))
        violations = quota.get("violations", {})
        owner_violations = violations.get("owner_violations", [])
        rule_violations = violations.get("rule_violations", [])
        
        print("**Exception Quota**:")
        print(f"- Owner Quota Violations: {len(owner_violations)}")
        print(f"- Rule Quota Violations: {len(rule_violations)}")
        if owner_violations:
            print(f"  - Owners: {', '.join(owner_violations)}")
        if rule_violations:
            print(f"  - Rules: {', '.join(rule_violations)}")
        print()
    except:
        pass
