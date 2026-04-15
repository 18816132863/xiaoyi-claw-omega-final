# 检索策略 - V1.0.0

## 检索模式

### 1. 精确检索
用于查找特定信息，如文件名、日期、人名。

```python
def exact_search(query: str) -> List[Result]:
    return [r for r in memories if query.lower() in r.content.lower()]
```

### 2. 语义检索
用于理解意图，查找相关内容。

```python
def semantic_search(query: str, k: int = 10) -> List[Result]:
    query_vec = embed(query)
    return vector_store.search(query_vec, k)
```

### 3. 混合检索
结合精确和语义检索，提供最佳结果。

```python
def hybrid_search(query: str, k: int = 10) -> List[Result]:
    exact = exact_search(query)
    semantic = semantic_search(query, k)
    return reciprocal_rank_fusion([exact, semantic], k)
```

## 排序算法

### Reciprocal Rank Fusion (RRF)
```python
def rrf(rankings: List[List[Result]], k: int = 60) -> List[Result]:
    scores = defaultdict(float)
    for ranking in rankings:
        for i, result in enumerate(ranking):
            scores[result] += 1 / (k + i + 1)
    
    return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
```

## 查询优化

### 1. 查询扩展
```python
def expand_query(query: str) -> List[str]:
    # 同义词扩展
    synonyms = get_synonyms(query)
    
    # 拼写纠正
    corrected = spell_check(query)
    
    return [query] + synonyms + [corrected]
```

### 2. 查询重写
```python
def rewrite_query(query: str, context: Dict) -> str:
    # 代词消解
    query = resolve_pronouns(query, context)
    
    # 添加上下文
    query = add_context(query, context)
    
    return query
```

## 结果过滤

### 1. 时间过滤
```python
def filter_by_time(results: List[Result], 
                   start: datetime, 
                   end: datetime) -> List[Result]:
    return [r for r in results if start <= r.timestamp <= end]
```

### 2. 相关性过滤
```python
def filter_by_relevance(results: List[Result], 
                        min_score: float = 0.5) -> List[Result]:
    return [r for r in results if r.score >= min_score]
```

## 缓存策略

### 1. 查询缓存
```python
@lru_cache(maxsize=1000)
def cached_search(query: str) -> List[Result]:
    return hybrid_search(query)
```

### 2. 结果缓存
```python
def get_or_search(query: str) -> List[Result]:
    cache_key = hash(query)
    if cache_key in result_cache:
        return result_cache[cache_key]
    
    results = hybrid_search(query)
    result_cache[cache_key] = results
    return results
```
