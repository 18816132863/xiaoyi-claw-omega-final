# COST_METRICS.md - 成本观测指标

## 目的
定义成本观测指标，确保成本优化有数据依据。

## 适用范围
所有系统运行的成本监控。

## 核心成本指标

### 单任务成本
| 指标 | 计算方式 | 说明 |
|------|----------|------|
| per_task_token_cost | 总Token / 任务数 | 单任务Token成本 |
| per_task_time_cost | 总时间 / 任务数 | 单任务时间成本 |
| per_task_step_cost | 总步骤 / 任务数 | 单任务步骤成本 |

### 成功率成本
| 指标 | 计算方式 | 说明 |
|------|----------|------|
| per_success_cost | 总成本 / 成功数 | 每次成功成本 |
| per_failure_cost | 失败成本 / 失败数 | 每次失败成本 |
| success_cost_ratio | 成功成本 / 总成本 | 成功成本占比 |

### 工具成本
| 指标 | 计算方式 | 说明 |
|------|----------|------|
| tool_call_cost | 工具调用成本 | 工具调用消耗 |
| tool_retry_cost | 重试消耗成本 | 重试额外成本 |
| tool_timeout_cost | 超时消耗成本 | 超时浪费成本 |

### 校验成本
| 指标 | 计算方式 | 说明 |
|------|----------|------|
| validation_cost | 校验消耗成本 | 校验过程成本 |
| fact_check_cost | 事实校验成本 | 事实校验消耗 |
| security_check_cost | 安全检查成本 | 安全检查消耗 |

### 重试成本
| 指标 | 计算方式 | 说明 |
|------|----------|------|
| retry_token_cost | 重试Token消耗 | 重试额外Token |
| retry_time_cost | 重试时间消耗 | 重试额外时间 |
| retry_rate | 重试次数 / 总调用 | 重试率 |

### 缓存节省
| 指标 | 计算方式 | 说明 |
|------|----------|------|
| cache_hit_savings | 命中节省成本 | 缓存命中节省 |
| cache_hit_rate | 命中次数 / 总请求 | 缓存命中率 |
| cache_efficiency | 节省成本 / 缓存成本 | 缓存效率 |

## 成本计算公式

### 总成本
```
total_cost = token_cost + tool_cost + validation_cost + retry_cost - cache_savings
```

### Token成本
```
token_cost = (input_tokens × input_rate) + (output_tokens × output_rate)
```

### 工具成本
```
tool_cost = Σ(tool_calls × tool_cost_per_call)
```

### 校验成本
```
validation_cost = fact_check_cost + security_check_cost + format_check_cost
```

### 重试成本
```
retry_cost = Σ(retries × retry_cost_per_retry)
```

### 缓存节省
```
cache_savings = cache_hits × cost_per_query
```

## 成本指标与观测系统联动

### 写入 observability/METRICS.md
| 指标 | METRICS.md对应 |
|------|----------------|
| per_task_token_cost | avgTokenCost |
| per_success_cost | costPerSuccess |
| cache_hit_rate | cacheHitRate |
| retry_rate | retryRate |

### 告警阈值
| 指标 | 警告阈值 | 错误阈值 |
|------|----------|----------|
| per_task_token_cost | > 5000 | > 10000 |
| per_success_cost | > 0.1 | > 0.2 |
| retry_rate | > 10% | > 20% |
| cache_hit_rate | < 50% | < 30% |

## 成本指标与发布决策联动

### 发布前检查
| 指标 | 要求 |
|------|------|
| 成本变化 | 不超过基线20% |
| 成功率成本 | 不恶化 |
| 重试率 | 不增加 |

### 发布后监控
| 指标 | 监控周期 |
|------|----------|
| 实时成本 | 实时 |
| 小时成本 | 每小时 |
| 日成本 | 每天 |

## 成本报告格式

```json
{
  "report_id": "cost_20260406_001",
  "timestamp": "2026-04-06T10:32:00+08:00",
  "period": "hourly",
  "metrics": {
    "per_task_token_cost": 3500,
    "per_success_cost": 0.05,
    "per_failure_cost": 0.15,
    "tool_call_cost": 0.02,
    "validation_cost": 0.01,
    "retry_cost": 0.005,
    "cache_hit_savings": 0.03,
    "cache_hit_rate": 0.65,
    "retry_rate": 0.05
  },
  "total_cost": 0.08,
  "baseline": 0.07,
  "change": "+14%"
}
```

## 异常处理

| 异常 | 处理 |
|------|------|
| 成本激增 | 触发告警 |
| 成本超限 | 触发降级 |
| 统计失败 | 使用估算值 |

## 维护方式
- 新增成本指标: 添加到指标表
- 调整计算公式: 更新计算公式
- 调整告警阈值: 更新阈值表

## 引用文件
- `optimization/BUDGET_POLICY.md` - 预算策略
- `observability/METRICS.md` - 系统指标
- `evaluation/REGRESSION_GATE.json` - 回归门禁
