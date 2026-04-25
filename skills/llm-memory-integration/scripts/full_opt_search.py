#!/usr/bin/env python3
"""
完整优化搜索 - 向量 + FTS + RRF 融合（安全修复版）
"""
import sqlite3
import struct
import json
from pathlib import Path
from typing import Dict, List

VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"
VEC_EXT = Path.home() / ".openclaw" / "extensions" / "memory-tencentdb" / "node_modules" / "sqlite-vec-linux-x64" / "vec0.so"

results = {}

def get_db_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(str(VECTORS_DB))
    return conn

def search_vector(embedding: List[float]) -> List[Dict]:
    """向量搜索（使用 sqlite3 直接连接）"""
    results = []
    
    try:
        conn = get_db_connection()
        
        # 加载扩展
        conn.enable_load_extension(True)
        if VEC_EXT.exists():
            conn.load_extension(str(VEC_EXT))
        
        cursor = conn.cursor()
        
        # 将 embedding 转换为十六进制
        vec_hex = struct.pack(f'{len(embedding)}f', *embedding).hex()
        
        # 执行向量搜索
        cursor.execute(f"""
            SELECT v.record_id, r.content, r.type, r.scene_name, v.distance 
            FROM l1_vec v 
            JOIN l1_records r ON v.record_id = r.record_id 
            WHERE v.embedding MATCH X'{vec_hex}' AND k = 10 
            ORDER BY v.distance ASC
        """)
        
        for row in cursor.fetchall():
            if len(row) >= 5:
                try:
                    dist = float(row[4])
                    if dist > 0:
                        results.append({
                            "record_id": row[0],
                            "content": row[1],
                            "type": row[2],
                            "scene": row[3],
                            "distance": dist,
                            "score": 1.0 - dist
                        })
                except:
                    pass
        
        conn.close()
    except Exception as e:
        print(f"向量搜索失败: {e}")
    
    return results

def search_fts(queries: List[str]) -> List[Dict]:
    """FTS 搜索（使用 sqlite3 直接连接）"""
    results = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 合并所有查询词
        all_tokens = []
        for q in queries:
            all_tokens.extend(q.replace('，', ' ').replace('、', ' ').split())
        
        fts_query = " OR ".join(set(all_tokens))
        
        # 执行 FTS 搜索
        cursor.execute(f"""
            SELECT record_id, content, type, scene_name 
            FROM l1_fts 
            WHERE l1_fts MATCH '{fts_query}' 
            ORDER BY rank 
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            if len(row) >= 4:
                results.append({
                    "record_id": row[0],
                    "content": row[1],
                    "type": row[2],
                    "scene": row[3],
                    "source": "fts"
                })
        
        conn.close()
    except Exception as e:
        print(f"FTS 搜索失败: {e}")
    
    return results

def rrf_fusion(vector_results: List[Dict], fts_results: List[Dict], k: int = 60) -> List[Dict]:
    """RRF 融合排序"""
    scores = {}
    
    # 向量结果
    for i, r in enumerate(vector_results):
        rid = r["record_id"]
        scores[rid] = scores.get(rid, 0) + 1.0 / (k + i + 1)
        if "rrf_score" not in r:
            r["rrf_score"] = 0
        r["rrf_score"] += 1.0 / (k + i + 1)
    
    # FTS 结果
    for i, r in enumerate(fts_results):
        rid = r["record_id"]
        if rid in scores:
            # 合并
            for vr in vector_results:
                if vr["record_id"] == rid:
                    vr["rrf_score"] += 1.0 / (k + i + 1)
                    break
        else:
            r["rrf_score"] = 1.0 / (k + i + 1)
            scores[rid] = r["rrf_score"]
    
    # 合并并排序
    all_results = vector_results + [r for r in fts_results if r["record_id"] not in {v["record_id"] for v in vector_results}]
    all_results.sort(key=lambda x: x.get("rrf_score", 0), reverse=True)
    
    return all_results[:10]

def full_search(query: str, embedding: List[float]) -> Dict:
    """完整搜索"""
    # 向量搜索
    vector_results = search_vector(embedding)
    
    # FTS 搜索
    fts_results = search_fts([query])
    
    # RRF 融合
    fused = rrf_fusion(vector_results, fts_results)
    
    return {
        "query": query,
        "vector_count": len(vector_results),
        "fts_count": len(fts_results),
        "fused_count": len(fused),
        "results": fused
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: full_opt_search.py <查询词>")
        sys.exit(1)
    
    query = sys.argv[1]
    
    # 模拟 embedding（实际应从 API 获取）
    import random
    embedding = [random.random() for _ in range(4096)]
    
    result = full_search(query, embedding)
    
    print(f"查询: {query}")
    print(f"向量结果: {result['vector_count']} 条")
    print(f"FTS 结果: {result['fts_count']} 条")
    print(f"融合结果: {result['fused_count']} 条")
    
    for i, r in enumerate(result["results"][:5], 1):
        print(f"\n{i}. [{r.get('type', '?')}] RRF: {r.get('rrf_score', 0):.4f}")
        print(f"   场景: {r.get('scene', 'N/A')}")
        print(f"   内容: {r.get('content', '')[:80]}...")
