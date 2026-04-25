# 技能挂层映射表

## 一、已注册技能全量盘点

### L1 表达层（core/）

| skill_id | skill_name | 入口位置 | 注册位置 | 配置源 | 依赖关系 | 输出去向 | 迁移状态 |
|----------|-----------|---------|---------|-------|---------|---------|---------|
| - | AGENTS.md | core/AGENTS.md | skill_registry.json | core/AGENTS.md | 无 | L2/L3/L4/L5/L6 | ✅ 已完成 |
| - | IDENTITY.md | core/IDENTITY.md | skill_registry.json | core/IDENTITY.md | 无 | L1 | ✅ 已完成 |
| - | SOUL.md | core/SOUL.md | skill_registry.json | core/SOUL.md | 无 | L1 | ✅ 已完成 |
| - | USER.md | core/USER.md | skill_registry.json | core/USER.md | 无 | L1 | ✅ 已完成 |
| - | TOOLS.md | core/TOOLS.md | skill_registry.json | core/TOOLS.md | 无 | L1-L6 | ✅ 已完成 |
| - | ARCHITECTURE.md | core/ARCHITECTURE.md | skill_registry.json | core/ARCHITECTURE.md | 无 | L1-L6 | ✅ 已完成 |
| - | SKILL_ACCESS_RULES.md | core/SKILL_ACCESS_RULES.md | skill_registry.json | core/SKILL_ACCESS_RULES.md | 无 | L1-L6 | ✅ 已完成 |

---

### L2 应用编排层（orchestration/）

| skill_id | skill_name | 入口位置 | 注册位置 | 配置源 | 依赖关系 | 输出去向 | 迁移状态 |
|----------|-----------|---------|---------|-------|---------|---------|---------|
| skill_task_scheduler_v1 | 任务调度 | orchestration/task-scheduler/SKILL.md | skill_registry.json | infrastructure/inventory/ | queue, executor | L4 | ✅ 已完成 |
| skill_route_smoke_test_v1 | 路由冒烟测试 | orchestration/routing/route_smoke_test.py | skill_registry.json | infrastructure/inventory/ | test_framework, logger | L6 | ✅ 已完成 |
| skill_route_impact_analysis_v1 | 路由影响分析 | orchestration/routing/route_impact_analysis.py | skill_registry.json | infrastructure/inventory/ | analyzer, logger | L6 | ✅ 已完成 |
| skill_golden_path_regression_v1 | 黄金路径回归 | orchestration/routing/golden_path_regression.py | skill_registry.json | infrastructure/inventory/ | test_framework, logger | L6 | ✅ 已完成 |

---

### L3 领域规则层（governance/policy/）

| skill_id | skill_name | 入口位置 | 注册位置 | 配置源 | 依赖关系 | 输出去向 | 迁移状态 |
|----------|-----------|---------|---------|-------|---------|---------|---------|
| - | （暂无技能） | - | - | - | - | - | - |

**说明**：L3层用于核心业务规则、判断逻辑、能力边界，当前暂无独立技能，规则逻辑嵌入在各技能中。

---

### L4 服务能力层（execution/）

| skill_id | skill_name | 入口位置 | 注册位置 | 配置源 | 依赖关系 | 输出去向 | 迁移状态 |
|----------|-----------|---------|---------|-------|---------|---------|---------|
| skill_phone_engine_v1 | 手机操作引擎 | execution/phone-engine/SKILL.md | skill_registry.json | infrastructure/inventory/ | gui_agent, adb, screen_capture | L5, L6 | ✅ 已完成 |
| skill_image_verification_v1 | 图片验证 | execution/image-verification/SKILL.md | skill_registry.json | infrastructure/inventory/ | vision_model, cache | L5, L6 | ✅ 已完成 |
| skill_network_acceleration_v1 | 网络加速层 | execution/network-acceleration-layer/SKILL.md | skill_registry.json | infrastructure/inventory/ | http_client, cache, preload | L5, L6 | ✅ 已完成 |
| skill_network_acceleration_cpp_v1 | 网络加速层(C++) | execution/network-acceleration-layer-cpp/SKILL.md | skill_registry.json | infrastructure/inventory/ | http_client, cache, vector_index | L5, L6 | ✅ 已完成 |

---

### L5 数据访问层（memory_context/）

| skill_id | skill_name | 入口位置 | 注册位置 | 配置源 | 依赖关系 | 输出去向 | 迁移状态 |
|----------|-----------|---------|---------|-------|---------|---------|---------|
| skill_memory_management_v1 | 记忆管理 | memory_context/memory-management/SKILL.md | skill_registry.json | infrastructure/inventory/ | filesystem, cache | L6 | ✅ 已完成 |
| - | MEMORY.md | memory_context/MEMORY.md | skill_registry.json | memory_context/MEMORY.md | filesystem | L5, L6 | ✅ 已完成 |
| - | data/ | memory_context/data/ | skill_registry.json | memory_context/data/ | filesystem | L5, L6 | ✅ 已完成 |

---

### L6 基础设施层（infrastructure/ + governance/）

| skill_id | skill_name | 入口位置 | 注册位置 | 配置源 | 依赖关系 | 输出去向 | 迁移状态 |
|----------|-----------|---------|---------|-------|---------|---------|---------|
| skill_error_handling_v1 | 错误处理 | governance/error-handling/SKILL.md | skill_registry.json | infrastructure/inventory/ | logger, monitor, alert | L6 | ✅ 已完成 |
| skill_failover_test_v1 | 故障转移测试 | governance/failover/failover_smoke_test.py | skill_registry.json | infrastructure/inventory/ | monitor, alert, backup | L6 | ✅ 已完成 |
| skill_evidence_audit_v1 | 证据链审计 | governance/audit/evidence_chain_audit.py | skill_registry.json | infrastructure/inventory/ | logger, storage, analyzer | L6 | ✅ 已完成 |
| - | architecture_config.json | infrastructure/inventory/architecture_config.json | skill_registry.json | infrastructure/inventory/ | 无 | L1-L6 | ✅ 已完成 |
| - | skill_registry.json | infrastructure/inventory/skill_registry.json | skill_registry.json | 无 | L1-L6 | ✅ 已完成 |
| - | auto-backup.sh | infrastructure/backup/auto-backup.sh | skill_registry.json | infrastructure/backup/ | filesystem | L5, L6 | ✅ 已完成 |
| - | memory-auto-cleanup.sh | infrastructure/backup/memory-auto-cleanup.sh | skill_registry.json | infrastructure/backup/ | filesystem | L5, L6 | ✅ 已完成 |

---

## 二、技能统计

| 层级 | 层名 | 技能数 | 占比 |
|-----|------|-------|------|
| L1 | 表达层 | 7 | 28% |
| L2 | 应用编排层 | 4 | 16% |
| L3 | 领域规则层 | 0 | 0% |
| L4 | 服务能力层 | 4 | 16% |
| L5 | 数据访问层 | 3 | 12% |
| L6 | 基础设施层 | 7 | 28% |
| **总计** | - | **25** | **100%** |

---

## 三、依赖关系图

```
L1 表达层
    ↓
L2 应用编排层
    ↓
L3 领域规则层
    ↓
L4 服务能力层
    ↓
L5 数据访问层
    ↓
L6 基础设施层
```

**调用规则**：
- 上层只能调用下层的公开接口
- 禁止跨层直接调用
- 禁止下层调用上层

---

## 版本
- V1.0.0
- 创建日期：2026-04-10
