# SMART_ROUTING.md - 智能路由模式

## 目的
定义智能路由模式，根据查询复杂度自动选择最优检索策略，平衡延迟和准确率。

## 适用范围
所有检索场景，包括记忆检索、文档检索、知识检索。

---

## 一、路由模式定义

### 1.1 模式分类
| 模式 | 代码 | 策略 | 延迟目标 | 准确率目标 | 适用场景 |
|------|------|------|----------|------------|----------|
| 快速模式 | fast | 仅向量检索 | < 100ms | > 85% | 简单查询 |
| 均衡模式 | balanced | 向量 + FTS | < 500ms | > 92% | 一般查询 |
| 完整模式 | full | 向量 + FTS + LLM | < 3s | > 98% | 复杂查询 |
| 自适应模式 | auto | 智能选择 | 动态 | 动态 | 所有场景 |

### 1.2 模式对比
| 维度 | fast | balanced | full | auto |
|------|------|----------|------|------|
| 检索路数 | 1 | 2 | 3+ | 动态 |
| 平均延迟 | 50ms | 300ms | 2000ms | 动态 |
| 准确率 | 85% | 92% | 98% | 90-98% |
| Token 消耗 | 低 | 中 | 高 | 动态 |
| 适用比例 | 60% | 30% | 10% | 100% |

---

## 二、查询复杂度分析

### 2.1 复杂度因子
| 因子 | 权重 | 说明 | 计算方法 |
|------|------|------|----------|
| 查询长度 | 0.15 | 字符数/词数 | len(query) / 100 |
| 实体数量 | 0.20 | 命名实体数 | entity_count / 5 |
| 意图复杂度 | 0.25 | 意图类型 | 意图评分 |
| 关键词密度 | 0.15 | 关键词比例 | keyword_ratio |
| 上下文依赖 | 0.15 | 需要上下文 | context_score |
| 历史相似度 | 0.10 | 历史查询相似 | similarity_score |

### 2.2 复杂度计算
```python
def calculate_complexity(query, context=None, history=None):
    """
    计算查询复杂度分数 (0-1)
    
    Args:
        query: 用户查询
        context: 上下文信息
        history: 历史查询
    
    Returns:
        float: 复杂度分数 (0=简单, 1=复杂)
    """
    score = 0.0
    
    # 1. 查询长度 (0.15)
    length_score = min(len(query) / 100, 1.0)
    score += length_score * 0.15
    
    # 2. 实体数量 (0.20)
    entities = extract_entities(query)
    entity_score = min(len(entities) / 5, 1.0)
    score += entity_score * 0.20
    
    # 3. 意图复杂度 (0.25)
    intent = classify_intent(query)
    intent_scores = {
        'simple_lookup': 0.1,
        'fact_retrieval': 0.3,
        'comparison': 0.5,
        'analysis': 0.7,
        'synthesis': 0.9,
        'multi_step': 1.0
    }
    intent_score = intent_scores.get(intent, 0.5)
    score += intent_score * 0.25
    
    # 4. 关键词密度 (0.15)
    keywords = extract_keywords(query)
    keyword_ratio = len(keywords) / max(len(query.split()), 1)
    keyword_score = min(keyword_ratio * 2, 1.0)
    score += keyword_score * 0.15
    
    # 5. 上下文依赖 (0.15)
    context_score = 0.0
    if context:
        # 检查是否引用上下文
        if has_context_reference(query):
            context_score = 0.8
        # 检查是否需要上下文理解
        elif needs_context_understanding(query):
            context_score = 0.5
    score += context_score * 0.15
    
    # 6. 历史相似度 (0.10)
    history_score = 0.0
    if history:
        # 检查历史相似查询
        similar = find_similar_queries(query, history)
        if similar:
            # 相似查询多 = 可能是常见问题 = 简单
            history_score = 1.0 - min(len(similar) / 5, 1.0)
    score += history_score * 0.10
    
    return min(score, 1.0)
```

### 2.3 复杂度分级
| 级别 | 分数范围 | 推荐模式 | 说明 |
|------|----------|----------|------|
| L1-简单 | 0.0 - 0.3 | fast | 单一意图，关键词明确 |
| L2-一般 | 0.3 - 0.6 | balanced | 多实体，需要融合检索 |
| L3-复杂 | 0.6 - 0.8 | balanced/full | 多意图，需要深度理解 |
| L4-极复杂 | 0.8 - 1.0 | full | 多步骤，需要 LLM 重排 |

---

## 三、路由决策

### 3.1 决策流程
```
用户查询
    ↓
┌─────────────────────────────────────┐
│ 1. 查询分析                          │
│    - 意图识别                        │
│    - 实体提取                        │
│    - 复杂度计算                      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. 模式选择                          │
│    - 基于复杂度                      │
│    - 基于用户偏好                    │
│    - 基于系统负载                    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. 检索执行                          │
│    - 按选定模式执行                  │
│    - 监控执行状态                    │
│    - 动态调整策略                    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. 结果评估                          │
│    - 评估结果质量                    │
│    - 记录路由效果                    │
│    - 反馈学习                        │
└─────────────────────────────────────┘
    ↓
返回结果
```

### 3.2 路由规则
```yaml
routing_rules:
  by_complexity:
    description: "基于复杂度路由"
    rules:
      - range: [0.0, 0.3]
        mode: fast
        confidence: 0.9
      
      - range: [0.3, 0.6]
        mode: balanced
        confidence: 0.85
      
      - range: [0.6, 0.8]
        mode: balanced
        fallback: full
        fallback_condition: "result_count < 5"
      
      - range: [0.8, 1.0]
        mode: full
        confidence: 0.95
  
  by_intent:
    description: "基于意图路由"
    rules:
      - intent: simple_lookup
        mode: fast
      
      - intent: fact_retrieval
        mode: balanced
      
      - intent: comparison
        mode: balanced
      
      - intent: analysis
        mode: full
      
      - intent: synthesis
        mode: full
  
  by_user_preference:
    description: "基于用户偏好路由"
    rules:
      - preference: speed_first
        mode: fast
        override: true
      
      - preference: quality_first
        mode: full
        override: true
      
      - preference: balanced
        mode: auto
        override: false
```

### 3.3 动态调整
```yaml
dynamic_adjustment:
  load_aware:
    description: "负载感知调整"
    enabled: true
    rules:
      - condition: "system_load > 80%"
        action: "downgrade_mode"
        example: "full → balanced"
      
      - condition: "system_load > 90%"
        action: "force_fast"
        exception: "critical_queries"
  
  result_aware:
    description: "结果感知调整"
    enabled: true
    rules:
      - condition: "fast_result_score < 0.5"
        action: "upgrade_mode"
        example: "fast → balanced"
      
      - condition: "result_count == 0"
        action: "upgrade_mode"
        example: "balanced → full"
  
  time_aware:
    description: "时间感知调整"
    enabled: true
    rules:
      - condition: "latency > target * 1.5"
        action: "downgrade_next_similar"
```

---

## 四、各模式详细配置

### 4.1 快速模式 (fast)
```yaml
fast_mode:
  description: "快速检索模式"
  
  routes:
    - vector_search
  
  params:
    vector:
      top_k: 20
      min_score: 0.3
      timeout_ms: 100
  
  pipeline:
    - query_embedding
    - vector_search
    - score_filter
    - return_results
  
  fallback:
    enabled: true
    condition: "result_count < 3 or max_score < 0.5"
    action: "upgrade_to_balanced"
  
  performance:
    target_latency_ms: 100
    target_accuracy: 0.85
```

### 4.2 均衡模式 (balanced)
```yaml
balanced_mode:
  description: "均衡检索模式"
  
  routes:
    - vector_search
    - fts_search
  
  params:
    vector:
      top_k: 30
      min_score: 0.25
      timeout_ms: 200
    
    fts:
      top_k: 30
      min_score: 0.1
      timeout_ms: 100
  
  fusion:
    method: rrf
    k: 60
    weights:
      vector: 0.6
      fts: 0.4
  
  pipeline:
    - query_preprocess
    - parallel_search
    - rrf_fusion
    - dedup
    - return_results
  
  fallback:
    enabled: true
    condition: "result_count < 5 or max_score < 0.6"
    action: "upgrade_to_full"
  
  performance:
    target_latency_ms: 500
    target_accuracy: 0.92
```

### 4.3 完整模式 (full)
```yaml
full_mode:
  description: "完整检索模式"
  
  routes:
    - vector_search
    - fts_search
    - llm_rerank
  
  params:
    vector:
      top_k: 50
      min_score: 0.2
      timeout_ms: 300
    
    fts:
      top_k: 50
      min_score: 0.05
      timeout_ms: 200
    
    llm_rerank:
      top_k: 20
      batch_size: 5
      timeout_ms: 2000
  
  fusion:
    method: rrf
    k: 60
    weights:
      vector: 0.4
      fts: 0.3
      llm: 0.3
  
  pipeline:
    - query_preprocess
    - query_understand
    - parallel_search
    - initial_fusion
    - llm_rerank
    - final_fusion
    - dedup
    - return_results
  
  performance:
    target_latency_ms: 3000
    target_accuracy: 0.98
```

### 4.4 自适应模式 (auto)
```yaml
auto_mode:
  description: "自适应检索模式"
  
  strategy:
    - analyze_complexity
    - select_mode
    - execute_with_fallback
    - evaluate_and_learn
  
  mode_selection:
    method: "complexity_based"
    thresholds:
      fast: 0.3
      balanced: 0.6
      full: 0.8
  
  learning:
    enabled: true
    method: "online"
    update_rate: 0.01
  
  performance:
    target_latency_ms: dynamic
    target_accuracy: 0.90-0.98
```

---

## 五、意图识别

### 5.1 意图分类
| 意图 | 代码 | 特征 | 复杂度 |
|------|------|------|--------|
| 简单查询 | simple_lookup | 单一关键词，明确目标 | 0.1 |
| 事实检索 | fact_retrieval | 询问事实，需要精确答案 | 0.3 |
| 比较 | comparison | 比较、对比、差异 | 0.5 |
| 分析 | analysis | 分析、解释、原因 | 0.7 |
| 综合 | synthesis | 总结、归纳、整合 | 0.9 |
| 多步骤 | multi_step | 多个问题，需要分解 | 1.0 |

### 5.2 意图识别规则
```yaml
intent_rules:
  simple_lookup:
    patterns:
      - "^什么是"
      - "^定义"
      - "^查找"
      - "^搜索"
    keywords:
      - "定义"
      - "是什么"
      - "查找"
  
  fact_retrieval:
    patterns:
      - "什么时候"
      - "在哪里"
      - "有多少"
      - "谁"
    keywords:
      - "时间"
      - "地点"
      - "数量"
      - "人物"
  
  comparison:
    patterns:
      - ".*和.*的区别"
      - ".*和.*的比较"
      - "哪个更好"
      - "对比"
    keywords:
      - "区别"
      - "比较"
      - "对比"
      - "差异"
  
  analysis:
    patterns:
      - "为什么"
      - "原因"
      - "分析"
      - "解释"
    keywords:
      - "原因"
      - "分析"
      - "解释"
      - "原理"
  
  synthesis:
    patterns:
      - "总结"
      - "归纳"
      - "整合"
      - "概括"
    keywords:
      - "总结"
      - "归纳"
      - "整合"
      - "概括"
  
  multi_step:
    patterns:
      - "首先.*然后"
      - "第一步.*第二步"
      - "多个问题"
    indicators:
      - multiple_questions
      - sequential_keywords
```

---

## 六、性能监控

### 6.1 监控指标
| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 路由准确率 | 模式选择正确率 | < 85% |
| 平均延迟 | 各模式平均延迟 | > 目标 1.5x |
| 模式分布 | 各模式使用比例 | 异常偏离 |
| 升级率 | 模式升级比例 | > 30% |
| 降级率 | 模式降级比例 | > 20% |

### 6.2 模式统计
```yaml
mode_statistics:
  metrics:
    - mode_usage_ratio
    - mode_latency_avg
    - mode_accuracy_avg
    - mode_upgrade_count
    - mode_downgrade_count
  
  reporting:
    interval: 3600
    include:
      - 模式使用分布
      - 延迟分布
      - 准确率分布
      - 升级/降级统计
```

---

## 七、学习优化

### 7.1 在线学习
```yaml
online_learning:
  enabled: true
  
  signals:
    - user_satisfaction
    - result_click_rate
    - query_reformulation
    - explicit_feedback
  
  update:
    method: "gradient_descent"
    rate: 0.01
    batch_size: 100
  
  storage:
    path: "~/.openclaw/memory/routing_model.json"
```

### 7.2 A/B 测试
```yaml
ab_testing:
  enabled: true
  
  experiments:
    - name: "complexity_threshold_tuning"
      variants:
        - control: {fast: 0.3, balanced: 0.6}
        - variant_a: {fast: 0.25, balanced: 0.55}
        - variant_b: {fast: 0.35, balanced: 0.65}
      metrics: [latency, accuracy, satisfaction]
      traffic: 10%
```

---

## 八、配置汇总

### 8.1 完整配置
```json
{
  "smart_routing": {
    "enabled": true,
    "default_mode": "auto",
    
    "complexity": {
      "factors": {
        "query_length": 0.15,
        "entity_count": 0.20,
        "intent_complexity": 0.25,
        "keyword_density": 0.15,
        "context_dependency": 0.15,
        "history_similarity": 0.10
      },
      "thresholds": {
        "fast": 0.3,
        "balanced": 0.6,
        "full": 0.8
      }
    },
    
    "modes": {
      "fast": {
        "routes": ["vector"],
        "target_latency_ms": 100,
        "target_accuracy": 0.85
      },
      "balanced": {
        "routes": ["vector", "fts"],
        "target_latency_ms": 500,
        "target_accuracy": 0.92
      },
      "full": {
        "routes": ["vector", "fts", "llm"],
        "target_latency_ms": 3000,
        "target_accuracy": 0.98
      }
    },
    
    "dynamic_adjustment": {
      "load_aware": true,
      "result_aware": true,
      "time_aware": true
    },
    
    "learning": {
      "enabled": true,
      "online": true,
      "ab_testing": true
    }
  }
}
```

---

## 九、与其他模块联动

| 模块 | 联动方式 |
|------|----------|
| optimization/RRF_FUSION.md | 路由选择使用 RRF 融合 |
| optimization/QUERY_OPTIMIZATION.md | 查询优化配合路由 |
| optimization/PERFORMANCE_MONITORING.md | 监控路由性能 |
| auto_upgrade/SYSTEM_STATUS_REPORT.md | 报告路由统计 |

---

## 版本
- 版本: 1.0.0
- 更新时间: 2026-04-07
- 下次评审: 2026-07-07
