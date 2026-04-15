# 架构冻结 1.0 - V1.0.0

## 概述

本文档定义架构冻结范围、冻结对象和变更规则。

---

## 一、冻结范围

### 六层架构

| 层级 | 范围 | 状态 |
|------|------|------|
| L1 Core | 核心认知、身份、规则、标准 | 冻结 |
| L2 Memory Context | 记忆上下文、知识库 | 冻结 |
| L3 Orchestration | 任务编排、工作流 | 冻结 |
| L4 Execution | 能力执行、技能网关 | 冻结 |
| L5 Governance | 稳定治理、安全审计 | 冻结 |
| L6 Infrastructure | 基础设施、工具链 | 冻结 |

### Registry/Index

| 文件 | 说明 | 状态 |
|------|------|------|
| `core/RULE_REGISTRY.json` | 规则注册表 | 冻结 |
| `infrastructure/inventory/skill_registry.json` | 技能注册表 | 冻结 |
| `core/RULE_EXCEPTIONS.json` | 规则例外 | 受控 |

### Gates

| 文件 | 说明 | 状态 |
|------|------|------|
| `scripts/run_release_gate.py` | 发布门禁 | 冻结 |
| `infrastructure/verify_runtime_integrity.py` | 运行时验收 | 冻结 |
| `governance/quality_gate.py` | 质量门禁 | 冻结 |

### Rule Engine

| 文件 | 说明 | 状态 |
|------|------|------|
| `scripts/run_rule_engine.py` | 规则引擎 | 冻结 |
| `scripts/exception_manager.py` | 例外管理器 | 冻结 |

### Exception Governance

| 文件 | 说明 | 状态 |
|------|------|------|
| `core/RULE_EXCEPTION_POLICY.md` | 例外策略 | 冻结 |
| `core/RULE_EXCEPTION_DEBT_POLICY.md` | 债务策略 | 冻结 |
| `core/RULE_EXCEPTION_ENFORCEMENT_POLICY.md` | 强制策略 | 冻结 |
| `core/RULE_EXCEPTION_OPERATIONS.md` | 操作文档 | 冻结 |

### Control Plane

| 文件 | 说明 | 状态 |
|------|------|------|
| `scripts/control_plane.py` | 控制平面 | 冻结 |
| `scripts/control_plane_audit.py` | 控制平面审计 | 冻结 |
| `scripts/ops_center.py` | 运维中心 | 冻结 |

---

## 二、冻结对象

### 完全冻结（禁止修改）

- `core/ARCHITECTURE.md`
- `core/SINGLE_SOURCE_OF_TRUTH.md`
- `core/LAYER_DEPENDENCY_MATRIX.md`
- `core/LAYER_IO_CONTRACTS.md`
- `core/RULE_REGISTRY.json`
- `infrastructure/inventory/skill_registry.json`

### 受控修改（需审批）

- `core/RULE_EXCEPTIONS.json` - 通过 exception_manager 修改
- `reports/ops/*.json` - 自动生成
- `memory/*.md` - 日记更新

---

## 三、变更规则

### 禁止的变更

1. 新增无 owner 规则
2. 新增无 expiry 的 exception
3. 无变更影响说明的主链修改
4. 破坏层间依赖的修改
5. 绕过门禁的修改

### 允许的变更

1. 通过 exception_manager 的例外操作
2. 通过 ops_center 的运维操作
3. 日记和记忆更新
4. 技能新增（不破坏现有结构）

### 必须评审的变更

1. 规则注册表修改
2. 门禁逻辑修改
3. 架构文档修改
4. 核心模块修改

---

## 四、变更影响检查

所有对冻结文件的修改必须：

1. 运行 `check_change_impact.py`
2. 生成变更影响报告
3. 通过门禁检查
4. 记录变更原因

---

## 五、维护模式

进入维护模式后：

- 默认禁止新增功能
- 只允许修复和优化
- 所有变更需评审
- 定期审计

---

**冻结日期**: 2026-04-15
**版本**: 1.0.0
**维护者**: OpenClaw 架构团队
