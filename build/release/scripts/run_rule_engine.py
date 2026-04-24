#!/usr/bin/env python3
"""
统一规则引擎 - V3.0.0

读取 RULE_REGISTRY.json，按 profile 执行对应规则检查器，生成统一结果
支持规则生命周期：active / experimental / deprecated / disabled
支持规则例外：active / expired / revoked exception
支持例外债务：healthy / stale / overused / expired
支持性能缓存：规则注册表缓存、例外缓存

V3.0.0 新增：
- 例外债务识别（healthy / stale / overused / expired）
- 例外债务快照生成
- 过期例外不再生效
- 滥用例外进入 warning 或 blocking
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


# 全局缓存
_registry_cache = None
_exceptions_cache = None


def load_rule_registry() -> Dict:
    """加载规则注册表（带缓存）"""
    global _registry_cache
    if _registry_cache is not None:
        return _registry_cache
    root = get_project_root()
    registry_path = root / "core/RULE_REGISTRY.json"
    if not registry_path.exists():
        print(f"❌ 规则注册表不存在: {registry_path}")
        return {}
    try:
        _registry_cache = json.load(open(registry_path, encoding='utf-8'))
        return _registry_cache
    except Exception as e:
        print(f"❌ 无法加载规则注册表: {e}")
        return {}


def load_rule_exceptions() -> Dict:
    """加载规则例外注册表（带缓存）"""
    global _exceptions_cache
    if _exceptions_cache is not None:
        return _exceptions_cache
    root = get_project_root()
    exceptions_path = root / "core/RULE_EXCEPTIONS.json"
    if not exceptions_path.exists():
        _exceptions_cache = {"exceptions": []}
        return _exceptions_cache
    try:
        _exceptions_cache = json.load(open(exceptions_path, encoding='utf-8'))
        return _exceptions_cache
    except Exception as e:
        print(f"⚠️ 无法加载规则例外注册表: {e}")
        _exceptions_cache = {"exceptions": []}
        return _exceptions_cache


def normalize_exceptions(exceptions_data: Dict) -> List[Dict]:
    """将例外注册表统一规范化为 list[dict]，并补齐 exception_id"""
    raw = exceptions_data.get("exceptions", {})
    normalized: List[Dict] = []
    
    if isinstance(raw, dict):
        for exc_id, exc in raw.items():
            if not isinstance(exc, dict):
                continue
            item = dict(exc)
            item.setdefault("exception_id", exc_id)
            normalized.append(item)
    elif isinstance(raw, list):
        for exc in raw:
            if not isinstance(exc, dict):
                continue
            item = dict(exc)
            if not item.get("exception_id"):
                item["exception_id"] = f"auto_{len(normalized)+1}"
            normalized.append(item)
    
    return normalized


def classify_exception_debt(exception: Dict) -> Tuple[str, str]:
    """
    分类例外债务状态
    返回: (状态, 原因)
    
    状态:
    - healthy: 健康，正常生效
    - stale: 陈旧，即将过期或超过 escalation 阈值
    - overused: 滥用，超过续期次数
    - expired: 过期，不再生效
    """
    now = datetime.now()
    status = exception.get("status", "active")
    expires_at = exception.get("expires_at")
    debt_level = exception.get("debt_level", "medium")
    max_renewals = exception.get("max_renewals", 2)
    renewal_count = exception.get("renewal_count", 0)
    escalation_after_days = exception.get("escalation_after_days", 7)
    created_at = exception.get("created_at")
    
    # 1. 检查是否已过期
    if status == "expired" or status == "revoked":
        return "expired", "状态为 expired/revoked"
    
    if expires_at:
        try:
            expires_dt = datetime.fromisoformat(expires_at)
            if now > expires_dt:
                return "expired", f"已于 {expires_at} 过期"
        except:
            pass
    
    # 2. 检查是否滥用（超过续期次数）
    if renewal_count >= max_renewals:
        return "overused", f"续期次数 {renewal_count}/{max_renewals} 已达上限"
    
    # 3. 检查是否陈旧
    # 3.1 距离过期时间少于 warning_days
    warning_days_map = {"low": 7, "medium": 5, "high": 3}
    warning_days = warning_days_map.get(debt_level, 5)
    
    if expires_at:
        try:
            expires_dt = datetime.fromisoformat(expires_at)
            days_to_expire = (expires_dt - now).days
            if 0 < days_to_expire <= warning_days:
                return "stale", f"距离过期仅剩 {days_to_expire} 天"
        except:
            pass
    
    # 3.2 超过 escalation_after_days
    if created_at:
        try:
            created_dt = datetime.fromisoformat(created_at)
            days_since_created = (now - created_dt).days
            if days_since_created > escalation_after_days:
                return "stale", f"已存在 {days_since_created} 天，超过 escalation 阈值 {escalation_after_days} 天"
        except:
            pass
    
    # 4. 健康
    return "healthy", "正常生效"


def run_checker(script_path: str, root: Path) -> Dict:
    """执行单个规则检查器"""
    result = {"passed": False, "output": "", "error": None}
    full_path = root / script_path
    if not full_path.exists():
        result["error"] = f"检查器不存在: {script_path}"
        result["passed"] = False
        return result
    try:
        proc = subprocess.run(
            [sys.executable, str(full_path)],
            capture_output=True, text=True, timeout=120, cwd=root
        )
        result["passed"] = proc.returncode == 0
        result["output"] = proc.stdout[-1000:] if proc.stdout else ""
        if proc.returncode != 0 and proc.stderr:
            result["output"] += f"\n[stderr] {proc.stderr[-500:]}"
    except subprocess.TimeoutExpired:
        result["error"] = "检查器执行超时"
    except Exception as e:
        result["error"] = str(e)
    return result


def save_rule_snapshot(registry: Dict, root: Path):
    """保存规则快照"""
    snapshot_path = root / "reports/ops/rule_registry_snapshot.json"
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    rules_snapshot = []
    for key, rule in registry.get("rules", {}).items():
        rules_snapshot.append({
            "rule_id": rule.get("rule_id", key),
            "name": rule.get("name", key),
            "version": rule.get("version", "0.0.0"),
            "owner": rule.get("owner", "unknown"),
            "status": rule.get("status", "active"),
            "rollout_stage": rule.get("rollout_stage", "all"),
            "blocking": rule.get("blocking", True)
        })
    snapshot = {
        "generated_at": datetime.now().isoformat(),
        "registry_version": registry.get("version", "unknown"),
        "rules": rules_snapshot
    }
    with open(snapshot_path, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"  - {snapshot_path}")


def save_exception_debt_snapshot(exceptions_data: Dict, debt_analysis: Dict, root: Path):
    """保存例外债务快照"""
    snapshot_path = root / "reports/ops/rule_exception_debt.json"
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 按 owner 和 rule 分组
    exceptions_by_owner = {}
    exceptions_by_rule = {}
    
    for exc in normalize_exceptions(exceptions_data):
        owner = exc.get("owner", "unknown")
        rule_id = exc.get("rule_id", "unknown")
        
        if owner not in exceptions_by_owner:
            exceptions_by_owner[owner] = []
        exceptions_by_owner[owner].append(exc["exception_id"])
        
        if rule_id not in exceptions_by_rule:
            exceptions_by_rule[rule_id] = []
        exceptions_by_rule[rule_id].append(exc["exception_id"])
    
    snapshot = {
        "generated_at": datetime.now().isoformat(),
        "version": exceptions_data.get("version", "unknown"),
        "summary": {
            "active_count": debt_analysis["healthy_count"] + debt_analysis["stale_count"] + debt_analysis["overused_count"],
            "healthy_count": debt_analysis["healthy_count"],
            "stale_count": debt_analysis["stale_count"],
            "overused_count": debt_analysis["overused_count"],
            "expired_count": debt_analysis["expired_count"],
            "revoked_count": debt_analysis["revoked_count"],
            "high_debt_count": debt_analysis["high_debt_count"]
        },
        "exceptions_by_owner": exceptions_by_owner,
        "exceptions_by_rule": exceptions_by_rule,
        "details": {
            "healthy": debt_analysis["healthy"],
            "stale": debt_analysis["stale"],
            "overused": debt_analysis["overused"],
            "expired": debt_analysis["expired"]
        }
    }
    
    with open(snapshot_path, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    print(f"  - {snapshot_path}")


def run_rule_engine(profile: str) -> Dict:
    """运行规则引擎"""
    root = get_project_root()
    registry = load_rule_registry()
    exceptions_data = load_rule_exceptions()
    exceptions = normalize_exceptions(exceptions_data)
    
    if not registry:
        return {
            "profile": profile, "executed_rules": [], "passed_rules": [],
            "failed_rules": [], "warning_rules": [], "blocking_failures": [],
            "skipped_rules": [], "waived_rules": [], "error": "无法加载规则注册表",
            "generated_at": datetime.now().isoformat()
        }
    
    # 保存规则快照
    save_rule_snapshot(registry, root)
    
    # 分析例外债务
    now = datetime.now()
    debt_analysis = {
        "healthy": [], "stale": [], "overused": [], "expired": [], "revoked": [],
        "healthy_count": 0, "stale_count": 0, "overused_count": 0,
        "expired_count": 0, "revoked_count": 0, "high_debt_count": 0
    }
    
    for exc in exceptions:
        exc_id = exc.get("exception_id")
        status = exc.get("status", "active")
        debt_level = exc.get("debt_level", "medium")
        
        if status == "revoked":
            debt_analysis["revoked"].append(exc_id)
            debt_analysis["revoked_count"] += 1
            continue
        
        debt_status, debt_reason = classify_exception_debt(exc)
        
        exc_info = {
            "exception_id": exc_id,
            "rule_id": exc.get("rule_id"),
            "owner": exc.get("owner"),
            "debt_level": debt_level,
            "debt_status": debt_status,
            "debt_reason": debt_reason
        }
        
        if debt_status == "healthy":
            debt_analysis["healthy"].append(exc_info)
            debt_analysis["healthy_count"] += 1
        elif debt_status == "stale":
            debt_analysis["stale"].append(exc_info)
            debt_analysis["stale_count"] += 1
        elif debt_status == "overused":
            debt_analysis["overused"].append(exc_info)
            debt_analysis["overused_count"] += 1
            if debt_level == "high":
                debt_analysis["high_debt_count"] += 1
        elif debt_status == "expired":
            debt_analysis["expired"].append(exc_info)
            debt_analysis["expired_count"] += 1
    
    # 保存例外债务快照
    save_exception_debt_snapshot(exceptions_data, debt_analysis, root)
    
    # 获取该 profile 应执行的规则
    profile_config = registry.get("profiles", {}).get(profile, {})
    rule_ids = profile_config.get("rules", [])
    all_rules = registry.get("rules", {})
    
    rule_id_to_key = {}
    for key, rule in all_rules.items():
        rid = rule.get("rule_id", key)
        rule_id_to_key[rid] = key
    
    executed_rules = []
    passed_rules = []
    failed_rules = []
    warning_rules = []
    blocking_failures = []
    skipped_rules = []
    waived_rules = []
    
    active_rules = []
    experimental_rules = []
    deprecated_rules = []
    disabled_rules = []
    
    for rule_id in rule_ids:
        rule_key = rule_id_to_key.get(rule_id)
        if not rule_key:
            continue
        rule = all_rules.get(rule_key, {})
        if not rule:
            continue
        
        rule_name = rule.get("name", rule_id)
        checker_script = rule.get("checker_script", "")
        blocking = rule.get("blocking", True)
        status = rule.get("status", "active")
        owner = rule.get("owner", "unknown")
        version = rule.get("version", "0.0.0")
        
        if status == "active":
            active_rules.append(rule_id)
        elif status == "experimental":
            experimental_rules.append(rule_id)
        elif status == "deprecated":
            deprecated_rules.append(rule_id)
        elif status == "disabled":
            disabled_rules.append(rule_id)
        
        if status == "disabled":
            print(f"【跳过规则】{rule_name} ({rule_id}) - disabled")
            executed_rules.append({
                "rule_id": rule_id, "name": rule_name, "owner": owner,
                "status": status, "version": version, "checker": checker_script,
                "passed": None, "blocking": blocking, "skipped": True,
                "skip_reason": "disabled", "waived": False
            })
            skipped_rules.append(rule_id)
            continue
        
        # 检查是否有有效的例外（healthy 或 stale）
        valid_exception = None
        for exc_info in debt_analysis["healthy"] + debt_analysis["stale"]:
            if exc_info["rule_id"] == rule_id:
                # 检查 profile 是否匹配
                for exc in exceptions:
                    if exc["exception_id"] == exc_info["exception_id"]:
                        applies_to = exc.get("applies_to", {})
                        profiles = applies_to.get("profiles", [])
                        if not profiles or profile in profiles:
                            valid_exception = exc
                            break
                if valid_exception:
                    break
        
        # 检查 overused 例外（需要告警）
        overused_exception = None
        for exc_info in debt_analysis["overused"]:
            if exc_info["rule_id"] == rule_id:
                for exc in exceptions:
                    if exc["exception_id"] == exc_info["exception_id"]:
                        applies_to = exc.get("applies_to", {})
                        profiles = applies_to.get("profiles", [])
                        if not profiles or profile in profiles:
                            overused_exception = exc
                            break
                if overused_exception:
                    break
        
        if status == "deprecated":
            print(f"【执行规则】{rule_name} ({rule_id}) - ⚠️ deprecated")
        elif status == "experimental":
            print(f"【执行规则】{rule_name} ({rule_id}) - 🧪 experimental")
        else:
            print(f"【执行规则】{rule_name} ({rule_id})...")
        
        result = run_checker(checker_script, root)
        
        rule_result = {
            "rule_id": rule_id, "name": rule_name, "owner": owner,
            "status": status, "version": version, "checker": checker_script,
            "passed": result["passed"], "blocking": blocking, "skipped": False,
            "skip_reason": None, "waived": False, "waiver_reason": None,
            "error": result.get("error"), "output": result.get("output", "")[:500]
        }
        
        executed_rules.append(rule_result)
        
        if result["passed"]:
            passed_rules.append(rule_id)
            print(f"  ✅ {rule_name}: PASSED")
        else:
            # 检查是否有有效例外豁免
            if valid_exception:
                rule_result["waived"] = True
                rule_result["waiver_reason"] = valid_exception.get("reason")
                rule_result["waiver_debt_status"] = "healthy" if valid_exception["exception_id"] in [e["exception_id"] for e in debt_analysis["healthy"]] else "stale"
                waived_rules.append(rule_id)
                print(f"  ⏭️ {rule_name}: FAILED but WAIVED (exception: {valid_exception['exception_id']})")
            # 检查 overused 例外
            elif overused_exception:
                debt_level = overused_exception.get("debt_level", "medium")
                rule_result["waived"] = True
                rule_result["waiver_reason"] = f"OVERUSED: {overused_exception.get('reason')}"
                rule_result["waiver_debt_status"] = "overused"
                warning_rules.append(rule_id)
                print(f"  ⚠️ {rule_name}: FAILED with OVERUSED exception (debt_level={debt_level})")
                
                # high debt + blocking -> 进入 blocking_failures
                if debt_level == "high" and blocking:
                    blocking_failures.append({
                        "rule_id": rule_id, "name": rule_name, "owner": owner,
                        "status": status, "reason": "overused_exception_high_debt"
                    })
            elif status == "experimental":
                warning_rules.append(rule_id)
                print(f"  ⚠️ {rule_name}: FAILED (experimental, non-blocking)")
            elif status == "deprecated":
                warning_rules.append(rule_id)
                print(f"  ⚠️ {rule_name}: FAILED (deprecated, non-blocking)")
            else:
                failed_rules.append(rule_id)
                print(f"  ❌ {rule_name}: FAILED")
                if result.get("error"):
                    print(f"     错误: {result['error']}")
                if blocking:
                    blocking_failures.append({
                        "rule_id": rule_id, "name": rule_name, "owner": owner, "status": status
                    })
    
    return {
        "profile": profile,
        "executed_rules": executed_rules,
        "passed_rules": passed_rules,
        "failed_rules": failed_rules,
        "warning_rules": warning_rules,
        "blocking_failures": blocking_failures,
        "skipped_rules": skipped_rules,
        "waived_rules": waived_rules,
        "active_rules": active_rules,
        "experimental_rules": experimental_rules,
        "deprecated_rules": deprecated_rules,
        "disabled_rules": disabled_rules,
        "exception_debt": {
            "healthy": [{"exception_id": e["exception_id"], "rule_id": e["rule_id"]} for e in debt_analysis["healthy"]],
            "stale": debt_analysis["stale"],
            "overused": debt_analysis["overused"],
            "expired": debt_analysis["expired"],
            "summary": {
                "healthy_count": debt_analysis["healthy_count"],
                "stale_count": debt_analysis["stale_count"],
                "overused_count": debt_analysis["overused_count"],
                "expired_count": debt_analysis["expired_count"],
                "high_debt_count": debt_analysis["high_debt_count"]
            }
        },
        "total_rules": len([r for r in executed_rules if not r.get("skipped")]),
        "passed_count": len(passed_rules),
        "failed_count": len(failed_rules),
        "warning_count": len(warning_rules),
        "skipped_count": len(skipped_rules),
        "waived_count": len(waived_rules),
        "generated_at": datetime.now().isoformat()
    }


def save_reports(report: Dict):
    """保存报告"""
    root = get_project_root()
    index_path = root / "reports/ops/rule_execution_index.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    
    executions = []
    for r in report["executed_rules"]:
        executions.append({
            "rule_id": r["rule_id"], "status": r["status"], "owner": r["owner"],
            "passed": r["passed"], "blocking": r["blocking"],
            "skipped": r.get("skipped", False), "skip_reason": r.get("skip_reason"),
            "waived": r.get("waived", False), "waiver_reason": r.get("waiver_reason"),
            "waiver_debt_status": r.get("waiver_debt_status")
        })
    
    index = {
        "profile": report["profile"],
        "executions": executions,
        "summary": {
            "total": report["total_rules"],
            "passed": report["passed_count"],
            "failed": report["failed_count"],
            "warnings": report["warning_count"],
            "skipped": report["skipped_count"],
            "waived": report["waived_count"]
        },
        "exception_debt": report.get("exception_debt", {}),
        "timestamp": report["generated_at"]
    }
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    report_path = root / "reports/ops/rule_engine_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 保存 profile 专属快照
    profile_report_path = root / f"reports/ops/rule_engine_report_{report['profile']}.json"
    with open(profile_report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n报告已保存:")
    print(f"  - {index_path}")
    print(f"  - {report_path}")
    print(f"  - {profile_report_path}")


def print_summary(report: Dict):
    """打印摘要"""
    print("\n" + "=" * 50)
    print("【Rule Engine Summary】")
    print("=" * 50)
    print(f"  Profile: {report['profile']}")
    print(f"  Total Rules: {report['total_rules']}")
    print(f"  Passed: {report['passed_count']}")
    print(f"  Failed: {report['failed_count']}")
    print(f"  Warnings: {report['warning_count']}")
    print(f"  Skipped: {report['skipped_count']}")
    print(f"  Waived: {report['waived_count']}")
    
    print(f"\n  【By Status】")
    print(f"    Active: {len(report['active_rules'])}")
    print(f"    Experimental: {len(report['experimental_rules'])}")
    print(f"    Deprecated: {len(report['deprecated_rules'])}")
    print(f"    Disabled: {len(report['disabled_rules'])}")
    
    # 例外债务信息
    debt = report.get("exception_debt", {})
    if debt:
        print(f"\n  【Exception Debt】")
        summary = debt.get("summary", {})
        print(f"    Healthy: {summary.get('healthy_count', 0)}")
        print(f"    Stale: {summary.get('stale_count', 0)}")
        print(f"    Overused: {summary.get('overused_count', 0)}")
        print(f"    Expired: {summary.get('expired_count', 0)}")
        print(f"    High Debt: {summary.get('high_debt_count', 0)}")
        
        if debt.get("stale"):
            print(f"\n  ⚠️ Stale Exceptions:")
            for e in debt["stale"]:
                print(f"    - {e['exception_id']}: {e['rule_id']} ({e['debt_reason']})")
        
        if debt.get("overused"):
            print(f"\n  🚨 Overused Exceptions:")
            for e in debt["overused"]:
                print(f"    - {e['exception_id']}: {e['rule_id']} ({e['debt_reason']})")
    
    if report['blocking_failures']:
        print(f"\n  ❌ Blocking Failures: {len(report['blocking_failures'])}")
        for bf in report['blocking_failures']:
            print(f"    - {bf['rule_id']} (owner: {bf['owner']})")
    
    if report['warning_rules']:
        print(f"\n  ⚠️ Warning Rules: {report['warning_rules']}")
    
    if report['waived_rules']:
        print(f"\n  ⏭️ Waived Rules: {report['waived_rules']}")
    
    if report['skipped_rules']:
        print(f"\n  ⏭️ Skipped Rules: {report['skipped_rules']}")
    
    status = "✅ PASSED" if not report['blocking_failures'] else "❌ FAILED"
    print(f"\n  Overall: {status}")
    print("=" * 50)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="统一规则引擎 V3.0.0")
    parser.add_argument("--profile", required=True, choices=["premerge", "nightly", "release"])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()
    
    print("╔══════════════════════════════════════════════════╗")
    print("║          统一规则引擎 V3.0.0                   ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"Profile: {args.profile}")
    print()
    
    report = run_rule_engine(args.profile)
    
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_summary(report)
    
    if args.save:
        save_reports(report)
    
    return 0 if not report['blocking_failures'] else 1


if __name__ == "__main__":
    sys.exit(main())
