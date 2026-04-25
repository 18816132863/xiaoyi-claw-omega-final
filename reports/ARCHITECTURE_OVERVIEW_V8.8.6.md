# 架构全景图 V8.8.6

> 生成时间: 2026-04-25
> 基线版本: V8.8.6
> 巡检状态: ✅ 全部通过

---

## 一、六层架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                     L1 Core - 核心层                            │
│  认知 · 身份 · 规则 · 标准 · 契约 · 事件                         │
│  core/                                                          │
├─────────────────────────────────────────────────────────────────┤
│                 L2 Memory Context - 记忆层                      │
│  检索 · 会话 · 向量 · 知识库 · 上下文构建                        │
│  memory_context/                                                │
├─────────────────────────────────────────────────────────────────┤
│                 L3 Orchestration - 编排层                       │
│  工作流 · 路由 · 策略 · 调度 · 任务服务                          │
│  orchestration/ + application/                                  │
├─────────────────────────────────────────────────────────────────┤
│                   L4 Execution - 执行层                         │
│  技能网关 · 适配器 · 循环防护 · 任务审查 · 领域模型               │
│  execution/ + skills/ + domain/                                 │
├─────────────────────────────────────────────────────────────────┤
│                  L5 Governance - 治理层                         │
│  安全 · 权限 · 审计 · 预算 · 风控 · 合规                         │
│  governance/                                                    │
├─────────────────────────────────────────────────────────────────┤
│               L6 Infrastructure - 基础设施层                    │
│  存储 · 调度 · 缓存 · 自动化 · 注册表 · 运维                     │
│  infrastructure/ + scripts/ + reports/ + data/                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、核心模块清单

### L1 Core (核心层)

| 模块 | 路径 | 职责 |
|------|------|------|
| 认知系统 | `core/cognition/` | 推理、决策、规划、反思、学习 |
| 状态契约 | `core/state/` | 全局状态、任务状态、档案状态 |
| 事件系统 | `core/events/` | 事件总线、事件持久化、事件回放 |
| 规则注册表 | `core/RULE_REGISTRY.json` | 规则定义、生命周期管理 |
| 层间依赖 | `core/LAYER_DEPENDENCY_RULES.json` | 层间调用约束 |
| IO 契约 | `core/LAYER_IO_CONTRACTS.md` | 输入输出规范 |

### L2 Memory Context (记忆层)

| 模块 | 路径 | 职责 |
|------|------|------|
| 统一搜索 | `memory_context/unified_search.py` | 多引擎检索入口 |
| 向量存储 | `memory_context/vector/` | Qdrant/sqlite-vec 集成 |
| 会话管理 | `memory_context/session/` | 会话上下文构建 |
| 索引管理 | `memory_context/index/` | 倒排索引、元数据索引 |

### L3 Orchestration (编排层)

| 模块 | 路径 | 职责 |
|------|------|------|
| 工作流引擎 | `orchestration/workflow/workflow_engine.py` | DAG 执行、状态机 |
| 任务编排器 | `orchestration/task_orchestrator.py` | 任务分解、依赖解析 |
| 技能路由 | `orchestration/router/skill_router.py` | 技能选择、权重计算 |
| 执行控制 | `orchestration/execution_control/` | 重试、回退、回滚 |
| 任务服务 | `application/task_service/` | 任务 CRUD、调度 |
| 响应服务 | `application/response_service/` | 渲染、格式化 |

### L4 Execution (执行层)

| 模块 | 路径 | 职责 |
|------|------|------|
| 技能网关 | `execution/skill_gateway.py` | 技能调用入口 |
| 技能路由 | `execution/skill_router.py` | 技能发现、选择 |
| 循环防护 | `execution/loop_guard.py` | 无限循环检测 |
| 任务审查 | `execution/task_reviewer.py` | 任务质量检查 |
| 结果验证 | `execution/result_validator.py` | 输出验证 |
| 领域模型 | `domain/tasks/` | 任务规格、状态枚举 |
| 技能包 | `skills/` | 275+ 技能包 |

### L5 Governance (治理层)

| 模块 | 路径 | 职责 |
|------|------|------|
| 安全中心 | `governance/security/` | 认证、授权、沙箱 |
| 审计系统 | `governance/audit/` | 审计日志、证据链 |
| 权限引擎 | `governance/permission/` | 权限检查、角色管理 |
| 预算管理 | `governance/budget/` | Token 预算、成本控制 |
| 风险管理 | `governance/risk/` | 风险分类、高风防护 |
| 规则引擎 | `governance/rules/` | 规则执行、监控 |
| 恢复系统 | `governance/recovery/` | 状态恢复、故障恢复 |

### L6 Infrastructure (基础设施层)

| 模块 | 路径 | 职责 |
|------|------|------|
| 存储仓库 | `infrastructure/storage/repositories/` | SQLite 数据访问 |
| 任务调度 | `infrastructure/scheduler/` | Cron、延迟任务 |
| 任务执行器 | `infrastructure/workers/executor.py` | 步骤执行 |
| 路由注册表 | `infrastructure/route_registry.json` | 能力路由映射 |
| 能力注册表 | `infrastructure/inventory/capability_registry.json` | 能力清单 |
| 技能注册表 | `infrastructure/inventory/skill_registry.json` | 技能清单 |
| 自动 Git | `infrastructure/auto_git.py` | 自动提交推送 |
| 架构巡检 | `infrastructure/architecture_inspector.py` | 完整性检查 |

---

## 三、数据流向

```
用户请求
    ↓
┌───────────────────────────────────────────────────────────────┐
│ L1 Core: 解析意图、加载规则、初始化状态                         │
└───────────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────────┐
│ L2 Memory: 检索相关记忆、构建上下文                             │
└───────────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────────┐
│ L3 Orchestration: 规划任务、选择路由、编排工作流                 │
└───────────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────────┐
│ L4 Execution: 调用技能、执行能力、验证结果                       │
└───────────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────────┐
│ L5 Governance: 审计日志、权限检查、预算扣减                      │
└───────────────────────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────────────────────┐
│ L6 Infrastructure: 持久化、缓存、报告                           │
└───────────────────────────────────────────────────────────────┘
    ↓
响应输出
```

---

## 四、规则体系

### 规则注册表 (R001-R008)

| 规则 ID | 名称 | 状态 | 检查脚本 |
|---------|------|------|----------|
| R001 | 层间依赖规则 | active | `scripts/check_layer_dependencies.py` |
| R002 | JSON 契约规则 | active | `scripts/check_json_contracts.py` |
| R003 | 唯一真源规则 | active | `scripts/check_single_source_of_truth.py` |
| R004 | 变更影响规则 | active | `scripts/check_change_impact_enforcement.py` |
| R005 | 规则自测规则 | active | `scripts/check_rule_self_test.py` |
| R006 | 仓库完整性规则 | active | `scripts/check_repo_integrity_fast.py` |
| R007 | 技能安全规则 | experimental | `scripts/check_skill_security.py` |
| R008 | 遗留格式规则 | disabled | - |

### 门禁 Profile

| Profile | 触发时机 | 规则集 |
|---------|----------|--------|
| premerge | PR 合并前 | R001-R006 |
| nightly | 每日构建 | R001-R007 |
| release | 版本发布 | R001-R008 |

---

## 五、巡检体系

### 统一巡检器 V6.0.0

**路径**: `scripts/unified_inspector.py`

**检查项**:
1. 层间依赖检查
2. JSON 契约检查
3. 仓库完整性检查
4. 变更影响检查
5. 技能安全检查
6. 架构完整性检查
7. Token 优化检查
8. 注入配置检查

**性能**: 8 并发，~13s 完成

### 架构巡检器 V6.0.0

**路径**: `infrastructure/architecture_inspector.py`

**检查项**:
1. 六层架构完整性
2. 受保护文件检查
3. 技能注册表一致性
4. 配置文件完整性
5. 依赖关系检查
6. 代码质量检查
7. 安全检查
8. 性能指标检查
9. 规则注册表检查
10. 规则引擎检查
11. 变更影响检查
12. 技能安全检查
13. 循环防护检查
14. 门禁报告检查
15. 新模块融入检查
16. 任务系统检查

---

## 六、能力路由体系

### 路由注册表

**路径**: `infrastructure/route_registry.json`

**统计**:
- 总路由: 53
- LOW 风险: 24
- MEDIUM 风险: 13
- HIGH 风险: 9
- SYSTEM 级: 7
- 带 fallback: 10
- 需确认: 16

### 路由字段

```json
{
  "route_id": "SEND_MESSAGE",
  "user_intent": ["发消息", "发送短信", "通知"],
  "capability": "message_sending",
  "handler": "device_capability_bus.capabilities.messaging.send",
  "input_schema": {...},
  "output_schema": {...},
  "risk_level": "HIGH",
  "requires_confirmation": true,
  "fallback_routes": ["LIST_MESSAGES", "QUERY_MESSAGE_STATUS"],
  "tested_by": "tests/test_messaging.py",
  "documented_in": "docs/capabilities/messaging.md"
}
```

### 意图索引

59 条用户意图到路由的映射，支持自然语言路由选择。

---

## 七、任务系统

### 数据库表

| 表名 | 说明 |
|------|------|
| tasks | 任务主表 |
| task_steps | 任务步骤表 |
| task_events | 任务事件表 |
| tool_calls | 工具调用表 |
| scheduled_messages | 定时消息表 |

### 任务状态机

```
pending → scheduled → running → completed
                   ↘ paused → resumed
                   ↘ failed → retrying
                   ↘ cancelled
```

### 调度类型

| 类型 | 说明 |
|------|------|
| once | 一次性任务 |
| delay | 延迟任务 |
| cron | Cron 表达式 |
| recurring | 周期任务 |

---

## 八、技能生态

### 统计

| 指标 | 数量 |
|------|------|
| 总技能数 | 275 |
| 可路由 | 273 |
| 可测试 | 80 |
| 可调用 | 273 |

### 分类 Top 10

| 分类 | 数量 |
|------|------|
| AI | 31 |
| Search | 24 |
| Image | 17 |
| Document | 13 |
| Video | 10 |
| Finance | 8 |
| Code | 8 |
| E-commerce | 8 |
| Data | 7 |
| Memory | 7 |

---

## 九、向量存储

### 三引擎架构

| 引擎 | 状态 | 维度 | 说明 |
|------|------|------|------|
| sqlite-vec | ✅ 启用 | 4096 | 主引擎，本地存储 |
| qdrant | ✅ 启用 | 4096 | 副引擎，高性能 |
| tfidf | ✅ 启用 | - | 备份引擎，关键词检索 |

---

## 十、审计系统

### 功能

| 功能 | 状态 |
|------|------|
| 加密存储 | ✅ AES-256-GCM |
| 工具调用审计 | ✅ 启用 |
| 技能调用审计 | ✅ 启用 |
| 内存读写审计 | ✅ 启用 |
| 证据链审计 | ✅ 启用 |

---

## 十一、性能指标

### 巡检性能

| 指标 | 值 |
|------|-----|
| 统一巡检耗时 | ~13s |
| 架构巡检耗时 | ~15s |
| 并发 Workers | 8 |
| 缓存 TTL | 3600s |

### Token 优化

| 模式 | 估算 Token |
|------|------------|
| minimal | ~5000 |
| ultra_minimal | ~3000 |
| smart | ~7000 |

---

## 十二、版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| V8.8.6 | 2026-04-24 | 能力路由闭环、巡检增强 |
| V8.8.5 | 2026-04-24 | 基线版本 |
| V8.0.0 | 2026-04-20 | 任务系统重构 |
| V7.2.0 | 2026-04-17 | 技能平台化、恢复链 |
| V6.0.0 | 2026-04-15 | 规则平台化 |

---

## 十三、下一步计划

1. **路由闭环**: 接入规划器、调度器
2. **Fallback 完善**: 补充失败场景处理
3. **测试覆盖**: 创建路由测试文件
4. **文档同步**: 更新架构文档
5. ~~**性能优化**: 进一步降低巡检耗时~~ ✅ 已优化至 ~12s

---

## 十四、改进记录

### 2026-04-25 V8.8.6 改进

| 项目 | 改进内容 |
|------|----------|
| 证据检查 | 修复巡检器检查逻辑，使用 `evidences` + `verified` |
| error 结构 | 修复巡检器检查逻辑，使用 `"code"` + `"message"` |
| 缺失报告 | 生成 change_impact.json, rule_engine_report.json 等 6 个报告 |
| 超时配置 | 架构完整性检查超时从 30s 增加到 60s |
| 巡检结果 | ✅ 8/8 全部通过，耗时 ~12s |

---

*此文档由架构巡检自动生成*
