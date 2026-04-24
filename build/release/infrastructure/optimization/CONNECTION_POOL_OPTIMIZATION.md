# CONNECTION_POOL_OPTIMIZATION.md - 连接池优化策略

## 目的
优化连接池管理，提升连接复用率，降低连接开销。

## 适用范围
所有数据库连接、HTTP 连接、WebSocket 连接、外部服务连接。

## 连接池架构

```
┌─────────────────────────────────────────────────────────────┐
│                    连接池架构                                │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   数据库连接池  │    │   HTTP 连接池  │    │   服务连接池   │
│  (Database)   │    │  (HTTP)       │    │  (Service)    │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ - 主库连接     │    │ - 出站连接     │    │ - 模型服务     │
│ - 从库连接     │    │ - 入站连接     │    │ - 工具服务     │
│ - 事务连接     │    │ - Keep-Alive   │    │ - 外部 API     │
└───────────────┘    └───────────────┘    └───────────────┘
```

## 数据库连接池

### 连接池配置
| 参数 | 主库 | 从库 | 说明 |
|------|------|------|------|
| 最小连接数 | 5 | 3 | 预热连接 |
| 最大连接数 | 20 | 10 | 并发上限 |
| 空闲超时 | 300s | 300s | 空闲回收 |
| 最大生命周期 | 1800s | 1800s | 定期刷新 |
| 连接超时 | 5s | 5s | 获取超时 |

### 数据库连接池配置
```json
{
  "database_pool": {
    "primary": {
      "min_size": 5,
      "max_size": 20,
      "idle_timeout_s": 300,
      "max_lifetime_s": 1800,
      "connection_timeout_s": 5,
      "validation_query": "SELECT 1",
      "validation_interval_s": 30,
      "leak_detection_threshold_s": 60
    },
    "replica": {
      "min_size": 3,
      "max_size": 10,
      "idle_timeout_s": 300,
      "max_lifetime_s": 1800,
      "connection_timeout_s": 5,
      "load_balance": "round_robin"
    },
    "transaction": {
      "isolated_pool": true,
      "min_size": 2,
      "max_size": 5
    }
  }
}
```

### 连接池监控
| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 活跃连接数 | 当前使用连接 | > 80% 最大值 |
| 空闲连接数 | 当前空闲连接 | < 20% 最小值 |
| 等待队列 | 等待获取连接数 | > 5 |
| 获取延迟 | 获取连接耗时 | > 100ms |
| 连接泄漏 | 未释放连接数 | > 0 |

## HTTP 连接池

### 出站连接池
| 参数 | 默认值 | 说明 |
|------|--------|------|
| 最大连接数 | 50 | 总连接上限 |
| 每路由最大 | 10 | 单目标上限 |
| 连接超时 | 5s | 建立超时 |
| 读取超时 | 30s | 读取超时 |
| Keep-Alive | 60s | 保持时间 |

### HTTP 连接池配置
```json
{
  "http_pool": {
    "outbound": {
      "max_total": 50,
      "max_per_route": 10,
      "connect_timeout_s": 5,
      "read_timeout_s": 30,
      "keep_alive_s": 60,
      "idle_timeout_s": 120,
      "validate_after_inactivity_s": 30
    },
    "route_config": {
      "model_service": {
        "max_connections": 20,
        "timeout_s": 60
      },
      "external_api": {
        "max_connections": 10,
        "timeout_s": 30
      }
    },
    "retry": {
      "enabled": true,
      "max_retries": 2,
      "retry_on": [502, 503, 504]
    }
  }
}
```

### Keep-Alive 优化
| 策略 | 说明 | 效果 |
|------|------|------|
| 连接复用 | 复用已建立连接 | 减少 50% 握手 |
| 预热连接 | 预建立常用连接 | 降低首次延迟 |
| 健康检查 | 定期检查连接 | 避免坏连接 |

## 服务连接池

### 模型服务连接池
| 参数 | 配置 | 说明 |
|------|------|------|
| 最大连接 | 20 | 并发模型调用 |
| 队列大小 | 100 | 等待队列 |
| 超时时间 | 120s | 模型调用超时 |
| 重试次数 | 1 | 失败重试 |

### 模型服务连接池配置
```json
{
  "model_service_pool": {
    "max_connections": 20,
    "queue_size": 100,
    "timeout_s": 120,
    "retry_count": 1,
    "circuit_breaker": {
      "enabled": true,
      "failure_threshold": 5,
      "reset_timeout_s": 60
    },
    "load_balance": {
      "strategy": "weighted",
      "weights": {
        "model-a": 0.6,
        "model-b": 0.4
      }
    }
  }
}
```

### 工具服务连接池
```json
{
  "tool_service_pool": {
    "max_connections": 30,
    "queue_size": 200,
    "timeout_s": 60,
    "per_tool_config": {
      "browser": {
        "max_connections": 5,
        "timeout_s": 180
      },
      "file_operations": {
        "max_connections": 10,
        "timeout_s": 30
      }
    }
  }
}
```

## 连接池管理策略

### 弹性伸缩
| 策略 | 说明 | 触发条件 |
|------|------|----------|
| 扩容 | 增加连接数 | 使用率 > 80% |
| 缩容 | 减少连接数 | 使用率 < 30% |
| 预热 | 预创建连接 | 系统启动 |
| 清理 | 清理坏连接 | 定期检查 |

### 弹性伸缩配置
```json
{
  "elastic_scaling": {
    "enabled": true,
    "scale_up": {
      "trigger_threshold": 0.8,
      "scale_step": 5,
      "cooldown_s": 60
    },
    "scale_down": {
      "trigger_threshold": 0.3,
      "scale_step": 2,
      "cooldown_s": 300
    },
    "warmup": {
      "on_startup": true,
      "warmup_connections": "min_size"
    }
  }
}
```

### 连接健康检查
| 检查类型 | 频率 | 说明 |
|----------|------|------|
| 心跳检查 | 30s | 发送心跳 |
| 空闲检查 | 60s | 检查空闲连接 |
| 泄漏检查 | 60s | 检查未释放连接 |
| 验证检查 | 30s | 验证连接可用 |

### 健康检查配置
```json
{
  "health_check": {
    "heartbeat": {
      "enabled": true,
      "interval_s": 30,
      "timeout_s": 5
    },
    "idle_check": {
      "enabled": true,
      "interval_s": 60,
      "max_idle_s": 300
    },
    "leak_check": {
      "enabled": true,
      "interval_s": 60,
      "leak_threshold_s": 300
    },
    "validation": {
      "enabled": true,
      "interval_s": 30,
      "on_borrow": true
    }
  }
}
```

## 连接池监控

### 监控指标
| 指标 | 说明 | 目标 |
|------|------|------|
| 连接利用率 | 活跃/最大连接 | 60-80% |
| 获取延迟 | 获取连接时间 | < 10ms |
| 等待队列 | 等待请求数 | < 10 |
| 连接错误 | 连接失败率 | < 1% |
| 复用率 | 连接复用比例 | > 80% |

### 监控配置
```json
{
  "pool_monitoring": {
    "metrics": {
      "active_connections": true,
      "idle_connections": true,
      "wait_queue_size": true,
      "acquisition_latency": true,
      "connection_errors": true,
      "reuse_rate": true
    },
    "alerting": {
      "utilization_above": 0.9,
      "wait_queue_above": 20,
      "acquisition_latency_above_ms": 100,
      "error_rate_above": 0.05
    }
  }
}
```

## 性能优化效果

### 连接建立优化
| 场景 | 无连接池 | 有连接池 | 提升 |
|------|----------|----------|------|
| 首次请求 | 100ms | 100ms | 无变化 |
| 后续请求 | 100ms | 1ms | **99% ↓** |
| 高并发 | 1000ms+ | 10ms | **99% ↓** |

### 资源优化
| 资源 | 无连接池 | 有连接池 | 节省 |
|------|----------|----------|------|
| 连接数 | 不限 | 受控 | 可控 |
| 内存 | 高 | 低 | **50% ↓** |
| CPU | 高 | 低 | **30% ↓** |

## 版本
- 版本: 1.0.0
- 更新时间: 2026-04-06
