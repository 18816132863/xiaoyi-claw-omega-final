#!/usr/bin/env python3
"""重建 FTS 索引（安全修复版）"""
import sqlite3
from pathlib import Path

VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"

def rebuild_fts():
    """重建 FTS 索引（使用 sqlite3 直接连接）"""
    if not VECTORS_DB.exists():
        print(f"❌ 数据库不存在: {VECTORS_DB}")
        return
    
    conn = sqlite3.connect(str(VECTORS_DB))
    cursor = conn.cursor()
    
    try:
        # 删除旧索引
        cursor.execute("DROP TABLE IF EXISTS l1_fts;")
        print("✅ 已删除旧 FTS 索引")
        
        # 创建新索引
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS l1_fts USING fts5(
                record_id, content, type, scene_name, priority,
                session_key, session_id, timestamp_str, timestamp_start, timestamp_end, metadata,
                content='', tokenize='unicode61'
            );
        """)
        print("✅ 已创建新 FTS 索引")
        
        # 重新填充数据
        cursor.execute("""
            INSERT INTO l1_fts(rowid, record_id, content, type, scene_name, priority)
            SELECT rowid, record_id, content, type, scene_name, priority FROM l1_records;
        """)
        
        conn.commit()
        print(f"✅ FTS 索引重建完成，已填充 {cursor.rowcount} 条记录")
        
    except Exception as e:
        print(f"❌ FTS 索引重建失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    import datetime
    print(f"FTS 索引重建 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    rebuild_fts()
