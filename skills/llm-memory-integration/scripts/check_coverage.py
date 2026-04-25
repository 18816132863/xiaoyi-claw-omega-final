#!/usr/bin/env python3
"""
检查向量覆盖率（安全修复版 v8）
使用 sqlite3 直接连接
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# 数据库路径
VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"

# 向量扩展路径（动态检测）
def get_vec_extension_path() -> Optional[str]:
    """动态获取向量扩展路径"""
    possible_paths = [
        Path.home() / ".openclaw" / "extensions" / "memory-tencentdb" / "node_modules" / "sqlite-vec-linux-x64" / "vec0.so",
        Path.home() / ".openclaw" / "extensions" / "memory-tencentdb" / "node_modules" / "sqlite-vec-linux-x64" / "vec0",
    ]
    for p in possible_paths:
        if p.exists():
            return str(p)
    return None

def get_db_connection(load_ext: bool = False) -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(str(VECTORS_DB))
    
    if load_ext:
        vec_ext = get_vec_extension_path()
        if vec_ext:
            conn.enable_load_extension(True)
            conn.load_extension(vec_ext)
    
    return conn

def check_coverage():
    """检查向量覆盖率"""
    print(f"向量覆盖率检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not VECTORS_DB.exists():
        print(f"❌ 数据库不存在: {VECTORS_DB}")
        return
    
    try:
        # 查询普通表（不需要扩展）
        conn = get_db_connection(load_ext=False)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM l1_records")
        l1_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM l0_conversations")
        l0_conversations = cursor.fetchone()[0]
        
        conn.close()
        
        # 查询向量表（需要扩展）
        conn = get_db_connection(load_ext=True)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM l1_vec")
        l1_vec = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM l0_vec")
        l0_vec = cursor.fetchone()[0]
        
        conn.close()
        
        # 计算覆盖率
        l1_coverage = (l1_vec / l1_records * 100) if l1_records > 0 else 0
        l0_coverage = (l0_vec / l0_conversations * 100) if l0_conversations > 0 else 0
        
        print(f"L1 覆盖率: {l1_coverage:.1f}% ({l1_vec}/{l1_records})")
        print(f"L0 覆盖率: {l0_coverage:.1f}% ({l0_vec}/{l0_conversations})")
        
        # 检查阈值
        if l1_coverage < 95:
            print(f"⚠️ L1 覆盖率低于 95%，建议运行向量回填")
        
        if l0_coverage < 60:
            print(f"⚠️ L0 覆盖率低于 60%，建议运行向量回填")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    check_coverage()
