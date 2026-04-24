#!/usr/bin/env python3
"""
增量更新器 V1.0.0

功能：
- 检测文件变更
- 只更新变化的部分
- 维护变更历史
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

def get_file_hash(file_path: Path) -> str:
    """获取文件哈希"""
    try:
        content = file_path.read_bytes()
        return hashlib.md5(content).hexdigest()
    except:
        return ""

def detect_changes(directory: Path, cache_file: Path = None) -> dict:
    """检测目录变更"""
    cache = {}
    if cache_file and cache_file.exists():
        cache = json.load(open(cache_file))
    
    changes = {
        "added": [],
        "modified": [],
        "deleted": [],
        "unchanged": []
    }
    
    current_files = {}
    for f in directory.rglob("*"):
        if f.is_file() and not f.name.startswith("."):
            rel_path = str(f.relative_to(directory))
            file_hash = get_file_hash(f)
            current_files[rel_path] = file_hash
            
            if rel_path not in cache:
                changes["added"].append(rel_path)
            elif cache[rel_path] != file_hash:
                changes["modified"].append(rel_path)
            else:
                changes["unchanged"].append(rel_path)
    
    # 检测删除
    for rel_path in cache:
        if rel_path not in current_files:
            changes["deleted"].append(rel_path)
    
    return changes, current_files

if __name__ == "__main__":
    root = Path(__file__).parent.parent
    changes, current = detect_changes(root / "core")
    print(f"新增: {len(changes['added'])}")
    print(f"修改: {len(changes['modified'])}")
    print(f"删除: {len(changes['deleted'])}")
    print(f"未变: {len(changes['unchanged'])}")
