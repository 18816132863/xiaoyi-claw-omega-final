#!/usr/bin/env python3
"""
自动恢复脚本
从备份恢复系统
"""

import os
import json
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime

# 路径配置
BACKUP_DIR = Path.home() / ".openclaw" / "backups"
MEMORY_TDai = Path.home() / ".openclaw" / "memory-tdai"
WORKSPACE = Path.home() / ".openclaw" / "workspace"

def list_backups():
    """列出可用备份"""
    if not BACKUP_DIR.exists():
        return []
    
    backups = []
    for backup in sorted(BACKUP_DIR.iterdir(), key=lambda x: x.name, reverse=True):
        info_file = backup / "BACKUP_INFO.json"
        if info_file.exists():
            info = json.loads(info_file.read_text())
            backups.append({
                "path": backup,
                "timestamp": backup.name,
                "created_at": info.get("created_at", "unknown"),
                "l0_conversations": info.get("l0_conversations", 0),
                "l1_records": info.get("l1_records", 0)
            })
    
    return backups

def restore_from_backup(backup_path):
    """从备份恢复"""
    backup_path = Path(backup_path)
    
    if not backup_path.exists():
        print(f"❌ 备份不存在: {backup_path}")
        return False
    
    print(f"开始恢复: {backup_path}")
    
    # 1. 恢复向量数据库
    src_db = backup_path / "vectors.db"
    dst_db = MEMORY_TDai / "vectors.db"
    if src_db.exists():
        # 备份当前数据库
        if dst_db.exists():
            backup_current = MEMORY_TDai / f"vectors.db.broken_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(dst_db, backup_current)
            print(f"  📦 当前数据库已备份: {backup_current.name}")
        
        shutil.copy2(src_db, dst_db)
        print(f"  ✅ vectors.db 已恢复")
    
    # 2. 恢复记忆数据目录
    for subdir in ["records", "scene_blocks", ".metadata"]:
        src = backup_path / subdir
        dst = MEMORY_TDai / subdir
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  ✅ {subdir}/ 已恢复")
    
    # 3. 恢复配置文件
    config_files = [
        ("MEMORY.md", WORKSPACE / "MEMORY.md"),
        ("USER.md", WORKSPACE / "USER.md"),
        ("SOUL.md", WORKSPACE / "SOUL.md"),
        ("persona.md", WORKSPACE / "persona.md"),
    ]
    
    for name, dst in config_files:
        src = backup_path / name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  ✅ {name} 已恢复")
    
    print(f"\n✅ 恢复完成")
    return True

def auto_recover():
    """自动恢复（使用最新备份）"""
    backups = list_backups()
    
    if not backups:
        print("❌ 无可用备份")
        return False
    
    print("可用备份:")
    for i, b in enumerate(backups[:5]):
        print(f"  {i+1}. {b['timestamp']} - L0:{b['l0_conversations']}, L1:{b['l1_records']}")
    
    # 使用最新备份
    latest = backups[0]
    print(f"\n使用最新备份: {latest['timestamp']}")
    
    return restore_from_backup(latest['path'])

def main():
    import sys
    
    if len(sys.argv) > 1:
        backup_path = sys.argv[1]
        restore_from_backup(backup_path)
    else:
        auto_recover()

if __name__ == "__main__":
    main()
