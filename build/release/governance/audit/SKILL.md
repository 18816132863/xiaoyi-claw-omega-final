# L5 治理层 - 审计模块

## 模块概述

本模块从 `llm-memory-integration` 技能集成，提供反馈学习、结果解释和结果摘要能力。

## 模块列表

| 模块 | 文件 | 功能 |
|------|------|------|
| 反馈学习 | `feedback.py` | 记录用户点击优化排序 |
| 结果解释 | `explainer.py` | LLM 生成结果解释 |
| 结果摘要 | `summarizer.py` | LLM 生成结果摘要 |

## 反馈学习 (feedback.py)

### 功能
- 记录用户点击
- 优化排序权重
- A/B 测试支持

### 使用示例
```python
from governance.audit.feedback import FeedbackLearner

learner = FeedbackLearner(db_path="~/.openclaw/feedback.db")

# 记录点击
learner.record_click(
    query="推送规则",
    result_id=1,
    position=0,
    clicked=True
)

# 获取优化权重
weights = learner.get_optimized_weights("推送规则")
# weights = {"vector": 0.6, "fts": 0.4}  # 根据用户反馈调整
```

## 结果解释 (explainer.py)

### 功能
- LLM 生成结果解释
- 多语言支持
- 可定制 prompt

### 使用示例
```python
from governance.audit.explainer import ResultExplainer

explainer = ResultExplainer(
    llm_client=llm_client
)

explanation = explainer.explain(
    query="用户偏好设置",
    results=[{"content": "..."}, {"content": "..."}]
)
# explanation = "这些记忆记录了用户对AI行为模式、输出格式..."
```

## 结果摘要 (summarizer.py)

### 功能
- LLM 生成结果摘要
- 时间线整理
- 关键信息提取

### 使用示例
```python
from governance.audit.summarizer import ResultSummarizer

summarizer = ResultSummarizer(
    llm_client=llm_client
)

summary = summarizer.summarize(
    query="如何配置记忆系统",
    results=[{"content": "...", "date": "2026-04-04"}, ...]
)
# summary = "用户于2026年4月4日至5日完成OpenClaw记忆系统配置..."
```

## 性能指标

| 操作 | 耗时 |
|------|------|
| 反馈记录 | < 10ms |
| 结果解释 | 1-3s (LLM) |
| 结果摘要 | 1-3s (LLM) |

## 来源
- 集成自: llm-memory-integration v2.2.0
- 作者: @xkzs2007
- 链接: https://clawhub.ai/xkzs2007/llm-memory-integration
