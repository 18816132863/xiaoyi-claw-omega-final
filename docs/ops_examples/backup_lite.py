#!/usr/bin/env python3
"""
OpenClaw 精简备份脚本 - V1.0

排除大文件：
- 索引文件（可重建）
- repo/lib/（可重装）
- 大型技能的测试数据
"""

import os
import sys
import json
import hashlib
import tarfile
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from infrastructure.path_resolver import get_project_root

workspace = Path(str(get_project_root()))

# 精简排除规则
EXCLUDE_DIRS = {
    "node_modules", "__pycache__", ".git", ".svn",
    "archive", "reports", "backups", "tmp", "temp",
    "dist", "build", ".cache", "logs",
    "repo", "site-packages", "bin", "sbin",
    "backup", "index", "schemas", "dist", "cache",
}

EXCLUDE_EXTENSIONS = {
    ".pyc", ".pyo", ".so", ".dll", ".dylib",
    ".tar", ".gz", ".zip", ".rar", ".7z",
    ".mp3", ".mp4", ".avi", ".mov", ".wav",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico",
    ".pdf", ".db", ".sqlite", ".sqlite3",
    ".bin", ".exe", ".sh", ".bat", ".cmd", ".run",
    ".out", ".o", ".a", ".lib", ".xsd", ".pack",
}

EXCLUDE_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "composer.lock", "Cargo.lock", "poetry.lock",
    "keyword_index.json", "fts_index.json", "vector_index.json",
    "index_metadata.json", "file_states.json", "RECORD",
    "acp2service", "vsearch", "llm-analyze",
}

EXCLUDE_PATTERNS = [
    "site-packages",
    "/index/",
    "memory_context/index/",
    "/bin/",
    "/sbin/",
    "backup",
    "repo/lib/",
    "/schemas/",
    "/dist/",
    "/cache/",
    ".git/",
    "__pycache__/",
]

EXCLUDE_NO_EXT_PATTERNS = [
    "acp2service", "vsearch", "llm-analyze",
]


def should_exclude(path: Path) -> bool:
    """排除规则"""
    if path.is_symlink():
        return True
    
    path_parts = path.parts
    project_markers = {'workspace', 'core', 'skills', 'infrastructure', 'governance', 
                      'execution', 'orchestration', 'memory', 'memory_context',
                      'plugins', '.openclaw'}
    start_idx = 0
    for i, part in enumerate(path_parts):
        if part in project_markers:
            start_idx = i
            break
    
    project_parts = path_parts[start_idx:]
    
    if project_parts and project_parts[0] in {'workspace', '.openclaw'}:
        project_parts = project_parts[1:]
    
    for part in project_parts:
        if part in EXCLUDE_DIRS:
            return True
    
    if path.name in EXCLUDE_FILES:
        return True
    
    if path.suffix == "" or path.suffix == ".":
        name_lower = path.name.lower()
        for pattern in EXCLUDE_NO_EXT_PATTERNS:
            if pattern in name_lower:
                return True
        if "bin" in project_parts:
            return True
    
    if path.suffix.lower() in EXCLUDE_EXTENSIONS:
        return True
    
    path_str = str(Path(*project_parts)) if project_parts else str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    
    return False


def get_file_state(path: Path) -> dict:
    try:
        return {
            "mtime": path.stat().st_mtime,
            "size": path.stat().st_size,
            "hash": hashlib.md5(path.read_bytes()).hexdigest()[:16]
        }
    except:
        return {}


def create_lite_backup(output_dir: Path = None, version: str = "v4.3.3") -> Path:
    """创建精简备份"""
    output_dir = output_dir or Path("$HOME")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"openclaw_{version}_lite_{timestamp}.tar.gz"
    
    print("╔══════════════════════════════════════════════════╗")
    print("║        OpenClaw 精简备份 V1.0                    ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"版本: {version}")
    print(f"输出: {output_file}")
    print()
    
    # 排除说明
    print("排除内容:")
    print("  ✓ 索引文件 (memory_context/index/)")
    print("  ✓ Python 库 (repo/lib/)")
    print("  ✓ 缓存和临时文件")
    print("  ✓ 大型二进制文件")
    print()
    
    # 统计
    file_count = 0
    total_size = 0
    
    # 创建 tar.gz
    print("创建压缩包...")
    
    with tarfile.open(output_file, "w:gz") as tar:
        for f in workspace.rglob("*"):
            if not f.is_file():
                continue
            if f.is_symlink():
                continue
            if should_exclude(f):
                continue
            
            try:
                rel_path = f.relative_to(workspace)
                tar.add(f, arcname=str(rel_path))
                file_count += 1
                total_size += f.stat().st_size
            except:
                pass
    
    # 验证结果
    print()
    print("══════════════════════════════════════════════════")
    print("备份完成")
    print("══════════════════════════════════════════════════")
    print()
    print(f"文件: {output_file}")
    print(f"大小: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"文件数: {file_count}")
    print(f"原始大小: {total_size / 1024 / 1024:.2f} MB")
    print(f"压缩率: {(1 - output_file.stat().st_size / total_size) * 100:.1f}%")
    
    return output_file


if __name__ == "__main__":
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("$HOME")
    create_lite_backup(output_dir)
