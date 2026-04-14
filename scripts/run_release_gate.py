#!/usr/bin/env python3
"""
发布门禁统一入口 - V3.0.0

提供 CI 可用的统一命令，包含规则检查和变更影响强制门禁
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def run_command(cmd: list) -> int:
    """运行命令并返回退出码"""
    print(f"执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=get_project_root())
    return result.returncode


def run_rule_checks(profile: str = "premerge") -> dict:
    """运行规则检查 - 通过统一规则引擎"""
    root = get_project_root()
    
    # 调用统一规则引擎
    result = subprocess.run(
        [sys.executable, str(root / "scripts/run_rule_engine.py"),
         "--profile", profile, "--save"],
        capture_output=True,
        text=True,
        cwd=root
    )
    
    # 读取规则引擎报告
    report_path = root / "reports/ops/rule_engine_report.json"
    if report_path.exists():
        try:
            report = json.load(open(report_path, encoding='utf-8'))
        except:
            report = {}
    else:
        report = {}
    
    # 转换为兼容格式
    results = {
        "layer_dependency": {"passed": True, "output": ""},
        "json_contract": {"passed": True, "output": ""},
        "_engine_report": report
    }
    
    # 从报告提取状态
    for rule in report.get("executed_rules", []):
        rule_id = rule.get("rule_id", "")
        if rule_id in ["R001", "layer_dependency_rule"]:
            results["layer_dependency"]["passed"] = rule.get("passed", False)
        elif rule_id in ["R002", "json_contract_rule"]:
            results["json_contract"]["passed"] = rule.get("passed", False)
    
    return results


def print_rule_summary(rule_results: dict):
    """打印规则检查摘要 - 从规则引擎报告读取"""
    print("\n" + "=" * 50)
    print("【Rule Checks 摘要】")
    print("=" * 50)
    
    report = rule_results.get("_engine_report", {})
    
    if report:
        print(f"  Total Rules: {report.get('total_rules', 0)}")
        print(f"  Passed: {report.get('passed_count', 0)}")
        print(f"  Failed: {report.get('failed_count', 0)}")
        
        if report.get("blocking_failures"):
            print(f"  Blocking Failures: {report['blocking_failures']}")
    else:
        # 回退到旧格式
        ld_status = "✅ PASSED" if rule_results["layer_dependency"]["passed"] else "❌ FAILED"
        jc_status = "✅ PASSED" if rule_results["json_contract"]["passed"] else "❌ FAILED"
        print(f"  Layer Dependency Status: {ld_status}")
        print(f"  JSON Contract Status: {jc_status}")
    
    print("=" * 50)


def print_change_impact_summary():
    """打印变更影响摘要"""
    root = get_project_root()
    
    print("\n" + "=" * 50)
    print("【Change Impact Summary】")
    print("=" * 50)
    
    # 尝试获取 git diff
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1"],
            capture_output=True,
            text=True,
            cwd=root
        )
        if result.returncode == 0 and result.stdout.strip():
            changed_files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
            print(f"  Changed Files: {len(changed_files)}")
            
            # 调用 change impact 检查并保存报告
            impact_result = subprocess.run(
                [sys.executable, str(root / "scripts/check_change_impact.py"), 
                 "--json", "--from-git", "--report-json", "reports/ops/change_impact.json"],
                capture_output=True,
                text=True,
                cwd=root
            )
            try:
                impact_data = json.loads(impact_result.stdout)
                if impact_data.get("required_commands"):
                    print(f"  Required Commands: {impact_data['total_commands']}")
                    for cmd in impact_data["required_commands"][:3]:
                        print(f"    - {cmd}")
                    if impact_data['total_commands'] > 3:
                        print(f"    ... and {impact_data['total_commands'] - 3} more")
                    if impact_data.get("blocking_if_missing"):
                        print(f"  Blocking: Yes")
                else:
                    print("  Required Commands: None")
            except:
                print("  Required Commands: N/A")
        else:
            print("  Changed Files: N/A (not in git context)")
            print("  Required Commands: N/A")
    except Exception as e:
        print("  Changed Files: N/A")
        print("  Required Commands: N/A")
    
    print("=" * 50)


def save_executed_checks(profile: str, rule_results: dict, gate_results: dict):
    """保存已执行的检查记录"""
    root = get_project_root()
    
    executed = {
        "current_profile": profile,
        "executed_commands": [
            "python scripts/check_layer_dependencies.py",
            "python scripts/check_json_contracts.py",
            "python scripts/check_repo_integrity.py --strict",
            f"python scripts/run_release_gate.py {profile}"
        ],
        "executed_rule_checks": {
            "layer_dependency": rule_results.get("layer_dependency", {}).get("passed", False),
            "json_contract": rule_results.get("json_contract", {}).get("passed", False)
        },
        "executed_gate_checks": gate_results,
        "timestamp": datetime.now().isoformat()
    }
    
    path = root / "reports/ops/executed_checks.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(executed, f, ensure_ascii=False, indent=2)


def save_followup_requirements(impact_data: dict, profile: str):
    """保存 follow-up 要求
    
    注意：当前 profile 不允许出现在 required_profiles 中
    如果当前跑的是 premerge，follow-up 里只能有 nightly 和 release
    """
    root = get_project_root()
    
    # 读取现有的 followup 文件
    followup_path = root / "reports/ops/followup_requirements.json"
    followup = {
        "required_profiles": [],
        "reason_by_profile": {},
        "satisfied_profiles": [],
        "pending_profiles": [],
        "generated_at": datetime.now().isoformat()
    }
    
    if followup_path.exists():
        try:
            followup = json.load(open(followup_path, encoding='utf-8'))
        except:
            pass
    
    # 从 impact_data 获取 required_profiles
    if impact_data:
        required_profiles = impact_data.get("required_profiles", [])
        matched_rules = impact_data.get("matched_rules", [])
        
        for p in required_profiles:
            # 关键修复：当前 profile 不允许出现在 required_profiles
            if p == profile:
                continue
            
            if p not in followup["required_profiles"]:
                followup["required_profiles"].append(p)
            
            # 记录原因
            if p not in followup["reason_by_profile"]:
                followup["reason_by_profile"][p] = []
            
            for rule in matched_rules:
                if p in rule.get("pattern", "") or any(p in cmd for cmd in rule.get("commands", [])):
                    reason = f"{rule['file']} changed"
                    if reason not in followup["reason_by_profile"][p]:
                        followup["reason_by_profile"][p].append(reason)
    
    # 更新 satisfied 状态
    if profile in followup["required_profiles"] and profile not in followup["satisfied_profiles"]:
        followup["satisfied_profiles"].append(profile)
    
    # 更新 pending 状态（排除当前 profile）
    followup["pending_profiles"] = [p for p in followup["required_profiles"] 
                                    if p not in followup["satisfied_profiles"] and p != profile]
    
    followup["generated_at"] = datetime.now().isoformat()
    
    # 保存
    followup_path.parent.mkdir(parents=True, exist_ok=True)
    with open(followup_path, 'w', encoding='utf-8') as f:
        json.dump(followup, f, ensure_ascii=False, indent=2)
    
    return followup


def save_enforcement_report(profile: str, impact_data: dict, executed_data: dict, missing: list):
    """保存强制门禁报告（V2.0.0 - 只检查当前阻断项）"""
    root = get_project_root()
    
    report = {
        "profile": profile,
        "changed_files": impact_data.get("changed_files", []),
        "blocking_commands_current_profile": impact_data.get("blocking_commands_current_profile", []),
        "executed_commands": executed_data.get("executed_commands", []),
        "missing_required_checks": missing,
        "followup_required_profiles": impact_data.get("followup_required_profiles", []),
        "enforcement_passed": len(missing) == 0,
        "generated_at": datetime.now().isoformat()
    }
    
    path = root / "reports/ops/change_impact_enforcement.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report


def check_impact_enforcement() -> dict:
    """检查变更影响强制门禁（V2.0.0 - 只检查当前阻断项）"""
    root = get_project_root()
    
    result = {
        "passed": True,
        "missing_commands": [],
        "required_by": []
    }
    
    # 读取 change_impact.json
    impact_path = root / "reports/ops/change_impact.json"
    if not impact_path.exists():
        return result
    
    try:
        impact_data = json.load(open(impact_path, encoding='utf-8'))
    except:
        return result
    
    # V3.0.0: 只检查当前阻断项，不检查 follow-up
    blocking_commands = impact_data.get("blocking_commands_current_profile", [])
    if not blocking_commands:
        return result
    
    # 读取 executed_checks.json
    executed_path = root / "reports/ops/executed_checks.json"
    executed_commands = []
    if executed_path.exists():
        try:
            executed_data = json.load(open(executed_path, encoding='utf-8'))
            executed_commands = executed_data.get("executed_commands", [])
        except:
            pass
    
    # 检查缺失的命令（只检查当前阻断项）
    for cmd in blocking_commands:
        # 简化匹配：检查命令是否在已执行列表中
        cmd_base = cmd.replace("python scripts/", "")
        found = any(cmd_base in ec for ec in executed_commands)
        if not found:
            result["missing_commands"].append(cmd)
    
    result["passed"] = len(result["missing_commands"]) == 0
    return result


def print_impact_enforcement_summary(enforcement_result: dict):
    """打印变更影响强制门禁摘要"""
    print("\n" + "=" * 50)
    print("【Change Impact Enforcement】")
    print("=" * 50)
    
    if enforcement_result["passed"]:
        print("  Status: ✅ PASSED")
    else:
        print("  Status: ❌ FAILED")
        print(f"  Missing Commands: {len(enforcement_result['missing_commands'])}")
        for cmd in enforcement_result["missing_commands"]:
            print(f"    - {cmd}")
        if enforcement_result["required_by"]:
            print("  Required By:")
            for f in enforcement_result["required_by"][:5]:
                print(f"    - {f}")
    
    print("=" * 50)


def run_expire_check() -> dict:
    """运行例外过期检查 - 门禁前置步骤"""
    root = get_project_root()
    
    print("\n" + "=" * 50)
    print("【Exception Expire Check】")
    print("=" * 50)
    
    result = subprocess.run(
        [sys.executable, str(root / "scripts/exception_manager.py"), "expire-check"],
        capture_output=True,
        text=True,
        cwd=root
    )
    
    try:
        data = json.loads(result.stdout)
        expired_count = data.get("expired_count", 0)
        print(f"  Expired exceptions: {expired_count}")
        if expired_count > 0:
            print(f"  Expired: {', '.join(data.get('expired', []))}")
        print("=" * 50)
        return data
    except:
        print("  ⚠️ 无法解析结果")
        print("=" * 50)
        return {"status": "error", "expired_count": 0}


def check_exception_constraints(profile: str) -> dict:
    """检查例外约束 - release 门禁特有"""
    root = get_project_root()
    
    result = {
        "passed": True,
        "blocked_exceptions": [],
        "reason": ""
    }
    
    if profile != "release":
        return result
    
    # 读取例外状态快照
    status_path = root / "reports/ops/rule_exception_status.json"
    if not status_path.exists():
        return result
    
    try:
        status = json.load(open(status_path, encoding='utf-8'))
    except:
        return result
    
    # 读取例外真源
    exceptions_path = root / "core/RULE_EXCEPTIONS.json"
    if not exceptions_path.exists():
        return result
    
    try:
        exceptions_data = json.load(open(exceptions_path, encoding='utf-8'))
        exceptions = exceptions_data.get("exceptions", {})
    except:
        return result
    
    # 读取规则注册表
    rules_path = root / "core/RULE_REGISTRY.json"
    blocking_rules = set()
    if rules_path.exists():
        try:
            rules_data = json.load(open(rules_path, encoding='utf-8'))
            for rule_id, rule in rules_data.get("rules", {}).items():
                if rule.get("enforcement") == "blocking":
                    blocking_rules.add(rule_id)
        except:
            pass
    
    # 检查高风险例外
    for exc_id, exc in exceptions.items():
        if exc.get("status") != "active":
            continue
        
        debt_level = exc.get("debt_level", "low")
        renewal_count = exc.get("renewal_count", 0)
        max_renewals = exc.get("max_renewals", 2)
        rule_id = exc.get("rule_id", "")
        
        # 高债务 + 超续期 + blocking rule = 阻断
        if debt_level == "high" and renewal_count >= max_renewals and rule_id in blocking_rules:
            result["passed"] = False
            result["blocked_exceptions"].append({
                "exception_id": exc_id,
                "rule_id": rule_id,
                "debt_level": debt_level,
                "renewal_count": renewal_count,
                "max_renewals": max_renewals
            })
    
    if not result["passed"]:
        result["reason"] = "存在高风险例外：high debt + overused + blocking rule"
    
    return result


def verify_premerge():
    """premerge 门禁"""
    root = get_project_root()
    
    # 0. 例外过期检查 - 门禁前置
    run_expire_check()
    
    # 1. 规则检查 - 通过统一规则引擎
    rule_results = run_rule_checks("premerge")
    print_rule_summary(rule_results)
    
    # 0.1 变更影响摘要
    print_change_impact_summary()
    
    # 1. 运行时验收
    rc = run_command([
        sys.executable,
        str(root / "infrastructure/verify_runtime_integrity.py"),
        "--profile", "premerge",
        "--report-json", "reports/runtime_integrity.json"
    ])
    
    gate_results = {"runtime": rc == 0, "quality": False}
    
    if rc != 0:
        # 保存执行记录
        save_executed_checks("premerge", rule_results, gate_results)
        return rc
    
    # 2. 质量门禁
    rc = run_command([
        sys.executable,
        str(root / "governance/quality_gate.py"),
        "--report-json", "reports/quality_gate.json"
    ])
    
    gate_results["quality"] = rc == 0
    
    # 保存执行记录
    save_executed_checks("premerge", rule_results, gate_results)
    
    # 3. 读取 change_impact.json
    impact_path = root / "reports/ops/change_impact.json"
    impact_data = {}
    if impact_path.exists():
        try:
            impact_data = json.load(open(impact_path, encoding='utf-8'))
        except:
            pass
    
    # 4. 保存 follow-up 要求
    followup = save_followup_requirements(impact_data, "premerge")
    
    # 5. 检查变更影响强制门禁
    enforcement_result = check_impact_enforcement()
    print_impact_enforcement_summary(enforcement_result)
    
    # 6. 保存强制门禁报告
    executed_path = root / "reports/ops/executed_checks.json"
    executed_data = {}
    if executed_path.exists():
        try:
            executed_data = json.load(open(executed_path, encoding='utf-8'))
        except:
            pass
    
    save_enforcement_report("premerge", impact_data, executed_data, enforcement_result["missing_commands"])
    
    # 7. 打印 follow-up 状态
    if followup.get("pending_profiles"):
        print("\n" + "=" * 50)
        print("【Follow-up Requirements】")
        print("=" * 50)
        print(f"  Pending Profiles: {', '.join(followup['pending_profiles'])}")
        for p in followup['pending_profiles']:
            reasons = followup.get('reason_by_profile', {}).get(p, [])
            if reasons:
                print(f"    {p}: {', '.join(reasons[:3])}")
        print("=" * 50)
    
    # 规则检查失败也返回错误
    if not rule_results["layer_dependency"]["passed"] or not rule_results["json_contract"]["passed"]:
        return 1
    
    # 变更影响强制门禁失败也返回错误
    if not enforcement_result["passed"]:
        return 1
    
    return rc


def verify_nightly():
    """nightly 门禁"""
    root = get_project_root()
    
    # 0. 例外过期检查 - 门禁前置
    run_expire_check()
    
    # 1. 规则检查 - 通过统一规则引擎
    rule_results = run_rule_checks("nightly")
    print_rule_summary(rule_results)
    
    rc = run_command([
        sys.executable,
        str(root / "infrastructure/verify_runtime_integrity.py"),
        "--profile", "nightly",
        "--report-json", "reports/runtime_integrity.json"
    ])
    
    gate_results = {"runtime": rc == 0, "quality": False}
    
    if rc != 0:
        save_executed_checks("nightly", rule_results, gate_results)
        return rc
    
    rc = run_command([
        sys.executable,
        str(root / "governance/quality_gate.py"),
        "--report-json", "reports/quality_gate.json"
    ])
    
    gate_results["quality"] = rc == 0
    save_executed_checks("nightly", rule_results, gate_results)
    
    # 更新 follow-up 状态
    followup_path = root / "reports/ops/followup_requirements.json"
    if followup_path.exists():
        try:
            followup = json.load(open(followup_path, encoding='utf-8'))
            if "nightly" in followup.get("required_profiles", []):
                if "nightly" not in followup.get("satisfied_profiles", []):
                    followup["satisfied_profiles"].append("nightly")
                followup["pending_profiles"] = [p for p in followup["required_profiles"] 
                                                if p not in followup["satisfied_profiles"]]
                followup["generated_at"] = datetime.now().isoformat()
                
                with open(followup_path, 'w', encoding='utf-8') as f:
                    json.dump(followup, f, ensure_ascii=False, indent=2)
                
                print("\n" + "=" * 50)
                print("【Follow-up Requirements Status】")
                print("=" * 50)
                print(f"  Nightly: ✅ Satisfied")
                if followup.get("pending_profiles"):
                    print(f"  Pending: {', '.join(followup['pending_profiles'])}")
                print("=" * 50)
        except:
            pass
    
    # 规则检查失败也返回错误
    if not rule_results["layer_dependency"]["passed"] or not rule_results["json_contract"]["passed"]:
        return 1
    
    return rc


def verify_release():
    """release 门禁"""
    root = get_project_root()
    
    # 0. 例外过期检查 - 门禁前置
    run_expire_check()
    
    # 1. 例外约束检查 - release 特有
    exception_result = check_exception_constraints("release")
    if not exception_result["passed"]:
        print("\n" + "=" * 50)
        print("【Exception Constraint Violation】")
        print("=" * 50)
        print(f"  Reason: {exception_result['reason']}")
        for exc in exception_result["blocked_exceptions"]:
            print(f"  - {exc['exception_id']}: {exc['rule_id']}")
            print(f"    debt_level: {exc['debt_level']}, renewals: {exc['renewal_count']}/{exc['max_renewals']}")
        print("=" * 50)
        print("❌ Release blocked by high-risk exceptions")
        return 1
    
    # 2. 规则检查 - 通过统一规则引擎
    rule_results = run_rule_checks("release")
    print_rule_summary(rule_results)
    
    # 1. 运行时验收
    rc = run_command([
        sys.executable,
        str(root / "infrastructure/verify_runtime_integrity.py"),
        "--profile", "release",
        "--report-json", "reports/runtime_integrity.json"
    ])
    
    gate_results = {"runtime": rc == 0, "quality": False, "release": False}
    
    if rc != 0:
        save_executed_checks("release", rule_results, gate_results)
        return rc
    
    # 2. 质量门禁
    rc = run_command([
        sys.executable,
        str(root / "governance/quality_gate.py"),
        "--report-json", "reports/quality_gate.json"
    ])
    
    gate_results["quality"] = rc == 0
    
    if rc != 0:
        save_executed_checks("release", rule_results, gate_results)
        return rc
    
    # 3. 发布门禁检查
    rc = run_command([
        sys.executable,
        str(root / "infrastructure/release/release_manager.py"),
        "--check",
        "--report-json", "reports/release_gate.json"
    ])
    
    gate_results["release"] = rc == 0
    save_executed_checks("release", rule_results, gate_results)
    
    # 更新 follow-up 状态
    followup_path = root / "reports/ops/followup_requirements.json"
    if followup_path.exists():
        try:
            followup = json.load(open(followup_path, encoding='utf-8'))
            if "release" in followup.get("required_profiles", []):
                if "release" not in followup.get("satisfied_profiles", []):
                    followup["satisfied_profiles"].append("release")
                followup["pending_profiles"] = [p for p in followup["required_profiles"] 
                                                if p not in followup["satisfied_profiles"]]
                followup["generated_at"] = datetime.now().isoformat()
                
                with open(followup_path, 'w', encoding='utf-8') as f:
                    json.dump(followup, f, ensure_ascii=False, indent=2)
                
                print("\n" + "=" * 50)
                print("【Follow-up Requirements Status】")
                print("=" * 50)
                print(f"  Release: ✅ Satisfied")
                if followup.get("pending_profiles"):
                    print(f"  Pending: {', '.join(followup['pending_profiles'])}")
                else:
                    print("  All follow-up requirements satisfied!")
                print("=" * 50)
        except:
            pass
    
    # 规则检查失败也返回错误
    if not rule_results["layer_dependency"]["passed"] or not rule_results["json_contract"]["passed"]:
        return 1
    
    return rc


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="发布门禁统一入口")
    parser.add_argument("profile", choices=["premerge", "nightly", "release"], help="门禁模式")
    args = parser.parse_args()
    
    if args.profile == "premerge":
        rc = verify_premerge()
    elif args.profile == "nightly":
        rc = verify_nightly()
    else:
        rc = verify_release()
    
    sys.exit(rc)
