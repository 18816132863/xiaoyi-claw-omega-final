#!/usr/bin/env python3
"""
报告清理脚本 - V1.0.0

自动清理旧报告，保留最近 N 个。
"""

import os
import json
import gzip
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple

# 配置
REPORTS_DIR = Path("reports")
MAX_REPORTS = {
    "inspection_*.json": 10,      # 巡检报告保留 10 个
    "runtime_integrity*.json": 5,  # 运行时报告保留 5 个
    "history/**/*.json": 30,       # 历史报告保留 30 个
}
MAX_AGE_DAYS = 30  # 超过 30 天的报告压缩
ARCHIVE_DIR = REPORTS_DIR / "archive"


def get_file_age(file_path: Path) -> timedelta:
    """获取文件年龄"""
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    return datetime.now() - mtime


def compress_file(file_path: Path) -> Path:
    """压缩文件"""
    archive_path = ARCHIVE_DIR / f"{file_path.name}.gz"
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'rb') as f_in:
        with gzip.open(archive_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    file_path.unlink()
    return archive_path


def cleanup_by_pattern(pattern: str, max_count: int) -> Tuple[int, int]:
    """按模式清理报告"""
    deleted = 0
    compressed = 0

    files = sorted(
        REPORTS_DIR.glob(pattern),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    for i, file_path in enumerate(files):
        if i >= max_count:
            # 超出数量限制，删除
            file_path.unlink()
            deleted += 1
        elif get_file_age(file_path).days > MAX_AGE_DAYS:
            # 超过年龄限制，压缩
            compress_file(file_path)
            compressed += 1

    return deleted, compressed


def cleanup_history() -> Tuple[int, int]:
    """清理历史目录"""
    deleted = 0
    compressed = 0

    history_dir = REPORTS_DIR / "history"
    if not history_dir.exists():
        return deleted, compressed

    for subdir in history_dir.iterdir():
        if not subdir.is_dir():
            continue

        files = sorted(
            subdir.glob("*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )

        for i, file_path in enumerate(files):
            if i >= 30:  # 每个子目录保留 30 个
                file_path.unlink()
                deleted += 1

    return deleted, compressed


def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║          报告清理 V1.0.0                        ║")
    print("╚══════════════════════════════════════════════════╝")
    print()

    total_deleted = 0
    total_compressed = 0

    # 按模式清理
    print("【清理报告】")
    for pattern, max_count in MAX_REPORTS.items():
        if "**" in pattern:
            continue
        deleted, compressed = cleanup_by_pattern(pattern, max_count)
        if deleted or compressed:
            print(f"  {pattern}: 删除 {deleted}, 压缩 {compressed}")
        total_deleted += deleted
        total_compressed += compressed

    # 清理历史
    print()
    print("【清理历史】")
    deleted, compressed = cleanup_history()
    if deleted or compressed:
        print(f"  history/: 删除 {deleted}, 压缩 {compressed}")
    total_deleted += deleted
    total_compressed += compressed

    # 统计
    print()
    print("【统计】")
    print(f"  删除: {total_deleted} 个文件")
    print(f"  压缩: {total_compressed} 个文件")

    # 目录大小
    total_size = sum(f.stat().st_size for f in REPORTS_DIR.rglob("*") if f.is_file())
    print(f"  当前大小: {total_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
