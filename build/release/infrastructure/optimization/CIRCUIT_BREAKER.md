# CIRCUIT_BREAKER.md - 熔断策略

## 目的
定义熔断器的状态转换、触发条件和恢复机制。

## 适用范围
所有外部依赖调用，包括API调用、数据库访问、缓存访问。

## 熔断器状态

| 状态 | 行为 | 转换条件 | 说明 |
|------|------|----------|------|
| CLOSED | 正常调用 | 失败率超阈值→OPEN | 初始状态 |
| OPEN | 快速失败 | 超时→HALF_OPEN | 熔断状态 |
| HALF_OPEN | 探测调用 | 成功→CLOSED, 失败→OPEN | 恢复探测 |

## 熔断配置

### 基础配置
```yaml
circuit_breaker:
  enabled: true
  failure_threshold: 5        # 失败次数阈值
  failure_rate_threshold: 50  # 失败率阈值(%)
  slow_call_threshold: 2s     # 慢调用阈值
  slow_call_rate_threshold: 80 # 慢调用率阈值(%)
  wait_duration_in_open: 30s  # OPEN状态等待时间
  permitted_calls_in_half_open: 3 # HALF_OPEN允许调用数
  sliding_window_size: 100    # 滑动窗口大小
  sliding_window_type: count_based
```

### 分服务配置
| 服务 | 失败阈值 | 失败率阈值 | 等待时间 | 慢调用阈值 |
|------|----------|------------|----------|------------|
| AI服务 | 3 | 30% | 60s | 5s |
| 数据库 | 5 | 50% | 30s | 1s |
| 缓存 | 10 | 70% | 10s | 100ms |
| 外部API | 3 | 40% | 60s | 3s |

## 状态转换

### CLOSED → OPEN
```javascript
// 触发条件
if (failureCount >= failureThreshold || 
    failureRate >= failureRateThreshold ||
    slowCallRate >= slowCallRateThreshold) {
  transitionTo(OPEN);
}
```

### OPEN → HALF_OPEN
```javascript
// 触发条件
if (timeSinceOpen >= waitDurationInOpen) {
  transitionTo(HALF_OPEN);
}
```

### HALF_OPEN → CLOSED/OPEN
```javascript
// 触发条件
if (successCount >= successThreshold) {
  transitionTo(CLOSED);
} else if (failureCount >= 1) {
  transitionTo(OPEN);
}
```

## 熔断动作

### 熔断响应
| 场景 | 响应策略 | 响应内容 |
|------|----------|----------|
| API调用 | 降级响应 | 缓存数据/默认值 |
| 数据库 | 读写分离 | 从库读取 |
| 缓存 | 直接访问 | 访问数据库 |
| 消息队列 | 本地缓存 | 先存本地 |

### 熔断通知
```yaml
notification:
  on_open:
    level: P1
    channels: [sms, im]
  on_close:
    level: P2
    channels: [im]
  on_half_open:
    level: P3
    channels: [log]
```

## 监控指标

| 指标 | 计算方式 | 告警阈值 |
|------|----------|----------|
| 熔断次数 | open_count | >3/小时 |
| 熔断时长 | avg(open_duration) | >5分钟 |
| 失败率 | failures/total | >阈值 |
| 慢调用率 | slow_calls/total | >阈值 |

## 熔断器组合

### 级联熔断
```yaml
cascade:
  enabled: true
  order:
    - external_api
    - ai_service
    - database
  propagation_delay: 5s
```

### 并行熔断
```yaml
parallel:
  enabled: true
  services:
    - name: service_a
      weight: 0.5
    - name: service_b
      weight: 0.5
  aggregate_threshold: 0.3
```

## 熔断恢复

### 自动恢复
```yaml
auto_recovery:
  enabled: true
  gradual: true
  steps:
    - traffic: 10%
      duration: 30s
    - traffic: 30%
      duration: 30s
    - traffic: 100%
      duration: 0s
```

### 手动恢复
```yaml
manual_recovery:
  enabled: true
  require_approval: true
  approvers: [admin, ops]
```

## 熔断演练

### 演练场景
| 场景 | 触发方式 | 预期结果 | 频率 |
|------|----------|----------|------|
| API超时 | 模拟延迟 | 熔断+降级 | 月度 |
| 服务不可用 | 停止服务 | 熔断+告警 | 季度 |
| 高失败率 | 模拟错误 | 熔断+恢复 | 月度 |

## 维护方式
- 新增服务: 更新分服务配置表
- 调整阈值: 更新基础配置
- 新增场景: 更新演练场景表

## 引用文件
- `optimization/DEGRADATION_STRATEGY.md` - 降级策略
- `optimization/LOAD_BALANCE.md` - 负载均衡
