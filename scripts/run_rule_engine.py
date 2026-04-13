#!/usr/bin/env python3
"""
统一规则引擎 - V1.0.0

读取 RULE_REGISTRY.json，按 profile 执行对应规则检查器，生成统一结果
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def load_rule_registry() -> Dict:
    """加载规则注册表"""
    root = get_project_root()
    registry_path = root / "core/RULE_REGISTRY.json"
    
    if not registry_path.exists():
        print(f"❌ 规则注册表不存在: {registry_path}")
        return {}
    
    try:
        return json.load(open(registry_path, encoding='utf-8'))
    except Exception as e:
        print(f"❌ 无法加载规则注册表: {e}")
        return {}


def run_checker(script_path: str, root: Path) -> Dict:
    """执行单个规则检查器"""
    result = {
        "passed": False,
        "output": "",
        "error": None
    }
    
    full_path = root / script_path
    if not full_path.exists():
        result["error"] = f"检查器不存在: {script_path}"
        return result
    
    try:
        proc = subprocess.run(
            [sys.executable, str(full_path)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=root
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


def run_rule_engine(profile: str) -> Dict:
    """运行规则引擎"""
    root = get_project_root()
    registry = load_rule_registry()
    
    if not registry:
        return {
            "profile": profile,
            "executed_rules": [],
            "passed_rules": [],
            "failed_rules": [],
            "warning_rules": [],
            "blocking_failures": [],
            "generated_at": datetime.now().isoformat(),
            "error": "无法加载规则注册表"
        }
    
    # 获取该 profile 应执行的规则
    profile_config = registry.get("profiles", {}).get(profile, {})
    rule_ids = profile_config.get("rules", [])
    all_rules = registry.get("rules", {})
    
    # 构建 rule_id -> rule_key 的映射
    rule_id_to_key = {}
    for key, rule in all_rules.items():
        rid = rule.get("rule_id", key)
        rule_id_to_key[rid] = key
    
    executed_rules = []
    passed_rules = []
    failed_rules = []
    warning_rules = []
    blocking_failures = []
    
    for rule_id in rule_ids:
        # 通过 rule_id 找到规则 key
        rule_key = rule_id_to_key.get(rule_id)
        if not rule_key:
            print(f"  ⚠️ 规则 {rule_id} 未找到")
            continue
        
        rule = all_rules.get(rule_key, {})
        if not rule:
            continue
        
        rule_name = rule.get("name", rule_id)
        checker_script = rule.get("checker_script", "")
        blocking = rule.get("blocking", True)
        
        print(f"【执行规则】{rule_name} ({rule_id})...")
        
        result = run_checker(checker_script, root)
        
        rule_result = {
            "rule_id": rule_id,
            "name": rule_name,
            "checker": checker_script,
            "passed": result["passed"],
            "blocking": blocking,
            "error": result.get("error"),
            "output": result.get("output", "")[:500]
        }
        
        executed_rules.append(rule_result)
        
        if result["passed"]:
            passed_rules.append(rule_id)
            print(f"  ✅ {rule_name}: PASSED")
        else:
            failed_rules.append(rule_id)
            print(f"  ❌ {rule_name}: FAILED")
            if result.get("error"):
                print(f"     错误: {result['error']}")
            
            if blocking:
                blocking_failures.append(rule_id)
    
    return {
        "profile": profile,
        "executed_rules": executed_rules,
        "passed_rules": passed_rules,
        "failed_rules": failed_rules,
        "warning_rules": warning_rules,
        "blocking_failures": blocking_failures,
        "total_rules": len(executed_rules),
        "passed_count": len(passed_rules),
        "failed_count": len(failed_rules),
        "generated_at": datetime.now().isoformat()
    }


def save_reports(report: Dict):
    """保存报告"""
    root = get_project_root()
    
    # 保存规则执行索引
    index_path = root / "reports/ops/rule_execution_index.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    
    index = {
        "profile": report["profile"],
        "executed_rule_ids": [r["rule_id"] for r in report["executed_rules"]],
        "passed_rule_ids": report["passed_rules"],
        "failed_rule_ids": report["failed_rules"],
        "blocking_failures": report["blocking_failures"],
        "timestamp": report["generated_at"]
    }
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    # 保存完整报告
    report_path = root / "reports/ops/rule_engine_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n报告已保存:")
    print(f"  - {index_path}")
    print(f"  - {report_path}")


def print_summary(report: Dict):
    """打印摘要"""
    print("\n" + "=" * 50)
    print("【Rule Engine Summary】")
    print("=" * 50)
    print(f"  Profile: {report['profile']}")
    print(f"  Total Rules: {report['total_rules']}")
    print(f"  Passed: {report['passed_count']}")
    print(f"  Failed: {report['failed_count']}")
    
    if report['blocking_failures']:
        print(f"\n  ❌ Blocking Failures: {len(report['blocking_failures'])}")
        for rule_id in report['blocking_failures']:
            print(f"    - {rule_id}")
    
    status = "✅ PASSED" if not report['blocking_failures'] else "❌ FAILED"
    print(f"\n  Overall: {status}")
    print("=" * 50)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="统一规则引擎 V1.0.0")
    parser.add_argument("--profile", required=True, choices=["premerge", "nightly", "release"],
                        help="门禁模式")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--save", action="store_true", help="保存报告到文件")
    args = parser.parse_args()
    
    print("╔══════════════════════════════════════════════════╗")
    print("║          统一规则引擎 V1.0.0                   ║")
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
