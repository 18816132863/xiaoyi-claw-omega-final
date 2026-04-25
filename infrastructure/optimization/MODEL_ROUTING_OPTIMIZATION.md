# MODEL_ROUTING_OPTIMIZATION.md - 模型路由优化策略

## 目的
优化模型路由策略，按任务复杂度选择最优模型，平衡质量与成本。

## 适用范围
所有模型调用、任务分发、成本优化。

## 路由策略架构

```
┌─────────────────────────────────────────────────────────────┐
│                    模型路由架构                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    任务复杂度评估                            │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   简单任务     │    │   中等任务     │    │   复杂任务     │
│  (Simple)     │    │  (Medium)     │    │  (Complex)    │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   小模型       │    │   中模型       │    │   大模型       │
│  成本: 低      │    │  成本: 中      │    │  成本: 高      │
│  质量: 标准    │    │  质量: 良好    │    │  质量: 优秀    │
└───────────────┘    └───────────────┘    └───────────────┘
```

## 模型分层

### 模型等级定义
| 等级 | 模型类型 | 成本系数 | 适用场景 |
|------|----------|----------|----------|
| S1 | 经济模型 | 0.1x | 简单分类、格式化 |
| S2 | 标准模型 | 0.3x | 标准问答、总结 |
| S3 | 中端模型 | 0.6x | 分析、推理 |
| S4 | 高端模型 | 1.0x | 复杂推理、创作 |
| S5 | 特殊模型 | 2.0x | 专业领域、高要求 |

### 模型池配置
```json
{
  "model_pool": {
    "S1": {
      "models": ["economy-model-v1"],
      "cost_per_1k_tokens": 0.001,
      "max_tokens": 2000,
      "capabilities": ["classification", "formatting", "extraction"]
    },
    "S2": {
      "models": ["standard-model-v1"],
      "cost_per_1k_tokens": 0.003,
      "max_tokens": 4000,
      "capabilities": ["qa", "summarization", "translation"]
    },
    "S3": {
      "models": ["medium-model-v1"],
      "cost_per_1k_tokens": 0.006,
      "max_tokens": 8000,
      "capabilities": ["analysis", "reasoning", "planning"]
    },
    "S4": {
      "models": ["premium-model-v1"],
      "cost_per_1k_tokens": 0.01,
      "max_tokens": 16000,
      "capabilities": ["complex_reasoning", "creative", "code"]
    },
    "S5": {
      "models": ["special-model-v1"],
      "cost_per_1k_tokens": 0.02,
      "max_tokens": 32000,
      "capabilities": ["domain_expert", "high_stakes", "custom"]
    }
  }
}
```

## 任务复杂度评估

### 评估维度
| 维度 | 权重 | 评估指标 |
|------|------|----------|
| 输入复杂度 | 20% | 输入长度、结构复杂度 |
| 任务类型 | 30% | 任务类型复杂度评分 |
| 上下文依赖 | 20% | 上下文需求程度 |
| 输出要求 | 20% | 输出复杂度要求 |
| 风险等级 | 10% | 错误影响程度 |

### 复杂度评分
```json
{
  "complexity_scoring": {
    "dimensions": {
      "input_complexity": {
        "weight": 0.2,
        "factors": {
          "input_length": {
            "< 100": 1,
            "100-500": 2,
            "500-1000": 3,
            "> 1000": 4
          },
          "structure_complexity": {
            "simple": 1,
            "moderate": 2,
            "complex": 3
          }
        }
      },
      "task_type": {
        "weight": 0.3,
        "scores": {
          "classification": 1,
          "extraction": 1,
          "formatting": 1,
          "qa": 2,
          "summarization": 2,
          "translation": 2,
          "analysis": 3,
          "reasoning": 3,
          "planning": 3,
          "creative": 4,
          "code": 4,
          "complex_reasoning": 5
        }
      },
      "context_dependency": {
        "weight": 0.2,
        "scores": {
          "no_context": 1,
          "light_context": 2,
          "moderate_context": 3,
          "heavy_context": 4
        }
      },
      "output_requirement": {
        "weight": 0.2,
        "scores": {
          "simple_output": 1,
          "structured_output": 2,
          "detailed_output": 3,
          "creative_output": 4
        }
      },
      "risk_level": {
        "weight": 0.1,
        "scores": {
          "low_risk": 1,
          "medium_risk": 2,
          "high_risk": 3,
          "critical_risk": 4
        }
      }
    }
  }
}
```

## 路由规则

### 基于复杂度的路由
| 复杂度分数 | 路由目标 | 说明 |
|------------|----------|------|
| 1.0 - 1.5 | S1 | 简单任务，经济模型 |
| 1.5 - 2.5 | S2 | 标准任务，标准模型 |
| 2.5 - 3.5 | S3 | 中等任务，中端模型 |
| 3.5 - 4.5 | S4 | 复杂任务，高端模型 |
| 4.5 - 5.0 | S5 | 极复杂任务，特殊模型 |

### 路由配置
```json
{
  "routing_rules": [
    {
      "name": "simple_tasks",
      "condition": "complexity_score <= 1.5",
      "target_tier": "S1",
      "fallback": "S2",
      "expected_savings": "90%"
    },
    {
      "name": "standard_tasks",
      "condition": "complexity_score > 1.5 AND complexity_score <= 2.5",
      "target_tier": "S2",
      "fallback": "S3",
      "expected_savings": "70%"
    },
    {
      "name": "medium_tasks",
      "condition": "complexity_score > 2.5 AND complexity_score <= 3.5",
      "target_tier": "S3",
      "fallback": "S4",
      "expected_savings": "40%"
    },
    {
      "name": "complex_tasks",
      "condition": "complexity_score > 3.5 AND complexity_score <= 4.5",
      "target_tier": "S4",
      "fallback": "S5",
      "expected_savings": "0%"
    },
    {
      "name": "critical_tasks",
      "condition": "complexity_score > 4.5",
      "target_tier": "S5",
      "fallback": null,
      "expected_savings": "0%"
    }
  ]
}
```

## 特殊路由规则

### 按用户/租户路由
| 规则 | 说明 |
|------|------|
| 企业版用户 | 最低使用 S3 模型 |
| 高合规租户 | 使用指定模型 |
| 试用用户 | 最高使用 S2 模型 |

### 按任务类型路由
| 任务类型 | 强制路由 | 说明 |
|----------|----------|------|
| 代码生成 | S4+ | 代码质量要求 |
| 安全分析 | S4+ | 安全准确性要求 |
| 合规审查 | S4+ | 合规准确性要求 |
| 简单分类 | S1 | 成本优化 |

### 按时间路由
| 时段 | 路由策略 | 说明 |
|------|----------|------|
| 高峰期 | 偏向小模型 | 成本控制 |
| 低峰期 | 正常路由 | 质量优先 |

## 熔断与降级

### 模型熔断
| 条件 | 动作 | 说明 |
|------|------|------|
| 错误率 > 10% | 熔断 | 停止使用该模型 |
| 响应时间 > 30s | 熔断 | 性能问题 |
| 连续失败 > 5 | 熔断 | 连续失败 |

### 降级策略
| 原模型 | 降级目标 | 说明 |
|--------|----------|------|
| S5 | S4 | 特殊模型降级 |
| S4 | S3 | 高端模型降级 |
| S3 | S2 | 中端模型降级 |
| S2 | S1 | 标准模型降级 |

### 熔断配置
```json
{
  "circuit_breaker": {
    "enabled": true,
    "failure_threshold": 5,
    "error_rate_threshold": 0.1,
    "latency_threshold_ms": 30000,
    "recovery_timeout_seconds": 60,
    "half_open_requests": 3
  }
}
```

## 负载均衡

### 模型池负载均衡
| 策略 | 说明 | 适用场景 |
|------|------|----------|
| 轮询 | 依次使用 | 同级模型 |
| 加权 | 按权重分配 | 性能差异 |
| 最少连接 | 选最空闲 | 负载不均 |
| 响应时间 | 选最快 | 性能优先 |

### 负载均衡配置
```json
{
  "load_balancing": {
    "strategy": "weighted",
    "weights": {
      "model-a": 0.6,
      "model-b": 0.4
    },
    "health_check": {
      "enabled": true,
      "interval_seconds": 30,
      "timeout_seconds": 5
    }
  }
}
```

## 成本监控

### 成本指标
| 指标 | 说明 | 目标 |
|------|------|------|
| 平均单次成本 | 平均每次请求成本 | < ¥0.01 |
| 模型分布 | 各模型使用比例 | S1+S2 > 50% |
| 路由准确率 | 正确路由比例 | > 90% |
| 成本节省率 | 相比全用 S4 节省 | > 40% |

### 成本报告
| 报告类型 | 频率 | 内容 |
|----------|------|------|
| 实时监控 | 实时 | 当前成本状态 |
| 日报 | 每日 | 日成本统计 |
| 周报 | 每周 | 成本趋势分析 |
| 月报 | 每月 | 成本优化建议 |

## 版本
- 版本: 1.0.0
- 更新时间: 2026-04-06
