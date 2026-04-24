# TEMPLATE_CACHE.md - 模板缓存系统

## 目的
定义模板缓存机制，提升模板加载和渲染性能。

## 适用范围
所有模板的缓存、复用、预编译。

---

## 一、缓存架构

### 1.1 多级缓存
```
┌─────────────────────────────────────────────────────────────┐
│                    模板缓存架构                              │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  L1 内存缓存  │    │  L2 磁盘缓存  │    │  L3 压缩缓存  │
│   100 模板    │    │  1000 模板    │    │  5000 模板    │
│   TTL: 1h     │    │   TTL: 24h    │    │   TTL: 7d     │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ 热点模板      │    │ 常用模板      │    │ 归档模板      │
│ 即时访问      │    │ 快速访问      │    │ 按需加载      │
└───────────────┘    └───────────────┘    └───────────────┘
```

### 1.2 缓存层级配置
| 层级 | 容量 | TTL | 命中率目标 | 访问延迟 |
|------|------|-----|------------|----------|
| L1 内存 | 100 模板 | 1 小时 | 80% | < 1ms |
| L2 磁盘 | 1000 模板 | 24 小时 | 15% | < 10ms |
| L3 压缩 | 5000 模板 | 7 天 | 5% | < 100ms |

---

## 二、缓存策略

### 2.1 缓存策略类型
| 策略 | 说明 | 适用场景 |
|------|------|----------|
| LRU | 最近最少使用 | 通用场景 |
| LFU | 最少使用频率 | 热点场景 |
| FIFO | 先进先出 | 顺序场景 |
| ARC | 自适应替换 | 混合场景 |

### 2.2 缓存策略配置
```json
{
  "cache_strategy": {
    "L1": {
      "type": "LRU",
      "max_size": 100,
      "ttl_seconds": 3600,
      "eviction_policy": "lru"
    },
    "L2": {
      "type": "LFU",
      "max_size": 1000,
      "ttl_seconds": 86400,
      "eviction_policy": "lfu"
    },
    "L3": {
      "type": "FIFO",
      "max_size": 5000,
      "ttl_seconds": 604800,
      "eviction_policy": "fifo",
      "compression": {
        "enabled": true,
        "algorithm": "gzip",
        "level": 6
      }
    }
  }
}
```

### 2.3 预加载策略
```yaml
preload:
  on_startup:
    description: "启动时预加载"
    enabled: true
    templates:
      - core/document.md.tmpl
      - core/config.json.tmpl
      - security/threat_model.md.tmpl
      - governance/memory_policy.md.tmpl
  
  on_demand:
    description: "按需预加载"
    enabled: true
    trigger:
      - 用户访问相关目录
      - 用户提及相关主题
      - 批量创建任务
  
  predictive:
    description: "预测性预加载"
    enabled: true
    model: "usage_pattern"
    lookahead: 5
```

---

## 三、缓存内容

### 3.1 缓存内容类型
| 类型 | 说明 | 缓存方式 |
|------|------|----------|
| 原始模板 | 模板源文件 | 完整缓存 |
| 编译模板 | 预编译结果 | 编译缓存 |
| 渲染结果 | 常用渲染结果 | 结果缓存 |
| 变量映射 | 变量解析结果 | 映射缓存 |

### 3.2 缓存内容结构
```json
{
  "cache_entry": {
    "key": "templates/security/threat_model.md.tmpl",
    "type": "compiled",
    "content": "...",
    "metadata": {
      "size_bytes": 2048,
      "created_at": "2026-04-07T10:00:00Z",
      "last_accessed": "2026-04-07T10:30:00Z",
      "access_count": 15,
      "hit_rate": 0.85
    },
    "dependencies": [
      "templates/base/document.md.tmpl",
      "templates/partials/header.md.tmpl"
    ],
    "variables": [
      "timestamp",
      "date",
      "version",
      "project"
    ],
    "checksum": "sha256:abc123..."
  }
}
```

### 3.3 缓存索引
```yaml
cache_index:
  by_path:
    description: "按路径索引"
    enabled: true
  
  by_type:
    description: "按类型索引"
    enabled: true
    types:
      - document
      - config
      - policy
      - security
  
  by_usage:
    description: "按使用频率索引"
    enabled: true
    update_interval: 60s
  
  by_dependency:
    description: "按依赖关系索引"
    enabled: true
    for_invalidation: true
```

---

## 四、缓存操作

### 4.1 缓存读取流程
```
请求模板
    ↓
检查 L1 缓存
    ├── 命中 → 返回（< 1ms）
    └── 未命中 ↓
检查 L2 缓存
    ├── 命中 → 提升到 L1 → 返回（< 10ms）
    └── 未命中 ↓
检查 L3 缓存
    ├── 命中 → 解压 → 提升到 L2 → 返回（< 100ms）
    └── 未命中 ↓
加载原始模板
    ↓
编译模板
    ↓
存入 L1 缓存
    ↓
返回（< 500ms）
```

### 4.2 缓存写入流程
```
模板更新
    ↓
计算校验和
    ↓
检查是否变化
    ├── 无变化 → 更新访问时间
    └── 有变化 ↓
使旧缓存失效
    ↓
重新编译模板
    ↓
写入 L1 缓存
    ↓
异步写入 L2/L3
    ↓
更新索引
```

### 4.3 缓存失效策略
```yaml
invalidation:
  on_change:
    description: "模板变更时失效"
    enabled: true
    propagate: true
  
  on_dependency_change:
    description: "依赖变更时失效"
    enabled: true
    cascade: true
  
  on_config_change:
    description: "配置变更时失效"
    enabled: true
    selective: true
  
  periodic:
    description: "定期失效"
    enabled: true
    interval: 86400s
  
  ttl_based:
    description: "TTL 过期失效"
    enabled: true
    check_interval: 60s
```

---

## 五、缓存性能

### 5.1 性能指标
| 指标 | 目标 | 说明 |
|------|------|------|
| L1 命中率 | > 80% | 热点模板命中 |
| L2 命中率 | > 95% | 常用模板命中 |
| 总命中率 | > 99% | 全部缓存命中 |
| 平均延迟 | < 5ms | 平均访问延迟 |
| 内存占用 | < 100MB | L1 缓存占用 |

### 5.2 性能优化效果
| 场景 | 无缓存 | 有缓存 | 提升 |
|------|--------|--------|------|
| 单模板加载 | 200ms | 1ms | **200x ↑** |
| 模板渲染 | 100ms | 5ms | **20x ↑** |
| 批量创建 | 10s | 0.5s | **20x ↑** |

### 5.3 性能监控
```yaml
monitoring:
  metrics:
    - hit_rate_by_level
    - average_latency
    - cache_size
    - eviction_count
    - miss_count
  
  alerting:
    hit_rate_below: 0.8
    latency_above_ms: 50
    size_above_mb: 100
  
  reporting:
    interval: 60s
    include:
      - 热点模板排行
      - 缓存效率报告
      - 失效统计
```

---

## 六、缓存预热

### 6.1 预热策略
```yaml
warmup:
  startup:
    description: "启动预热"
    enabled: true
    templates:
      - top_20_used
      - core_templates
      - recent_used
  
  scheduled:
    description: "定时预热"
    enabled: true
    schedule: "0 */6 * * *"
    refresh:
      - update_hot_list
      - preload_predicted
  
  on_event:
    description: "事件触发预热"
    enabled: true
    events:
      - user_login
      - project_switch
      - batch_task_start
```

### 6.2 预热效果
| 预热类型 | 预热时间 | 首次命中提升 |
|----------|----------|--------------|
| 启动预热 | 5s | 60% → 90% |
| 定时预热 | 2s | 维持 90%+ |
| 事件预热 | 1s | 即时提升 |

---

## 七、缓存一致性

### 7.1 一致性保证
```yaml
consistency:
  validation:
    description: "缓存验证"
    enabled: true
    method: "checksum"
    interval: 300s
  
  synchronization:
    description: "缓存同步"
    enabled: true
    on_update: "immediate"
    on_delete: "immediate"
  
  fallback:
    description: "降级策略"
    enabled: true
    on_inconsistency: "reload"
    max_retries: 3
```

### 7.2 一致性检查
```yaml
consistency_check:
  checksum:
    algorithm: "sha256"
    include:
      - template_content
      - dependencies
      - variables
  
  comparison:
    source: "original_template"
    cached: "cached_template"
    action: "reload_on_mismatch"
```

---

## 八、缓存统计

### 8.1 统计指标
```json
{
  "cache_stats": {
    "timestamp": "2026-04-07T10:00:00Z",
    "L1": {
      "size": 85,
      "max_size": 100,
      "hit_count": 8500,
      "miss_count": 1500,
      "hit_rate": 0.85,
      "eviction_count": 20,
      "avg_latency_ms": 0.8
    },
    "L2": {
      "size": 450,
      "max_size": 1000,
      "hit_count": 1400,
      "miss_count": 100,
      "hit_rate": 0.93,
      "eviction_count": 50,
      "avg_latency_ms": 8
    },
    "L3": {
      "size": 800,
      "max_size": 5000,
      "hit_count": 95,
      "miss_count": 5,
      "hit_rate": 0.95,
      "eviction_count": 10,
      "avg_latency_ms": 50
    },
    "overall": {
      "total_hit_rate": 0.995,
      "avg_latency_ms": 2.5,
      "memory_usage_mb": 45
    }
  }
}
```

### 8.2 热点模板排行
```yaml
hot_templates:
  - path: "templates/core/document.md.tmpl"
    access_count: 1500
    last_accessed: "2026-04-07T10:00:00Z"
  
  - path: "templates/security/threat_model.md.tmpl"
    access_count: 850
    last_accessed: "2026-04-07T09:55:00Z"
  
  - path: "templates/governance/memory_policy.md.tmpl"
    access_count: 620
    last_accessed: "2026-04-07T09:50:00Z"
```

---

## 九、缓存配置

### 9.1 完整配置
```json
{
  "template_cache": {
    "enabled": true,
    "levels": {
      "L1": {
        "type": "memory",
        "max_size": 100,
        "ttl_seconds": 3600,
        "strategy": "LRU"
      },
      "L2": {
        "type": "disk",
        "max_size": 1000,
        "ttl_seconds": 86400,
        "strategy": "LFU",
        "path": "~/.openclaw/cache/templates/L2"
      },
      "L3": {
        "type": "compressed",
        "max_size": 5000,
        "ttl_seconds": 604800,
        "strategy": "FIFO",
        "path": "~/.openclaw/cache/templates/L3",
        "compression": {
          "algorithm": "gzip",
          "level": 6
        }
      }
    },
    "preload": {
      "on_startup": true,
      "templates": [
        "templates/core/document.md.tmpl",
        "templates/core/config.json.tmpl"
      ]
    },
    "invalidation": {
      "on_change": true,
      "on_dependency_change": true,
      "periodic_seconds": 86400
    },
    "monitoring": {
      "enabled": true,
      "interval_seconds": 60,
      "alerting": {
        "hit_rate_below": 0.8,
        "latency_above_ms": 50
      }
    }
  }
}
```

---

## 十、与其他模块联动

| 模块 | 联动方式 |
|------|----------|
| optimization/FILE_CREATION_OPTIMIZATION.md | 文件创建使用模板缓存 |
| optimization/PERFORMANCE_MONITORING.md | 监控缓存性能 |
| auto_upgrade/ONE_CLICK_OPTIMIZE.md | 优化时检查缓存效率 |
| governance/AUDIT_LOG.md | 缓存操作审计 |

---

## 版本
- 版本: 1.0.0
- 更新时间: 2026-04-07
- 下次评审: 2026-07-07
