# 层间依赖矩阵 V2.0.0

> **唯一真源** - 定义六层架构的依赖关系白名单与黑名单

---

## 一、架构层级定义

| 层级 | 名称 | 目录 | 职责 |
|------|------|------|------|
| L1 | core | `core/` | 核心认知、身份、规则、标准 |
| L2 | memory_context | `memory_context/` | 记忆上下文、知识库、统一搜索 |
| L3 | orchestration | `orchestration/` | 任务编排、工作流、路由 |
| L4 | execution | `execution/`, `skills/` | 能力执行、技能网关 |
| L5 | governance | `governance/` | 稳定治理、安全审计、合规 |
| L6 | infrastructure | `infrastructure/` | 基础设施、工具链、注册表 |
| - | control_plane | `scripts/`, `reports/`, `ops/` | 控制面（非业务真源层） |

---

## 二、依赖白名单

| 层级 | 可读取层级 | 说明 |
|------|-----------|------|
| core | 无 | 核心层不依赖任何其他层 |
| orchestration | core, infrastructure | 可引用核心规则和基础设施 |
| execution | core, infrastructure | 可引用核心规则和基础设施 |
| memory_context | core, infrastructure | 可引用核心规则和基础设施 |
| governance | core, infrastructure | 可引用核心规则和基础设施 |
| infrastructure | core | 仅引用核心规则 |
| control_plane | 所有层 | 可聚合所有层，但不是真源 |

---

## 三、依赖黑名单

| 层级 | 禁止依赖层级 | 原因 |
|------|-------------|------|
| core | orchestration, execution, memory_context, governance, infrastructure, scripts | 核心层不能依赖实现层 |
| orchestration | scripts | 编排层不能依赖脚本 |
| execution | governance, scripts | 执行层不能直接依赖治理规则 |
| memory_context | scripts | 搜索层不能依赖脚本 |
| governance | execution | 治理层不能依赖具体技能实现 |

---

## 四、硬规则

1. **core 只能被读，不承担业务执行**
2. **execution 不直接依赖 governance 规则实现**
3. **governance 不直接依赖具体 skills 实现**
4. **control_plane 只能聚合，不是业务真源**
5. **registry 是真源，index 是派生物**
6. **reports 是产物，不是主逻辑输入真源**

---

## 五、版本历史

- V2.0.0: 规则硬化版，简化为白名单/黑名单模式
- V1.0.0: 初始版本

---

**维护者**: OpenClaw 架构团队
**更新日期**: 2026-04-13
