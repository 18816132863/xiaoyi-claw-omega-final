#!/usr/bin/env python3
"""
发布门禁统一入口 - V2.0.0

提供 CI 可用的统一命令，包含规则检查
"""

import sys
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


def run_rule_checks() -> dict:
    """运行规则检查"""
    root = get_project_root()
    results = {
        "layer_dependency": {"passed": True, "output": ""},
        "json_contract": {"passed": True, "output": ""}
    }
    
    # 层间依赖检查
    print("\n【规则检查】层间依赖...")
    result = subprocess.run(
        [sys.executable, str(root / "scripts/check_layer_dependencies.py")],
        capture_output=True,
        text=True,
        cwd=root
    )
    results["layer_dependency"]["passed"] = result.returncode == 0
    results["layer_dependency"]["output"] = result.stdout[-500:] if result.stdout else ""
    
    # JSON 契约检查
    print("【规则检查】JSON 契约...")
    result = subprocess.run(
        [sys.executable, str(root / "scripts/check_json_contracts.py")],
        capture_output=True,
        text=True,
        cwd=root
    )
    results["json_contract"]["passed"] = result.returncode == 0
    results["json_contract"]["output"] = result.stdout[-500:] if result.stdout else ""
    
    return results


def print_rule_summary(rule_results: dict):
    """打印规则检查摘要"""
    print("\n" + "=" * 50)
    print("【Rule Checks 摘要】")
    print("=" * 50)
    
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
            
            # 调用 change impact 检查
            impact_result = subprocess.run(
                [sys.executable, str(root / "scripts/check_change_impact.py"), "--json", "--files"] + changed_files,
                capture_output=True,
                text=True,
                cwd=root
            )
            if impact_result.returncode == 0:
                import json
                try:
                    impact_data = json.loads(impact_result.stdout)
                    if impact_data.get("required_commands"):
                        print(f"  Required Commands: {impact_data['total_commands']}")
                        for cmd in impact_data["required_commands"][:3]:
                            print(f"    - {cmd}")
                        if impact_data['total_commands'] > 3:
                            print(f"    ... and {impact_data['total_commands'] - 3} more")
                    else:
                        print("  Required Commands: None")
                except:
                    print("  Required Commands: N/A")
            else:
                print("  Required Commands: N/A")
        else:
            print("  Changed Files: N/A (not in git context)")
            print("  Required Commands: N/A")
    except Exception as e:
        print("  Changed Files: N/A")
        print("  Required Commands: N/A")
    
    print("=" * 50)


def verify_premerge():
    """premerge 门禁"""
    root = get_project_root()
    
    # 0. 规则检查
    rule_results = run_rule_checks()
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
    if rc != 0:
        return rc
    
    # 2. 质量门禁
    rc = run_command([
        sys.executable,
        str(root / "governance/quality_gate.py"),
        "--report-json", "reports/quality_gate.json"
    ])
    
    # 规则检查失败也返回错误
    if not rule_results["layer_dependency"]["passed"] or not rule_results["json_contract"]["passed"]:
        return 1
    
    return rc


def verify_nightly():
    """nightly 门禁"""
    root = get_project_root()
    
    # 0. 规则检查
    rule_results = run_rule_checks()
    print_rule_summary(rule_results)
    
    rc = run_command([
        sys.executable,
        str(root / "infrastructure/verify_runtime_integrity.py"),
        "--profile", "nightly",
        "--report-json", "reports/runtime_integrity.json"
    ])
    if rc != 0:
        return rc
    
    rc = run_command([
        sys.executable,
        str(root / "governance/quality_gate.py"),
        "--report-json", "reports/quality_gate.json"
    ])
    
    # 规则检查失败也返回错误
    if not rule_results["layer_dependency"]["passed"] or not rule_results["json_contract"]["passed"]:
        return 1
    
    return rc


def verify_release():
    """release 门禁"""
    root = get_project_root()
    
    # 0. 规则检查
    rule_results = run_rule_checks()
    print_rule_summary(rule_results)
    
    # 1. 运行时验收
    rc = run_command([
        sys.executable,
        str(root / "infrastructure/verify_runtime_integrity.py"),
        "--profile", "release",
        "--report-json", "reports/runtime_integrity.json"
    ])
    if rc != 0:
        return rc
    
    # 2. 质量门禁
    rc = run_command([
        sys.executable,
        str(root / "governance/quality_gate.py"),
        "--report-json", "reports/quality_gate.json"
    ])
    if rc != 0:
        return rc
    
    # 3. 发布门禁检查
    rc = run_command([
        sys.executable,
        str(root / "infrastructure/release/release_manager.py"),
        "--check",
        "--report-json", "reports/release_gate.json"
    ])
    
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
