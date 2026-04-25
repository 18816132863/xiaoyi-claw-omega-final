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
        except:
            pass
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
    except:
        return None

def search_vector(query, embedding):
    """向量搜索"""
    if not embedding:
        results["vector"] = []
        return
    
    vec_hex = struct.pack(f'{len(embedding)}f', *embedding).hex()
    sql = f"SELECT v.record_id, r.content, r.type, r.scene_name, v.distance FROM l1_vec v JOIN l1_records r ON v.record_id = r.record_id WHERE v.embedding MATCH X'{vec_hex}' AND k = 10 ORDER BY v.distance ASC;"
    
    try:
        result = subprocess.run(
            f'sqlite3 -cmd ".load {VEC_EXT}" "{VECTORS_DB}" "{sql}"', shell=False, capture_output=True, text=True, timeout=5
        )  # SECURITY FIX: shell=False removed
        lines = result.stdout.strip().split('\n')
        results["vector"] = []
        for line in lines:
            if line and '|' in line:
                parts = line.split('|')
                if len(parts) >= 5:
                    try:
                        dist = float(parts[4])
                        if dist > 0:
                            results["vector"].append({
                                "record_id": parts[0],
                                "content": parts[1],
                                "type": parts[2],
                                "scene": parts[3],
                                "distance": dist,
                                "score": 1.0 - dist
                            })
                    except:
                        pass
    except:
        results["vector"] = []

def search_fts(query):
    """FTS 搜索"""
    tokens = query.replace('，', ' ').replace('、', ' ').split()
    fts_query = " OR ".join(tokens)
    
    sql = f"SELECT record_id, content, type, scene_name FROM l1_fts WHERE l1_fts MATCH '{fts_query}' ORDER BY rank LIMIT 10;"
    
    try:
        result = subprocess.run(
            f'sqlite3 "{VECTORS_DB}" "{sql}"', shell=False, capture_output=True, text=True, timeout=5
        )  # SECURITY FIX: shell=False removed
        lines = result.stdout.strip().split('\n')
        results["fts"] = []
        for line in lines:
            if line and '|' in line:
                parts = line.split('|')
                if len(parts) >= 4:
                    results["fts"].append({
                        "record_id": parts[0],
                        "content": parts[1],
                        "type": parts[2],
                        "scene": parts[3],
                        "source": "fts"
                    })
    except:
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
