# 向量存储配置 - V1.0.0

## 三引擎架构

| 引擎 | 状态 | 维度 | 用途 |
|------|------|------|------|
| sqlite-vec | 主引擎 | 4096 | 本地存储，快速检索 |
| qdrant | 副引擎 | 4096 | 高性能，分布式 |
| tfidf | 备份引擎 | - | 关键词检索，兜底 |

## Embedding 配置

```yaml
provider: gitee_ai
model: Qwen3-Embedding-8B
dimensions: 4096
max_tokens: 8192
batch_size: 32
```

## 存储路径

```
memory_context/
├── vectors/
│   ├── sqlite_vec.db      # sqlite-vec 数据库
│   ├── qdrant/            # qdrant 数据目录
│   └── tfidf_index.pkl    # TF-IDF 索引
└── cache/
    └── embedding_cache/   # Embedding 缓存
```

## 检索策略

### 1. 混合检索
```python
def hybrid_search(query: str, k: int = 10) -> List[Result]:
    # 向量检索
    vec_results = sqlite_vec_search(query, k * 2)
    
    # 关键词检索
    tfidf_results = tfidf_search(query, k * 2)
    
    # 融合排序
    return reciprocal_rank_fusion([vec_results, tfidf_results], k)
```

### 2. 分数阈值
| 引擎 | 最小分数 | 说明 |
|------|----------|------|
| sqlite-vec | 0.7 | 余弦相似度 |
| qdrant | 0.7 | 余弦相似度 |
| tfidf | 0.3 | TF-IDF 分数 |

## 性能指标

| 指标 | 目标 | 当前 |
|------|------|------|
| 索引速度 | < 100ms | ✅ |
| 检索速度 | < 50ms | ✅ |
| 内存占用 | < 500MB | ✅ |
| 准确率 | > 90% | ✅ |

## 维护

### 索引重建
```bash
python -c "from memory_context.vector_store import rebuild_index; rebuild_index()"
```

### 缓存清理
```bash
rm -rf memory_context/cache/embedding_cache/*
```
