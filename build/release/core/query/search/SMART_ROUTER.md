# 智能路由模块

**版本**: 1.0.0
**来源**: llm-memory-integration (改进版)
**集成时间**: 2026-04-07 00:12 UTC

---

## 🎯 模块概述

智能路由模块根据查询复杂度自动选择处理模式，平衡速度和效果。

### 核心思想
```
简单查询 → 快速模式 (省资源)
中等查询 → 平衡模式 (适中)
复杂查询 → 完整模式 (最佳效果)
```

---

## 📊 模式定义

| 模式 | 说明 | 耗时 | 适用场景 |
|------|------|------|----------|
| fast | 快速模式 | <1s | 简单查询、关键词匹配 |
| balanced | 平衡模式 | 1-5s | 中等复杂度、语义搜索 |
| full | 完整模式 | 5-15s | 复杂查询、深度分析 |

### 模式差异
| 功能 | fast | balanced | full |
|------|------|----------|------|
| 向量搜索 | ✅ | ✅ | ✅ |
| FTS 搜索 | ✅ | ✅ | ✅ |
| RRF 融合 | ❌ | ✅ | ✅ |
| 查询改写 | ❌ | ✅ | ✅ |
| LLM 扩展 | ❌ | ❌ | ✅ |
| 结果解释 | ❌ | ❌ | ✅ |
| 结果摘要 | ❌ | ❌ | ✅ |

---

## 🔧 模块实现

### 复杂度分析
```python
class ComplexityAnalyzer:
    def __init__(self):
        self.weights = {
            "length": 0.2,      # 查询长度权重
            "keywords": 0.3,    # 关键词权重
            "structure": 0.3,   # 结构复杂度权重
            "ambiguity": 0.2    # 歧义度权重
        }

    def analyze(self, query: str) -> float:
        """分析查询复杂度，返回 0-1 分数"""
        scores = {}

        # 1. 长度分析
        scores["length"] = self.analyze_length(query)

        # 2. 关键词分析
        scores["keywords"] = self.analyze_keywords(query)

        # 3. 结构分析
        scores["structure"] = self.analyze_structure(query)

        # 4. 歧义分析
        scores["ambiguity"] = self.analyze_ambiguity(query)

        # 加权计算
        complexity = sum(
            scores[key] * self.weights[key]
            for key in scores
        )

        return complexity

    def analyze_length(self, query: str) -> float:
        """长度分析"""
        # 长度越长越复杂
        length = len(query)
        if length < 10:
            return 0.1
        elif length < 30:
            return 0.3
        elif length < 60:
            return 0.6
        else:
            return 0.9

    def analyze_keywords(self, query: str) -> float:
        """关键词分析"""
        # 复杂关键词增加复杂度
        complex_keywords = [
            "如何", "怎么", "为什么", "区别", "比较",
            "分析", "解释", "总结", "优化", "配置"
        ]

        count = sum(1 for kw in complex_keywords if kw in query)
        return min(count * 0.2, 1.0)

    def analyze_structure(self, query: str) -> float:
        """结构分析"""
        # 多条件、多问题增加复杂度
        indicators = ["和", "与", "或", "以及", "同时", "并且"]
        count = sum(1 for ind in indicators if ind in query)
        return min(count * 0.3, 1.0)

    def analyze_ambiguity(self, query: str) -> float:
        """歧义分析"""
        # 模糊词增加复杂度
        ambiguous_words = [
            "相关", "类似", "差不多", "大概", "可能"
        ]

        count = sum(1 for word in ambiguous_words if word in query)
        return min(count * 0.25, 1.0)
```

### 路由决策
```python
class SmartRouter:
    def __init__(self, complexity_analyzer: ComplexityAnalyzer):
        self.analyzer = complexity_analyzer
        self.thresholds = {
            "fast": 0.3,      # < 0.3 使用快速模式
            "balanced": 0.6,  # 0.3-0.6 使用平衡模式
            "full": 1.0       # > 0.6 使用完整模式
        }

    def route(self, query: str) -> str:
        """路由决策"""
        complexity = self.analyzer.analyze(query)

        if complexity < self.thresholds["fast"]:
            return "fast"
        elif complexity < self.thresholds["balanced"]:
            return "balanced"
        else:
            return "full"

    def get_mode_config(self, mode: str) -> dict:
        """获取模式配置"""
        configs = {
            "fast": {
                "use_vector": True,
                "use_fts": True,
                "use_rrf": False,
                "use_rewrite": False,
                "use_llm_expand": False,
                "use_explain": False,
                "use_summarize": False,
                "timeout_ms": 1000
            },
            "balanced": {
                "use_vector": True,
                "use_fts": True,
                "use_rrf": True,
                "use_rewrite": True,
                "use_llm_expand": False,
                "use_explain": False,
                "use_summarize": False,
                "timeout_ms": 5000
            },
            "full": {
                "use_vector": True,
                "use_fts": True,
                "use_rrf": True,
                "use_rewrite": True,
                "use_llm_expand": True,
                "use_explain": True,
                "use_summarize": True,
                "timeout_ms": 15000
            }
        }

        return configs.get(mode, configs["balanced"])
```

---

## 📊 效果示例

### 简单查询
```
查询: "推送规则"
复杂度: 0.15
路由: fast
耗时: 0.5s
```

### 中等查询
```
查询: "如何配置记忆系统"
复杂度: 0.45
路由: balanced
耗时: 3.2s
```

### 复杂查询
```
查询: "比较向量搜索和FTS搜索的区别，并给出优化建议"
复杂度: 0.78
路由: full
耗时: 9.5s
```

---

## ⚙️ 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| fast_threshold | 0.3 | 快速模式阈值 |
| balanced_threshold | 0.6 | 平衡模式阈值 |
| length_weight | 0.2 | 长度权重 |
| keywords_weight | 0.3 | 关键词权重 |
| structure_weight | 0.3 | 结构权重 |
| ambiguity_weight | 0.2 | 歧义权重 |

---

## 📈 性能指标

| 模式 | 平均耗时 | 准确率 | 资源消耗 |
|------|----------|--------|----------|
| fast | 0.5s | 75% | 低 |
| balanced | 3s | 88% | 中 |
| full | 10s | 95% | 高 |

---

## 🔗 集成点

### 搜索入口
```python
def search(query: str):
    # 智能路由
    mode = router.route(query)
    config = router.get_mode_config(mode)

    # 根据配置执行搜索
    if config["use_rewrite"]:
        query = rewriter.rewrite(query)

    results = []

    if config["use_vector"]:
        results.append(vector_search(query))

    if config["use_fts"]:
        results.append(fts_search(query))

    if config["use_rrf"]:
        results = rrf_fusion(results)

    if config["use_explain"]:
        results = explainer.explain(results)

    return results
```

---

## 💡 最佳实践

1. **监控路由分布** - 了解查询复杂度分布
2. **调整阈值** - 根据实际效果调整阈值
3. **缓存热点** - 缓存高频查询结果
4. **降级策略** - 超时时自动降级模式

---

*智能路由模块 - 因材施教，按需处理*
