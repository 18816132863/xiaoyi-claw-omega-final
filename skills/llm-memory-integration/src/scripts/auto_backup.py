#!/usr/bin/env python3
"""
自动备份脚本
每日备份记忆系统数据
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
TFIDF_STORAGE = Path.home() / ".openclaw" / "tfidf-storage"

def create_backup():
    """创建完整备份"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / timestamp
    backup_path.mkdir(parents=True, exist_ok=True)
    
    print(f"创建备份: {backup_path}")
    
    # 1. 备份向量数据库
    vectors_db = MEMORY_TDai / "vectors.db"
    if vectors_db.exists():
        shutil.copy2(vectors_db, backup_path / "vectors.db")
        print(f"  ✅ vectors.db ({vectors_db.stat().st_size // 1024 // 1024}MB)")
    
    # 2. 备份 TF-IDF 数据库
    tfidf_db = TFIDF_STORAGE / "tfidf.db"
    if tfidf_db.exists():
        shutil.copy2(tfidf_db, backup_path / "tfidf.db")
        print(f"  ✅ tfidf.db ({tfidf_db.stat().st_size // 1024}KB)")
    
    # 3. 备份配置文件
    config_files = [
        ("openclaw.json", Path.home() / ".openclaw" / "openclaw.json"),
        ("MEMORY.md", WORKSPACE / "MEMORY.md"),
        ("USER.md", WORKSPACE / "USER.md"),
        ("SOUL.md", WORKSPACE / "SOUL.md"),
        ("persona.md", WORKSPACE / "persona.md"),
    ]
    
    for name, path in config_files:
        if path.exists():
            shutil.copy2(path, backup_path / name)
            print(f"  ✅ {name}")
    
    # 4. 备份记忆数据目录
    for subdir in ["records", "scene_blocks", ".metadata"]:
        src = MEMORY_TDai / subdir
        if src.exists():
            dst = backup_path / subdir
            shutil.copytree(src, dst)
            print(f"  ✅ {subdir}/")
    
    # 5. 创建备份信息文件
    info = {
        "timestamp": timestamp,
        "created_at": datetime.now().isoformat(),
        "files": {
            "vectors.db": (backup_path / "vectors.db").exists(),
            "tfidf.db": (backup_path / "tfidf.db").exists(),
        }
    }
    
    # 获取数据库统计
    if (backup_path / "vectors.db").exists():
        conn = sqlite3.connect(str(backup_path / "vectors.db"))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM l0_conversations")
        info["l0_conversations"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM l1_records")
        info["l1_records"] = cursor.fetchone()[0]
        conn.close()
    
    (backup_path / "BACKUP_INFO.json").write_text(json.dumps(info, indent=2))
    print(f"  ✅ BACKUP_INFO.json")
    
    # 6. 清理旧备份（保留最近7个）
    backups = sorted(BACKUP_DIR.iterdir(), key=lambda x: x.name, reverse=True)
    if len(backups) > 7:
        for old in backups[7:]:
            shutil.rmtree(old)
            print(f"  🗑️ 清理旧备份: {old.name}")
    
    print(f"\n✅ 备份完成: {backup_path}")
    return backup_path

if __name__ == "__main__":
    create_backup()
