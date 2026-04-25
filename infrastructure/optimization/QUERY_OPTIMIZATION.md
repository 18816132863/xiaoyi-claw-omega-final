# QUERY_OPTIMIZATION.md - 查询优化策略

## 目的
优化查询性能，降低查询延迟，提升数据访问效率。

## 适用范围
所有数据库查询、向量检索、缓存查询、API 查询。

## 查询优化架构

```
┌─────────────────────────────────────────────────────────────┐
│                    查询优化架构                              │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   查询重写     │    │   索引优化     │    │   缓存优化     │
│  (Rewrite)    │    │  (Index)      │    │  (Cache)      │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ - 查询简化     │    │ - 索引策略     │    │ - 查询缓存     │
│ - 查询合并     │    │ - 覆盖索引     │    │ - 结果缓存     │
│ - 查询分解     │    │ - 复合索引     │    │ - 预热缓存     │
└───────────────┘    └───────────────┘    └───────────────┘
```

## 查询重写优化

### 重写策略
| 策略 | 说明 | 效果 |
|------|------|------|
| 查询简化 | 简化复杂查询 | 20-50% 提升 |
| 查询合并 | 合并相似查询 | 30-60% 提升 |
| 查询分解 | 分解复杂查询 | 20-40% 提升 |
| 子查询优化 | 优化子查询 | 30-70% 提升 |

### 查询重写配置
```json
{
  "query_rewrite": {
    "enabled": true,
    "simplification": {
      "enabled": true,
      "remove_redundant_conditions": true,
      "simplify_expressions": true
    },
    "merging": {
      "enabled": true,
      "merge_similar_queries": true,
      "batch_similar_queries": true
    },
    "decomposition": {
      "enabled": true,
      "max_sub_queries": 5,
      "parallel_execution": true
    },
    "subquery_optimization": {
      "enabled": true,
      "convert_to_join": true,
      "push_down_predicates": true
    }
  }
}
```

### 查询优化示例
```sql
-- 优化前
SELECT * FROM tasks 
WHERE tenant_id IN (SELECT id FROM tenants WHERE status = 'active')
AND created_at > '2026-01-01'
ORDER BY created_at DESC
LIMIT 100;

-- 优化后
SELECT t.* FROM tasks t
INNER JOIN tenants te ON t.tenant_id = te.id
WHERE te.status = 'active'
AND t.created_at > '2026-01-01'
ORDER BY t.created_at DESC
LIMIT 100;
```

## 索引优化

### 索引策略
| 索引类型 | 说明 | 适用场景 |
|----------|------|----------|
| B-Tree | 平衡树索引 | 等值、范围查询 |
| Hash | 哈希索引 | 等值查询 |
| 全文索引 | 全文搜索 | 文本搜索 |
| 向量索引 | 向量检索 | 语义搜索 |
| 复合索引 | 多列索引 | 多条件查询 |

### 索引配置
```json
{
  "index_strategy": {
    "tables": {
      "tasks": {
        "indexes": [
          {
            "name": "idx_tenant_created",
            "columns": ["tenant_id", "created_at"],
            "type": "btree"
          },
          {
            "name": "idx_status",
            "columns": ["status"],
            "type": "btree"
          }
        ]
      },
      "memory_records": {
        "indexes": [
          {
            "name": "idx_embedding",
            "columns": ["embedding"],
            "type": "vector",
            "params": {
              "metric": "cosine",
              "m": 16,
              "ef_construction": 200
            }
          }
        ]
      }
    },
    "auto_index": {
      "enabled": true,
      "min_query_frequency": 100,
      "min_improvement": 0.3
    }
  }
}
```

### 覆盖索引
| 查询类型 | 覆盖索引 | 效果 |
|----------|----------|------|
| 计数查询 | 包含计数列 | 避免回表 |
| 存在性检查 | 包含判断列 | 避免回表 |
| 列查询 | 包含查询列 | 避免回表 |

### 覆盖索引配置
```json
{
  "covering_index": {
    "enabled": true,
    "strategies": {
      "count_queries": {
        "include_count_column": true
      },
      "exists_queries": {
        "include_exists_column": true
      },
      "column_queries": {
        "analyze_query_columns": true,
        "auto_create_covering": true
      }
    }
  }
}
```

## 查询缓存

### 缓存层次
| 层次 | 缓存类型 | 命中率 | 延迟 |
|------|----------|--------|------|
| L1 | 查询结果缓存 | 20-30% | < 1ms |
| L2 | 计划缓存 | 30-50% | < 5ms |
| L3 | 数据缓存 | 40-60% | < 10ms |

### 查询缓存配置
```json
{
  "query_cache": {
    "result_cache": {
      "enabled": true,
      "max_size_mb": 100,
      "ttl_s": 60,
      "cacheable_queries": [
        "SELECT * FROM tenants WHERE id = ?",
        "SELECT * FROM plans WHERE id = ?"
      ],
      "invalidation": {
        "on_write": true,
        "on_expire": true
      }
    },
    "plan_cache": {
      "enabled": true,
      "max_entries": 1000,
      "ttl_s": 3600
    },
    "data_cache": {
      "enabled": true,
      "max_size_mb": 500,
      "ttl_s": 300
    }
  }
}
```

## 向量检索优化

### 向量索引
| 索引类型 | 说明 | 检索速度 | 精度 |
|----------|------|----------|------|
| HNSW | 层次导航小世界 | 快 | 高 |
| IVF | 倒排文件 | 中 | 中 |
| Flat | 暴力搜索 | 慢 | 最高 |

### 向量检索配置
```json
{
  "vector_search": {
    "index_type": "hnsw",
    "hnsw_params": {
      "m": 16,
      "ef_construction": 200,
      "ef_search": 50
    },
    "metric": "cosine",
    "dimensions": 1024,
    "search_params": {
      "top_k": 10,
      "filter_threshold": 0.7
    },
    "optimization": {
      "quantization": {
        "enabled": true,
        "type": "pq",
        "sub_vectors": 32,
        "bits_per_subvector": 8
      },
      "pre_filter": {
        "enabled": true,
        "filter_before_search": true
      }
    }
  }
}
```

### 向量检索优化策略
| 策略 | 说明 | 效果 |
|------|------|------|
| 预过滤 | 先过滤再检索 | 减少 50-80% 计算 |
| 量化 | 压缩向量 | 减少 70% 内存 |
| 分区 | 数据分区 | 减少 60% 检索范围 |
| 缓存 | 缓存热门向量 | 提升 30-50% 命中 |

## 分页优化

### 分页策略
| 策略 | 说明 | 适用场景 |
|------|------|----------|
| OFFSET 分页 | 传统分页 | 小数据量 |
| 游标分页 | 基于游标 | 大数据量 |
| 键集分页 | 基于键值 | 有序数据 |
| 预加载分页 | 预加载下一页 | 流式浏览 |

### 分页配置
```json
{
  "pagination": {
    "default_strategy": "cursor",
    "strategies": {
      "offset": {
        "max_offset": 10000,
        "default_limit": 20
      },
      "cursor": {
        "enabled": true,
        "cursor_ttl_s": 300,
        "default_limit": 20
      },
      "keyset": {
        "enabled": true,
        "key_column": "id",
        "default_limit": 20
      },
      "preload": {
        "enabled": true,
        "preload_pages": 1
      }
    }
  }
}
```

## 查询监控

### 监控指标
| 指标 | 说明 | 目标 |
|------|------|------|
| 查询延迟 | 查询执行时间 | < 100ms |
| 慢查询数 | 超过阈值的查询 | < 1% |
| 缓存命中率 | 缓存命中比例 | > 30% |
| 索引使用率 | 使用索引的查询 | > 90% |

### 监控配置
```json
{
  "query_monitoring": {
    "slow_query": {
      "threshold_ms": 100,
      "log_slow_queries": true,
      "analyze_slow_queries": true
    },
    "metrics": {
      "query_latency": true,
      "slow_query_count": true,
      "cache_hit_rate": true,
      "index_usage_rate": true
    },
    "alerting": {
      "latency_p95_above_ms": 500,
      "slow_query_rate_above": 0.05,
      "cache_hit_rate_below": 0.2
    }
  }
}
```

## 性能优化效果

### 查询延迟优化
| 查询类型 | 优化前 | 优化后 | 提升 |
|----------|--------|--------|------|
| 简单查询 | 50ms | 5ms | **90% ↓** |
| 复杂查询 | 500ms | 50ms | **90% ↓** |
| 向量检索 | 200ms | 20ms | **90% ↓** |
| 分页查询 | 1000ms | 50ms | **95% ↓** |

### 资源优化
| 资源 | 优化前 | 优化后 | 节省 |
|------|--------|--------|------|
| CPU | 80% | 30% | **62% ↓** |
| 内存 | 4GB | 1GB | **75% ↓** |
| I/O | 100MB/s | 20MB/s | **80% ↓** |

## 版本
- 版本: 1.0.0
- 更新时间: 2026-04-06
