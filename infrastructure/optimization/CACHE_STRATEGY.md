# CACHE_STRATEGY.md - 缓存策略

## 目的
定义缓存层级、策略和失效机制。

## 适用范围
所有缓存操作，包括内存缓存、文件缓存、分布式缓存。

## 缓存层级

| 层级 | 存储 | 容量 | 延迟 | 用途 |
|------|------|------|------|------|
| L1 | 进程内存 | 100MB | <1ms | 热点数据 |
| L2 | 本地文件 | 1GB | <10ms | 常用数据 |
| L3 | Redis | 10GB | <50ms | 共享数据 |

## 缓存策略

### 缓存模式
| 模式 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| Cache-Aside | 读多写少 | 简单可靠 | 缓存不一致窗口 |
| Write-Through | 写多 | 强一致性 | 写延迟高 |
| Write-Behind | 写密集 | 写性能高 | 可能丢数据 |

### 过期策略
| 策略 | 适用场景 | 配置 |
|------|----------|------|
| TTL | 时效性数据 | expire: 3600s |
| LRU | 容量受限 | max_size: 1000 |
| LFU | 访问不均 | top_k: 100 |

### 预热策略
```yaml
warmup:
  schedule: "0 0 * * *"  # 每日凌晨
  sources:
    - hot_queries
    - user_profiles
    - system_config
```

## 缓存键设计

### 命名规范
```
{namespace}:{type}:{id}:{version}

示例:
- user:profile:123:v1
- session:context:abc:v2
- config:system:global:v1
```

### 键过期时间
| 数据类型 | TTL | 说明 |
|----------|-----|------|
| 用户会话 | 30m | 活跃续期 |
| 用户画像 | 24h | 变更失效 |
| 系统配置 | 1h | 变更失效 |
| 查询结果 | 5m | 短期有效 |

## 失效机制

### 主动失效
```javascript
// 数据变更时主动清除
await cache.delete(`user:profile:${userId}`);
```

### 被动失效
```yaml
# TTL过期自动清除
ttl:
  default: 3600
  max: 86400
```

### 批量失效
```javascript
// 按模式批量清除
await cache.deletePattern('session:*');
```

## 缓存穿透防护

### 空值缓存
```javascript
// 缓存空值防止穿透
if (!data) {
  await cache.set(key, NULL_VALUE, { ttl: 60 });
}
```

### 布隆过滤器
```yaml
bloom_filter:
  enabled: true
  size: 1000000
  hash_functions: 3
```

## 监控指标

| 指标 | 计算方式 | 告警阈值 |
|------|----------|----------|
| 命中率 | hits/(hits+misses) | <80% |
| 平均延迟 | avg(response_time) | >10ms |
| 内存使用 | used/total | >90% |
| 错误率 | errors/total | >1% |

## 维护方式
- 新增缓存: 更新缓存层级表
- 调整策略: 更新策略配置
- 调整TTL: 更新过期时间表

## 引用文件
- `runtime/EXECUTION_POLICY.md` - 执行策略
- `observability/METRICS.md` - 监控指标
