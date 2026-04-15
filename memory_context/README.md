# Memory 目录结构说明

## 目录职责

### memory/ - 会话记忆数据
存储每日日记和会话记录，由 `agent-chronicle` 技能自动生成。

```
memory/
├── 2026-04-10.md    # 每日日记
├── 2026-04-11.md
├── 2026-04-12.md
├── ...
└── cron/            # 定时任务记录
```

**特点**:
- 自动生成，按日期命名
- 记录会话重要事件和决策
- 可被 `memory_search` 检索

### memory_context/ - 记忆策略文档
存储记忆系统的策略、规则和配置文档。

```
memory_context/
├── ANSWER_POLICY.md        # 回答策略
├── ANSWER_VALIDATION.md    # 回答验证
├── CITATION_POLICY.md      # 引用策略
├── CONTEXT_ASSEMBLY.md     # 上下文组装
├── CONTEXT_COMPRESSION.md  # 上下文压缩
├── ENTITY_RESOLUTION.md    # 实体解析
├── FRESHNESS_GOVERNANCE.md # 新鲜度治理
├── GRAPH_*.md              # 图谱相关
├── INGESTION_POLICY.md     # 摄入策略
└── ...
```

**特点**:
- 手动维护的策略文档
- 定义记忆系统的行为规则
- 被 L2 层引用

## 边界说明

| 目录 | 内容类型 | 生成方式 | 用途 |
|------|----------|----------|------|
| memory/ | 数据 | 自动 | 会话记录 |
| memory_context/ | 策略 | 手动 | 系统配置 |

## 引用关系

```
L2: Memory Context
├── memory/           → 数据存储
├── memory_context/   → 策略定义
└── MEMORY.md         → 长期记忆索引
```

## 注意事项

1. **不要混淆**: `memory/` 存数据，`memory_context/` 存策略
2. **不要删除**: 两个目录都是 L2 层核心组件
3. **定期清理**: `memory/` 中的旧日记可归档，但不要删除策略文档
