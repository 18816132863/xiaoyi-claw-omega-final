# 组件分级治理策略 V1.0.0

## 概述

本文档定义组件的层级、类型、权限和职责，确保组件各司其职、调用有序。

---

## 一、层级定义

| 层级 | 名称 | 描述 | 可修改 | 目录 |
|------|------|------|--------|------|
| L1 | Core | 核心认知、身份、规则 | ❌ | core/ |
| L2 | Memory | 记忆上下文、知识库 | ✅ | memory/, memory_context/ |
| L3 | Orchestration | 任务编排、工作流 | ✅ | orchestration/ |
| L4 | Execution | 能力执行、技能网关 | ✅ | execution/, skills/ |
| L5 | Governance | 稳定治理、安全审计 | ✅ | governance/ |
| L6 | Infrastructure | 基础设施、工具链 | ✅ | infrastructure/, scripts/ |

---

## 二、类型定义

| 类型 | 名称 | 必需层级 | 说明 |
|------|------|----------|------|
| core | 核心文件 | L1 | 架构、规则、身份等核心定义 |
| engine | 引擎 | L1/L6 | 融合引擎、规则引擎等 |
| module | 模块 | L6 | 例外管理器、依赖管理器等 |
| skill | 技能 | L4 | llm-memory-integration 等 |
| tool | 工具 | L6 | 备份工具、巡检器等 |
| config | 配置 | L6 | JSON 配置文件 |
| registry | 注册表 | L6 | 索引、注册表 |
| doc | 文档 | L6 | 说明文档 |
| report | 报告 | L6 | 运行报告 |

---

## 三、调用权限

### 调用规则

- **L1 Core**: 可调用 L2-L6，不可被调用
- **L2 Memory**: 可调用 L3-L6，可被 L1 调用
- **L3 Orchestration**: 可调用 L4-L6，可被 L1-L2 调用
- **L4 Execution**: 可调用 L4-L6，可被 L1-L3 调用
- **L5 Governance**: 可调用 L4-L6，可被 L1-L4 调用
- **L6 Infrastructure**: 可调用 L4-L6，可被 L1-L5 调用

### 禁止调用

- ❌ L6 不可调用 L1（核心文件不可被基础设施修改）
- ❌ L4 不可调用 L1-L3（技能不可修改核心）
- ❌ 低层级不可调用高层级

---

## 四、类型权限矩阵

| 类型 | 可调用层级 | 可被调用层级 |
|------|------------|--------------|
| core | L2-L6 | 无 |
| engine | L2-L6 | L3-L6 |
| module | L4-L6 | L3-L6 |
| skill | L4-L6 | L3-L4 |
| tool | L4-L6 | L3-L6 |
| config | 无 | L1-L6 |
| registry | 无 | L1-L6 |
| doc | 无 | L1-L6 |
| report | 无 | L3-L6 |

---

## 五、位置建议

| 类型 | 建议目录 | 原因 |
|------|----------|------|
| core | core/ | 核心文件集中管理 |
| engine | infrastructure/ | 基础设施引擎 |
| module | scripts/ | 功能模块脚本 |
| skill | skills/ | 技能包目录 |
| tool | scripts/ | 工具脚本 |
| config | infrastructure/config/ | 配置集中管理 |
| registry | infrastructure/inventory/ | 注册表集中管理 |
| doc | docs/ | 文档集中管理 |
| report | reports/ops/ | 报告集中管理 |

---

## 六、分类示例

### 用户认为 fusion_index 是技能

```
用户建议: skill
正确分类: engine
原因: 融合引擎是核心基础设施，不是技能
位置: infrastructure/inventory/fusion_index.json
```

### 用户认为 exception_manager 是技能

```
用户建议: skill
正确分类: module
原因: 模块在 scripts/ 目录，不在 skills/ 目录
位置: scripts/exception_manager.py
```

### 用户认为 ARCHITECTURE.md 是文档

```
用户建议: doc
正确分类: core
原因: 架构文档是核心定义，不可修改
位置: core/ARCHITECTURE.md
```

---

## 七、使用方式

### 分类组件
```bash
python scripts/component_classifier.py classify --name xxx --type skill
```

### 注册组件
```bash
python scripts/component_classifier.py register \
    --name my_module.py \
    --layer L6 \
    --type module \
    --official-name "我的模块"
```

### 查看层级
```bash
python scripts/component_classifier.py layer --id L1
```

### 查看类型
```bash
python scripts/component_classifier.py type --id module
```

### 检查调用权限
```bash
python scripts/component_classifier.py check-call --caller a --callee b
```

### 建议位置
```bash
python scripts/component_classifier.py suggest --name xxx --type module
```

---

## 八、文件位置

| 文件 | 说明 |
|------|------|
| `scripts/component_classifier.py` | 分级治理脚本 |
| `infrastructure/config/component_classification.json` | 分级配置 |

---

## 九、版本

- V1.0.0 - 2026-04-15 - 初始版本
