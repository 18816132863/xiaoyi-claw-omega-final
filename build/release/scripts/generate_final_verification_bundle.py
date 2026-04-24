#!/usr/bin/env python3
"""
生成最终验收包 - V1.0.0

汇总所有 profile 的验收结果
"""

import json
from pathlib import Path
from datetime import datetime


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def check_file_exists(path: Path) -> bool:
    return path.exists()


def load_json(path: Path) -> dict:
    if path.exists():
        try:
            return json.load(open(path, encoding='utf-8'))
        except:
            return {}
    return {}


def main():
    root = get_project_root()
    timestamp = datetime.now()
    
    # 检查各 profile 报告
    profiles = ["premerge", "nightly", "release"]
    
    results = {
        "generated_at": timestamp.isoformat(),
        "repo_integrity_passed": False,
        "profiles": {},
        "report_files": {}
    }
    
    # 检查 repo integrity
    repo_integrity_path = root / "reports/runtime_integrity.json"
    if repo_integrity_path.exists():
        data = load_json(repo_integrity_path)
        results["repo_integrity_passed"] = data.get("overall_passed", False)
    
    # 检查各 profile
    for profile in profiles:
        profile_result = {
            "rule_engine_passed": False,
            "gate_passed": False,
            "enforcement_passed": False,
            "runtime_passed": False,
            "quality_passed": False
        }
        
        # rule engine
        rule_engine_path = root / f"reports/ops/rule_engine_report_{profile}.json"
        if rule_engine_path.exists():
            data = load_json(rule_engine_path)
            profile_result["rule_engine_passed"] = len(data.get("blocking_failures", [])) == 0
        
        # executed checks
        executed_path = root / f"reports/ops/executed_checks_{profile}.json"
        if executed_path.exists():
            data = load_json(executed_path)
            profile_result["gate_passed"] = not data.get("engine_failed", True)
        
        # enforcement
        enforcement_path = root / f"reports/ops/change_impact_enforcement_{profile}.json"
        if enforcement_path.exists():
            data = load_json(enforcement_path)
            profile_result["enforcement_passed"] = data.get("enforcement_passed", False)
        
        # runtime
        runtime_path = root / f"reports/runtime_integrity_{profile}.json"
        if runtime_path.exists():
            data = load_json(runtime_path)
            profile_result["runtime_passed"] = data.get("overall_passed", False)
        
        # quality
        quality_path = root / f"reports/quality_gate_{profile}.json"
        if quality_path.exists():
            data = load_json(quality_path)
            profile_result["quality_passed"] = data.get("overall_passed", False)
        
        results["profiles"][profile] = profile_result
        
        # 记录报告文件路径
        results["report_files"][profile] = {
            "rule_engine": str(rule_engine_path.relative_to(root)) if rule_engine_path.exists() else None,
            "executed_checks": str(executed_path.relative_to(root)) if executed_path.exists() else None,
            "enforcement": str(enforcement_path.relative_to(root)) if enforcement_path.exists() else None,
            "runtime": str(runtime_path.relative_to(root)) if runtime_path.exists() else None,
            "quality": str(quality_path.relative_to(root)) if quality_path.exists() else None
        }
    
    # 计算总体通过状态
    all_passed = (
        results["repo_integrity_passed"] and
        all(
            p.get("rule_engine_passed", False) and
            p.get("gate_passed", False) and
            p.get("enforcement_passed", False)
            for p in results["profiles"].values()
        )
    )
    
    results["overall_passed"] = all_passed
    
    # 保存
    bundle_dir = root / "reports/bundles"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    
    bundle_path = bundle_dir / "final_verification_bundle.json"
    with open(bundle_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 打印结果
    print("╔══════════════════════════════════════════════════╗")
    print("║          最终验收包                            ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    print(f"生成时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print(f"【Repo Integrity】 {'✅ PASSED' if results['repo_integrity_passed'] else '❌ FAILED'}")
    print()
    
    for profile, presult in results["profiles"].items():
        print(f"【{profile.upper()}】")
        print(f"  Rule Engine: {'✅' if presult['rule_engine_passed'] else '❌'}")
        print(f"  Gate: {'✅' if presult['gate_passed'] else '❌'}")
        print(f"  Enforcement: {'✅' if presult['enforcement_passed'] else '❌'}")
        print()
    
    print("══════════════════════════════════════════════════")
    if all_passed:
        print("✅ 所有验收通过")
    else:
        print("❌ 存在验收失败")
    print("══════════════════════════════════════════════════")
    print()
    print(f"验收包已保存: {bundle_path}")
    
    import sys
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
