#!/usr/bin/env python3
"""
记忆向量存储集成
终极鸽子王 V23.0 - 向量极致层

将 SQLite-vec 集成到记忆系统，提供:
- 记忆自动向量化
- 语义搜索
- 记忆去重
- 相似记忆关联
"""

import os
import json
import hashlib
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

# 导入 SQLite-vec 客户端
from sqlite_vec_client import (
    SQLiteVecClient,
    VectorConfig,
    QwenEmbeddingProvider,
    LocalEmbeddingProvider,
    create_client
)


@dataclass
class MemoryItem:
    """记忆项"""
    id: str
    content: str
    memory_type: str  # user, system, session, project
    source: str  # 文件路径或来源
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str


class MemoryVectorStore:
    """记忆向量存储"""
    
    def __init__(
        self,
        db_path: str = None,
        use_qwen: bool = False,
        qwen_api_key: str = None
    ):
        # 默认数据库路径
        if db_path is None:
            try:
                from infrastructure.path_resolver import get_project_root
                db_path = str(get_project_root() / "memory/vectors.db")
            except ImportError:
                db_path = "memory/vectors.db"
        
        # 确保目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 创建向量客户端
        self.client = create_client(
            db_path=db_path,
            dimension=1024,
            use_qwen=use_qwen,
            qwen_api_key=qwen_api_key
        )
        
        self.db_path = db_path
    
    def add_memory(
        self,
        content: str,
        memory_type: str = "general",
        source: str = "",
        metadata: Dict = None
    ) -> str:
        """添加记忆"""
        # 生成唯一 ID
        memory_id = self._generate_id(content)
        
        # 构建元数据
        full_metadata = {
            "memory_type": memory_type,
            "source": source,
            **(metadata or {})
        }
        
        # 插入向量
        self.client.insert(
            id=memory_id,
            text=content,
            metadata=full_metadata
        )
        
        return memory_id
    
    def add_memory_from_file(
        self,
        file_path: str,
        memory_type: str = "document"
    ) -> List[str]:
        """从文件添加记忆"""
        added_ids = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按段落分割
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        for i, para in enumerate(paragraphs):
            if len(para) < 50:  # 跳过太短的段落
                continue
            
            memory_id = self.add_memory(
                content=para,
                memory_type=memory_type,
                source=file_path,
                metadata={"paragraph_index": i}
            )
            added_ids.append(memory_id)
        
        return added_ids
    
    def search_memories(
        self,
        query: str,
        top_k: int = 10,
        memory_type: str = None,
        min_score: float = 0.0
    ) -> List[Dict]:
        """搜索记忆"""
        # 构建过滤条件
        filter_metadata = {}
        if memory_type:
            filter_metadata["memory_type"] = memory_type
        
        # 执行搜索
        results = self.client.search(
            query=query,
            top_k=top_k * 2,  # 多取一些用于过滤
            filter_metadata=filter_metadata if filter_metadata else None
        )
        
        # 过滤低分结果
        filtered = [r for r in results if r["score"] >= min_score]
        
        return filtered[:top_k]
    
    def find_similar(
        self,
        content: str,
        top_k: int = 5,
        exclude_self: bool = True
    ) -> List[Dict]:
        """查找相似记忆"""
        results = self.search_memories(content, top_k=top_k + 1)
        
        if exclude_self:
            content_id = self._generate_id(content)
            results = [r for r in results if r["id"] != content_id]
        
        return results[:top_k]
    
    def check_duplicate(
        self,
        content: str,
        threshold: float = 0.95
    ) -> Optional[Dict]:
        """检查重复记忆"""
        similar = self.find_similar(content, top_k=1)
        
        if similar and similar[0]["score"] >= threshold:
            return similar[0]
        
        return None
    
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """获取单个记忆"""
        return self.client.get(memory_id)
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        return self.client.delete(memory_id)
    
    def delete_by_source(self, source: str) -> int:
        """按来源删除记忆"""
        # 获取所有记忆
        conn = self.client._get_connection()
        rows = conn.execute(
            "SELECT id FROM embeddings WHERE json_extract(metadata, '$.source') = ?",
            (source,)
        ).fetchall()
        
        deleted_count = 0
        for row in rows:
            if self.client.delete(row[0]):
                deleted_count += 1
        
        return deleted_count
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        conn = self.client._get_connection()
        
        total = self.client.count()
        
        # 按类型统计
        type_stats = {}
        rows = conn.execute(
            "SELECT metadata FROM embeddings"
        ).fetchall()
        
        for row in rows:
            metadata = json.loads(row[0]) if row[0] else {}
            mem_type = metadata.get("memory_type", "unknown")
            type_stats[mem_type] = type_stats.get(mem_type, 0) + 1
        
        return {
            "total": total,
            "by_type": type_stats,
            "db_path": self.db_path
        }
    
    def _generate_id(self, content: str) -> str:
        """生成记忆 ID"""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def close(self):
        """关闭连接"""
        self.client.close()


# 便捷函数
_memory_store = None

def get_memory_store(
    db_path: str = None,
    use_qwen: bool = False,
    qwen_api_key: str = None
) -> MemoryVectorStore:
    """获取全局记忆存储实例"""
    global _memory_store
    
    if _memory_store is None:
        _memory_store = MemoryVectorStore(
            db_path=db_path,
            use_qwen=use_qwen,
            qwen_api_key=qwen_api_key
        )
    
    return _memory_store


def add_memory(content: str, **kwargs) -> str:
    """添加记忆 (便捷函数)"""
    store = get_memory_store()
    return store.add_memory(content, **kwargs)


def search_memories(query: str, **kwargs) -> List[Dict]:
    """搜索记忆 (便捷函数)"""
    store = get_memory_store()
    return store.search_memories(query, **kwargs)


# 测试
if __name__ == "__main__":
    print("🧪 Testing Memory Vector Store...")
    
    # 创建测试存储
    store = MemoryVectorStore(db_path="/tmp/test_memory.db")
    
    # 添加测试记忆
    test_memories = [
        ("用户喜欢简洁的技术文档", "preference"),
        ("项目使用 Python 和 OpenClaw", "project"),
        ("系统版本 V23.0", "system"),
        ("用户偏好表格和结构化输出", "preference"),
    ]
    
    for content, mem_type in test_memories:
        memory_id = store.add_memory(content, memory_type=mem_type)
        print(f"  ✅ Added: {memory_id} ({mem_type})")
    
    # 搜索测试
    print("\n🔍 Searching for '用户偏好':")
    results = store.search_memories("用户偏好", top_k=3)
    for r in results:
        print(f"  [{r['score']:.3f}] {r['content']} ({r['metadata'].get('memory_type')})")
    
    # 检查重复
    print("\n🔄 Checking duplicate:")
    dup = store.check_duplicate("用户喜欢简洁的技术文档")
    if dup:
        print(f"  ⚠️ Found duplicate: {dup['id']} (score: {dup['score']:.3f})")
    else:
        print("  ✅ No duplicate found")
    
    # 统计
    print("\n📊 Stats:")
    stats = store.get_stats()
    print(f"  Total: {stats['total']}")
    print(f"  By type: {stats['by_type']}")
    
    store.close()
    print("\n🎉 Test completed!")
