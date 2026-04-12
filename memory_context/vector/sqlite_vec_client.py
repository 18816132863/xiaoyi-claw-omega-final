#!/usr/bin/env python3
"""
SQLite-vec 向量客户端封装
终极鸽子王 V23.0 - 向量极致层

功能:
- 自动加载 vec0 扩展
- 向量存储与检索
- 批量操作支持
- 中文优化 Embedding (Qwen3)
- 缓存与性能优化
"""

import os
import json
import hashlib
import sqlite3
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone
import threading
import logging

# 使用 pysqlite3 支持扩展加载
try:
    from pysqlite3 import dbapi2 as sqlite3
except ImportError:
    import sqlite3

logger = logging.getLogger(__name__)


def _get_default_vec0_path() -> str:
    """获取默认 vec0.so 路径"""
    try:
        from infrastructure.path_resolver import get_project_root
        return str(get_project_root() / "repo/lib/python3.12/site-packages/sqlite_vec/vec0.so")
    except ImportError:
        return "repo/lib/python3.12/site-packages/sqlite_vec/vec0.so"


@dataclass
class VectorConfig:
    """向量配置"""
    db_path: str = ":memory:"
    vec0_path: str = field(default_factory=_get_default_vec0_path)
    dimension: int = 1024
    table_name: str = "embeddings"
    cache_size: int = 10000
    enable_cache: bool = True


class EmbeddingProvider:
    """Embedding 提供者基类"""
    
    def get_embedding(self, text: str) -> List[float]:
        raise NotImplementedError
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self.get_embedding(t) for t in texts]


class QwenEmbeddingProvider(EmbeddingProvider):
    """Qwen3-Embedding-8B 提供者"""
    
    def __init__(self, api_key: str = None, dimension: int = 1024):
        self.api_key = api_key or os.getenv("GITEE_API_KEY", "")
        self.dimension = dimension
        self.base_url = "https://ai.gitee.com/v1/embeddings"
        self._cache: Dict[str, List[float]] = {}
        self._cache_lock = threading.Lock()
    
    def _cache_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    def get_embedding(self, text: str) -> List[float]:
        # 检查缓存
        cache_key = self._cache_key(text)
        with self._cache_lock:
            if cache_key in self._cache:
                return self._cache[cache_key]
        
        # 调用 API
        try:
            import requests
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "Qwen3-Embedding-8B",
                    "input": text
                },
                timeout=30
            )
            response.raise_for_status()
            embedding = response.json()["data"][0]["embedding"]
            
            # 缓存结果
            with self._cache_lock:
                self._cache[cache_key] = embedding
            
            return embedding
        except Exception as e:
            logger.error(f"Qwen embedding failed: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        # 批量请求优化
        results = []
        for text in texts:
            results.append(self.get_embedding(text))
        return results


class LocalEmbeddingProvider(EmbeddingProvider):
    """本地 Embedding 提供者 (备用)"""
    
    def __init__(self, dimension: int = 1024):
        self.dimension = dimension
        # 可以集成 transformers.js 或其他本地模型
    
    def get_embedding(self, text: str) -> List[float]:
        # 简单的哈希向量作为备用
        import hashlib
        # 生成足够长的哈希
        h = hashlib.sha512(text.encode()).digest()
        while len(h) < self.dimension:
            h = h + hashlib.sha512(h).digest()
        vec = [float(b) / 255.0 for b in h[:self.dimension]]
        # 归一化
        norm = sum(v * v for v in vec) ** 0.5
        return [v / norm for v in vec] if norm > 0 else vec


class SQLiteVecClient:
    """SQLite-vec 向量客户端"""
    
    def __init__(
        self,
        config: VectorConfig = None,
        embedding_provider: EmbeddingProvider = None
    ):
        self.config = config or VectorConfig()
        self.embedding_provider = embedding_provider or LocalEmbeddingProvider()
        self._conn = None
        self._lock = threading.Lock()
        self._query_cache: Dict[str, List[Tuple]] = {}
        
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self._conn is None:
            self._conn = sqlite3.connect(self.config.db_path)
            self._conn.enable_load_extension(True)
            self._conn.load_extension(self.config.vec0_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn
    
    def _init_db(self):
        """初始化数据库"""
        conn = self._get_connection()
        
        # 创建向量表
        conn.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS {self.config.table_name} 
            USING vec0(
                id TEXT PRIMARY KEY,
                embedding float[{self.config.dimension}],
                content TEXT,
                metadata TEXT,
                created_at TEXT
            )
        """)
        
        # 创建元数据表
        conn.execute("""
            CREATE TABLE IF NOT EXISTS _vec_metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        conn.commit()
        logger.info(f"SQLite-vec initialized: {self.config.db_path}")
    
    def insert(
        self,
        id: str,
        text: str,
        embedding: List[float] = None,
        metadata: Dict = None
    ) -> bool:
        """插入向量"""
        if embedding is None:
            embedding = self.embedding_provider.get_embedding(text)
        
        conn = self._get_connection()
        with self._lock:
            try:
                conn.execute(
                    f"INSERT INTO {self.config.table_name} (id, embedding, content, metadata, created_at) VALUES (?, ?, ?, ?, ?)",
                    (
                        id,
                        json.dumps(embedding),
                        text,
                        json.dumps(metadata or {}),
                        datetime.now(timezone.utc).isoformat()
                    )
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                # 更新已存在的记录
                conn.execute(
                    f"UPDATE {self.config.table_name} SET embedding=?, content=?, metadata=?, created_at=? WHERE id=?",
                    (
                        json.dumps(embedding),
                        text,
                        json.dumps(metadata or {}),
                        datetime.now(timezone.utc).isoformat(),
                        id
                    )
                )
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Insert failed: {e}")
                return False
    
    def batch_insert(
        self,
        items: List[Dict[str, Any]],
        batch_size: int = 32
    ) -> int:
        """批量插入"""
        success_count = 0
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # 批量获取 embedding
            texts = [item["text"] for item in batch]
            embeddings = self.embedding_provider.get_embeddings(texts)
            
            conn = self._get_connection()
            with self._lock:
                for item, embedding in zip(batch, embeddings):
                    try:
                        conn.execute(
                            f"INSERT OR REPLACE INTO {self.config.table_name} (id, embedding, content, metadata, created_at) VALUES (?, ?, ?, ?, ?)",
                            (
                                item["id"],
                                json.dumps(embedding),
                                item["text"],
                                json.dumps(item.get("metadata", {})),
                                datetime.now(timezone.utc).isoformat()
                            )
                        )
                        success_count += 1
                    except Exception as e:
                        logger.error(f"Batch insert failed for {item['id']}: {e}")
                
                conn.commit()
        
        return success_count
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        threshold: float = 0.0,
        filter_metadata: Dict = None
    ) -> List[Dict]:
        """向量搜索"""
        # 检查缓存
        cache_key = hashlib.md5(f"{query}:{top_k}:{filter_metadata}".encode()).hexdigest()
        if self.config.enable_cache and cache_key in self._query_cache:
            return self._query_cache[cache_key]
        
        # 获取查询向量
        query_embedding = self.embedding_provider.get_embedding(query)
        
        conn = self._get_connection()
        
        # 构建查询
        sql = f"""
            SELECT id, content, metadata, created_at, distance
            FROM {self.config.table_name}
            WHERE embedding MATCH ?
            AND k = ?
            ORDER BY distance
        """
        
        results = []
        try:
            rows = conn.execute(
                sql,
                (json.dumps(query_embedding), top_k * 2)  # 多取一些用于过滤
            ).fetchall()
            
            for row in rows:
                # 距离阈值过滤
                if row["distance"] < threshold:
                    continue
                
                # 元数据过滤
                metadata = json.loads(row["metadata"]) if row["metadata"] else {}
                if filter_metadata:
                    match = all(metadata.get(k) == v for k, v in filter_metadata.items())
                    if not match:
                        continue
                
                results.append({
                    "id": row["id"],
                    "content": row["content"],
                    "metadata": metadata,
                    "created_at": row["created_at"],
                    "distance": row["distance"],
                    "score": 1.0 - row["distance"]  # 转换为相似度
                })
                
                if len(results) >= top_k:
                    break
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
        
        # 缓存结果
        if self.config.enable_cache:
            self._query_cache[cache_key] = results
        
        return results
    
    def delete(self, id: str) -> bool:
        """删除向量"""
        conn = self._get_connection()
        with self._lock:
            try:
                conn.execute(f"DELETE FROM {self.config.table_name} WHERE id = ?", (id,))
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Delete failed: {e}")
                return False
    
    def get(self, id: str) -> Optional[Dict]:
        """获取单个向量"""
        conn = self._get_connection()
        try:
            row = conn.execute(
                f"SELECT id, content, metadata, created_at FROM {self.config.table_name} WHERE id = ?",
                (id,)
            ).fetchone()
            
            if row:
                return {
                    "id": row["id"],
                    "content": row["content"],
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                    "created_at": row["created_at"]
                }
        except Exception as e:
            logger.error(f"Get failed: {e}")
        
        return None
    
    def count(self) -> int:
        """统计向量数量"""
        conn = self._get_connection()
        try:
            result = conn.execute(f"SELECT COUNT(*) FROM {self.config.table_name}").fetchone()
            return result[0]
        except:
            return 0
    
    def clear(self) -> bool:
        """清空所有向量"""
        conn = self._get_connection()
        with self._lock:
            try:
                conn.execute(f"DELETE FROM {self.config.table_name}")
                conn.commit()
                self._query_cache.clear()
                return True
            except Exception as e:
                logger.error(f"Clear failed: {e}")
                return False
    
    def close(self):
        """关闭连接"""
        if self._conn:
            self._conn.close()
            self._conn = None


# 便捷函数
def create_client(
    db_path: str = ":memory:",
    dimension: int = 1024,
    use_qwen: bool = False,
    qwen_api_key: str = None
) -> SQLiteVecClient:
    """创建向量客户端"""
    config = VectorConfig(
        db_path=db_path,
        dimension=dimension
    )
    
    if use_qwen:
        provider = QwenEmbeddingProvider(api_key=qwen_api_key, dimension=dimension)
    else:
        provider = LocalEmbeddingProvider(dimension=dimension)
    
    return SQLiteVecClient(config=config, embedding_provider=provider)


# 测试代码
if __name__ == "__main__":
    print("🧪 Testing SQLite-vec client...")
    
    # 创建客户端
    client = create_client(dimension=4)  # 测试用小维度
    
    # 插入测试数据
    test_data = [
        {"id": "doc1", "text": "Python 是一门编程语言"},
        {"id": "doc2", "text": "JavaScript 用于网页开发"},
        {"id": "doc3", "text": "机器学习是人工智能的分支"},
    ]
    
    for item in test_data:
        # 使用简单的测试向量
        vec = [float(i) / 10.0 for i in range(4)]
        client.insert(item["id"], item["text"], embedding=vec)
    
    print(f"✅ Inserted {client.count()} vectors")
    
    # 搜索测试
    results = client.search("编程语言", top_k=2)
    print(f"✅ Search results: {len(results)}")
    for r in results:
        print(f"   - {r['id']}: {r['content']} (score: {r['score']:.3f})")
    
    client.close()
    print("🎉 Test completed!")
