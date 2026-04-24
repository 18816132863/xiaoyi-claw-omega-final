# L1 核心认知层 - 查询处理模块

## 模块概述

本模块从 `llm-memory-integration` 技能集成，提供查询理解、改写和多语言支持能力。

## 模块列表

| 模块 | 文件 | 功能 |
|------|------|------|
| 查询理解 | `understand.py` | 意图识别 + 实体提取 |
| 查询改写 | `rewriter.py` | 拼写纠正 + 同义词扩展 + 语义扩展 |
| 语言检测 | `langdetect.py` | 多语言支持 |

## 查询理解 (understand.py)

### 意图类型
- `search` - 搜索查询
- `config` - 配置查询
- `explain` - 解释查询
- `compare` - 比较查询

### 使用示例
```python
from core.query.understand import QueryUnderstander

understander = QueryUnderstander()
result = understander.analyze("如何配置记忆系统")
# result = {
#     "intent": "config",
#     "entities": ["记忆系统", "配置"],
#     "complexity": "medium"
# }
```

## 查询改写 (rewriter.py)

### 功能
- 拼写纠正
- 同义词扩展
- 语义扩展

### 使用示例
```python
from core.query.rewriter import QueryRewriter

rewriter = QueryRewriter()
result = rewriter.rewrite("推送规责")
# result = {
#     "original": "推送规责",
#     "corrected": "推送规则",
#     "synonyms": ["推送配置", "推送设置"],
#     "semantic_expansions": ["消息推送", "通知规则"]
# }
```

## 语言检测 (langdetect.py)

### 支持语言
- 中文 (zh)
- 英文 (en)
- 日文 (ja)
- 韩文 (ko)
- 自动检测

### 使用示例
```python
from core.query.langdetect import LanguageDetector

detector = LanguageDetector()
lang = detector.detect("Hello world")
# lang = "en"
```

## 性能指标

| 操作 | 耗时 |
|------|------|
| 意图识别 | < 10ms |
| 查询改写 | < 50ms |
| 语言检测 | < 5ms |

## 来源
- 集成自: llm-memory-integration v2.2.0
- 作者: @xkzs2007
- 链接: https://clawhub.ai/xkzs2007/llm-memory-integration
