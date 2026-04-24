# TOKEN_OPTIMIZATION.md - Token 优化策略

## 目的
定义 Token 使用优化策略，降低成本、提升效率。

## 适用范围
所有 LLM 调用、上下文构建、输出生成。

## Token 优化原则

### 核心原则
1. **最小必要**: 只传递必要信息
2. **延迟加载**: 按需加载技能和上下文
3. **智能压缩**: 压缩冗余内容
4. **缓存复用**: 复用已计算结果

## Token 预算分配

### 单轮预算
| 场景 | 输入预算 | 输出预算 | 总预算 |
|------|----------|----------|--------|
| 简单问答 | 2,000 | 1,000 | 3,000 |
| 标准任务 | 5,000 | 2,000 | 7,000 |
| 复杂任务 | 10,000 | 5,000 | 15,000 |
| 深度分析 | 20,000 | 10,000 | 30,000 |
| 最大限制 | 50,000 | 20,000 | 70,000 |

### 预算监控
```yaml
token_monitoring:
  warning_threshold: 0.8  # 80% 预警
  hard_limit: 0.95        # 95% 硬限制
  on_exceed: truncate_output
```

## 输入优化

### 上下文压缩
| 策略 | 说明 | 压缩率 |
|------|------|--------|
| 历史摘要 | 压缩历史对话 | 60-80% |
| 技能精简 | 只加载必要技能 | 50-70% |
| 文档截断 | 截断过长文档 | 40-60% |
| 去重去噪 | 移除重复内容 | 20-40% |

### 技能加载优化
```yaml
skill_loading:
  strategy: lazy_load
  max_skill_size: 2048  # 单技能最大 2KB
  priority_loading:
    P0: always_load     # 核心技能始终加载
    P1: on_demand       # 按需加载
    P2: lazy_load       # 延迟加载
    P3: never_preload   # 不预加载
```

### 提示优化
| 优化项 | 说明 | 节省 |
|--------|------|------|
| 移除冗余 | 删除不必要描述 | 10-20% |
| 结构化 | 使用结构化格式 | 15-25% |
| 符号化 | 用符号替代文字 | 5-10% |
| 引用化 | 引用替代重复 | 10-15% |

## 输出优化

### 输出控制
| 策略 | 说明 | 适用场景 |
|------|------|----------|
| 长度限制 | 限制最大输出长度 | 所有场景 |
| 格式简化 | 使用简洁格式 | 标准输出 |
| 分段输出 | 分多次输出 | 长内容 |
| 摘要优先 | 先摘要后详情 | 信息展示 |

### 输出格式
```yaml
output_format:
  default: concise      # 默认简洁
  max_length: 2000      # 最大 2000 字符
  structure_preference:
    - table             # 优先表格
    - list              # 其次列表
    - paragraph         # 最后段落
```

## 缓存策略

### 缓存层级
| 层级 | 缓存内容 | TTL | 命中率目标 |
|------|----------|-----|------------|
| L1 | 会话上下文 | 会话内 | 80% |
| L2 | 常用技能 | 1小时 | 60% |
| L3 | 检索结果 | 1天 | 40% |
| L4 | 计算结果 | 7天 | 30% |

### 缓存键生成
```yaml
cache_key:
  components:
    - intent_hash      # 意图哈希
    - context_hash     # 上下文哈希
    - skill_id         # 技能ID
  collision_handling: overwrite
```

## Token 统计

### 统计维度
| 维度 | 说明 | 用途 |
|------|------|------|
| 按会话 | 每会话 Token 消耗 | 会话管理 |
| 按技能 | 每技能 Token 消耗 | 技能优化 |
| 按任务类型 | 按类型统计 | 任务优化 |
| 按时间 | 按时间段统计 | 趋势分析 |

### 统计报告
```json
{
  "reportId": "token_report_001",
  "period": "2026-04-06",
  "summary": {
    "totalInput": 1000000,
    "totalOutput": 500000,
    "avgInputPerRequest": 5000,
    "avgOutputPerRequest": 2500
  },
  "bySkill": {
    "xiaoyi-web-search": {"input": 200000, "output": 100000},
    "deep-search": {"input": 300000, "output": 150000}
  },
  "optimization": {
    "savedByCache": 200000,
    "savedByCompression": 150000,
    "totalSaved": 350000
  }
}
```

## 优化触发

### 自动优化
| 触发条件 | 优化动作 |
|----------|----------|
| 预算 > 80% | 启用压缩模式 |
| 预算 > 90% | 启用精简模式 |
| 预算 > 95% | 启用最小模式 |
| 缓存命中率 < 30% | 优化缓存策略 |

### 优化模式
```yaml
optimization_modes:
  normal:
    compression: false
    cache: true
    preload_skills: [P0]
  
  compressed:
    compression: true
    cache: true
    preload_skills: [P0]
  
  minimal:
    compression: true
    cache: true
    preload_skills: []
    max_output: 500
```

## 异常处理

| 异常 | 处理 |
|------|------|
| 预算超限 | 截断输出 + 标注 |
| 缓存失效 | 重新计算 |
| 压缩失败 | 使用原内容 |

## 维护方式
- 调整预算: 修改预算分配表
- 新增策略: 添加到优化策略表
- 调整缓存: 更新缓存配置

## 引用文件
- `optimization/BUDGET_POLICY.md` - 预算策略
- `optimization/CACHE_STRATEGY.md` - 缓存策略
- `optimization/LAZY_LOADING.md` - 延迟加载
