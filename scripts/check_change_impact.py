#!/usr/bin/env python3
"""
变更影响检查器 - V1.0.0

根据 CHANGE_IMPACT_MATRIX.md 规则，分析变更文件并输出必须执行的命令

使用方法：
    python scripts/check_change_impact.py --files file1.py file2.json
    python scripts/check_change_impact.py --git-diff HEAD~1
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


# 变更影响规则映射
CHANGE_IMPACT_RULES = {
    # (文件模式, 必须执行的命令)
    "infrastructure/inventory/skill_registry.json": {
        "required_commands": [
            "python scripts/check_repo_integrity.py --strict",
            "python scripts/run_release_gate.py premerge"
        ],
        "description": "技能注册表变更，必须验证仓库完整性和 premerge 门禁"
    },
    "execution/*": {
        "required_commands": [
            "python scripts/check_layer_dependencies.py",
            "python scripts/run_release_gate.py premerge",
            "python scripts/run_release_gate.py nightly"
        ],
        "description": "执行层变更，必须验证依赖规则和 premerge + nightly 门禁"
    },
    "governance/*": {
        "required_commands": [
            "python scripts/check_layer_dependencies.py",
            "python scripts/run_release_gate.py premerge",
            "python scripts/run_release_gate.py release"
        ],
        "description": "治理层变更，必须验证依赖规则和 premerge + release 门禁"
    },
    "scripts/approval_manager.py": {
        "required_commands": [
            "python scripts/run_release_gate.py nightly",
            "python scripts/run_release_gate.py release"
        ],
        "description": "审批管理器变更，必须验证 nightly + release 门禁"
    },
    "core/contracts/*": {
        "required_commands": [
            "python scripts/check_json_contracts.py",
            "python scripts/check_repo_integrity.py --strict"
        ],
        "description": "契约文件变更，必须验证 JSON 契约和仓库完整性"
    },
    "core/LAYER_DEPENDENCY_RULES.json": {
        "required_commands": [
            "python scripts/check_layer_dependencies.py",
            "python scripts/check_repo_integrity.py --strict"
        ],
        "description": "依赖规则变更，必须验证层间依赖和仓库完整性"
    },
    "scripts/check_*.py": {
        "required_commands": [
            "python scripts/check_repo_integrity.py --strict"
        ],
        "description": "检查脚本变更，必须验证仓库完整性"
    },
    "infrastructure/release/*": {
        "required_commands": [
            "python scripts/run_release_gate.py release"
        ],
        "description": "发布管理变更，必须验证 release 门禁"
    },
    "reports/ops/*": {
        "required_commands": [
            "python scripts/check_json_contracts.py"
        ],
        "description": "控制平面报告变更，必须验证 JSON 契约"
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


def get_required_commands(changed_files: List[str]) -> Dict:
    """获取变更文件需要执行的命令"""
    all_commands: Set[str] = set()
    matched_rules = []
    
    for file_path in changed_files:
        for pattern, rule in CHANGE_IMPACT_RULES.items():
            if match_pattern(file_path, pattern):
                matched_rules.append({
                    "file": file_path,
                    "pattern": pattern,
                    "description": rule["description"],
                    "commands": rule["required_commands"]
                })
                all_commands.update(rule["required_commands"])
    
    return {
        "changed_files": changed_files,
        "matched_rules": matched_rules,
        "required_commands": list(all_commands),
        "total_commands": len(all_commands)
    }


def get_git_diff_files(commit_range: str) -> List[str]:
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


def print_impact_report(report: Dict):
    """打印影响报告"""
    print("╔══════════════════════════════════════════════════╗")
    print("║              变更影响分析                       ║")
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
    
    if report['required_commands']:
        print("【必须执行的命令】")
        for i, cmd in enumerate(report['required_commands'], 1):
            print(f"  {i}. {cmd}")
        print()
        print(f"共 {report['total_commands']} 条命令需要执行")
    else:
        print("✅ 无需执行额外命令")
    
    print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="变更影响检查器")
    parser.add_argument("--files", nargs="+", help="变更文件列表")
    parser.add_argument("--git-diff", help="git diff 范围 (如 HEAD~1)")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")
    args = parser.parse_args()
    
    changed_files = []
    
    if args.files:
        changed_files = args.files
    elif args.git_diff:
        changed_files = get_git_diff_files(args.git_diff)
    else:
        print("请指定 --files 或 --git-diff")
        return 1
    
    if not changed_files:
        print("无变更文件")
        return 0
    
    report = get_required_commands(changed_files)
    
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_impact_report(report)
    
    return 0 if report['total_commands'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
