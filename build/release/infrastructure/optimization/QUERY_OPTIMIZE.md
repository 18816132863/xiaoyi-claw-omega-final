# QUERY_OPTIMIZE.md - 查询优化策略

## 目的
定义查询优化规则、索引策略和性能基准。

## 适用范围
所有数据查询操作，包括数据库查询、缓存查询、文件查询。

## 查询分类

| 类型 | 特点 | 优化重点 | 性能目标 |
|------|------|----------|----------|
| 点查 | 单条记录 | 索引覆盖 | <10ms |
| 范围查 | 多条记录 | 索引优化 | <100ms |
| 聚合查 | 统计计算 | 预计算 | <500ms |
| 全文查 | 文本搜索 | 倒排索引 | <200ms |
| 关联查 | 多表关联 | 反范式 | <300ms |

## 索引策略

### 索引类型
| 类型 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| B+树 | 范围查询 | 有序 | 写入开销 |
| 哈希 | 等值查询 | 快速 | 无序 |
| 全文 | 文本搜索 | 支持分词 | 空间大 |
| 复合 | 多条件 | 覆盖索引 | 维护成本 |

### 索引设计原则
1. **最左前缀**: 复合索引按查询顺序设计
2. **选择性高**: 优先索引区分度高的列
3. **覆盖索引**: 索引包含查询所需字段
4. **适度索引**: 避免过多索引影响写入

### 索引维护
```yaml
index_maintenance:
  analyze_frequency: daily
  rebuild_threshold:
    fragmentation: 30%
    size_change: 50%
  monitor_metrics:
    - index_usage_rate
    - index_size
    - scan_rows
```

## 查询优化规则

### 规则列表
| 规则 | 说明 | 示例 |
|------|------|------|
| 避免全表扫描 | 使用索引 | WHERE indexed_col = value |
| 避免SELECT * | 指定字段 | SELECT id, name FROM ... |
| 避免函数索引列 | 保持索引有效 | WHERE create_time > '2024-01-01' |
| 避免隐式转换 | 类型匹配 | WHERE id = '123' → id = 123 |
| 分页优化 | 使用游标 | WHERE id > last_id LIMIT 100 |

### 慢查询处理
```yaml
slow_query:
  threshold: 1000ms
  log: true
  analyze: true
  actions:
    - alert
    - suggest_index
    - auto_optimize
```

## 缓存策略

### 查询缓存
| 场景 | 缓存策略 | TTL | 说明 |
|------|----------|-----|------|
| 热点数据 | 主动缓存 | 5m | 预加载 |
| 历史数据 | 被动缓存 | 1h | 按需加载 |
| 统计数据 | 定时刷新 | 10m | 定时更新 |
| 用户数据 | 变更失效 | 30m | 主动失效 |

### 缓存键设计
```
query:{hash(sql)}:{version}
```

## 性能基准

### 基准指标
| 操作 | P50 | P95 | P99 | 最大 |
|------|-----|-----|-----|------|
| 点查 | 5ms | 20ms | 50ms | 100ms |
| 范围查 | 20ms | 100ms | 300ms | 500ms |
| 聚合查 | 100ms | 300ms | 500ms | 1s |
| 关联查 | 50ms | 200ms | 400ms | 800ms |

### 性能测试
```yaml
performance_test:
  frequency: weekly
  scenarios:
    - name: point_query
      qps: 10000
      duration: 5m
    - name: range_query
      qps: 1000
      duration: 5m
  thresholds:
    error_rate: 0.1%
    p99_latency: 500ms
```

## 监控指标

| 指标 | 计算方式 | 告警阈值 |
|------|----------|----------|
| 查询延迟 | avg/p99 | 超基准50% |
| 慢查询率 | slow/total | >1% |
| 索引命中率 | hit/total | <80% |
| 缓存命中率 | hit/total | <70% |

## 维护方式
- 新增规则: 更新优化规则表
- 调整基准: 更新性能基准表
- 新增索引: 更新索引策略

## 引用文件
- `optimization/CACHE_STRATEGY.md` - 缓存策略
- `optimization/PERFORMANCE_MONITOR.md` - 性能监控
