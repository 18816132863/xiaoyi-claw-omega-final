#!/usr/bin/env python3
from safe_extension_loader import safe_load_extension
"""
混合记忆搜索（安全修复版）

安全修复：
- 移除 shell=False，使用 sqlite3 直接连接
- 使用参数化查询防止 SQL 注入
- 从配置文件读取 API Key
"""

import os
import json
import sqlite3
import struct
import urllib.request
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# 配置路径
CONFIG_DIR = Path(__file__).parent.parent / "config"
LLM_CONFIG = CONFIG_DIR / "llm_config.json"

# 数据库路径
VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"

# 向量扩展路径（动态检测）
def get_vec_extension_path() -> Path:
    """动态获取向量扩展路径"""
    possible_paths = [
        Path.home() / ".openclaw" / "extensions" / "memory-tencentdb" / "node_modules" / "sqlite-vec-linux-x64" / "vec0.so",
        Path.home() / ".openclaw" / "extensions" / "memory-tencentdb" / "node_modules" / "sqlite-vec-linux-x64" / "vec0",
    ]
    for p in possible_paths:
        if p.exists():
            return p
    return possible_paths[0]


def load_config() -> Dict:
    """加载配置"""
    if LLM_CONFIG.exists():
        try:
            return json.loads(LLM_CONFIG.read_text())
        except Exception as e:
            logger.error(f"操作失败: {e}")
    return {}


def get_db_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(str(VECTORS_DB))
    try:
        conn.enable_load_extension(True)
        vec_ext = get_vec_extension_path()
        if vec_ext.exists():
            safe_load_extension(conn, vec_ext)
    except Exception as e:
        print(f"⚠️ 向量扩展加载失败: {e}")
    return conn


def get_embedding(text: str) -> Optional[List[float]]:
    """获取向量"""
    config = load_config()
    api_key = config.get("embedding", {}).get("api_key", "")
    
    if not api_key:
        return None
    
    api_url = config.get("embedding", {}).get("base_url", "")
    if not api_url:
        return None
    model = config.get("embedding", {}).get("model", "Qwen3-Embedding-8B")
    dimensions = config.get("embedding", {}).get("dimensions", 4096)
    
    data = json.dumps({
        "input": text[:2000],
        "model": model,
        "dimensions": dimensions
    }).encode('utf-8')
    
    req = urllib.request.Request(
        api_url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result['data'][0]['embedding']
    except Exception as e:
        print(f"API 错误: {e}")
        return None


def vector_search(query_embedding: List[float], top_k: int = 10) -> List[Dict]:
    """向量搜索"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        vec_bytes = struct.pack(f'{len(query_embedding)}f', *query_embedding)
        
        # 使用参数化查询
        cursor.execute("""
            SELECT record_id, content, type, scene_name, created_at,
                   vec_distance_cosine(embedding, ?) as distance
            FROM l1_records r
            JOIN l1_vec v ON r.record_id = v.record_id
            ORDER BY distance ASC
            LIMIT ?
        """, (vec_bytes, top_k))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "record_id": row[0],
                "content": row[1],
                "type": row[2],
                "scene": row[3],
                "timestamp": row[4],
                "distance": row[5]
            })
        
        return results
    except Exception as e:
        print(f"向量搜索错误: {e}")
        return []
    finally:
        conn.close()


def fts_search(query: str, top_k: int = 10) -> List[Dict]:
    """全文搜索"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 使用参数化查询
        cursor.execute("""
            SELECT record_id, content, type, scene_name, created_at
            FROM l1_records
            WHERE content LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (f"%{query}%", top_k))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "record_id": row[0],
                "content": row[1],
                "type": row[2],
                "scene": row[3],
                "timestamp": row[4],
                "source": "fts"
            })
        
        return results
    except Exception as e:
        print(f"FTS 搜索错误: {e}")
        return []
    finally:
        conn.close()


def hybrid_search(query: str, top_k: int = 10) -> List[Dict]:
    """混合搜索"""
    print(f"🔍 混合搜索: {query}")
    
    # 1. 获取查询向量
    query_embedding = get_embedding(query)
    
    # 2. 向量搜索
    vector_results = []
    if query_embedding:
        vector_results = vector_search(query_embedding, top_k)
        print(f"  向量搜索: {len(vector_results)} 条")
    
    # 3. FTS 搜索
    fts_results = fts_search(query, top_k)
    print(f"  FTS 搜索: {len(fts_results)} 条")
    
    # 4. 合并去重
    seen_ids = set()
    combined = []
    
    for r in vector_results:
        if r["record_id"] not in seen_ids:
            r["source"] = "vector"
            combined.append(r)
            seen_ids.add(r["record_id"])
    
    for r in fts_results:
        if r["record_id"] not in seen_ids:
            combined.append(r)
            seen_ids.add(r["record_id"])
    
    # 5. 返回 top_k
    return combined[:top_k]


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: hybrid_memory_search.py <query>")
        sys.exit(1)
    
    query = sys.argv[1]
    results = hybrid_search(query)
    
    print(f"\n找到 {len(results)} 条结果:")
    for i, r in enumerate(results, 1):
        content_short = r["content"][:80] + "..." if len(r["content"]) > 80 else r["content"]
        print(f"{i}. [{r.get('source', 'unknown')}] {content_short}")
