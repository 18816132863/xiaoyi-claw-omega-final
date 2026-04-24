# 规则生命周期策略 V1.0.0

> 定义规则从引入到废弃的完整生命周期

---

## 一、状态定义

| 状态 | 说明 | 阻断行为 |
|------|------|----------|
| `active` | 正式生效 | 失败时阻断（若 blocking=true） |
| `experimental` | 实验阶段 | 失败时不阻断，仅警告 |
| `deprecated` | 已废弃 | 默认不阻断，可跳过 |
| `disabled` | 已禁用 | 不执行 |

---

## 二、状态流转

### 1. 新规则进入 `experimental`

- 新规则必须先设为 `experimental`
- 至少在一个完整门禁周期（premerge + nightly）中验证
- 验证期间失败不阻断主流程

### 2. 升级为 `active`

条件：
- 在 `experimental` 状态下连续 7 天无阻断性失败
- 或经过 3 次 release 门禁验证通过
- owner 确认规则逻辑稳定

操作：
- `status: experimental → active`
- `version: x.y.z → x.(y+1).0`

### 3. 标记为 `deprecated`

条件：
- 规则被新规则替代
- 或规则检查的场景已不存在
- 或规则逻辑与当前架构冲突

操作：
- `status: active → deprecated`
- `deprecated_in: "当前阶段标识"`
- 保留 30 天观察期后可 `disabled`

### 4. 禁用为 `disabled`

条件：
- `deprecated` 状态超过 30 天
- 或规则检查器脚本已删除
- 或 owner 明确要求禁用

操作：
- `status: deprecated → disabled`
- 规则不再执行，但保留注册记录

---

## 三、版本号规则

格式：`MAJOR.MINOR.PATCH`

| 变更类型 | 版本变化 | 示例 |
|----------|----------|------|
| 状态变更 | MINOR +1 | 1.0.0 → 1.1.0 |
| 逻辑修复 | PATCH +1 | 1.0.0 → 1.0.1 |
| 重大重构 | MAJOR +1 | 1.0.0 → 2.0.0 |

---

## 四、Owner 职责

| Owner | 职责范围 |
|-------|----------|
| `architecture` | 架构相关规则（层间依赖、契约、真源） |
| `governance` | 治理相关规则（变更影响、自测） |
| `infrastructure` | 基础设施规则（仓库完整性） |

Owner 必须：
1. 维护规则的 checker_script
2. 处理规则失败的事件追踪
3. 发起状态变更申请
4. 更新规则文档

---

## 五、Rollout Stage 说明

| Stage | 说明 |
|-------|------|
| `premerge` | 仅在 premerge 门禁执行 |
| `nightly` | 仅在 nightly 门禁执行 |
| `release` | 仅在 release 门禁执行 |
| `all` | 所有门禁都执行 |

---

## 六、快照审计

每次执行规则引擎时生成快照：
- 路径：`reports/ops/rule_registry_snapshot.json`
- 内容：当前所有规则的 lifecycle 状态
- 用途：审计规则变更历史

---

**维护者**: OpenClaw 架构团队
**更新日期**: 2026-04-14
