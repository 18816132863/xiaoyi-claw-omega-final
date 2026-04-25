#!/usr/bin/env python3
"""带缓存的搜索（安全修复版）"""
import sys
import json
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

CACHE_DIR = Path.home() / ".openclaw" / "memory-tdai" / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_TTL = 3600  # 1小时

def get_cache_key(query):
    return hashlib.md5(query.encode()).hexdigest()

def get_cached(key):
    cache_file = CACHE_DIR / f"{key}.json"
    if cache_file.exists():
        data = json.loads(cache_file.read_text())
        cached_time = datetime.fromisoformat(data["time"])
        if datetime.now() - cached_time < timedelta(seconds=CACHE_TTL):
            return data["results"]
    return None

def set_cache(key, results):
    cache_file = CACHE_DIR / f"{key}.json"
    cache_file.write_text(json.dumps({
        "time": datetime.now().isoformat(),
        "results": results
    }, ensure_ascii=False))

def search_direct(query):
    """直接搜索（使用 sqlite3 连接）"""
    from pathlib import Path
    
    VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"
    
    if not VECTORS_DB.exists():
        return []
    
    try:
        conn = sqlite3.connect(str(VECTORS_DB))
        cursor = conn.cursor()
        
        # FTS 搜索
        cursor.execute("""
            SELECT record_id, content, type, scene_name 
            FROM l1_fts 
            WHERE l1_fts MATCH ? 
            ORDER BY rank 
            LIMIT 10
        """, (query,))
        
        results = []
        for row in cursor.fetchall():
            results.append(f"[{row[2]}] {row[1][:80]}...")
        
        conn.close()
        return results
    except Exception as e:
        return []

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    if not query:
        print("用法: cached_search.py '查询'")
        sys.exit(1)
    
    key = get_cache_key(query)
    
    # 检查缓存
    cached = get_cached(key)
    if cached:
        print(f"缓存命中: {query}")
        for r in cached[:5]:
            print(f"  - {r}")
        return
    
    # 执行搜索
    print(f"搜索: {query}")
    results = search_direct(query)
    
    if results:
        for r in results:
            print(f"  - {r}")
        
        # 缓存结果
        set_cache(key, results)
    else:
        print("  无结果")

if __name__ == "__main__":
    main()
