#!/usr/bin/env python3
"""
仓库完整性快速检查 - V4.0.0

优化：
1. 减少文件 I/O
2. 并行检查
3. 缓存结果
4. 只检查关键项
"""

import os
import sys
import json
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


# 关键文件（精简列表）
CRITICAL_FILES = [
    "core/ARCHITECTURE.md",
    "core/RULE_REGISTRY.json",
    "core/LAYER_DEPENDENCY_RULES.json",
    "infrastructure/inventory/skill_registry.json",
    "governance/guard/protected_files.json",
    "scripts/run_release_gate.py",
]

# 关键目录
CRITICAL_DIRS = [
    "core",
    "governance",
    "infrastructure",
    "scripts",
    "skills",
    "execution",
    "reports",
]


def check_file(args):
    """检查单个文件"""
    root, filepath = args
    full_path = root / filepath
    return {
        "path": filepath,
        "exists": full_path.exists(),
        "is_file": full_path.is_file() if full_path.exists() else False
    }


def check_dir(args):
    """检查单个目录"""
    root, dirpath = args
    full_path = root / dirpath
    return {
        "path": dirpath,
        "exists": full_path.exists(),
        "is_dir": full_path.is_dir() if full_path.exists() else False
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="仓库完整性快速检查 V4.0.0")
    parser.add_argument("--strict", action="store_true", help="严格模式")
    parser.add_argument("--report-json", type=str, help="保存报告到 JSON 文件")
    args = parser.parse_args()
    
    root = get_project_root()
    
    print("╔══════════════════════════════════════════════════╗")
    print("║      仓库完整性快速检查 V4.0.0                 ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    results = {
        "passed": 0,
        "failed": 0,
        "warnings": 0,
        "checks": []
    }
    
    # 并行检查文件
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        file_args = [(root, f) for f in CRITICAL_FILES]
        file_results = list(executor.map(check_file, file_args))
    
    for r in file_results:
        if r["exists"] and r["is_file"]:
            results["passed"] += 1
            print(f"  ✅ {r['path']}")
        else:
            results["failed"] += 1
            print(f"  ❌ {r['path']} (不存在)")
        results["checks"].append({"type": "file", **r})
    
    # 并行检查目录
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        dir_args = [(root, d) for d in CRITICAL_DIRS]
        dir_results = list(executor.map(check_dir, dir_args))
    
    for r in dir_results:
        if r["exists"] and r["is_dir"]:
            results["passed"] += 1
            print(f"  ✅ {r['path']}/")
        else:
            results["failed"] += 1
            print(f"  ❌ {r['path']}/ (不存在)")
        results["checks"].append({"type": "dir", **r})
    
    # 汇总
    print()
    print("=" * 50)
    print(f"  ✅ 通过: {results['passed']}")
    print(f"  ⚠️ 警告: {results['warnings']}")
    print(f"  ❌ 错误: {results['failed']}")
    print("=" * 50)
    
    if results["failed"] == 0:
        print("✅ 所有检查通过")
    else:
        print("❌ 存在检查失败")
        return 1
    
    # 保存报告
    if args.report_json:
        report = {
            "timestamp": datetime.now().isoformat(),
            "passed": results["passed"],
            "failed": results["failed"],
            "warnings": results["warnings"],
            "checks": results["checks"]
        }
        Path(args.report_json).write_text(json.dumps(report, indent=2, ensure_ascii=False))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
