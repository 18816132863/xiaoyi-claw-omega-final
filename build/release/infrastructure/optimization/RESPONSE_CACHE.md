# RESPONSE_CACHE.md - 响应缓存策略

## 目的
定义 LLM 响应缓存策略，减少重复计算、降低延迟和成本。

## 适用范围
所有 LLM 调用的响应缓存。

## 缓存原则

### 核心原则
1. **确定性缓存**: 相同输入必产生相同输出
2. **时效性控制**: 缓存有时效限制
3. **失效机制**: 条件变化时主动失效
4. **透明性**: 缓存命中不影响用户体验

## 缓存键生成

### 键组成
```yaml
cache_key_components:
  - intent_hash        # 意图哈希 (权重最高)
  - context_hash       # 上下文哈希
  - skill_id           # 技能ID
  - model_id           # 模型ID
  - parameters_hash    # 参数哈希
```

### 键生成规则
```yaml
key_generation:
  algorithm: sha256
  normalization:
    - lowercase        # 小写化
    - trim_whitespace  # 去空格
    - sort_params      # 参数排序
  collision_handling: version_suffix
```

## 缓存层级

### 多级缓存
| 层级 | 存储 | TTL | 命中率目标 | 说明 |
|------|------|-----|------------|------|
| L1 | 内存 | 5分钟 | 30% | 热点缓存 |
| L2 | 内存 | 1小时 | 50% | 会话缓存 |
| L3 | 磁盘 | 1天 | 20% | 持久缓存 |

### 缓存配置
```yaml
cache_config:
  L1:
    max_size: 10MB
    max_items: 100
    ttl: 300
    eviction: LRU
  
  L2:
    max_size: 50MB
    max_items: 500
    ttl: 3600
    eviction: LRU
  
  L3:
    max_size: 500MB
    max_items: 5000
    ttl: 86400
    eviction: LFU
```

## 缓存策略

### 可缓存响应
| 类型 | 可缓存 | TTL | 说明 |
|------|--------|-----|------|
| 事实问答 | ✅ | 1天 | 事实不变 |
| 知识解释 | ✅ | 1天 | 知识稳定 |
| 文档摘要 | ✅ | 1小时 | 文档不变 |
| 代码生成 | ✅ | 1小时 | 需求不变 |
| 创意内容 | ❌ | - | 每次不同 |
| 实时数据 | ❌ | - | 数据变化 |

### 缓存条件
```yaml
cache_conditions:
  must_match:
    - deterministic_output: true
    - no_time_sensitivity: true
    - no_user_specific: false  # 用户特定也可缓存
  
  should_cache:
    - request_frequency: high
    - computation_cost: high
    - response_stability: high
```

## 缓存失效

### 主动失效
| 触发条件 | 失效范围 |
|----------|----------|
| 知识更新 | 相关主题缓存 |
| 技能更新 | 相关技能缓存 |
| 用户纠正 | 用户相关缓存 |
| 时间过期 | 过期缓存 |

### 失效策略
```yaml
invalidation:
  on_knowledge_update:
    scope: topic_related
    action: invalidate
  
  on_user_feedback:
    scope: user_specific
    action: invalidate
  
  on_time_expire:
    scope: expired
    action: remove
  
  on_memory_pressure:
    scope: LRU
    action: evict
```

## 缓存预热

### 预热策略
| 策略 | 说明 | 触发 |
|------|------|------|
| 热点预热 | 预加载热点查询 | 定时 |
| 会话预热 | 预加载会话相关 | 会话开始 |
| 用户预热 | 预加载用户常用 | 用户登录 |

### 预热配置
```yaml
warmup:
  schedule: "0 */6 * * *"  # 每6小时
  max_items: 50
  sources:
    - popular_queries
    - user_frequent
    - recent_sessions
```

## 缓存监控

### 监控指标
| 指标 | 说明 | 目标 | 告警阈值 |
|------|------|------|----------|
| 命中率 | 命中/总请求 | > 50% | < 30% |
| L1命中率 | L1命中/总命中 | > 30% | < 20% |
| 平均延迟 | 缓存响应延迟 | < 10ms | > 50ms |
| 内存使用 | 缓存内存占用 | < 50MB | > 80MB |

### 监控报告
```json
{
  "reportId": "cache_report_001",
  "timestamp": "2026-04-06T10:32:00+08:00",
  "summary": {
    "totalRequests": 1000,
    "hits": 600,
    "misses": 400,
    "hitRate": 0.6
  },
  "byLevel": {
    "L1": {"hits": 200, "hitRate": 0.2},
    "L2": {"hits": 300, "hitRate": 0.3},
    "L3": {"hits": 100, "hitRate": 0.1}
  },
  "performance": {
    "avgHitLatency": 5,
    "avgMissLatency": 2000,
    "savedLatency": 790000
  }
}
```

## 成本节省

### 节省计算
```yaml
cost_savings:
  per_hit:
    token_saved: 500      # 平均节省Token
    latency_saved: 2000   # 平均节省延迟(ms)
  
  estimation:
    daily_hits: 10000
    daily_token_saved: 5000000
    daily_cost_saved: 50  # USD
```

## 异常处理

| 异常 | 处理 |
|------|------|
| 缓存读取失败 | 回源计算 |
| 缓存写入失败 | 记录日志，继续 |
| 内存不足 | 清理 L3 缓存 |
| 键冲突 | 版本后缀 |

## 维护方式
- 调整TTL: 修改缓存配置
- 调整大小: 更新大小限制
- 新增策略: 添加缓存策略

## 引用文件
- `optimization/CACHE_STRATEGY.md` - 缓存策略
- `optimization/TOKEN_OPTIMIZATION.md` - Token 优化
- `optimization/PERFORMANCE_MONITOR.md` - 性能监控
