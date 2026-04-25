# CONCURRENCY_CONTROL.md - 并发控制策略

## 目的
定义并发控制机制、锁策略和资源争用处理。

## 适用范围
所有并发操作，包括数据访问、资源分配、任务执行。

## 并发控制机制

| 机制 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| 悲观锁 | 写冲突多 | 强一致 | 性能低 |
| 乐观锁 | 读多写少 | 高性能 | 冲突重试 |
| MVCC | 读多写少 | 无锁读 | 版本管理 |
| 原子操作 | 简单操作 | 高效 | 功能有限 |

## 锁策略

### 锁类型
| 类型 | 范围 | 粒度 | 用途 |
|------|------|------|------|
| 共享锁 | 读 | 行/表 | 并发读 |
| 排他锁 | 写 | 行/表 | 独占写 |
| 意向锁 | 事务 | 表 | 锁升级 |
| 间隙锁 | 范围 | 区间 | 防幻读 |

### 锁超时
```yaml
lock_timeout:
  default: 30s
  critical: 60s
  background: 10s
  retry:
    max: 3
    backoff: exponential
```

### 死锁处理
```yaml
deadlock:
  detection: enabled
  interval: 5s
  victim: youngest_transaction
  retry: true
  max_retry: 3
```

## 限流策略

### 限流算法
| 算法 | 特点 | 适用场景 | 配置 |
|------|------|----------|------|
| 固定窗口 | 简单 | 流量均匀 | 100/min |
| 滑动窗口 | 平滑 | 流量波动 | 100/min |
| 令牌桶 | 允许突发 | API限流 | 100/s, burst=20 |
| 漏桶 | 恒定速率 | 流量整形 | 100/s |

### 限流配置
```yaml
rate_limit:
  global:
    qps: 10000
    concurrent: 1000
  per_user:
    qps: 100
    concurrent: 10
  per_ip:
    qps: 500
    concurrent: 50
```

## 并发控制实现

### 数据库并发
```sql
-- 乐观锁
UPDATE users 
SET name = 'new', version = version + 1 
WHERE id = 1 AND version = 10;

-- 悲观锁
SELECT * FROM users WHERE id = 1 FOR UPDATE;
```

### 分布式锁
```javascript
// Redis 分布式锁
const lock = await redis.lock('resource:123', {
  ttl: 30000,
  retry: 3,
  delay: 100
});
try {
  await doWork();
} finally {
  await lock.unlock();
}
```

### 并发队列
```yaml
concurrent_queue:
  max_concurrency: 10
  queue_size: 1000
  timeout: 30s
  rejection_policy: caller_runs
```

## 资源争用处理

### 争用检测
| 指标 | 阈值 | 处理 |
|------|------|------|
| 锁等待时间 | >1s | 告警 |
| 锁冲突率 | >5% | 优化 |
| 死锁次数 | >0 | 告警 |
| 队列积压 | >100 | 扩容 |

### 争用优化
| 措施 | 说明 | 效果 |
|------|------|------|
| 减小锁粒度 | 行锁代替表锁 | 减少冲突 |
| 缩短持锁时间 | 事务精简 | 减少等待 |
| 读写分离 | 读无锁 | 提升并发 |
| 分片 | 数据分片 | 减少争用 |

## 监控指标

| 指标 | 计算方式 | 告警阈值 |
|------|----------|----------|
| 并发数 | current_concurrent | >限制80% |
| 等待时间 | avg(wait_time) | >1s |
| 冲突率 | conflicts/total | >5% |
| 死锁率 | deadlocks/total | >0 |

## 维护方式
- 新增机制: 更新控制机制表
- 调整策略: 更新锁策略配置
- 优化争用: 更新优化措施

## 引用文件
- `runtime/EXECUTION_POLICY.md` - 执行策略
- `optimization/RESOURCE_POOL.md` - 资源池管理
