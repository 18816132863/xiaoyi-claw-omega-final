# WARMUP_PRELOAD_OPTIMIZATION.md - 预热预加载优化策略

## 目的
优化预热和预加载策略，减少冷启动延迟，提升首次访问性能。

## 适用范围
所有服务启动、模型加载、缓存预热、连接初始化。

## 预热预加载架构

```
┌─────────────────────────────────────────────────────────────┐
│                    预热预加载架构                            │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   服务预热     │    │   模型预热     │    │   缓存预热     │
│  (Service)    │    │  (Model)      │    │  (Cache)      │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ - 连接预热     │    │ - 模型加载     │    │ - 热点数据     │
│ - 资源预热     │    │ - 推理预热     │    │ - 配置缓存     │
│ - 依赖预热     │    │ - 缓存预热     │    │ - 模板缓存     │
└───────────────┘    └───────────────┘    └───────────────┘
```

## 服务预热

### 启动预热流程
```
服务启动
    ↓
核心资源初始化
    ↓
连接池预热
    ↓
依赖服务预热
    ↓
健康检查
    ↓
流量接入
```

### 服务预热配置
```json
{
  "service_warmup": {
    "enabled": true,
    "startup_sequence": [
      {
        "stage": "core_init",
        "components": ["config", "logger", "metrics"],
        "timeout_s": 10
      },
      {
        "stage": "connection_pool",
        "components": ["database", "redis", "http"],
        "timeout_s": 30
      },
      {
        "stage": "dependencies",
        "components": ["model_service", "tool_service"],
        "timeout_s": 60
      },
      {
        "stage": "health_check",
        "components": ["self", "dependencies"],
        "timeout_s": 10
      }
    ],
    "traffic_acceptance": {
      "delay_after_ready_s": 5,
      "gradual_ramp_up": true,
      "ramp_up_duration_s": 30
    }
  }
}
```

### 连接池预热
| 连接类型 | 预热数量 | 预热时机 | 说明 |
|----------|----------|----------|------|
| 数据库 | min_size | 启动时 | 预建立连接 |
| Redis | min_size | 启动时 | 预建立连接 |
| HTTP | 10 | 启动时 | 预建立连接 |
| 模型服务 | 5 | 启动时 | 预建立连接 |

### 连接池预热配置
```json
{
  "connection_warmup": {
    "database": {
      "enabled": true,
      "warmup_connections": 5,
      "validate_on_warmup": true
    },
    "redis": {
      "enabled": true,
      "warmup_connections": 5,
      "ping_on_warmup": true
    },
    "http": {
      "enabled": true,
      "warmup_connections": 10,
      "target_hosts": ["model-service", "tool-service"]
    },
    "model_service": {
      "enabled": true,
      "warmup_connections": 5,
      "test_request": true
    }
  }
}
```

## 模型预热

### 模型加载预热
| 模型类型 | 预热策略 | 预热时间 | 说明 |
|----------|----------|----------|------|
| 小模型 | 启动加载 | 5s | 立即可用 |
| 中模型 | 启动加载 | 15s | 立即可用 |
| 大模型 | 懒加载+预热 | 30s | 按需加载 |
| 特殊模型 | 懒加载 | 按需 | 首次使用加载 |

### 模型预热配置
```json
{
  "model_warmup": {
    "enabled": true,
    "models": {
      "small_model": {
        "load_strategy": "startup",
        "warmup_requests": 5,
        "warmup_timeout_s": 10
      },
      "medium_model": {
        "load_strategy": "startup",
        "warmup_requests": 3,
        "warmup_timeout_s": 20
      },
      "large_model": {
        "load_strategy": "lazy",
        "preload_on_schedule": true,
        "schedule": "0 8 * * *",
        "warmup_requests": 2
      }
    },
    "warmup_requests": {
      "simple_prompt": "Hello",
      "expected_response_length": 10
    }
  }
}
```

### 推理预热
| 预热类型 | 说明 | 效果 |
|----------|------|------|
| 简单推理 | 发送简单请求 | 初始化推理引擎 |
| 批量预热 | 批量发送请求 | 预热并发能力 |
| 渐进预热 | 逐步增加负载 | 平滑预热 |

### 推理预热配置
```json
{
  "inference_warmup": {
    "enabled": true,
    "warmup_requests": [
      {
        "prompt": "Hello",
        "max_tokens": 10
      },
      {
        "prompt": "What is AI?",
        "max_tokens": 50
      }
    ],
    "batch_warmup": {
      "enabled": true,
      "batch_size": 5,
      "interval_s": 1
    },
    "progressive_warmup": {
      "enabled": true,
      "start_qps": 1,
      "target_qps": 10,
      "duration_s": 30
    }
  }
}
```

## 缓存预热

### 热点数据预热
| 数据类型 | 预热策略 | 预热时机 | 说明 |
|----------|----------|----------|------|
| 配置数据 | 全量预热 | 启动时 | 系统配置 |
| 租户数据 | 热点预热 | 启动时 | 活跃租户 |
| 模型数据 | 按需预热 | 启动时 | 常用模型 |
| 模板数据 | 全量预热 | 启动时 | 响应模板 |

### 缓存预热配置
```json
{
  "cache_warmup": {
    "enabled": true,
    "data_types": {
      "config": {
        "strategy": "full",
        "priority": "high",
        "ttl_s": 300
      },
      "tenant": {
        "strategy": "hot",
        "hot_tenant_count": 100,
        "priority": "medium",
        "ttl_s": 60
      },
      "model": {
        "strategy": "on_demand",
        "preload_models": ["small_model", "medium_model"],
        "priority": "medium"
      },
      "template": {
        "strategy": "full",
        "priority": "low",
        "ttl_s": 3600
      }
    },
    "warmup_order": ["config", "template", "tenant", "model"]
  }
}
```

### 查询结果预热
| 查询类型 | 预热策略 | 说明 |
|----------|----------|------|
| 热点查询 | 预热结果 | 高频查询 |
| 模板查询 | 预热结果 | 标准查询 |
| 聚合查询 | 预热结果 | 统计查询 |

### 查询预热配置
```json
{
  "query_warmup": {
    "enabled": true,
    "hot_queries": [
      {
        "query": "SELECT * FROM plans WHERE id = ?",
        "params": ["plan-basic", "plan-professional", "plan-enterprise"]
      },
      {
        "query": "SELECT * FROM features WHERE enabled = true"
      }
    ],
    "template_queries": [
      "tenant_status_check",
      "quota_validation"
    ],
    "aggregate_queries": [
      {
        "query": "daily_usage_stats",
        "schedule": "0 0 * * *"
      }
    ]
  }
}
```

## 定时预热

### 预热计划
| 时间 | 预热内容 | 说明 |
|------|----------|------|
| 00:00 | 日统计预热 | 新一天开始 |
| 06:00 | 早高峰预热 | 工作日开始 |
| 08:00 | 模型预热 | 工作时间 |
| 12:00 | 午高峰预热 | 午间高峰 |
| 18:00 | 晚高峰预热 | 晚间高峰 |

### 定时预热配置
```json
{
  "scheduled_warmup": {
    "enabled": true,
    "schedules": [
      {
        "time": "00:00",
        "tasks": ["daily_stats", "report_cache"],
        "timezone": "Asia/Shanghai"
      },
      {
        "time": "06:00",
        "tasks": ["connection_pool", "hot_tenants"],
        "timezone": "Asia/Shanghai"
      },
      {
        "time": "08:00",
        "tasks": ["model_cache", "template_cache"],
        "timezone": "Asia/Shanghai"
      },
      {
        "time": "12:00",
        "tasks": ["connection_pool", "hot_queries"],
        "timezone": "Asia/Shanghai"
      },
      {
        "time": "18:00",
        "tasks": ["connection_pool", "model_cache"],
        "timezone": "Asia/Shanghai"
      }
    ]
  }
}
```

## 预热监控

### 监控指标
| 指标 | 说明 | 目标 |
|------|------|------|
| 预热完成率 | 预热任务完成比例 | 100% |
| 预热耗时 | 预热总耗时 | < 60s |
| 预热成功率 | 预热任务成功率 | > 99% |
| 首次请求延迟 | 预热后首次请求延迟 | < 100ms |

### 监控配置
```json
{
  "warmup_monitoring": {
    "metrics": {
      "completion_rate": true,
      "duration": true,
      "success_rate": true,
      "first_request_latency": true
    },
    "alerting": {
      "completion_rate_below": 0.9,
      "duration_above_s": 120,
      "success_rate_below": 0.95
    }
  }
}
```

## 性能优化效果

### 冷启动优化
| 场景 | 无预热 | 有预热 | 提升 |
|------|--------|--------|------|
| 首次请求延迟 | 5s | 100ms | **98% ↓** |
| 服务启动时间 | 60s | 30s | **50% ↓** |
| 首次推理延迟 | 10s | 500ms | **95% ↓** |

### 高峰期优化
| 场景 | 无预热 | 有预热 | 提升 |
|------|--------|--------|------|
| 高峰响应延迟 | 2s | 200ms | **90% ↓** |
| 连接等待时间 | 500ms | 10ms | **98% ↓** |
| 缓存命中率 | 20% | 60% | **200% ↑** |

## 版本
- 版本: 1.0.0
- 更新时间: 2026-04-06
