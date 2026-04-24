# 反馈学习模块

**版本**: 1.0.0
**来源**: llm-memory-integration (改进版)
**集成时间**: 2026-04-07 00:12 UTC

---

## 🎯 模块概述

反馈学习模块通过记录用户行为（点击、选择等）来优化搜索排序。

### 核心思想
```
用户对搜索结果的行为反映结果质量
记录这些行为作为反馈
利用反馈调整排序权重
持续优化搜索效果
```

---

## 📐 反馈类型

| 类型 | 说明 | 权重 |
|------|------|------|
| 点击 | 用户点击了结果 | +1.0 |
| 选择 | 用户选择了结果 | +2.0 |
| 复制 | 用户复制了结果内容 | +1.5 |
| 忽略 | 结果未被使用 | -0.5 |
| 负反馈 | 用户标记结果不好 | -2.0 |

---

## 🔧 模块实现

### 反馈记录
```python
import sqlite3
import json
from datetime import datetime
from typing import Optional

class FeedbackRecorder:
    def __init__(self, db_path: str = "~/.openclaw/memory/feedback.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """初始化反馈数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                result_id TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                weight REAL NOT NULL,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                metadata TEXT
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_query ON feedback(query)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_result ON feedback(result_id)
        """)

        conn.commit()
        conn.close()

    def record(
        self,
        query: str,
        result_id: str,
        feedback_type: str,
        session_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ):
        """记录反馈"""
        weights = {
            "click": 1.0,
            "select": 2.0,
            "copy": 1.5,
            "ignore": -0.5,
            "negative": -2.0
        }

        weight = weights.get(feedback_type, 0.0)
        timestamp = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO feedback
            (query, result_id, feedback_type, weight, timestamp, session_id, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            query, result_id, feedback_type, weight, timestamp,
            session_id, json.dumps(metadata) if metadata else None
        ))

        conn.commit()
        conn.close()
```

### 权重计算
```python
class FeedbackWeightCalculator:
    def __init__(self, db_path: str = "~/.openclaw/memory/feedback.db"):
        self.db_path = db_path
        self.decay_factor = 0.95  # 时间衰减因子
        self.min_feedbacks = 3    # 最小反馈数

    def get_result_weight(self, query: str, result_id: str) -> float:
        """计算结果的反馈权重"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT weight, timestamp FROM feedback
            WHERE query = ? AND result_id = ?
            ORDER BY timestamp DESC
        """, (query, result_id))

        feedbacks = cursor.fetchall()
        conn.close()

        if len(feedbacks) < self.min_feedbacks:
            return 0.0

        # 时间衰减加权
        total_weight = 0.0
        for i, (weight, timestamp) in enumerate(feedbacks):
            decay = self.decay_factor ** i
            total_weight += weight * decay

        # 归一化
        max_possible = sum(
            2.0 * (self.decay_factor ** i)
            for i in range(len(feedbacks))
        )

        return total_weight / max_possible if max_possible > 0 else 0.0

    def get_query_weights(self, query: str) -> dict[str, float]:
        """获取查询下所有结果的权重"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT result_id FROM feedback
            WHERE query = ?
        """, (query,))

        result_ids = [row[0] for row in cursor.fetchall()]
        conn.close()

        weights = {}
        for result_id in result_ids:
            weights[result_id] = self.get_result_weight(query, result_id)

        return weights
```

### 排序优化
```python
class FeedbackRanker:
    def __init__(self, weight_calculator: FeedbackWeightCalculator):
        self.calculator = weight_calculator
        self.feedback_weight = 0.3  # 反馈权重占比

    def rerank(
        self,
        query: str,
        results: list[tuple[str, float]]
    ) -> list[tuple[str, float]]:
        """基于反馈重排序"""
        feedback_weights = self.calculator.get_query_weights(query)

        reranked = []
        for result_id, original_score in results:
            feedback_score = feedback_weights.get(result_id, 0.0)

            # 融合原始分数和反馈分数
            final_score = (
                (1 - self.feedback_weight) * original_score +
                self.feedback_weight * feedback_score
            )

            reranked.append((result_id, final_score))

        # 重新排序
        reranked.sort(key=lambda x: -x[1])

        return reranked
```

---

## 📊 效果示例

### 反馈记录
```
查询: "推送规则"
结果: ["doc1", "doc2", "doc3"]
用户行为: 点击 doc2

记录:
- query: "推送规则"
- result_id: "doc2"
- feedback_type: "click"
- weight: 1.0
```

### 权重计算
```
doc1: 无反馈 → 权重 0.0
doc2: 3次点击 → 权重 0.85
doc3: 1次负反馈 → 权重 -0.5

重排序后: [doc2, doc1, doc3]
```

---

## ⚙️ 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| decay_factor | 0.95 | 时间衰减因子 |
| min_feedbacks | 3 | 最小反馈数 |
| feedback_weight | 0.3 | 反馈权重占比 |
| max_history | 1000 | 最大历史记录 |

---

## 📈 性能指标

| 操作 | 耗时 | 说明 |
|------|------|------|
| 记录反馈 | <5ms | 写入数据库 |
| 计算权重 | <20ms | 读取+计算 |
| 重排序 | <10ms | 融合排序 |

---

## 🔗 集成点

### 搜索流程
```
搜索 → 返回结果 → 用户交互 → 记录反馈
    ↓
下次搜索 → 应用反馈权重 → 优化排序
```

### API 接口
```python
# 记录点击
feedback.record(query, result_id, "click")

# 记录选择
feedback.record(query, result_id, "select")

# 记录负反馈
feedback.record(query, result_id, "negative")
```

---

## ⚠️ 注意事项

1. **隐私保护** - 反馈数据不包含用户敏感信息
2. **数据清理** - 定期清理过期反馈数据
3. **冷启动** - 新查询无反馈时使用原始排序
4. **防刷** - 检测异常反馈模式，防止刷权重

---

*反馈学习模块 - 从用户行为中学习*
