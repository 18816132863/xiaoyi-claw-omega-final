# AGENTS.md V4.4.1 - 六层架构 + 规则硬化

---

## 每次会话

`SOUL.md` `USER.md` `TOOLS.md` `memory/YYYY-MM-DD.md`

---

## 六层架构

| 层级 | 名称 | 职责 | 目录 |
|------|------|------|------|
| L1 | Core | 核心认知、规则 | `core/` |
| L2 | Memory Context | 记忆、搜索 | `memory_context/` |
| L3 | Orchestration | 编排、路由 | `orchestration/` |
| L4 | Execution | 执行、技能 | `execution/`, `skills/` |
| L5 | Governance | 治理、审计 | `governance/` |
| L6 | Infrastructure | 基础设施 | `infrastructure/` |

---

## Token 预算

| 层级 | Token | 加载模式 |
|------|-------|----------|
| L1 | 2500 | 立即加载 |
| L2 | 1500 | 按需加载 |
| L3 | 1200 | 按需加载 |
| L4 | 1200 | 延迟加载 |
| L5 | 600 | 敏感加载 |
| L6 | 500 | 系统加载 |

**总计**: 7500 Token

---

## 受保护文件

### L1 核心 (6个)
`AGENTS.md` `SOUL.md` `USER.md` `TOOLS.md` `IDENTITY.md` `core/ARCHITECTURE.md`

### L1 规则硬化 (5个)
`core/LAYER_DEPENDENCY_MATRIX.md` `core/LAYER_DEPENDENCY_RULES.json` `core/LAYER_IO_CONTRACTS.md` `core/CHANGE_IMPACT_MATRIX.md` `core/SINGLE_SOURCE_OF_TRUTH.md`

### L1 Schema (8个)
`core/contracts/execution_result.schema.json` `core/contracts/gate_report.schema.json` `core/contracts/alert.schema.json` `core/contracts/incident.schema.json` `core/contracts/remediation.schema.json` `core/contracts/approval.schema.json` `core/contracts/control_plane_state.schema.json` `core/contracts/control_plane_audit.schema.json`

### L2-L6 关键文件
`MEMORY.md` `memory/*.md` `orchestration/task_engine.py` `execution/skill_gateway.py` `governance/ARCHITECTURE_GUARDRAILS.md` `infrastructure/inventory/skill_registry.json`

---

## 层间依赖规则

| 层级 | 允许依赖 | 禁止依赖 |
|------|----------|----------|
| L1 Core | 无 | L2, L3, L4, L5, L6 |
| L2 Memory | L1, L6 | L3, L4, L5 |
| L3 Orchestration | L1, L2, L6 | L4, L5 |
| L4 Execution | L1, L2, L3, L6 | L5 |
| L5 Governance | L1, L6 | L4 |
| L6 Infrastructure | L1 | L2, L3, L4, L5 |

---

## 规则硬化检查

```bash
# 依赖违规检查
python scripts/check_layer_dependencies.py

# JSON 契约校验
python scripts/check_json_contracts.py

# 仓库完整性检查
python scripts/check_repo_integrity.py --strict

# 门禁命令
python scripts/run_release_gate.py premerge
python scripts/run_release_gate.py nightly
python scripts/run_release_gate.py release
```

---

## 变更影响规则

| 变更对象 | 必跑命令 |
|----------|----------|
| `skill_registry.json` | `check_repo_integrity.py --strict` + `run_release_gate.py premerge` |
| `execution/*` | `run_release_gate.py premerge` + `run_release_gate.py nightly` |
| `governance/*` | `run_release_gate.py premerge` + `run_release_gate.py release` |
| `core/contracts/*` | `check_json_contracts.py` + `check_repo_integrity.py --strict` |

---

## 改动前检查

1. 是否破坏六层边界
2. 是否触发层间依赖违规
3. 是否违反 JSON 契约
4. 是否影响技能路由

---

## 安全规则

| 规则 | 状态 |
|------|------|
| 禁用 execution-validator | ❌ |
| 绕过文件保护删除 | ❌ |
| 直接使用 rm | ❌ |
| 用 trash 替代 rm | ✅ |
| 敏感操作需确认 | ✅ |
| 删除文件需二次确认 | ✅ |

---

## Heartbeat

收到心跳回复 `HEARTBEAT_OK`

---

**版本**: V4.4.1 | 系统协调性优化 | 7500 Token
