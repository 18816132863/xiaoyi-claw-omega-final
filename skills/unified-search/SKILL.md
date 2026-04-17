---
name: unified-search
description: 搜索统一入口。自动路由到最佳搜索技能。支持联网搜索、深度调研、多引擎搜索。触发词：搜索、查一下、调研、找资料。
---

# 搜索统一入口

自动路由到最佳搜索技能。

## 工作流

```
用户请求
    ↓
判断搜索类型
    ↓
┌─────────────────────────────────┐
│ 快速搜索 → xiaoyi-web-search    │
│ 深度调研 → deep-search          │
│ 多引擎 → prismfy-search         │
│ 专业搜索 → tavily-search        │
└─────────────────────────────────┘
```

## 优先级

1. xiaoyi-web-search (快速)
2. deep-search (深度)
3. prismfy-search (多引擎)

## 使用

直接描述需求：
- "搜索一下 xxx"
- "深度调研 xxx"
- "帮我查资料"
