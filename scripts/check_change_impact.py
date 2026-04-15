#!/usr/bin/env python3
"""
变更影响检查器 - V2.0.0

根据 CHANGE_IMPACT_ENFORCEMENT_POLICY.md 规则，分析变更文件并输出必须执行的命令

使用方法：
    python scripts/check_change_impact.py --files file1.py file2.json
    python scripts/check_change_impact.py --from-git
    python scripts/check_change_impact.py --from-git --report-json reports/ops/change_impact.json
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


# 变更影响规则映射 (V3.0.0 - 拆分当前阻断项和 follow-up)
# blocking_commands_for_profile: 当前 profile 必须执行的命令
# followup_profiles: 后续需要补跑的 profile
CHANGE_IMPACT_RULES = {
    "infrastructure/inventory/skill_registry.json": {
        "blocking_commands_for_profile": {
            "premerge": [
                "python scripts/check_repo_integrity.py --strict"
            ],
            "nightly": [],
            "release": []
        },
        "followup_profiles": [],
        "description": "技能注册表变更，必须验证仓库完整性"
    },
    "execution/*": {
        "blocking_commands_for_profile": {
            "premerge": [
                "python scripts/check_layer_dependencies.py"
            ],
            "nightly": [],
            "release": []
        },
        "followup_profiles": ["nightly"],
        "description": "执行层变更，premerge 必须通过，nightly 为 follow-up"
    },
    "governance/*": {
        "blocking_commands_for_profile": {
            "premerge": [
                "python scripts/check_layer_dependencies.py"
            ],
            "nightly": [],
            "release": []
        },
        "followup_profiles": ["release"],
        "description": "治理层变更，premerge 必须通过，release 为 follow-up"
    },
    "scripts/approval_manager.py": {
        "blocking_commands_for_profile": {
            "premerge": [],
            "nightly": [],
            "release": []
        },
        "followup_profiles": ["nightly", "release"],
        "description": "审批管理器变更，nightly + release 为 follow-up"
    },
    "core/contracts/*": {
        "blocking_commands_for_profile": {
            "premerge": [
                "python scripts/check_json_contracts.py",
                "python scripts/check_repo_integrity.py --strict",
                "python scripts/run_release_gate.py premerge"
            ],
            "nightly": [],
            "release": []
        },
        "followup_profiles": [],
        "description": "契约文件变更，必须验证 JSON 契约和仓库完整性"
    },
    "core/LAYER_DEPENDENCY_RULES.json": {
        "blocking_commands_for_profile": {
            "premerge": [
                "python scripts/check_layer_dependencies.py",
                "python scripts/check_repo_integrity.py --strict"
            ],
            "nightly": [],
            "release": []
        },
        "followup_profiles": [],
        "description": "依赖规则变更，必须验证层间依赖和仓库完整性"
    },
    "scripts/check_*.py": {
        "blocking_commands_for_profile": {
            "premerge": [
                "python scripts/check_repo_integrity.py --strict"
            ],
            "nightly": [],
            "release": []
        },
        "followup_profiles": [],
        "description": "检查脚本变更，建议验证仓库完整性"
    },
    "infrastructure/release/*": {
        "blocking_commands_for_profile": {
            "premerge": [],
            "nightly": [],
            "release": []
        },
        "followup_profiles": ["release"],
        "description": "发布管理变更，release 为 follow-up"
    },
    "reports/ops/*": {
        "blocking_commands_for_profile": {
            "premerge": [
                "python scripts/check_json_contracts.py"
            ],
            "nightly": [],
            "release": []
        },
        "followup_profiles": [],
        "description": "控制平面报告变更，建议验证 JSON 契约"
    }
}


def match_pattern(file_path: str, pattern: str) -> bool:
    """检查文件是否匹配模式"""
    if pattern.endswith("/*"):
        # 目录通配符
        dir_prefix = pattern[:-2]
        return file_path.startswith(dir_prefix + "/") or file_path.startswith(dir_prefix)
    elif pattern.startswith("*"):
        # 后缀通配符
        suffix = pattern[1:]
        return file_path.endswith(suffix)
    elif "*" in pattern:
        # 中间通配符
        parts = pattern.split("*")
        return file_path.startswith(parts[0]) and file_path.endswith(parts[-1])
    else:
        # 精确匹配
        return file_path == pattern


def get_required_commands(changed_files: List[str], current_profile: str = "premerge") -> Dict:
    """获取变更文件需要执行的命令（V3.0.0 - 拆分当前阻断和 follow-up）"""
    blocking_commands: Set[str] = set()
    followup_profiles: Set[str] = set()
    followup_reason_by_profile: Dict[str, List[str]] = {}
    matched_rules = []
    changed_categories = set()
    
    for file_path in changed_files:
        for pattern, rule in CHANGE_IMPACT_RULES.items():
            if match_pattern(file_path, pattern):
                # 提取变更类别
                if "/*" in pattern:
                    changed_categories.add(pattern.split("/*")[0])
                else:
                    changed_categories.add(pattern)
                
                # 获取当前 profile 的阻断命令
                profile_commands = rule.get("blocking_commands_for_profile", {}).get(current_profile, [])
                blocking_commands.update(profile_commands)
                
                # 获取 follow-up profiles
                for fp in rule.get("followup_profiles", []):
                    followup_profiles.add(fp)
                    if fp not in followup_reason_by_profile:
                        followup_reason_by_profile[fp] = []
                    followup_reason_by_profile[fp].append(f"{file_path} changed")
                
                matched_rules.append({
                    "file": file_path,
                    "pattern": pattern,
                    "description": rule["description"],
                    "blocking_commands": profile_commands,
                    "followup_profiles": rule.get("followup_profiles", [])
                })
    
    return {
        "changed_files": changed_files,
        "changed_categories": list(changed_categories),
        "matched_rules": matched_rules,
        "blocking_commands_current_profile": list(blocking_commands),
        "followup_required_profiles": list(followup_profiles),
        "followup_reason_by_profile": followup_reason_by_profile,
        "generated_at": datetime.now().isoformat()
    }


def get_git_diff_files(commit_range: str = "HEAD~1") -> List[str]:
    """获取 git diff 的变更文件列表"""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", commit_range],
            capture_output=True,
            text=True,
            cwd=get_project_root()
        )
        if result.returncode == 0:
            return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except Exception as e:
        print(f"获取 git diff 失败: {e}")
    return []


def save_report(report: Dict, report_path: str):
    """保存报告到文件"""
    root = get_project_root()
    path = root / report_path
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # 添加时间戳
    report["generated_at"] = datetime.now().isoformat()
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"报告已保存: {report_path}")


def print_impact_report(report: Dict):
    """打印影响报告"""
    print("╔══════════════════════════════════════════════════╗")
    print("║              变更影响分析 V3.0.0                ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    print(f"变更文件数: {len(report['changed_files'])}")
    print()
    
    if report['matched_rules']:
        print("【匹配规则】")
        for rule in report['matched_rules']:
            print(f"  📄 {rule['file']}")
            print(f"     规则: {rule['pattern']}")
            print(f"     说明: {rule['description']}")
            print()
    
    if report.get('blocking_commands_current_profile'):
        print("【当前阻断命令】")
        for i, cmd in enumerate(report['blocking_commands_current_profile'], 1):
            print(f"  {i}. {cmd}")
        print()
    
    if report.get('followup_required_profiles'):
        print("【Follow-up Required Profiles】")
        for p in report['followup_required_profiles']:
            reasons = report.get('followup_reason_by_profile', {}).get(p, [])
            print(f"  ⏳ {p}: {', '.join(reasons[:2])}")
        print()
    
    if not report.get('blocking_commands_current_profile') and not report.get('followup_required_profiles'):
        print("✅ 无需执行额外命令")
    
    print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="变更影响检查器 V3.0.0")
    parser.add_argument("--files", nargs="+", help="变更文件列表")
    parser.add_argument("--from-git", action="store_true", help="从 git diff HEAD~1 获取变更文件")
    parser.add_argument("--git-diff", help="git diff 范围 (如 HEAD~1，--from-git 的替代)")
    parser.add_argument("--profile", default="premerge", help="当前门禁模式 (premerge/nightly/release)")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    parser.add_argument("--report-json", help="保存报告到 JSON 文件")
    args = parser.parse_args()
    
    changed_files = []
    
    if args.files:
        changed_files = args.files
    elif args.from_git:
        changed_files = get_git_diff_files("HEAD~1")
    elif args.git_diff:
        changed_files = get_git_diff_files(args.git_diff)
    else:
        print("请指定 --files, --from-git 或 --git-diff")
        return 1
    
    if not changed_files:
        print("无变更文件")
        report = {
            "changed_files": [],
            "changed_categories": [],
            "matched_rules": [],
            "blocking_commands_current_profile": [],
            "followup_required_profiles": [],
            "followup_reason_by_profile": {},
            "generated_at": datetime.now().isoformat()
        }
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        if args.report_json:
            save_report(report, args.report_json)
        return 0
    
    report = get_required_commands(changed_files, args.profile)
    
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_impact_report(report)
    
    if args.report_json:
        save_report(report, args.report_json)
    
    return 0 if len(report.get('blocking_commands_current_profile', [])) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
