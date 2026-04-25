# THROTTLE_STRATEGY.md - 限流策略

## 目的
定义限流规则、算法选择和限流效果监控。

## 适用范围
所有需要流量控制的场景，包括API访问、资源使用、任务执行。

## 限流维度

| 维度 | 说明 | 配置示例 |
|------|------|----------|
| 全局 | 系统总流量 | 10000 QPS |
| 用户 | 单用户流量 | 100 QPS/user |
| IP | 单IP流量 | 500 QPS/ip |
| 接口 | 单接口流量 | 1000 QPS/api |
| 租户 | 单租户流量 | 5000 QPS/tenant |

## 限流算法

| 算法 | 特点 | 适用场景 | 配置 |
|------|------|----------|------|
| 固定窗口 | 简单高效 | 流量均匀 | 100/min |
| 滑动窗口 | 平滑精确 | 流量波动 | 100/min |
| 令牌桶 | 允许突发 | API限流 | 100/s, burst=20 |
| 漏桶 | 恒定速率 | 流量整形 | 100/s |
| 自适应 | 动态调整 | 系统保护 | 基于负载 |

## 限流配置

### 全局限流
```yaml
global_throttle:
  algorithm: token_bucket
  qps: 10000
  burst: 2000
  concurrent: 1000
```

### 用户限流
```yaml
user_throttle:
  algorithm: sliding_window
  limits:
    default:
      qps: 100
      qpm: 6000
      qpd: 100000
    premium:
      qps: 500
      qpm: 30000
      qpd: 500000
    enterprise:
      qps: 2000
      qpm: 120000
      qpd: 2000000
```

### 接口限流
```yaml
api_throttle:
  /api/chat:
    qps: 100
    concurrent: 50
  /api/search:
    qps: 500
    concurrent: 200
  /api/upload:
    qps: 20
    concurrent: 10
```

## 限流响应

### 响应策略
| 策略 | 说明 | 响应码 | 响应内容 |
|------|------|--------|----------|
| 拒绝 | 直接拒绝 | 429 | 限流提示 |
| 排队 | 等待处理 | 202 | 预计等待时间 |
| 降级 | 返回降级 | 200 | 缓存/默认值 |
| 延迟 | 延迟处理 | 200 | 正常响应 |

### 响应示例
```json
{
  "code": 429,
  "message": "请求过于频繁，请稍后重试",
  "retry_after": 60,
  "limit": 100,
  "remaining": 0,
  "reset": 1704067200
}
```

## 限流实现

### 令牌桶实现
```javascript
class TokenBucket {
  constructor(rate, burst) {
    this.rate = rate;        // 令牌生成速率
    this.burst = burst;      // 桶容量
    this.tokens = burst;     // 当前令牌数
    this.lastTime = Date.now();
  }
  
  acquire(tokens = 1) {
    const now = Date.now();
    const elapsed = (now - this.lastTime) / 1000;
    this.tokens = Math.min(
      this.burst,
      this.tokens + elapsed * this.rate
    );
    this.lastTime = now;
    
    if (this.tokens >= tokens) {
      this.tokens -= tokens;
      return true;
    }
    return false;
  }
}
```

### 滑动窗口实现
```javascript
class SlidingWindow {
  constructor(limit, windowMs) {
    this.limit = limit;
    this.windowMs = windowMs;
    this.requests = [];
  }
  
  isAllowed() {
    const now = Date.now();
    const windowStart = now - this.windowMs;
    
    // 清理过期请求
    this.requests = this.requests.filter(t => t > windowStart);
    
    if (this.requests.length < this.limit) {
      this.requests.push(now);
      return true;
    }
    return false;
  }
}
```

## 自适应限流

### 系统保护
```yaml
adaptive_throttle:
  enabled: true
  metrics:
    - cpu_usage
    - memory_usage
    - response_time
  rules:
    - condition: cpu_usage > 80%
      action: reduce_limit 20%
    - condition: response_time > 2s
      action: reduce_limit 30%
    - condition: memory_usage > 90%
      action: reduce_limit 50%
```

### 动态调整
```yaml
dynamic_adjustment:
  enabled: true
  min_limit: 100
  max_limit: 10000
  adjustment_interval: 10s
  increase_step: 10%
  decrease_step: 20%
```

## 监控指标

| 指标 | 计算方式 | 告警阈值 |
|------|----------|----------|
| 限流触发率 | throttled/total | >5% |
| 平均等待时间 | avg(wait_time) | >1s |
| 队列长度 | queue_size | >100 |
| 限流影响用户 | affected_users | >100 |

## 限流告警

| 事件 | 告警级别 | 通知方式 |
|------|----------|----------|
| 限流触发 | P2 | IM |
| 限流率超阈值 | P1 | 短信+IM |
| 限流配置变更 | P3 | 日志 |
| 限流失效 | P0 | 电话+短信 |

## 维护方式
- 新增维度: 更新限流维度表
- 调整配置: 更新限流配置
- 新增算法: 更新限流算法表

## 引用文件
- `optimization/DEGRADATION_STRATEGY.md` - 降级策略
- `optimization/CIRCUIT_BREAKER.md` - 熔断策略
