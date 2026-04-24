# 变更影响强制门禁策略 V1.0.0

> **Change Impact Enforcement Policy** - 定义变更与门禁的强制关系

---

## 一、变更分类与门禁要求

### 1. Blocking 变更（必须执行）

| 变更模式 | 必须执行 | 阻断级别 |
|----------|----------|----------|
| `core/contracts/*` | `check_json_contracts.py` | **BLOCKING** |
| `infrastructure/inventory/skill_registry.json` | `premerge` | **BLOCKING** |
| `execution/*` | `premerge` + `nightly` | **BLOCKING** |
| `governance/*` | `premerge` + `release` | **BLOCKING** |
| `scripts/approval_manager.py` | `nightly` + `release` | **BLOCKING** |
| `core/LAYER_DEPENDENCY_RULES.json` | `check_layer_dependencies.py` | **BLOCKING** |

### 2. Follow-up Required 变更（提示补跑）

| 变更模式 | 建议执行 | 级别 |
|----------|----------|------|
| `scripts/check_*.py` | `check_repo_integrity.py --strict` | FOLLOW-UP |
| `infrastructure/release/*` | `release` | FOLLOW-UP |
| `reports/ops/*` | `check_json_contracts.py` | FOLLOW-UP |

---

## 二、门禁执行流程

### Premerge 流程

```
1. 获取变更文件列表 (git diff 或 --files)
2. 生成 change_impact.json
3. 执行 required commands
4. 记录 executed_checks.json
5. 校验：required commands 是否都已执行
6. 若缺失 → FAIL + 输出 missing_required_checks
7. 若满足 → PASS
```

### Nightly 流程

```
1. 读取 change_impact.json (如有)
2. 检查是否被标记为 required
3. 执行门禁检查
4. 输出：whether it was required by prior change impact
```

### Release 流程

```
1. 读取 change_impact.json (如有)
2. 检查 governance/approval/remediation 变更是否要求 release
3. 执行门禁检查
4. 输出：whether governance changes require it
```

---

## 三、文件关系

### change_impact.json

```json
{
  "generated_at": "2026-04-14T00:00:00Z",
  "changed_files": ["core/contracts/alert.schema.json"],
  "changed_categories": ["core/contracts"],
  "required_commands": [
    "python scripts/check_json_contracts.py"
  ],
  "required_profiles": ["premerge"],
  "blocking_if_missing": true
}
```

### executed_checks.json

```json
{
  "current_profile": "premerge",
  "executed_commands": [
    "python scripts/check_layer_dependencies.py",
    "python scripts/check_json_contracts.py",
    "python scripts/run_release_gate.py premerge"
  ],
  "executed_rule_checks": {
    "layer_dependency": true,
    "json_contract": true
  },
  "executed_gate_checks": {
    "runtime": true,
    "quality": true
  },
  "timestamp": "2026-04-14T00:00:00Z"
}
```

### 校验逻辑

```
for cmd in change_impact.required_commands:
    if cmd not in executed_checks.executed_commands:
        return FAIL, missing: [cmd]
return PASS
```

---

## 四、阻断规则

### 强制阻断场景

1. **改了 `core/contracts/*` 但没跑 `check_json_contracts.py`**
   - 输出: `Missing required check: check_json_contracts.py`
   - 结果: `overall_passed = false`

2. **改了 `execution/*` 但没跑 `premerge`**
   - 输出: `Missing required profile: premerge`
   - 结果: `overall_passed = false`

3. **改了 `governance/*` 但没跑 `release`**
   - 输出: `Missing required profile: release (follow-up required)`
   - 结果: `premerge` 可通过，但提示需要补跑 `release`

---

## 五、Summary 输出格式

### Change Impact Enforcement: PASSED

```
【Change Impact Enforcement】
  Status: ✅ PASSED
  Changed Files: 3
  Required Commands: 2
  Executed: 2/2
```

### Change Impact Enforcement: FAILED

```
【Change Impact Enforcement】
  Status: ❌ FAILED
  Changed Files: 3
  Required Commands: 2
  Executed: 1/2
  Missing:
    - python scripts/check_json_contracts.py
  Required By: core/contracts/alert.schema.json
```

---

## 六、版本历史

- V1.0.0: 初始版本，定义变更影响强制门禁策略

---

**维护者**: OpenClaw 架构团队
**更新日期**: 2026-04-14
