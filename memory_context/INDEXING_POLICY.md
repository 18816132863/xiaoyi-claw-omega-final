# 索引策略 - V1.0.0

## 索引类型

| 类型 | 用途 | 更新频率 |
|------|------|----------|
| 全量索引 | 完整数据 | 每日 |
| 增量索引 | 新增数据 | 实时 |
| 热点索引 | 高频访问 | 每小时 |

## 索引流程

```
数据写入
    ↓
增量索引 (实时)
    ↓
热点索引 (每小时)
    ↓
全量索引 (每日)
```

## 索引规则

### 1. 自动索引
- 新创建的日记文件
- 更新的 MEMORY.md
- 用户标记的重要内容

### 2. 手动索引
```bash
# 全量重建
python -c "from memory_context.indexer import rebuild_all; rebuild_all()"

# 增量更新
python -c "from memory_context.indexer import update_incremental; update_incremental()"
```

## 索引字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识 |
| content | text | 原始内容 |
| embedding | vector | 4096维向量 |
| timestamp | datetime | 创建时间 |
| source | string | 来源文件 |
| category | string | 内容分类 |
| importance | float | 重要性分数 |

## 索引优化

### 1. 分片策略
```
memory_index/
├── shard_0/    # 2026-01 ~ 2026-03
├── shard_1/    # 2026-04 ~ 2026-06
└── shard_2/    # 2026-07 ~ 2026-09
```

### 2. 压缩策略
- 超过30天的索引压缩存储
- 低重要性内容降级存储

## 索引监控

| 指标 | 阈值 | 告警 |
|------|------|------|
| 索引大小 | > 1GB | 警告 |
| 索引延迟 | > 5s | 警告 |
| 索引错误率 | > 1% | 严重 |
