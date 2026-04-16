# memory_context/ - L2 记忆上下文层

## 定位

L2 层是**真正的二级核心**，负责所有上下文构建、记忆管理和知识检索。

## 职责

1. **会话管理** - 短期上下文、会话状态、历史记录
2. **长期记忆** - 用户偏好、项目历史、决策日志
3. **检索系统** - 向量检索、关键词检索、混合检索
4. **上下文构建** - 统一的上下文构建入口
5. **策略管理** - 记忆策略、衰减策略、优先级策略

## 目录结构

```
memory_context/
├── contracts/           # JSON Schema 契约
│   ├── memory_record.schema.json
│   ├── context_bundle.schema.json
│   └── retrieval_result.schema.json
├── session/             # 会话管理
│   ├── session_state.py
│   ├── session_history.py
│   └── session_summary.py
├── long_term/           # 长期记忆
│   ├── user_memory_store.py
│   └── __init__.py
├── retrieval/           # 检索系统
│   ├── retrieval_router.py
│   ├── hybrid_search.py
│   ├── reranker.py
│   └── source_selector.py
├── builder/             # 上下文构建
│   ├── context_builder.py
│   ├── context_budgeter.py
│   ├── conflict_resolver.py
│   └── priority_ranker.py
├── policies/            # 记忆策略
├── adapters/            # 外部适配器
├── __init__.py
└── README.md
```

## 核心接口

### ContextBuilder (统一入口)

```python
from memory_context.builder.context_builder import build_context

# 构建上下文
bundle = build_context(
    task_id="task_123",
    profile="developer",
    intent="Find architecture documentation",
    token_budget=4000
)

# 转换为 LLM 提示
prompt_context = bundle.to_prompt_context()
```

### 检索系统

```python
from memory_context.retrieval.retrieval_router import RetrievalRouter, RetrievalRequest

router = RetrievalRouter()
request = RetrievalRequest(
    query="architecture design",
    sources=["memory", "document"],
    max_results=10
)
result = router.route(request)
```

### 会话管理

```python
from memory_context.session.session_state import SessionStateStore

store = SessionStateStore()
state = store.create("session_123")
state = store.update("session_123", status="running", current_step="step_1")
```

## 契约

所有数据结构都有 JSON Schema 定义：

- `memory_record.schema.json` - 记忆记录格式
- `context_bundle.schema.json` - 上下文包格式
- `retrieval_result.schema.json` - 检索结果格式

## 纵向能力带

记忆与知识带贯穿：
- core (规则定义)
- memory_context (本层)
- orchestration (工作流使用)

## 扩展方式

1. 新增记忆类型 → 在 `long_term/` 添加 store
2. 新增检索引擎 → 在 `retrieval/` 添加 engine
3. 新增上下文策略 → 在 `policies/` 添加 policy
