#!/usr/bin/env python3
"""
向量化修复脚本
使用 pysqlite3-binary 支持扩展加载
"""

import sys
import json
import requests
from pathlib import Path

# 添加 core 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

try:
    from sqlite_vec import connect, is_vec_available, get_vec_version
    USE_PYSQLITE3 = True
except ImportError:
    import sqlite3
    USE_PYSQLITE3 = False
    print("⚠️ pysqlite3 未安装，使用标准 sqlite3")

# 配置
VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"
CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"

def get_embedding_config():
    """从配置文件获取 Embedding 配置"""
    config = json.loads(CONFIG_PATH.read_text())
    plugin_config = config.get("plugins", {}).get("entries", {}).get("memory-tencentdb", {}).get("config", {})
    embedding = plugin_config.get("embedding", {})
    return {
        "provider": embedding.get("provider", "gitee"),
        "base_url": embedding.get("baseUrl", "https://ai.gitee.com/v1"),
        "api_key": embedding.get("apiKey", ""),
        "model": embedding.get("model", "Qwen3-Embedding-8B"),
        "dimensions": embedding.get("dimensions", 4096)
    }

def get_embedding(text, config):
    """调用 Embedding API 获取向量"""
    if not config["api_key"]:
        print("❌ Embedding API Key 未配置")
        return None
    
    try:
        response = requests.post(
            f"{config['base_url']}/embeddings",
            headers={
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json"
            },
            json={
                "model": config["model"],
                "input": text[:8000]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["data"][0]["embedding"]
        else:
            print(f"❌ Embedding API 错误: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Embedding 请求失败: {e}")
        return None

def check_status():
    """检查向量化状态"""
    # 使用上下文管理器确保连接关闭
    if USE_PYSQLITE3:
        conn_ctx = connect(str(VECTORS_DB))
    else:
        conn_ctx = sqlite3.connect(str(VECTORS_DB))
    
    with conn_ctx as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM l0_conversations")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM l0_vec_rowids")
        vectorized = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM l1_records")
        l1_total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM l1_vec_rowids")
        l1_vectorized = cursor.fetchone()[0]
    
    print("=" * 50)
    print("   向量化状态报告")
    print("=" * 50)
    
    if USE_PYSQLITE3 and is_vec_available():
        print(f"sqlite-vec 版本: {get_vec_version()}")
    
    print(f"\nL0 对话层:")
    print(f"  总数: {total}")
    print(f"  已向量化: {vectorized}")
    print(f"  未向量化: {total - vectorized}")
    if total > 0:
        coverage = vectorized * 100 / total
        print(f"  覆盖率: {coverage:.1f}%")
    
    print(f"\nL1 记忆层:")
    print(f"  总数: {l1_total}")
    print(f"  已向量化: {l1_vectorized}")
    if l1_total > 0:
        l1_coverage = l1_vectorized * 100 / l1_total
        print(f"  覆盖率: {l1_coverage:.1f}%")

def fix_vectorization():
    """修复未向量化的对话"""
    if not USE_PYSQLITE3:
        print("❌ 需要安装 pysqlite3-binary 才能执行向量化")
        print("   运行: pip install pysqlite3-binary")
        return
    
    config = get_embedding_config()
    print(f"Embedding 配置: {config['provider']}/{config['model']} ({config['dimensions']}D)")
    
    with connect(str(VECTORS_DB)) as conn:
        cursor = conn.cursor()
        
        # 获取未向量化的对话
        cursor.execute("""
            SELECT record_id, message_text 
            FROM l0_conversations 
            WHERE record_id NOT IN (SELECT rowid FROM l0_vec_rowids)
            ORDER BY timestamp DESC
        """)
        unvectorized = cursor.fetchall()
        
        print(f"\n发现 {len(unvectorized)} 条未向量化的对话")
        
        if len(unvectorized) == 0:
            print("✅ 所有对话已向量化")
            return
        
        success_count = 0
        for record_id, message_text in unvectorized:
            print(f"\n处理: {record_id[:50]}...")
            
            # 获取向量
            embedding = get_embedding(message_text, config)
            
            if embedding:
                try:
                    # 将向量转换为 blob
                    import struct
                    vector_blob = struct.pack(f'{len(embedding)}f', *embedding)
                    
                    cursor.execute("""
                        INSERT OR REPLACE INTO l0_vec (record_id, embedding, recorded_at)
                        VALUES (?, ?, datetime('now'))
                    """, (record_id, vector_blob))
                    
                    conn.commit()
                    print(f"  ✅ 向量化成功")
                    success_count += 1
                except Exception as e:
                    print(f"  ❌ 存储失败: {e}")
            else:
                print(f"  ⏭️ 跳过")
    
    print(f"\n========================================")
    print(f"向量化完成: {success_count}/{len(unvectorized)} 条成功")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        check_status()
    else:
        check_status()
        print("\n")
        fix_vectorization()
