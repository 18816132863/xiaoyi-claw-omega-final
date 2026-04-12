#!/usr/bin/env python3
"""
发布门禁统一入口 - V1.0.0

提供 CI 可用的统一命令
"""

import sys
import subprocess
from pathlib import Path

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


def verify_premerge():
    """premerge 门禁"""
    root = get_project_root()
    
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
    return rc


def verify_nightly():
    """nightly 门禁"""
    root = get_project_root()
    
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
    return rc


def verify_release():
    """release 门禁"""
    root = get_project_root()
    
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
