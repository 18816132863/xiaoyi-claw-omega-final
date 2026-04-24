#!/usr/bin/env python3
"""
OpenClaw CLI 工具 - V1.0.0

提供命令行接口管理 OpenClaw 工作空间。
"""

import argparse
import sys
import subprocess
from pathlib import Path


def cmd_verify(args):
    """运行门禁检查"""
    profile = args.profile or "premerge"
    cmd = [sys.executable, "scripts/run_release_gate.py", profile]
    return subprocess.run(cmd).returncode


def cmd_inspect(args):
    """运行统一巡检"""
    cmd = [sys.executable, "scripts/unified_inspector.py"]
    return subprocess.run(cmd).returncode


def cmd_health(args):
    """技能健康检查"""
    cmd = [sys.executable, "scripts/skill_health_check.py"]
    return subprocess.run(cmd).returncode


def cmd_classify(args):
    """技能自动分类"""
    cmd = [sys.executable, "scripts/auto_classify_skills.py"]
    if args.apply:
        cmd.append("--apply")
    return subprocess.run(cmd).returncode


def cmd_cleanup(args):
    """清理旧报告"""
    cmd = [sys.executable, "scripts/cleanup_reports.py"]
    return subprocess.run(cmd).returncode


def cmd_status(args):
    """显示状态"""
    print("╔══════════════════════════════════════════════════╗")
    print("║          OpenClaw 工作空间状态                  ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    # 检查核心文件
    core_files = ["AGENTS.md", "MEMORY.md", "TOOLS.md", "SOUL.md"]
    print("【核心文件】")
    for f in core_files:
        status = "✅" if Path(f).exists() else "❌"
        print(f"  {status} {f}")
    
    # 检查层级目录
    layers = ["core", "memory_context", "orchestration", "execution", "governance", "infrastructure"]
    print("\n【层级目录】")
    for layer in layers:
        status = "✅" if Path(layer).is_dir() else "❌"
        print(f"  {status} {layer}")
    
    # 技能统计
    import json
    registry_path = Path("infrastructure/inventory/skill_registry.json")
    if registry_path.exists():
        with open(registry_path) as f:
            data = json.load(f)
        skills = data.get("skills", {})
        print(f"\n【技能统计】")
        print(f"  总技能数: {len(skills)}")
        print(f"  版本: {data.get('version', 'unknown')}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw CLI 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # verify 命令
    verify_parser = subparsers.add_parser("verify", help="运行门禁检查")
    verify_parser.add_argument("--profile", choices=["premerge", "nightly", "release"],
                               help="门禁模式")
    verify_parser.set_defaults(func=cmd_verify)
    
    # inspect 命令
    inspect_parser = subparsers.add_parser("inspect", help="运行统一巡检")
    inspect_parser.set_defaults(func=cmd_inspect)
    
    # health 命令
    health_parser = subparsers.add_parser("health", help="技能健康检查")
    health_parser.set_defaults(func=cmd_health)
    
    # classify 命令
    classify_parser = subparsers.add_parser("classify", help="技能自动分类")
    classify_parser.add_argument("--apply", action="store_true", help="应用更改")
    classify_parser.set_defaults(func=cmd_classify)
    
    # cleanup 命令
    cleanup_parser = subparsers.add_parser("cleanup", help="清理旧报告")
    cleanup_parser.set_defaults(func=cmd_cleanup)
    
    # status 命令
    status_parser = subparsers.add_parser("status", help="显示状态")
    status_parser.set_defaults(func=cmd_status)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
