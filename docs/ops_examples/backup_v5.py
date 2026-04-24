#!/usr/bin/env python3
"""
OpenClaw 备份打包脚本 - V5.0.0

修复问题：
1. file_states 必须从"最终将被打进包的文件集合"生成
2. 符号链接不写入 file_states
3. 统一排除规则

流程：
1. 确定打包排除规则
2. 生成"最终打包文件清单"
3. 基于这个清单生成 file_states.json
4. 再打 tar.gz
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

# 统一排除规则 - 必须与 IndexExcludeList 一致
EXCLUDE_DIRS = {
    "node_modules", "__pycache__", ".git", ".svn",
    "archive", "reports", "backups", "tmp", "temp",
    "dist", "build", ".cache", "logs",
    "repo", "site-packages", "bin", "sbin",
    "backup",
    # 注意：不排除 "index"，因为 memory_context/index/ 需要打包
}

EXCLUDE_EXTENSIONS = {
    ".pyc", ".pyo", ".so", ".dll", ".dylib",
    ".tar", ".gz", ".zip", ".rar", ".7z",
    ".mp3", ".mp4", ".avi", ".mov", ".wav",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico",
    ".pdf",
    ".db", ".sqlite", ".sqlite3",
    ".bin", ".exe", ".sh", ".bat", ".cmd", ".run",
    ".out", ".o", ".a", ".lib",
}

EXCLUDE_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "composer.lock", "Cargo.lock", "poetry.lock",
    # 索引文件需要打包，不能排除
    # "keyword_index.json", "fts_index.json", "vector_index.json",
    # "index_metadata.json", "file_states.json",
    "RECORD",
}

EXCLUDE_PATTERNS = [
    "site-packages",
    # "/index/",  # 不能排除 index 目录，需要打包索引文件
    # "memory_context/index/",  # 不能排除
    "/bin/",
    "/sbin/",
    "backup",
]

EXCLUDE_NO_EXT_PATTERNS = [
    "acp2service", "vsearch", "llm-analyze",
]


def should_exclude(path: Path) -> bool:
    """统一排除规则 - V5.0.0
    
    重要：只检查相对路径的目录部分，不检查绝对路径中的系统目录
    """
    # 跳过符号链接
    if path.is_symlink():
        return True
    
    # 获取相对路径部分（排除系统临时目录等）
    # 只检查项目内的目录名
    path_parts = path.parts
    
    # 找到项目根目录的起始位置
    # 项目根目录特征：包含 workspace 或 core/skills/infrastructure 等项目目录
    project_markers = {'workspace', 'core', 'skills', 'infrastructure', 'governance', 
                      'execution', 'orchestration', 'memory', 'memory_context',
                      'plugins', '.openclaw'}
    start_idx = 0
    for i, part in enumerate(path_parts):
        if part in project_markers:
            start_idx = i
            break
    
    # 只检查项目内的目录（从 workspace 或 .openclaw 开始）
    project_parts = path_parts[start_idx:]
    
    # 跳过 workspace 和 .openclaw 本身，只检查其子目录
    if project_parts and project_parts[0] in {'workspace', '.openclaw'}:
        project_parts = project_parts[1:]
    
    for part in project_parts:
        if part in EXCLUDE_DIRS:
            return True
    
    # 检查文件名
    if path.name in EXCLUDE_FILES:
        return True
    
    # 检查无扩展名的可执行文件
    if path.suffix == "" or path.suffix == ".":
        name_lower = path.name.lower()
        for pattern in EXCLUDE_NO_EXT_PATTERNS:
            if pattern in name_lower:
                return True
        if "bin" in project_parts:
            return True
    
    # 检查扩展名
    if path.suffix.lower() in EXCLUDE_EXTENSIONS:
        return True
    
    # 检查路径模式（只检查项目内路径）
    path_str = str(Path(*project_parts)) if project_parts else str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    
    return False


def get_file_state(path: Path) -> dict:
    """获取文件状态"""
    try:
        return {
            "mtime": path.stat().st_mtime,
            "size": path.stat().st_size,
            "hash": hashlib.md5(path.read_bytes()).hexdigest()[:16]
        }
    except:
        return {}


def generate_file_states(base_dir: Path) -> dict:
    """生成 file_states - 只包含最终将被打包的文件
    
    重要：索引文件不写入 file_states，因为它们会在打包时被覆盖
    """
    file_states = {}
    
    # 索引文件名（不写入 file_states）
    index_files = {
        "keyword_index.json", "fts_index.json", "vector_index.json",
        "index_metadata.json", "file_states.json"
    }
    
    for f in base_dir.rglob("*"):
        if not f.is_file():
            continue
        # 跳过符号链接
        if f.is_symlink():
            continue
        # 跳过索引文件
        if f.name in index_files:
            continue
        # 使用统一排除规则
        if should_exclude(f):
            continue
        
        try:
            file_id = str(f.relative_to(base_dir))
            file_states[file_id] = get_file_state(f)
        except:
            pass
    
    return file_states


def create_backup(output_dir: Path = None, version: str = "v4.3.2") -> Path:
    """创建备份包"""
    # 使用相对路径获取路径
    base_dir = Path(__file__).parent.parent.parent  # .openclaw 目录
    output_dir = output_dir or base_dir.parent  # $HOME
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"openclaw_{version}_{timestamp}.tar.gz"
    
    print("╔══════════════════════════════════════════════════╗")
    print(f"║        OpenClaw 备份打包 V5.0.0                  ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"版本: {version}")
    print(f"输出: {output_file}")
    print()
    
    # 1. 生成 file_states（从最终打包文件集合）
    print("生成 file_states...")
    file_states = generate_file_states(base_dir / "workspace")
    print(f"  文件数: {len(file_states)}")
    
    # 2. 写入 file_states 到临时位置
    temp_dir = Path(tempfile.mkdtemp())
    temp_file_states = temp_dir / "file_states.json"
    temp_file_states.write_text(json.dumps(file_states, ensure_ascii=False, indent=2))
    
    # 3. 创建 tar.gz
    print("创建压缩包...")
    file_count = 0
    
    with tarfile.open(output_file, "w:gz") as tar:
        # 添加 .openclaw 目录
        for f in base_dir.rglob("*"):
            if f.is_file():
                # 跳过符号链接
                if f.is_symlink():
                    continue
                # 使用统一排除规则
                rel_path = f.relative_to(base_dir)
                if should_exclude(Path(rel_path)):
                    continue
                
                tar.add(f, arcname=f".openclaw/{rel_path}")
                file_count += 1
        
        # 添加 .local/bin 目录
        local_bin = base_dir.parent / ".local" / "bin"
        if local_bin.exists():
            for f in local_bin.rglob("*"):
                if f.is_file() and not f.is_symlink():
                    rel_path = f.relative_to(base_dir.parent)
                    tar.add(f, arcname=str(rel_path))
                    file_count += 1
        
        # 添加 file_states.json（覆盖包内的）
        tar.add(temp_file_states, arcname=".openclaw/workspace/memory_context/index/file_states.json")
    
    # 4. 清理临时目录
    shutil.rmtree(temp_dir)
    
    # 5. 验证结果
    print()
    print("══════════════════════════════════════════════════")
    print("备份完成")
    print("══════════════════════════════════════════════════")
    print()
    print(f"文件: {output_file}")
    print(f"大小: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"文件数: {file_count}")
    print(f"file_states 记录数: {len(file_states)}")
    
    return output_file


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else base_dir.parent
    create_backup(output_dir)
