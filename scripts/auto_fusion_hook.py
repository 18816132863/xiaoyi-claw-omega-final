#!/usr/bin/env python3
"""
自动融合钩子 - 在 git commit 前自动运行融合引擎

使用方式：
1. 作为 git pre-commit hook
2. 作为 Makefile 命令
3. 作为 CI/CD 步骤
"""

import sys
import subprocess
from pathlib import Path


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


def run_fusion_check(root: Path) -> bool:
    """运行融合检查"""
    print("\n🔍 运行融合引擎检查...")
    
    # 1. 检查新文件是否在架构目录中
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=A'],
        cwd=str(root),
        capture_output=True,
        text=True
    )
    
    new_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
    
    if not new_files:
        print("  ✅ 没有新增文件")
        return True
    
    # 架构目录
    ARCH_DIRS = [
        'core/', 'memory_context/', 'orchestration/', 
        'execution/', 'skills/', 'governance/', 'infrastructure/',
        'tests/', 'scripts/', 'reports/', 'memory/', 'docs/'
    ]
    
    # 检查新文件
    not_in_arch = []
    for f in new_files:
        if f.endswith('.py') and not any(f.startswith(d) for d in ARCH_DIRS):
            not_in_arch.append(f)
    
    if not_in_arch:
        print("  ⚠️  以下文件未融入架构:")
        for f in not_in_arch:
            print(f"    - {f}")
        print("\n  建议运行: python infrastructure/fusion_engine.py --auto-fuse")
        return False
    
    print(f"  ✅ 所有新增文件 ({len(new_files)} 个) 已融入架构")
    return True


def run_fusion_engine(root: Path) -> bool:
    """运行融合引擎"""
    print("\n🔧 运行融合引擎...")
    
    result = subprocess.run(
        [sys.executable, str(root / 'infrastructure/fusion_engine.py'), '--execute'],
        cwd=str(root),
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("  ✅ 融合引擎执行成功")
        return True
    else:
        print(f"  ❌ 融合引擎执行失败: {result.stderr}")
        return False


def main():
    """主函数"""
    root = get_project_root()
    
    print("=" * 60)
    print("  自动融合钩子 V7.2.0")
    print("=" * 60)
    
    # 1. 检查新文件
    check_passed = run_fusion_check(root)
    
    # 2. 如果有文件未融入，运行融合引擎
    if not check_passed:
        fuse_passed = run_fusion_engine(root)
        if not fuse_passed:
            print("\n❌ 融合失败，请手动处理")
            return 1
    
    print("\n" + "=" * 60)
    print("  ✅ 融合检查通过")
    print("=" * 60 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
