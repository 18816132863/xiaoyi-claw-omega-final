#!/usr/bin/env python3
"""优化搜索 - 缓存 + 并行 + 禁用LLM"""
import subprocess
import sys
import json
import hashlib
import struct
import urllib.request
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta

# 配置
VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"
from paths import VEC_EXT
GITEE_API = None  # 从配置文件读取
GITEE_KEY = os.environ.get("EMBEDDING_API_KEY", "")
CACHE_DIR = Path.home() / ".openclaw" / "memory-tdai" / ".cache"
CACHE_TTL = 3600  # 1小时

CACHE_DIR.mkdir(parents=True, exist_ok=True)

results = {"vector": [], "fts": []}
embedding_cache = {}

def get_cache_key(query):
    return hashlib.md5(query.encode()).hexdigest()

def get_cached(key):
    cache_file = CACHE_DIR / f"{key}.json"
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text())
            cached_time = datetime.fromisoformat(data["time"])
            if datetime.now() - cached_time < timedelta(seconds=CACHE_TTL):
                return data["results"]
        except Exception as e:
            logger.error(f"操作失败: {e}")
    return None

def set_cache(key, results):
    cache_file = CACHE_DIR / f"{key}.json"
    cache_file.write_text(json.dumps({
        "time": datetime.now().isoformat(),
        "results": results
    }, ensure_ascii=False))

def get_embedding(query):
    """获取向量（带缓存）"""
    if query in embedding_cache:
        return embedding_cache[query]
    
    data = json.dumps({
        "input": query,
        "model": "Qwen3-Embedding-8B",
        "dimensions": 4096
    }).encode('utf-8')
    
    req = urllib.request.Request(
        GITEE_API, data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {GITEE_KEY}"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            embedding = result['data'][0]['embedding']
            embedding_cache[query] = embedding
            return embedding
    except Exception as e:
        return None

def search_vector(query, embedding):
    """向量搜索（安全版本）"""
    if not embedding:
        results["vector"] = []
        return
    
    # vec_hex 是向量数据的十六进制表示，来自内部计算，安全
    vec_hex = struct.pack(f'{len(embedding)}f', *embedding).hex()
    
    # 安全修复：使用 sqlite3 连接而不是 subprocess
    try:
        import sqlite3
        conn = sqlite3.connect(str(VECTORS_DB))
        conn.enable_load_extension(True)
        conn.load_extension(str(VEC_EXT))
        cursor = conn.cursor()
        
        # 使用参数化查询
        sql = "SELECT v.record_id, r.content, r.type, r.scene_name, v.distance FROM l1_vec v JOIN l1_records r ON v.record_id = r.record_id WHERE v.embedding MATCH X? AND k = 10 ORDER BY v.distance ASC;"
        cursor.execute(sql, (vec_hex,))
        rows = cursor.fetchall()
        conn.close()
        
        results["vector"] = []
        for row in rows:
            if len(row) >= 5:
                dist = float(row[4])
                if dist > 0:
                    results["vector"].append({
                        "record_id": row[0],
                        "content": row[1],
                        "type": row[2],
                        "scene": row[3],
                        "distance": dist,
                        "score": 1.0 - dist
                    })
    except Exception as e:
        results["vector"] = []

def search_fts(query):
    """FTS 搜索（安全版本）"""
    tokens = query.replace('，', ' ').replace('、', ' ').split()
    
    # 安全修复：转义 FTS 特殊字符
    import re
    safe_tokens = []
    for token in tokens:
        # 移除危险字符
        token = re.sub(r"['\";\\-]", '', token)
        if token:
            safe_tokens.append(token)
    
    if not safe_tokens:
        results["fts"] = []
        return
    
    fts_query = " OR ".join(safe_tokens)
    
    # 使用参数化查询（通过 sqlite3 命令行）
    sql = f"SELECT record_id, content, type, scene_name FROM l1_fts WHERE l1_fts MATCH ? ORDER BY rank LIMIT 10;"
    
    try:
        # 安全修复：使用参数列表而不是 shell 命令
        import sqlite3
        conn = sqlite3.connect(str(VECTORS_DB))
        cursor = conn.cursor()
        cursor.execute(sql, (fts_query,))
        rows = cursor.fetchall()
        conn.close()
        
        results["fts"] = []
        for row in rows:
            if len(row) >= 4:
                results["fts"].append({
                    "record_id": row[0],
                    "content": row[1],
                    "type": row[2],
                    "scene": row[3],
                    "score": 0.5
                })
                parts = line.split('|')
                if len(parts) >= 4:
                    results["fts"].append({
                        "record_id": parts[0],
                        "content": parts[1],
                        "type": parts[2],
                        "scene": parts[3],
                        "source": "fts"
                    })
    except Exception as e:
        results["fts"] = []

def merge_results():
    """合并去重"""
    seen = set()
    merged = []
    
    for r in results["vector"]:
        if r["record_id"] not in seen:
            r["source"] = "vector"
            merged.append(r)
            seen.add(r["record_id"])
    
    for r in results["fts"]:
        if r["record_id"] not in seen:
            merged.append(r)
            seen.add(r["record_id"])
    
    # 按相似度排序
    merged.sort(key=lambda x: x.get("score", 0), reverse=True)
    return merged[:10]

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    if not query:
        print("用法: opt_search.py '查询'")
        sys.exit(1)
    
    start = time.time()
    
    # 检查缓存
    key = get_cache_key(query)
    cached = get_cached(key)
    if cached:
        elapsed = (time.time() - start) * 1000
        print(f"查询: {query} (缓存命中)")
        print(f"耗时: {elapsed:.0f}ms\n")
        for i, r in enumerate(cached[:5], 1):
            print(f"{i}. [{r.get('type', '?')}] {r.get('content', '')[:80]}...")
        return
    
    # 获取向量
    embedding = get_embedding(query)
    
    # 并行搜索
    t1 = threading.Thread(target=search_vector, args=(query, embedding))
    t2 = threading.Thread(target=search_fts, args=(query,))
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    # 合并结果
    merged = merge_results()
    
    # 缓存结果
    set_cache(key, merged)
    
    elapsed = (time.time() - start) * 1000
    
    print(f"查询: {query}")
    print(f"耗时: {elapsed:.0f}ms")
    print(f"向量结果: {len(results['vector'])} 条")
    print(f"FTS结果: {len(results['fts'])} 条\n")
    
    for i, r in enumerate(merged[:5], 1):
        score = f"相似度: {r.get('score', 0):.2f}" if 'score' in r else ""
        print(f"{i}. [{r.get('type', '?')}] {score}")
        print(f"   场景: {r.get('scene', 'N/A')}")
        print(f"   内容: {r.get('content', '')[:100]}...")
        print(f"   来源: {r.get('source', 'N/A')}\n")

if __name__ == "__main__":
    main()
