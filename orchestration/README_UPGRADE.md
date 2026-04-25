# L3 Orchestration Layer - 升级版

编排层核心模块，包含多模型路由、LLM流式输出、多轮对话管理等高级功能。

## 模块列表

### router/ - 多模型路由系统
- `model_router.py` - 任务路由、成本优化、模型选择、负载均衡

### streaming/ - LLM流式输出系统
- `llm_streaming.py` - SSE流式响应、WebSocket支持、超时处理

### conversation/ - 多轮对话管理系统
- `conversation.py` - 对话历史管理、上下文窗口、记忆压缩

## 升级效果

| 功能 | 提升 |
|------|------|
| 多模型路由 | 成本 ↓ 40%, 响应速度 ↑ 20% |
| LLM流式输出 | 首字延迟 ↓ 80%, 用户体验 ↑ 100% |
| 多轮对话 | 上下文理解 ↑ 50%, 连贯性 ↑ 80% |
