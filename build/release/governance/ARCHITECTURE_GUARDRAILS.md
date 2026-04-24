# 架构护栏 V1.0.0

> **治理层文档** - 定义架构变更的护栏规则

---

## 一、变更护栏

### 1. 禁止直接修改的文件

以下文件禁止直接修改，必须通过审批流程：

| 文件 | 原因 |
|------|------|
| `core/ARCHITECTURE.md` | 主架构定义 |
| `infrastructure/inventory/skill_registry.json` | 技能注册表真源 |
| `governance/guard/protected_files.json` | 文件保护配置 |

### 2. 需要审批的变更

| 变更类型 | 审批级别 | 说明 |
|----------|----------|------|
| 修改 core/ 下的规则文件 | semi_auto | 需人工确认 |
| 修改 skill_registry.json | semi_auto | 需人工确认 |
| 修改 governance/ 下的门禁逻辑 | semi_auto | 需人工确认 |
| 删除任何受保护文件 | forbidden_auto | 禁止自动执行 |

---

## 二、依赖护栏

### 1. 禁止的依赖

| 层级 | 禁止依赖 | 原因 |
|------|----------|------|
| core | execution, orchestration, governance, infrastructure | 核心层不能依赖实现层 |
| execution | governance | 执行层不能直接依赖治理规则 |
| governance | execution, skills | 治理层不能依赖具体实现 |

### 2. 依赖检查

```bash
# 检查依赖违规
python scripts/check_layer_dependencies.py
```

---

## 三、契约护栏

### 1. 必须符合 Schema 的文件

| 文件 | Schema |
|------|--------|
| `reports/quality_gate.json` | `core/contracts/gate_report.schema.json` |
| `reports/release_gate.json` | `core/contracts/gate_report.schema.json` |
| `reports/alerts/latest_alerts.json` | `core/contracts/alert.schema.json` |
| `reports/remediation/approval_history.json` | `core/contracts/approval.schema.json` |
| `reports/ops/control_plane_state.json` | `core/contracts/control_plane_state.schema.json` |

### 2. 契约检查

```bash
# 检查 JSON 契约
python scripts/check_json_contracts.py
```

---

## 四、门禁护栏

### 1. Profile 规则

| Profile | P0 | Local | Integration | External |
|---------|-----|-------|-------------|----------|
| premerge | =0 | 必须 | 不阻塞 | 不阻塞 |
| nightly | =0 | 必须 | 必须 | 不阻塞 |
| release | =0 | 必须 | 必须 | 无 error |

### 2. 门禁命令

```bash
# CI 门禁
python scripts/run_release_gate.py premerge
python scripts/run_release_gate.py nightly
python scripts/run_release_gate.py release
```

---

## 五、审批护栏

### 1. 审批状态

| 状态 | 说明 |
|------|------|
| pending | 待审批 |
| approved | 已批准 |
| executed | 已执行（必须有 execute_record_id） |
| denied | 已拒绝 |

### 2. 审批关联

- `status: executed` 的记录必须有 `execute_record_id`
- `execute_record_id` 对应的 `reports/remediation/history/{id}.json` 必须存在

---

## 六、版本历史

- V1.0.0: 初始版本

---

**维护者**: OpenClaw 架构团队
**更新日期**: 2026-04-13
