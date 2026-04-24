# 查询改写模块

**版本**: 1.0.0
**来源**: llm-memory-integration (改进版)
**集成时间**: 2026-04-07 00:12 UTC

---

## 🎯 模块概述

查询改写模块用于优化用户查询，提高检索召回率和准确率。

### 核心能力
```
拼写纠正 → 修正输入错误
同义词扩展 → 增加语义覆盖
语义扩展 → LLM 生成相关词
语言检测 → 多语言支持
```

---

## 📐 改写流程

```
原始查询
    ↓
┌─────────────────────────────────────┐
│ 1. 语言检测                          │
│    - 检测查询语言                    │
│    - 选择对应处理策略                │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. 拼写纠正                          │
│    - 检测拼写错误                    │
│    - 自动纠正常见错误                │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. 同义词扩展                        │
│    - 查询同义词词典                  │
│    - 添加同义词到查询                │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 4. 语义扩展 (可选)                   │
│    - LLM 生成相关词                  │
│    - 扩展查询语义                    │
└─────────────────────────────────────┘
    ↓
改写后查询
```

---

## 🔧 模块实现

### 拼写纠正
```python
class SpellCorrector:
    def __init__(self, dictionary_path: str = None):
        self.dictionary = self.load_dictionary(dictionary_path)
        self.common_errors = {
            # 中文常见错误
            "规责": "规则",
            "配值": "配置",
            "系通": "系统",
            # 英文常见错误
            "configuraton": "configuration",
            "memroy": "memory",
        }

    def correct(self, query: str) -> str:
        """纠正拼写错误"""
        # 检查常见错误
        for wrong, correct in self.common_errors.items():
            query = query.replace(wrong, correct)

        # 词典检查
        words = query.split()
        corrected = []
        for word in words:
            if word not in self.dictionary:
                # 寻找最相似的词
                suggestion = self.find_similar(word)
                corrected.append(suggestion or word)
            else:
                corrected.append(word)

        return " ".join(corrected)

    def find_similar(self, word: str, max_distance: int = 2) -> str:
        """寻找编辑距离最小的词"""
        best_match = None
        best_distance = max_distance + 1

        for dict_word in self.dictionary:
            distance = self.levenshtein_distance(word, dict_word)
            if distance < best_distance:
                best_distance = distance
                best_match = dict_word

        return best_match

    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """计算编辑距离"""
        if len(s1) < len(s2):
            return SpellCorrector.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]
```

### 同义词扩展
```python
class SynonymExpander:
    def __init__(self, thesaurus_path: str = None):
        self.thesaurus = self.load_thesaurus(thesaurus_path)

    def expand(self, query: str, max_synonyms: int = 3) -> list[str]:
        """扩展同义词"""
        words = query.split()
        expanded_queries = [query]

        for word in words:
            synonyms = self.thesaurus.get(word, [])
            if synonyms:
                for synonym in synonyms[:max_synonyms]:
                    new_query = query.replace(word, synonym)
                    expanded_queries.append(new_query)

        return expanded_queries

    def load_thesaurus(self, path: str) -> dict:
        """加载同义词词典"""
        default_thesaurus = {
            # 中文同义词
            "配置": ["设置", "设定", "config"],
            "规则": ["策略", "policy", "rule"],
            "记忆": ["存储", "保存", "memory"],
            "搜索": ["查找", "检索", "search"],
            # 英文同义词
            "config": ["configuration", "setting", "配置"],
            "memory": ["storage", "记忆", "存储"],
            "search": ["query", "find", "搜索"],
        }
        return default_thesaurus
```

### 语义扩展 (LLM)
```python
class SemanticExpander:
    def __init__(self, llm_client, max_expansions: int = 5):
        self.llm = llm_client
        self.max_expansions = max_expansions

    def expand(self, query: str) -> list[str]:
        """使用 LLM 生成语义相关词"""
        prompt = f"""
        请为以下查询生成 {self.max_expansions} 个语义相关的扩展词：
        查询: {query}

        要求:
        1. 扩展词应与原查询语义相关
        2. 可以是同义词、相关概念或常见表达
        3. 每行一个词，不要编号

        扩展词:
        """

        response = self.llm.generate(prompt, max_tokens=100, temperature=0.5)
        expansions = response.strip().split("\n")

        return [e.strip() for e in expansions if e.strip()][:self.max_expansions]
```

---

## 📊 效果示例

### 拼写纠正
```
输入: "推送规责"
输出: "推送规则"
```

### 同义词扩展
```
输入: "配置记忆"
扩展: ["配置记忆", "设置记忆", "设定记忆", "config记忆"]
```

### 语义扩展
```
输入: "如何让AI记住重要信息"
扩展: ["记忆存储", "持久化", "知识保存", "信息记录", "长期记忆"]
```

---

## ⚙️ 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| enable_spell_correct | true | 启用拼写纠正 |
| enable_synonym_expand | true | 启用同义词扩展 |
| enable_semantic_expand | false | 启用语义扩展 (需 LLM) |
| max_synonyms | 3 | 最大同义词数 |
| max_semantic_expansions | 5 | 最大语义扩展数 |
| max_edit_distance | 2 | 最大编辑距离 |

---

## 📈 性能指标

| 操作 | 耗时 | 说明 |
|------|------|------|
| 拼写纠正 | <10ms | 本地词典 |
| 同义词扩展 | <5ms | 本地词典 |
| 语义扩展 | 200-500ms | 需要 LLM |

---

## 🔗 集成点

### 搜索流程
```
用户查询 → 查询改写 → 向量搜索 → 返回结果
```

### 配置示例
```json
{
  "query_rewriter": {
    "enabled": true,
    "spell_correct": true,
    "synonym_expand": true,
    "semantic_expand": false,
    "max_synonyms": 3,
    "max_semantic_expansions": 5
  }
}
```

---

*查询改写模块 - 理解用户，扩展语义*
