# RRF 融合算法

**版本**: 1.0.0
**来源**: llm-memory-integration (改进版)
**集成时间**: 2026-04-07 00:12 UTC

---

## 🎯 算法概述

RRF (Reciprocal Rank Fusion) 是一种将多个排序结果融合的算法，用于混合检索场景。

### 核心思想
```
多个检索系统返回各自的排序列表
RRF 根据每个列表中的排名位置计算融合分数
最终得到一个综合排序结果
```

---

## 📐 算法公式

### RRF 分数计算
```
RRF_score(d) = Σ (1 / (k + rank_i(d)))
```

其中：
- `d` = 文档
- `k` = 平滑参数 (默认 60)
- `rank_i(d)` = 文档 d 在第 i 个排序列表中的排名

### 参数说明
| 参数 | 默认值 | 说明 |
|------|--------|------|
| k | 60 | 平滑参数，减少排名差异的影响 |
| top_k | 20 | 每个检索系统返回的文档数 |

---

## 🔧 算法实现

### 伪代码
```
function rrf_fusion(rankings: List[List[Document]], k=60):
    scores = {}

    for ranking in rankings:
        for rank, doc in enumerate(ranking, start=1):
            if doc not in scores:
                scores[doc] = 0
            scores[doc] += 1 / (k + rank)

    # 按分数降序排序
    sorted_docs = sorted(scores.items(), key=lambda x: -x[1])

    return sorted_docs
```

### Python 实现
```python
def rrf_fusion(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """
    RRF 融合算法

    Args:
        rankings: 多个排序列表，每个列表包含文档ID
        k: 平滑参数，默认60

    Returns:
        融合后的排序列表，包含 (doc_id, score) 元组
    """
    scores = {}

    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            if doc_id not in scores:
                scores[doc_id] = 0
            scores[doc_id] += 1.0 / (k + rank)

    # 按分数降序排序
    sorted_results = sorted(scores.items(), key=lambda x: -x[1])

    return sorted_results
```

---

## 📊 应用场景

### 混合检索
```
向量搜索结果: [A, B, C, D, E]
FTS搜索结果:   [C, A, F, B, G]

RRF 融合:
- A: 1/(60+1) + 1/(60+2) = 0.0164 + 0.0159 = 0.0323
- B: 1/(60+2) + 1/(60+4) = 0.0159 + 0.0156 = 0.0315
- C: 1/(60+3) + 1/(60+1) = 0.0159 + 0.0164 = 0.0323
- D: 1/(60+4) = 0.0156
- E: 1/(60+5) = 0.0154
- F: 1/(60+3) = 0.0159
- G: 1/(60+5) = 0.0154

最终排序: [A, C, B, F, D, E, G]
```

### 多模型融合
```
模型1排序: [A, B, C]
模型2排序: [B, A, D]
模型3排序: [C, A, B]

RRF 融合后得到综合最优排序
```

---

## ⚙️ 参数调优

### k 值影响
| k 值 | 效果 | 适用场景 |
|------|------|----------|
| 20 | 排名靠前的文档权重更大 | 精确匹配 |
| 60 | 平衡 | 通用场景 |
| 100 | 排名差异影响更小 | 召回优先 |

### 权重扩展
```python
def weighted_rrf_fusion(
    rankings: list[list[str]],
    weights: list[float],
    k: int = 60
) -> list[tuple[str, float]]:
    """
    带权重的 RRF 融合

    Args:
        rankings: 多个排序列表
        weights: 每个列表的权重
        k: 平滑参数
    """
    scores = {}

    for ranking, weight in zip(rankings, weights):
        for rank, doc_id in enumerate(ranking, start=1):
            if doc_id not in scores:
                scores[doc_id] = 0
            scores[doc_id] += weight / (k + rank)

    return sorted(scores.items(), key=lambda x: -x[1])
```

---

## 📈 性能指标

| 指标 | 值 |
|------|-----|
| 时间复杂度 | O(n * m) |
| 空间复杂度 | O(n) |
| n = 文档数, m = 排序列表数 |

---

## 🔗 集成点

### 记忆搜索
```
用户查询
    ↓
向量搜索 → 排序1
FTS搜索  → 排序2
    ↓
RRF 融合 → 最终排序
    ↓
返回结果
```

### 技能搜索
```
技能查询
    ↓
语义匹配 → 排序1
关键词匹配 → 排序2
使用频率 → 排序3
    ↓
RRF 融合 → 最终排序
    ↓
返回技能列表
```

---

## 📋 使用示例

```python
# 向量搜索结果
vector_results = ["doc1", "doc3", "doc5", "doc7", "doc9"]

# FTS 搜索结果
fts_results = ["doc2", "doc1", "doc4", "doc3", "doc6"]

# RRF 融合
final_ranking = rrf_fusion([vector_results, fts_results], k=60)

# 输出: [("doc1", 0.0323), ("doc3", 0.0315), ...]
```

---

*RRF 融合算法 - 多源融合，智能排序*
