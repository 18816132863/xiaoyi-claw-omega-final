#!/usr/bin/env python3
"""并行搜索 - 同时执行向量和FTS"""
import subprocess
import sys
import threading
import time

from paths import VECTORS_DB
from paths import VEC_EXT
GITEE_API = None  # 从配置文件读取
GITEE_KEY = os.environ.get("EMBEDDING_API_KEY", "")

results = {"vector": [], "fts": []}

def search_vector(query):
    """向量搜索"""
    import urllib.request
    import json
    import struct
    
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
            vec_hex = struct.pack(f'{len(embedding)}f', *embedding).hex()
            
            sql = f"SELECT v.record_id, r.content FROM l1_vec v JOIN l1_records r ON v.record_id = r.record_id WHERE v.embedding MATCH X'{vec_hex}' AND k = 5 ORDER BY v.distance ASC;"
            result = subprocess.run(
                f'sqlite3 -cmd ".load {VEC_EXT}" "{VECTORS_DB}" "{sql}"', shell=False, capture_output=True, text=True, timeout=5
            )  # SECURITY FIX: shell=False removed
            results["vector"] = result.stdout.strip().split('\n')
    except Exception as e:
        results["vector"] = [f"Error: {e}"]

def search_fts(query):
    """FTS 搜索"""
    tokens = query.replace('，', ' ').replace('、', ' ').split()
    fts_query = " OR ".join(tokens)
    
    sql = f"SELECT record_id, content FROM l1_fts WHERE l1_fts MATCH '{fts_query}' ORDER BY rank LIMIT 5;"
    result = subprocess.run(
        f'sqlite3 "{VECTORS_DB}" "{sql}"', shell=False, capture_output=True, text=True, timeout=5
    )  # SECURITY FIX: shell=False removed
    results["fts"] = result.stdout.strip().split('\n')

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    if not query:
        print("用法: parallel_search.py '查询'")
        sys.exit(1)
    
    start = time.time()
    
    # 并行执行
    t1 = threading.Thread(target=search_vector, args=(query,))
    t2 = threading.Thread(target=search_fts, args=(query,))
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    elapsed = (time.time() - start) * 1000
    
    print(f"查询: {query}")
    print(f"耗时: {elapsed:.0f}ms")
    print(f"\n向量结果: {len([r for r in results['vector'] if r])} 条")
    print(f"FTS结果: {len([r for r in results['fts'] if r])} 条")

if __name__ == "__main__":
    main()
