# RRF_FUSION.md - RRF 融合检索算法

## 目的
定义 RRF (Reciprocal Rank Fusion) 融合检索算法，实现多路检索结果的最优融合排序。

## 适用范围
所有需要多路检索融合的场景，包括记忆检索、文档检索、知识检索。

---

## 一、RRF 算法原理

### 1.1 算法定义
RRF 是一种简单而有效的多路检索融合算法，通过倒数排名融合多个检索系统的结果。

**核心公式**：
```
RRF_score(d) = Σ (1 / (k + rank_i(d)))
```

其中：
- `d`：文档/记忆片段
- `rank_i(d)`：文档在第 i 个检索系统中的排名
- `k`：平滑常数（默认 60）

### 1.2 算法优势
| 优势 | 说明 |
|------|------|
| 无需分数归一化 | 直接使用排名，避免分数尺度问题 |
| 对异常值鲁棒 | 排名不受极端分数影响 |
| 简单高效 | 计算复杂度低，易于实现 |
| 效果优异 | 在多种场景下表现优秀 |

### 1.3 参数说明
| 参数 | 默认值 | 说明 | 调优建议 |
|------|--------|------|----------|
| k | 60 | 平滑常数 | 40-80 范围内效果稳定 |
| weights | 均等 | 各路检索权重 | 根据检索质量调整 |

---

## 二、检索路数定义

### 2.1 检索路数
| 路数 | 类型 | 说明 | 权重 |
|------|------|------|------|
| R1 | 向量检索 | 语义相似度匹配 | 0.5 |
| R2 | FTS 检索 | 关键词精确匹配 | 0.3 |
| R3 | LLM 重排 | 语义理解重排 | 0.15 |
| R4 | 时间衰减 | 时序相关性 | 0.05 |

### 2.2 各路检索说明

#### R1 向量检索
```yaml
vector_search:
  provider: voyage
  model: voyage-4-large
  dimension: 1024
  
  params:
    top_k: 50
    min_score: 0.3
    max_distance: 0.8
  
  index:
    type: sqlite_vec
    table: memory_vectors
    index_type: ivf
    nlist: 100
```

#### R2 FTS 检索
```yaml
fts_search:
  engine: sqlite_fts5
  
  params:
    top_k: 50
    min_score: 0.1
    bm25_k1: 1.2
    bm25_b: 0.75
  
  tokenizer:
    type: unicode61
    remove_diacritics: 1
    tokenchars: _
```

#### R3 LLM 重排
```yaml
llm_rerank:
  model: default
  max_tokens: 150
  
  params:
    top_k: 20          # 只重排 top 20
    batch_size: 5
    timeout_ms: 5000
  
  prompt_template: |
    对以下检索结果进行相关性打分（0-10分）：
    查询：{query}
    结果：{result}
    只返回分数，不要解释。
```

#### R4 时间衰减
```yaml
time_decay:
  enabled: true
  
  params:
    half_life_days: 30
    min_weight: 0.1
  
  formula: "weight = exp(-ln(2) * age_days / half_life)"
```

---

## 三、RRF 融合流程

### 3.1 融合流程
```
用户查询
    ↓
┌─────────────────────────────────────┐
│ 1. 查询预处理                        │
│    - 意图识别                        │
│    - 实体提取                        │
│    - 查询扩展                        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. 多路并行检索                      │
│    - R1 向量检索                     │
│    - R2 FTS 检索                     │
│    - R3 LLM 重排（可选）             │
│    - R4 时间衰减                     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. RRF 融合排序                      │
│    - 收集各路结果                    │
│    - 计算排名                        │
│    - RRF 分数计算                    │
│    - 加权融合                        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. 后处理                            │
│    - 去重                            │
│    - 分数归一化                      │
│    - 结果截断                        │
│    - 元数据补充                      │
└─────────────────────────────────────┘
    ↓
返回融合结果
```

### 3.2 RRF 分数计算
```python
def rrf_score(doc_id, rankings, k=60, weights=None):
    """
    计算 RRF 融合分数
    
    Args:
        doc_id: 文档ID
        rankings: {路数: {doc_id: rank}} 各路排名
        k: 平滑常数
        weights: {路数: weight} 各路权重
    
    Returns:
        float: RRF 融合分数
    """
    if weights is None:
        weights = {r: 1.0 / len(rankings) for r in rankings}
    
    score = 0.0
    for route, route_rankings in rankings.items():
        if doc_id in route_rankings:
            rank = route_rankings[doc_id]
            weight = weights.get(route, 1.0)
            score += weight / (k + rank)
    
    return score
```

### 3.3 融合算法实现
```python
def rrf_fusion(results_by_route, k=60, weights=None, top_k=20):
    """
    RRF 融合多路检索结果
    
    Args:
        results_by_route: {路数: [结果列表]} 各路检索结果
        k: RRF 平滑常数
        weights: {路数: weight} 各路权重
        top_k: 返回结果数量
    
    Returns:
        list: 融合后的结果列表
    """
    # 默认权重
    if weights is None:
        weights = {
            'vector': 0.5,
            'fts': 0.3,
            'llm': 0.15,
            'time': 0.05
        }
    
    # 收集所有文档ID
    all_doc_ids = set()
    for route, results in results_by_route.items():
        for result in results:
            all_doc_ids.add(result['id'])
    
    # 计算各路排名
    rankings = {}
    for route, results in results_by_route.items():
        rankings[route] = {}
        for rank, result in enumerate(results, start=1):
            rankings[route][result['id']] = rank
    
    # 计算 RRF 分数
    doc_scores = {}
    for doc_id in all_doc_ids:
        doc_scores[doc_id] = rrf_score(doc_id, rankings, k, weights)
    
    # 排序并返回 top_k
    sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    
    # 构建返回结果
    final_results = []
    for doc_id, score in sorted_docs[:top_k]:
        # 从任一路结果中获取文档详情
        doc_info = None
        for route, results in results_by_route.items():
            for result in results:
                if result['id'] == doc_id:
                    doc_info = result.copy()
                    break
            if doc_info:
                break
        
        if doc_info:
            doc_info['rrf_score'] = score
            doc_info['fusion_rank'] = len(final_results) + 1
            final_results.append(doc_info)
    
    return final_results
```

---

## 四、权重优化

### 4.1 动态权重
```yaml
dynamic_weights:
  enabled: true
  
  strategies:
    by_query_type:
      description: "按查询类型调整权重"
      rules:
        - type: factual
          weights: {vector: 0.4, fts: 0.4, llm: 0.15, time: 0.05}
        - type: semantic
          weights: {vector: 0.6, fts: 0.2, llm: 0.15, time: 0.05}
        - type: keyword
          weights: {vector: 0.3, fts: 0.5, llm: 0.15, time: 0.05}
        - type: recent
          weights: {vector: 0.3, fts: 0.2, llm: 0.1, time: 0.4}
    
    by_result_quality:
      description: "按结果质量调整权重"
      rules:
        - condition: "vector_avg_score > 0.8"
          action: "increase vector weight by 0.1"
        - condition: "fts_result_count < 5"
          action: "decrease fts weight by 0.1"
```

### 4.2 学习权重
```yaml
learned_weights:
  enabled: true
  
  learning:
    method: "online_learning"
    update_rate: 0.01
    min_samples: 100
  
  signals:
    - click_through_rate
    - dwell_time
    - explicit_feedback
    - retry_pattern
  
  storage:
    path: "~/.openclaw/memory/rrf_weights.json"
    update_interval: 3600
```

---

## 五、性能优化

### 5.1 并行检索
```yaml
parallel_retrieval:
  enabled: true
  max_parallel: 4
  
  timeout:
    vector_ms: 500
    fts_ms: 200
    llm_ms: 5000
    total_ms: 3000
  
  fallback:
    on_timeout: "return_partial"
    on_error: "skip_route"
```

### 5.2 结果缓存
```yaml
result_cache:
  enabled: true
  
  levels:
    L1_query:
      description: "查询结果缓存"
      ttl: 300
      max_size: 1000
    
    L2_route:
      description: "单路结果缓存"
      ttl: 600
      max_size: 5000
  
  invalidation:
    on_memory_update: true
    on_config_change: true
```

### 5.3 增量融合
```yaml
incremental_fusion:
  enabled: true
  
  strategy:
    - 先返回快速路结果（vector + fts）
    - 后台计算 LLM 重排
    - 增量更新结果
  
  threshold:
    fast_result_count: 10
    llm_batch_size: 5
```

---

## 六、评估指标

### 6.1 检索质量指标
| 指标 | 说明 | 目标 |
|------|------|------|
| MRR | 平均倒数排名 | > 0.7 |
| NDCG@10 | 归一化折损累积增益 | > 0.8 |
| Recall@20 | 召回率 | > 0.9 |
| Precision@10 | 精确率 | > 0.85 |

### 6.2 性能指标
| 指标 | 说明 | 目标 |
|------|------|------|
| 融合延迟 | RRF 计算时间 | < 10ms |
| 总检索延迟 | 端到端时间 | < 500ms |
| 缓存命中率 | 结果缓存命中 | > 60% |

### 6.3 监控配置
```yaml
monitoring:
  metrics:
    - rrf_latency_ms
    - fusion_score_distribution
    - route_contribution_ratio
    - cache_hit_rate
  
  alerting:
    latency_above_ms: 100
    mrr_below: 0.6
    cache_hit_below: 0.5
```

---

## 七、配置汇总

### 7.1 完整配置
```json
{
  "rrf_fusion": {
    "enabled": true,
    "k": 60,
    "weights": {
      "vector": 0.5,
      "fts": 0.3,
      "llm": 0.15,
      "time": 0.05
    },
    "routes": {
      "vector": {
        "enabled": true,
        "top_k": 50,
        "min_score": 0.3
      },
      "fts": {
        "enabled": true,
        "top_k": 50,
        "min_score": 0.1
      },
      "llm": {
        "enabled": false,
        "top_k": 20,
        "batch_size": 5
      },
      "time": {
        "enabled": true,
        "half_life_days": 30
      }
    },
    "parallel": {
      "enabled": true,
      "max_parallel": 4,
      "timeout_ms": 3000
    },
    "cache": {
      "enabled": true,
      "ttl": 300,
      "max_size": 1000
    },
    "dynamic_weights": {
      "enabled": true,
      "by_query_type": true,
      "by_result_quality": true
    }
  }
}
```

---

## 八、与其他模块联动

| 模块 | 联动方式 |
|------|----------|
| governance/MEMORY_POLICY.md | RRF 用于记忆检索 |
| optimization/QUERY_OPTIMIZATION.md | 查询优化配合 RRF |
| optimization/RESPONSE_CACHE_V2.md | 结果缓存支持 |
| auto_upgrade/SYSTEM_STATUS_REPORT.md | 报告检索性能 |

---

## 版本
- 版本: 1.0.0
- 更新时间: 2026-04-07
- 下次评审: 2026-07-07
