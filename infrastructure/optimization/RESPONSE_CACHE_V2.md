# RESPONSE_CACHE_V2.md - 响应缓存深度策略

## 目的
深度优化响应缓存，最大化缓存命中率，降低重复计算成本。

## 适用范围
所有模型响应、工具执行结果、常用模板响应。

## 缓存层次架构

```
┌─────────────────────────────────────────────────────────────┐
│                    缓存层次架构                              │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   L1 缓存      │    │   L2 缓存      │    │   L3 缓存      │
│  (内存缓存)    │    │  (本地缓存)    │    │  (分布式缓存)  │
│  热点数据      │    │  常用数据      │    │  共享数据      │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ TTL: 5 分钟    │    │ TTL: 1 小时    │    │ TTL: 24 小时   │
│ 命中率: 30%    │    │ 命中率: 20%    │    │ 命中率: 10%    │
└───────────────┘    └───────────────┘    └───────────────┘
```

## 缓存类型

### 精确缓存 (Exact Cache)
| 配置项 | 说明 | 值 |
|--------|------|-----|
| 匹配方式 | 完全匹配 | Hash 精确匹配 |
| TTL | 缓存时间 | 24 小时 |
| 容量 | 最大条目 | 10000 |
| 命中率 | 预期命中率 | 10-20% |

### 语义缓存 (Semantic Cache)
| 配置项 | 说明 | 值 |
|--------|------|-----|
| 匹配方式 | 语义相似 | 向量相似度匹配 |
| 相似度阈值 | 匹配阈值 | 0.95 |
| TTL | 缓存时间 | 12 小时 |
| 容量 | 最大条目 | 5000 |
| 命中率 | 预期命中率 | 20-40% |

### 模板缓存 (Template Cache)
| 配置项 | 说明 | 值 |
|--------|------|-----|
| 匹配方式 | 模板匹配 | 模板 ID 匹配 |
| TTL | 缓存时间 | 7 天 |
| 容量 | 最大条目 | 1000 |
| 命中率 | 预期命中率 | 30-50% |

## 缓存配置

### 精确缓存配置
```json
{
  "exact_cache": {
    "enabled": true,
    "storage": "distributed",
    "ttl_seconds": 86400,
    "max_entries": 10000,
    "max_entry_size_kb": 100,
    "eviction_policy": "lru",
    "key_generation": {
      "method": "hash",
      "include": ["model", "messages", "temperature", "max_tokens"],
      "exclude": ["request_id", "timestamp"]
    }
  }
}
```

### 语义缓存配置
```json
{
  "semantic_cache": {
    "enabled": true,
    "storage": "vector_db",
    "ttl_seconds": 43200,
    "max_entries": 5000,
    "similarity_threshold": 0.95,
    "embedding_model": "small-embedding",
    "index_type": "hnsw",
    "query_params": {
      "ef_search": 50,
      "max_results": 5
    }
  }
}
```

### 模板缓存配置
```json
{
  "template_cache": {
    "enabled": true,
    "storage": "local",
    "ttl_seconds": 604800,
    "templates": {
      "greeting": {
        "pattern": "^(你好|hi|hello|您好)",
        "response": "你好！我是小艺 Claw，有什么可以帮你的？"
      },
      "help": {
        "pattern": "^(帮助|help|怎么用|使用说明)",
        "response": "[帮助内容模板]"
      },
      "error_generic": {
        "pattern": "error:generic",
        "response": "抱歉，处理时出现问题，请稍后重试。"
      }
    }
  }
}
```

## 缓存键生成

### 精确缓存键
```json
{
  "cache_key_generation": {
    "method": "hash",
    "algorithm": "sha256",
    "components": [
      "model_id",
      "system_prompt_hash",
      "user_message_hash",
      "tool_definitions_hash",
      "parameters_hash"
    ],
    "normalization": {
      "lowercase": true,
      "trim_whitespace": true,
      "normalize_unicode": true
    }
  }
}
```

### 语义缓存键
```json
{
  "semantic_key_generation": {
    "method": "embedding",
    "embedding_input": "user_message",
    "embedding_model": "small-embedding",
    "dimensions": 384,
    "normalization": {
      "remove_stopwords": true,
      "lemmatize": true
    }
  }
}
```

## 缓存查找流程

### 查找顺序
```
1. L1 内存缓存查找
   ↓ (未命中)
2. L2 本地缓存查找
   ↓ (未命中)
3. L3 分布式缓存查找
   ↓ (未命中)
4. 精确缓存查找
   ↓ (未命中)
5. 语义缓存查找
   ↓ (未命中)
6. 模板缓存查找
   ↓ (未命中)
7. 执行请求
   ↓
8. 写入缓存
```

### 查找配置
```json
{
  "cache_lookup": {
    "order": ["memory", "local", "distributed", "exact", "semantic", "template"],
    "parallel_lookup": {
      "enabled": true,
      "parallel_layers": ["exact", "semantic"]
    },
    "timeout_ms": 100,
    "fallback_on_error": true
  }
}
```

## 缓存写入策略

### 写入条件
| 条件 | 说明 | 写入 |
|------|------|------|
| 响应成功 | 请求成功完成 | 是 |
| 响应失败 | 请求失败 | 否 |
| 响应过长 | 超过大小限制 | 否 |
| 敏感内容 | 包含敏感信息 | 否 |
| 用户禁止 | 用户禁止缓存 | 否 |

### 写入配置
```json
{
  "cache_write": {
    "conditions": {
      "success_only": true,
      "max_response_size_kb": 100,
      "exclude_sensitive": true,
      "respect_no_cache_header": true
    },
    "write_through": {
      "enabled": true,
      "layers": ["memory", "local", "distributed"]
    },
    "async_write": {
      "enabled": true,
      "queue_size": 1000
    }
  }
}
```

## 缓存失效策略

### 主动失效
| 触发条件 | 失效范围 | 说明 |
|----------|----------|------|
| 模型更新 | 相关模型缓存 | 模型版本变更 |
| 提示词更新 | 相关提示词缓存 | 系统提示词变更 |
| 工具更新 | 相关工具缓存 | 工具定义变更 |
| 用户数据更新 | 用户相关缓存 | 用户数据变更 |

### 被动失效
| 策略 | 说明 | 配置 |
|------|------|------|
| TTL 过期 | 时间过期 | 按缓存类型 |
| LRU 淘汰 | 最近最少使用 | 容量满时 |
| LFU 淘汰 | 最少频率使用 | 容量满时 |

### 失效配置
```json
{
  "cache_invalidation": {
    "active": {
      "on_model_update": true,
      "on_prompt_update": true,
      "on_tool_update": true,
      "on_user_data_update": true
    },
    "passive": {
      "eviction_policy": "lru",
      "eviction_batch_size": 100
    },
    "cascade_invalidation": {
      "enabled": true,
      "propagate_to_layers": ["memory", "local", "distributed"]
    }
  }
}
```

## 缓存预热

### 预热策略
| 策略 | 说明 | 触发 |
|------|------|------|
| 启动预热 | 服务启动时预热 | 服务启动 |
| 定时预热 | 定期预热热点 | 定时任务 |
| 预测预热 | 预测性预热 | 使用模式分析 |

### 预热配置
```json
{
  "cache_warmup": {
    "startup_warmup": {
      "enabled": true,
      "preload_templates": true,
      "preload_hot_queries": true,
      "hot_queries_count": 100
    },
    "scheduled_warmup": {
      "enabled": true,
      "interval_hours": 6,
      "refresh_hot_items": true
    },
    "predictive_warmup": {
      "enabled": true,
      "prediction_window_hours": 1,
      "confidence_threshold": 0.8
    }
  }
}
```

## 缓存监控

### 监控指标
| 指标 | 说明 | 目标 |
|------|------|------|
| 总命中率 | 总体命中比例 | > 30% |
| 精确命中率 | 精确缓存命中 | > 15% |
| 语义命中率 | 语义缓存命中 | > 10% |
| 模板命中率 | 模板缓存命中 | > 5% |
| 平均查找时间 | 缓存查找耗时 | < 10ms |
| 缓存容量使用 | 容量使用率 | < 80% |

### 监控配置
```json
{
  "cache_monitoring": {
    "metrics": {
      "hit_rate": true,
      "latency": true,
      "capacity": true,
      "eviction_count": true
    },
    "alerting": {
      "hit_rate_below": 0.2,
      "latency_above_ms": 50,
      "capacity_above": 0.9
    },
    "reporting": {
      "realtime_dashboard": true,
      "hourly_report": true,
      "daily_analysis": true
    }
  }
}
```

## 成本节省估算

### 节省计算
```
成本节省 = 命中请求数 × 单次请求成本 - 缓存系统成本
```

### 预期节省
| 缓存类型 | 命中率 | 单次成本 | 节省比例 |
|----------|--------|----------|----------|
| 精确缓存 | 15% | ¥0.01 | 15% |
| 语义缓存 | 10% | ¥0.01 | 10% |
| 模板缓存 | 5% | ¥0.01 | 5% |
| **总计** | **30%** | - | **30%** |

## 版本
- 版本: 2.0.0
- 更新时间: 2026-04-06
