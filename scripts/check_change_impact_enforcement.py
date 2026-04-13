#!/usr/bin/env python3
"""
变更影响强制门禁检查器 - V1.0.0

检查 required commands 是否已执行，follow-up profiles 是否已满足
"""

import sys
import json
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


def load_json_file(path: Path) -> Dict:
    """加载 JSON 文件"""
    if not path.exists():
        return {}
    try:
        return json.load(open(path, encoding='utf-8'))
    except:
        return {}


def check_enforcement(profile: str = "premerge") -> Dict:
    """检查变更影响强制门禁"""
    root = get_project_root()
    
    # 读取变更影响报告
    impact_data = load_json_file(root / "reports/ops/change_impact.json")
    
    # 读取已执行检查
    executed_data = load_json_file(root / "reports/ops/executed_checks.json")
    
    # 读取 follow-up 要求
    followup_data = load_json_file(root / "reports/ops/followup_requirements.json")
    
    result = {
        "profile": profile,
        "changed_files": impact_data.get("changed_files", []),
        "required_commands": impact_data.get("required_commands", []),
        "required_profiles": impact_data.get("required_profiles", []),
        "executed_commands": executed_data.get("executed_commands", []),
        "missing_required_checks": [],
        "followup_required_profiles": [],
        "enforcement_passed": True,
        "generated_at": datetime.now().isoformat()
    }
    
    # 检查 required commands
    for cmd in result["required_commands"]:
        cmd_base = cmd.replace("python scripts/", "")
        found = any(cmd_base in ec for ec in result["executed_commands"])
        if not found:
            result["missing_required_checks"].append(cmd)
    
    # 检查 follow-up profiles
    if followup_data:
        result["followup_required_profiles"] = followup_data.get("pending_profiles", [])
    
    # 判断是否通过
    if result["missing_required_checks"]:
        result["enforcement_passed"] = False
    
    return result


def save_enforcement_report(report: Dict):
    """保存强制门禁报告"""
    root = get_project_root()
    path = root / "reports/ops/change_impact_enforcement.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def print_enforcement_report(report: Dict):
    """打印强制门禁报告"""
    print("╔══════════════════════════════════════════════════╗")
    print("║          变更影响强制门禁检查                   ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    print(f"Profile: {report['profile']}")
    print(f"Changed Files: {len(report['changed_files'])}")
    print()
    
    print(f"Required Commands: {len(report['required_commands'])}")
    print(f"Executed Commands: {len(report['executed_commands'])}")
    print()
    
    if report['missing_required_checks']:
        print("【Missing Required Checks】")
        for cmd in report['missing_required_checks']:
            print(f"  ❌ {cmd}")
        print()
    
    if report['followup_required_profiles']:
        print("【Follow-up Required Profiles】")
        for p in report['followup_required_profiles']:
            print(f"  ⏳ {p}")
        print()
    
    status = "✅ PASSED" if report['enforcement_passed'] else "❌ FAILED"
    print(f"Enforcement Status: {status}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="变更影响强制门禁检查器")
    parser.add_argument("--profile", default="premerge", help="门禁模式")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--save", action="store_true", help="保存报告到文件")
    args = parser.parse_args()
    
    report = check_enforcement(args.profile)
    
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_enforcement_report(report)
    
    if args.save:
        save_enforcement_report(report)
        print(f"\n报告已保存: reports/ops/change_impact_enforcement.json")
    
    return 0 if report['enforcement_passed'] else 1


if __name__ == "__main__":
    sys.exit(main())
