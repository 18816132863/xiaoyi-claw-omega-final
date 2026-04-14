#!/usr/bin/env python3
"""
统一巡检器 - V1.0.0

整合所有检查脚本，提供一站式巡检能力

巡检项：
1. 规则引擎检查
2. 层间依赖检查
3. JSON 契约检查
4. 仓库完整性检查
5. 变更影响检查
6. 技能安全检查
7. 架构完整性检查
8. 例外债务检查
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import concurrent.futures

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def run_check(name: str, script: str, root: Path, timeout: int = 60) -> Dict:
    """运行单个检查"""
    result = {
        "name": name,
        "script": script,
        "passed": False,
        "duration_ms": 0,
        "output": "",
        "error": None
    }
    
    import time
    start = time.time()
    
    try:
        proc = subprocess.run(
            [sys.executable, str(root / script)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=root
        )
        result["passed"] = proc.returncode == 0
        result["output"] = proc.stdout[-500:] if proc.stdout else ""
        if proc.returncode != 0 and proc.stderr:
            result["error"] = proc.stderr[-300:]
    except subprocess.TimeoutExpired:
        result["error"] = "检查超时"
    except Exception as e:
        result["error"] = str(e)
    
    result["duration_ms"] = int((time.time() - start) * 1000)
    return result


def run_all_checks(profile: str = "premerge", parallel: bool = True) -> Dict:
    """运行所有检查"""
    root = get_project_root()
    
    checks = [
        ("规则引擎", "scripts/run_rule_engine.py", 180),
        ("层间依赖", "scripts/check_layer_dependencies.py", 60),
        ("JSON契约", "scripts/check_json_contracts.py", 60),
        ("仓库完整性", "scripts/check_repo_integrity_fast.py", 30),
        ("变更影响", "scripts/check_change_impact_enforcement.py", 60),
        ("技能安全", "scripts/check_skill_security.py", 120),
        ("架构完整性", "infrastructure/architecture_inspector.py", 60),
    ]
    
    results = {
        "profile": profile,
        "generated_at": datetime.now().isoformat(),
        "checks": [],
        "summary": {
            "total": len(checks),
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "total_duration_ms": 0
        }
    }
    
    print("╔══════════════════════════════════════════════════╗")
    print("║          统一巡检器 V1.0.0                     ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"Profile: {profile}")
    print(f"模式: {'并行' if parallel else '串行'}")
    print()
    
    if parallel:
        # 并行执行
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(run_check, name, script, root, timeout): name
                for name, script, timeout in checks
            }
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results["checks"].append(result)
                results["summary"]["total_duration_ms"] += result["duration_ms"]
                
                if result["passed"]:
                    results["summary"]["passed"] += 1
                    print(f"  ✅ {result['name']}: PASSED ({result['duration_ms']}ms)")
                else:
                    results["summary"]["failed"] += 1
                    print(f"  ❌ {result['name']}: FAILED ({result['duration_ms']}ms)")
                    if result.get("error"):
                        print(f"     错误: {result['error'][:100]}")
    else:
        # 串行执行
        for name, script, timeout in checks:
            result = run_check(name, script, root, timeout)
            results["checks"].append(result)
            results["summary"]["total_duration_ms"] += result["duration_ms"]
            
            if result["passed"]:
                results["summary"]["passed"] += 1
                print(f"  ✅ {result['name']}: PASSED ({result['duration_ms']}ms)")
            else:
                results["summary"]["failed"] += 1
                print(f"  ❌ {result['name']}: FAILED ({result['duration_ms']}ms)")
                if result.get("error"):
                    print(f"     错误: {result['error'][:100]}")
    
    return results


def save_report(results: Dict):
    """保存巡检报告"""
    root = get_project_root()
    report_path = root / "reports/ops/unified_inspection.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n报告已保存: {report_path}")


def print_summary(results: Dict):
    """打印摘要"""
    summary = results["summary"]
    
    print()
    print("=" * 50)
    print("【巡检摘要】")
    print("=" * 50)
    print(f"  总检查项: {summary['total']}")
    print(f"  通过: {summary['passed']}")
    print(f"  失败: {summary['failed']}")
    print(f"  总耗时: {summary['total_duration_ms']}ms")
    
    status = "✅ 全部通过" if summary['failed'] == 0 else "❌ 存在失败"
    print(f"\n  状态: {status}")
    print("=" * 50)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="统一巡检器 V1.0.0")
    parser.add_argument("--profile", default="premerge", choices=["premerge", "nightly", "release"])
    parser.add_argument("--serial", action="store_true", help="串行执行")
    parser.add_argument("--save", action="store_true", help="保存报告")
    args = parser.parse_args()
    
    results = run_all_checks(args.profile, parallel=not args.serial)
    print_summary(results)
    
    if args.save:
        save_report(results)
    
    return 0 if results["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
