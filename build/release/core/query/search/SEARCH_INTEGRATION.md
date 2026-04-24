# 搜索模块集成指南

**版本**: 1.0.0
**集成时间**: 2026-04-07 00:12 UTC

---

## 🎯 集成概述

将提取的搜索模块集成到终极鸽子王系统中。

---

## 📁 模块清单

| 模块 | 文件 | 功能 |
|------|------|------|
| RRF 融合 | RRF_FUSION.md | 多源结果融合排序 |
| 渐进式启用 | PROGRESSIVE_ENABLE.md | 分阶段功能启用 |
| 查询改写 | QUERY_REWRITER.md | 拼写纠正+同义词扩展 |
| 反馈学习 | FEEDBACK_LEARNING.md | 用户行为学习 |
| 智能路由 | SMART_ROUTER.md | 复杂度自适应路由 |

---

## 🏗️ 集成架构

```
用户查询
    ↓
┌─────────────────────────────────────────────────────────┐
│                    智能路由 (SMART_ROUTER)               │
│  分析复杂度 → 选择模式 (fast/balanced/full)              │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│                    查询改写 (QUERY_REWRITER)             │
│  拼写纠正 → 同义词扩展 → 语义扩展                        │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│                    多源搜索                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  向量搜索     │  │  FTS 搜索    │  │  记忆搜索     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│                    RRF 融合 (RRF_FUSION)                 │
│  多源结果融合 → 综合排序                                 │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│                    反馈学习 (FEEDBACK_LEARNING)          │
│  应用历史反馈 → 优化排序                                 │
└─────────────────────────────────────────────────────────┘
    ↓
返回结果
```

---

## 🔧 集成配置

```json
{
  "search": {
    "version": "1.0.0",

    "progressive": {
      "enabled": true,
      "stages": {
        "P0": { "enabled": true, "modules": ["router", "rrf", "dedup"] },
        "P1": { "enabled": true, "modules": ["rewriter", "understand"] },
        "P2": { "enabled": false, "modules": ["feedback", "history"] },
        "P3": { "enabled": false, "modules": ["explainer", "summarizer"] }
      }
    },

    "router": {
      "enabled": true,
      "thresholds": {
        "fast": 0.3,
        "balanced": 0.6
      }
    },

    "rewriter": {
      "enabled": true,
      "spell_correct": true,
      "synonym_expand": true,
      "semantic_expand": false
    },

    "rrf": {
      "enabled": true,
      "k": 60,
      "weights": {
        "vector": 1.0,
        "fts": 0.8,
        "memory": 1.2
      }
    },

    "feedback": {
      "enabled": false,
      "weight": 0.3,
      "decay_factor": 0.95
    }
  }
}
```

---

## 📋 使用示例

### 基础搜索
```python
from core.search import SearchEngine

engine = SearchEngine(config)

# 自动路由
results = engine.search("推送规则")

# 指定模式
results = engine.search("推送规则", mode="fast")
```

### 带反馈搜索
```python
# 搜索
results = engine.search("记忆配置")

# 记录用户点击
engine.record_feedback("记忆配置", results[0].id, "click")
```

### 渐进式管理
```python
from core.search import ProgressiveManager

manager = ProgressiveManager()

# 查看状态
manager.status()

# 启用阶段
manager.enable_stage("P2")

# 禁用阶段
manager.disable_stage("P3")
```

---

## 📊 性能预期

| 指标 | 目标 | 说明 |
|------|------|------|
| 快速模式延迟 | <1s | 简单查询 |
| 平衡模式延迟 | <5s | 中等查询 |
| 完整模式延迟 | <15s | 复杂查询 |
| 召回率 | >90% | 相关结果覆盖 |
| 准确率 | >85% | 首条结果准确 |

---

## 🔗 与现有系统集成

### 与记忆系统集成
```
搜索模块调用 memory_search 工具
结果与向量搜索结果 RRF 融合
统一返回给用户
```

### 与治理系统集成
```
搜索操作记录审计日志
反馈数据遵循数据治理规则
配置变更需审批
```

### 与安全系统集成
```
搜索请求经过权限检查
敏感数据过滤
异常查询检测
```

---

## ⚠️ 注意事项

1. **渐进式启用** - 建议先启用 P0，验证后再启用其他阶段
2. **资源监控** - 完整模式消耗更多资源，注意监控
3. **反馈数据** - 启用反馈学习前确保隐私合规
4. **缓存策略** - 高频查询建议启用缓存

---

*搜索模块集成指南 - 统一搜索，智能融合*
