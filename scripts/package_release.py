#!/usr/bin/env python
"""
发布打包脚本
自动生成发布包
"""

import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def clean_build_dir(build_dir: Path):
    """清理构建目录"""
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)


def copy_essential_files(build_dir: Path):
    """复制必要文件"""
    print("\n📦 复制必要文件...")
    
    # 要复制的目录
    dirs_to_copy = [
        "scripts",
        "config",
        "capabilities",
        "platform_adapter",
        "infrastructure",
        "tests",
        "skills",
        "core",
        "governance",
        "docs",
    ]
    
    for dir_name in dirs_to_copy:
        src = project_root / dir_name
        dst = build_dir / dir_name
        if src.exists():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "*.pyo", ".pytest_cache",
                "node_modules", ".venv", "*.egg-info"
            ))
            print(f"  ✅ {dir_name}/")
    
    # 要复制的文件
    files_to_copy = [
        "DEMO_QUICKSTART.md",
        "FINAL_DELIVERY_MODE_MATRIX.md",
        "NOTIFICATION_AUTH_GUIDE.md",
        "PLATFORM_HEALTH_CHECK.md",
        "PLATFORM_AUDIT_OPERATIONS.md",
        "PLATFORM_EXPORT_AND_BACKUP.md",
        "MANUAL_CONFIRMATION_PLAYBOOK.md",
        "USER_RESULT_MESSAGE_MATRIX.md",
        "PLATFORM_INVOCATION_AUDIT_REPORT.md",
        "RESULT_UNCERTAIN_HANDLING.md",
        "PLATFORM_INVOCATION_RETENTION_POLICY.md",
        "AGENTS.md",
        "SOUL.md",
        "USER.md",
        "IDENTITY.md",
        "TOOLS.md",
        "MEMORY.md",
        "HEARTBEAT.md",
    ]
    
    for file_name in files_to_copy:
        src = project_root / file_name
        dst = build_dir / file_name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✅ {file_name}")


def create_release_package(build_dir: Path, format: str) -> Path:
    """创建发布包"""
    print(f"\n📦 创建发布包 ({format})...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version = "v8.4.0"
    
    if format == "zip":
        output_path = project_root / f"release_{version}_{timestamp}.zip"
        subprocess.run([
            "zip", "-r", str(output_path), ".",
            "-x", "*.pyc", "-x", "*__pycache__*", "-x", "*/.git/*"
        ], cwd=str(build_dir), check=True)
    else:  # tar.gz
        output_path = project_root / f"release_{version}_{timestamp}.tar.gz"
        subprocess.run([
            "tar", "-czvf", str(output_path),
            "--exclude=*.pyc", "--exclude=__pycache__", "--exclude=.git",
            "."
        ], cwd=str(build_dir), check=True)
    
    return output_path


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="发布打包")
    parser.add_argument("--format", choices=["zip", "tar.gz"], default="tar.gz", help="打包格式")
    parser.add_argument("--output-dir", default="build", help="输出目录")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("📦 发布打包")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"格式: {args.format}")
    
    # 创建构建目录
    build_dir = project_root / args.output_dir / "release"
    clean_build_dir(build_dir)
    
    # 复制文件
    copy_essential_files(build_dir)
    
    # 创建发布包
    output_path = create_release_package(build_dir, args.format)
    
    # 获取文件大小
    size_mb = output_path.stat().st_size / (1024 * 1024)
    
    print("\n" + "=" * 60)
    print("✅ 打包完成")
    print("=" * 60)
    print(f"输出文件: {output_path}")
    print(f"文件大小: {size_mb:.2f} MB")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
