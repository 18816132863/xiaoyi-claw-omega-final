# PERFORMANCE_MONITORING.md - 性能监控体系

## 目的
建立完整性能监控体系，实时发现性能问题，持续优化系统性能。

## 适用范围
所有系统性能指标、应用性能监控、用户体验监控。

## 监控架构

```
┌─────────────────────────────────────────────────────────────┐
│                    性能监控架构                              │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   基础设施监控  │    │   应用性能监控  │    │   用户体验监控  │
│  (Infra)      │    │  (APM)        │    │  (UX)         │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ - CPU/内存     │    │ - 响应时间     │    │ - 首屏时间     │
│ - 网络/磁盘    │    │ - 吞吐量       │    │ - 交互延迟     │
│ - 容器/进程    │    │ - 错误率       │    │ - 满意度       │
└───────────────┘    └───────────────┘    └───────────────┘
```

## 基础设施监控

### 系统指标
| 指标类别 | 指标项 | 采集频率 | 告警阈值 |
|----------|--------|----------|----------|
| CPU | 使用率 | 10s | > 80% |
| CPU | 负载 | 10s | > 核心数 |
| 内存 | 使用率 | 10s | > 85% |
| 内存 | 交换使用 | 10s | > 0 |
| 磁盘 | 使用率 | 60s | > 85% |
| 磁盘 | I/O 等待 | 10s | > 20% |
| 网络 | 带宽使用 | 10s | > 80% |
| 网络 | 连接数 | 10s | > 10000 |

### 基础设施配置
```json
{
  "infrastructure_monitoring": {
    "collection_interval_s": 10,
    "metrics": {
      "cpu": {
        "usage_percent": true,
        "load_average": true,
        "per_core": true
      },
      "memory": {
        "usage_percent": true,
        "swap_usage": true,
        "cache_usage": true
      },
      "disk": {
        "usage_percent": true,
        "io_wait": true,
        "read_write_ops": true
      },
      "network": {
        "bandwidth_usage": true,
        "connection_count": true,
        "packet_loss": true
      }
    },
    "alerting": {
      "cpu_usage_above": 0.8,
      "memory_usage_above": 0.85,
      "disk_usage_above": 0.85,
      "network_bandwidth_above": 0.8
    }
  }
}
```

## 应用性能监控 (APM)

### 核心指标
| 指标 | 说明 | 目标 | 告警阈值 |
|------|------|------|----------|
| 响应时间 P50 | 中位数响应时间 | < 500ms | > 1s |
| 响应时间 P95 | 95 分位响应时间 | < 2s | > 5s |
| 响应时间 P99 | 99 分位响应时间 | < 5s | > 10s |
| 吞吐量 | 每秒请求数 | > 100 | < 50 |
| 错误率 | 请求错误比例 | < 1% | > 5% |
| 可用性 | 服务可用比例 | > 99.9% | < 99% |

### APM 配置
```json
{
  "apm_monitoring": {
    "sampling_rate": 0.1,
    "metrics": {
      "response_time": {
        "percentiles": [50, 90, 95, 99],
        "histogram_buckets": [100, 500, 1000, 2000, 5000, 10000]
      },
      "throughput": {
        "requests_per_second": true,
        "operations_per_second": true
      },
      "error_rate": {
        "by_type": true,
        "by_endpoint": true
      },
      "availability": {
        "health_check_interval_s": 10
      }
    },
    "tracing": {
      "enabled": true,
      "sample_rate": 0.01,
      "max_spans_per_trace": 100
    }
  }
}
```

### 端点监控
| 端点类型 | 监控重点 | SLA 目标 |
|----------|----------|----------|
| 推理接口 | 响应时间、Token 消耗 | P95 < 30s |
| 工具接口 | 执行时间、成功率 | P95 < 60s |
| 记忆接口 | 查询时间、命中率 | P95 < 5s |
| 管理接口 | 响应时间、可用性 | P95 < 1s |

## 用户体验监控

### 用户体验指标
| 指标 | 说明 | 目标 | 告警阈值 |
|------|------|------|----------|
| 首字时间 (TTFT) | 首字输出时间 | < 500ms | > 2s |
| 首屏时间 (FCP) | 首次内容渲染 | < 1s | > 3s |
| 交互时间 (TTI) | 可交互时间 | < 2s | > 5s |
| 完成时间 (TTC) | 任务完成时间 | < 30s | > 60s |
| 满意度评分 | 用户满意度 | > 4.0 | < 3.5 |

### UX 监控配置
```json
{
  "ux_monitoring": {
    "metrics": {
      "ttft": {
        "enabled": true,
        "target_ms": 500,
        "alert_above_ms": 2000
      },
      "fcp": {
        "enabled": true,
        "target_ms": 1000,
        "alert_above_ms": 3000
      },
      "tti": {
        "enabled": true,
        "target_ms": 2000,
        "alert_above_ms": 5000
      },
      "ttc": {
        "enabled": true,
        "target_ms": 30000,
        "alert_above_ms": 60000
      },
      "satisfaction": {
        "enabled": true,
        "collection_method": "implicit",
        "target_score": 4.0
      }
    },
    "session_replay": {
      "enabled": false,
      "sample_rate": 0.001
    }
  }
}
```

## 分布式追踪

### 追踪配置
| 配置项 | 说明 | 值 |
|--------|------|-----|
| 采样率 | 追踪采样比例 | 1% |
| 最大 Span | 单次追踪最大 Span | 100 |
| 追踪深度 | 最大追踪深度 | 10 |
| 保留时间 | 追踪数据保留 | 7 天 |

### 追踪配置
```json
{
  "distributed_tracing": {
    "enabled": true,
    "sample_rate": 0.01,
    "max_spans": 100,
    "max_depth": 10,
    "propagation_format": "w3c",
    "span_attributes": {
      "user_id": true,
      "tenant_id": true,
      "session_id": true,
      "request_id": true
    },
    "retention_days": 7
  }
}
```

## 告警体系

### 告警级别
| 级别 | 说明 | 响应时间 | 通知方式 |
|------|------|----------|----------|
| P0 - 紧急 | 服务不可用 | 5 分钟 | 电话 + 短信 |
| P1 - 严重 | 严重性能下降 | 15 分钟 | 短信 + IM |
| P2 - 警告 | 性能异常 | 1 小时 | IM + 邮件 |
| P3 - 提示 | 需要关注 | 24 小时 | 邮件 |

### 告警规则
```json
{
  "alerting_rules": [
    {
      "name": "high_latency",
      "condition": "p95_latency > 5000ms for 5m",
      "severity": "P1",
      "channels": ["sms", "slack"]
    },
    {
      "name": "high_error_rate",
      "condition": "error_rate > 5% for 3m",
      "severity": "P0",
      "channels": ["phone", "sms", "slack"]
    },
    {
      "name": "low_throughput",
      "condition": "throughput < 50 for 10m",
      "severity": "P2",
      "channels": ["slack", "email"]
    },
    {
      "name": "memory_pressure",
      "condition": "memory_usage > 90% for 5m",
      "severity": "P1",
      "channels": ["sms", "slack"]
    }
  ]
}
```

## 性能报告

### 报告类型
| 报告类型 | 频率 | 内容 |
|----------|------|------|
| 实时仪表盘 | 实时 | 当前性能状态 |
| 小时报表 | 每小时 | 小时性能统计 |
| 日报 | 每日 | 日性能分析 |
| 周报 | 每周 | 周趋势分析 |
| 月报 | 每月 | 月度性能评估 |

### 报告内容
```json
{
  "performance_report": {
    "daily": {
      "summary": ["avg_latency", "p95_latency", "throughput", "error_rate"],
      "trends": ["latency_trend", "throughput_trend"],
      "top_issues": ["slowest_endpoints", "most_errors"],
      "recommendations": true
    },
    "weekly": {
      "comparison": ["wow_change", "target_vs_actual"],
      "analysis": ["bottleneck_analysis", "capacity_analysis"],
      "forecast": ["traffic_forecast", "capacity_forecast"]
    },
    "monthly": {
      "sla_report": true,
      "capacity_planning": true,
      "optimization_recommendations": true
    }
  }
}
```

## 性能优化闭环

### 优化流程
```
监控发现 → 问题定位 → 根因分析 → 优化方案 → 实施验证 → 效果评估
    ↑                                                        ↓
    └────────────────── 持续改进 ←───────────────────────────┘
```

### 优化跟踪
| 阶段 | 说明 | 输出 |
|------|------|------|
| 发现 | 监控发现问题 | 问题工单 |
| 定位 | 定位问题位置 | 问题定位报告 |
| 分析 | 分析根本原因 | 根因分析报告 |
| 方案 | 制定优化方案 | 优化方案文档 |
| 实施 | 实施优化措施 | 变更记录 |
| 验证 | 验证优化效果 | 效果评估报告 |

## 版本
- 版本: 1.0.0
- 更新时间: 2026-04-06
