# RATE_LIMIT_OPTIMIZATION.md - 限流优化策略

## 目的
优化限流策略，保护系统稳定性，公平分配资源。

## 适用范围
所有 API 限流、用户限流、租户限流、资源限流。

## 限流架构

```
┌─────────────────────────────────────────────────────────────┐
│                    限流架构                                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   全局限流     │    │   租户限流     │    │   用户限流     │
│  (Global)     │    │  (Tenant)     │    │  (User)       │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ - 系统保护     │    │ - 配额限制     │    │ - 公平分配     │
│ - 过载保护     │    │ - 套餐限制     │    │ - 防滥用       │
│ - 降级触发     │    │ - 超额处理     │    │ - 行为控制     │
└───────────────┘    └───────────────┘    └───────────────┘
```

## 限流算法

### 算法对比
| 算法 | 说明 | 优点 | 缺点 |
|------|------|------|------|
| 固定窗口 | 固定时间窗口计数 | 简单 | 边界突发 |
| 滑动窗口 | 滑动时间窗口计数 | 平滑 | 内存占用 |
| 令牌桶 | 令牌生成消费 | 允许突发 | 实现复杂 |
| 漏桶 | 恒定速率流出 | 平滑 | 无突发 |

### 算法配置
```json
{
  "rate_limit_algorithms": {
    "default": "token_bucket",
    "algorithms": {
      "fixed_window": {
        "window_size_s": 1,
        "implementation": "redis"
      },
      "sliding_window": {
        "window_size_s": 1,
        "precision_ms": 100
      },
      "token_bucket": {
        "capacity": 100,
        "refill_rate": 10,
        "refill_interval_s": 1
      },
      "leaky_bucket": {
        "capacity": 100,
        "leak_rate": 10,
        "leak_interval_s": 1
      }
    }
  }
}
```

## 全局限流

### 系统保护限流
| 资源 | 限流阈值 | 说明 |
|------|----------|------|
| 总 QPS | 10000 | 系统总请求 |
| 并发连接 | 5000 | 并发连接数 |
| CPU 使用 | 80% | CPU 保护 |
| 内存使用 | 85% | 内存保护 |

### 全局限流配置
```json
{
  "global_rate_limit": {
    "total_qps": {
      "limit": 10000,
      "algorithm": "token_bucket",
      "burst": 12000
    },
    "concurrent_connections": {
      "limit": 5000,
      "timeout_s": 30
    },
    "resource_protection": {
      "cpu_threshold": 0.8,
      "memory_threshold": 0.85,
      "action": "throttle",
      "throttle_ratio": 0.5
    },
    "overload_protection": {
      "enabled": true,
      "trigger_threshold": 0.9,
      "degradation_actions": [
        "reject_low_priority",
        "enable_caching",
        "reduce_features"
      ]
    }
  }
}
```

## 租户限流

### 套餐限流配置
| 套餐 | QPS | 并发 | 日请求 | 说明 |
|------|-----|------|--------|------|
| 试用版 | 10 | 5 | 1000 | 严格限制 |
| 基础版 | 50 | 20 | 10000 | 标准限制 |
| 专业版 | 200 | 100 | 100000 | 较高限制 |
| 企业版 | 1000 | 500 | 1000000 | 高限制 |
| 企业增强版 | 5000 | 2000 | 无限 | 最高限制 |

### 租户限流配置
```json
{
  "tenant_rate_limit": {
    "by_plan": {
      "trial": {
        "qps": 10,
        "concurrent": 5,
        "daily_requests": 1000,
        "algorithm": "token_bucket"
      },
      "basic": {
        "qps": 50,
        "concurrent": 20,
        "daily_requests": 10000,
        "algorithm": "token_bucket"
      },
      "professional": {
        "qps": 200,
        "concurrent": 100,
        "daily_requests": 100000,
        "algorithm": "token_bucket"
      },
      "enterprise": {
        "qps": 1000,
        "concurrent": 500,
        "daily_requests": 1000000,
        "algorithm": "token_bucket"
      },
      "enterprise_plus": {
        "qps": 5000,
        "concurrent": 2000,
        "daily_requests": -1,
        "algorithm": "token_bucket"
      }
    },
    "exceeded_handling": {
      "action": "reject",
      "retry_after_s": 60,
      "notify_tenant": true
    }
  }
}
```

## 用户限流

### 用户限流配置
| 限流类型 | 默认限制 | 说明 |
|----------|----------|------|
| 用户 QPS | 5 | 单用户请求 |
| 用户并发 | 3 | 单用户并发 |
| 操作频率 | 按操作 | 特定操作限制 |

### 用户限流配置
```json
{
  "user_rate_limit": {
    "default": {
      "qps": 5,
      "concurrent": 3,
      "algorithm": "sliding_window"
    },
    "operation_limits": {
      "login": {
        "max_attempts": 5,
        "window_s": 300,
        "block_duration_s": 900
      },
      "password_reset": {
        "max_attempts": 3,
        "window_s": 3600
      },
      "api_key_generate": {
        "max_attempts": 10,
        "window_s": 86400
      }
    },
    "anti_abuse": {
      "enabled": true,
      "suspicious_threshold": 100,
      "block_duration_s": 3600
    }
  }
}
```

## API 限流

### API 分类限流
| API 类型 | 限流策略 | 说明 |
|----------|----------|------|
| 推理 API | 按模型 | 模型资源限制 |
| 工具 API | 按工具 | 工具资源限制 |
| 管理 API | 按操作 | 管理操作限制 |
| 查询 API | 按复杂度 | 查询成本限制 |

### API 限流配置
```json
{
  "api_rate_limit": {
    "inference_api": {
      "by_model": {
        "small_model": {
          "qps": 100,
          "concurrent": 50
        },
        "medium_model": {
          "qps": 50,
          "concurrent": 20
        },
        "large_model": {
          "qps": 20,
          "concurrent": 10
        }
      }
    },
    "tool_api": {
      "by_tool": {
        "read": {
          "qps": 100,
          "concurrent": 50
        },
        "write": {
          "qps": 50,
          "concurrent": 20
        },
        "external": {
          "qps": 20,
          "concurrent": 10
        }
      }
    },
    "admin_api": {
      "qps": 10,
      "concurrent": 5
    },
    "query_api": {
      "by_complexity": {
        "simple": {
          "qps": 200
        },
        "medium": {
          "qps": 100
        },
        "complex": {
          "qps": 20
        }
      }
    }
  }
}
```

## 限流响应

### 响应策略
| 策略 | 说明 | 适用场景 |
|------|------|----------|
| 拒绝 | 直接拒绝请求 | 硬限制 |
| 排队 | 请求排队等待 | 可等待场景 |
| 降级 | 返回降级响应 | 可降级场景 |
| 重试 | 返回重试信息 | 可重试场景 |

### 响应配置
```json
{
  "rate_limit_response": {
    "default": "reject",
    "strategies": {
      "reject": {
        "status_code": 429,
        "message": "请求过于频繁，请稍后重试",
        "headers": {
          "X-RateLimit-Limit": true,
          "X-RateLimit-Remaining": true,
          "X-RateLimit-Reset": true,
          "Retry-After": true
        }
      },
      "queue": {
        "enabled": true,
        "max_queue_size": 100,
        "max_wait_s": 30
      },
      "degrade": {
        "enabled": true,
        "fallback_response": "cached_or_default"
      }
    }
  }
}
```

## 限流监控

### 监控指标
| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 限流触发率 | 被限流请求比例 | > 5% |
| 平均等待时间 | 排队等待时间 | > 5s |
| 限流拒绝数 | 被拒绝请求数 | > 100/min |
| 资源使用率 | 资源使用比例 | > 80% |

### 监控配置
```json
{
  "rate_limit_monitoring": {
    "metrics": {
      "throttle_rate": true,
      "average_wait_time": true,
      "reject_count": true,
      "resource_usage": true
    },
    "alerting": {
      "throttle_rate_above": 0.05,
      "wait_time_above_s": 5,
      "reject_count_above_per_min": 100
    },
    "reporting": {
      "realtime_dashboard": true,
      "hourly_report": true
    }
  }
}
```

## 性能优化效果

### 系统稳定性
| 指标 | 无限流 | 有限流 | 提升 |
|------|--------|--------|------|
| 系统可用性 | 95% | 99.9% | **5% ↑** |
| 过载崩溃 | 偶发 | 无 | **100% ↓** |
| 响应稳定性 | 波动大 | 稳定 | **显著提升** |

### 公平性
| 指标 | 无限流 | 有限流 | 说明 |
|------|--------|--------|------|
| 资源分配 | 不公平 | 公平 | 按套餐分配 |
| 大用户影响 | 影响其他 | 不影响 | 隔离保护 |
| 小用户体验 | 差 | 好 | 公平保障 |

## 版本
- 版本: 1.0.0
- 更新时间: 2026-04-06
