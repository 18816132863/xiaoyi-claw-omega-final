# 变更影响矩阵 V2.0.0

> **唯一真源** - 定义各类变更的影响范围和必须重跑的命令

---

## 一、变更影响表

| 变更对象 | 影响范围 | 必跑命令 |
|----------|----------|----------|
| `infrastructure/inventory/skill_registry.json` | 技能路由、网关、门禁 | `check_repo_integrity.py --strict`<br>`run_release_gate.py premerge` |
| `execution/*` | 技能执行流程 | `run_release_gate.py premerge`<br>`run_release_gate.py nightly` |
| `governance/*` | 门禁检查、告警、审计 | `run_release_gate.py premerge`<br>`run_release_gate.py release` |
| `scripts/approval_manager.py` | 审批流程、控制平面 | `check_repo_integrity.py --strict`<br>`run_release_gate.py nightly`<br>`run_release_gate.py release` |
| `scripts/control_plane*.py` | 控制平面状态 | `check_repo_integrity.py --strict` |
| `core/contracts/*` | 契约校验 | `check_json_contracts.py`<br>`check_repo_integrity.py --strict` |
| `core/LAYER_DEPENDENCY_*` | 依赖规则 | `check_layer_dependencies.py`<br>`check_repo_integrity.py --strict` |

---

## 二、详细规则

### 1. 改 `infrastructure/inventory/skill_registry.json`

**影响范围**:
- 技能路由器依赖此文件
- 技能网关依赖此文件
- P0 技能健康检查
- 反向索引派生

**必跑命令**:
```bash
python scripts/check_repo_integrity.py --strict
python scripts/run_release_gate.py premerge
```

---

### 2. 改 `execution/*`

**影响范围**:
- 所有技能执行流程
- 网关路由
- 执行结果

**必跑命令**:
```bash
python scripts/run_release_gate.py premerge
python scripts/run_release_gate.py nightly
```

---

### 3. 改 `governance/*`

**影响范围**:
- 门禁检查
- 告警系统
- 审计日志
- 处置流程

**必跑命令**:
```bash
python scripts/run_release_gate.py premerge
python scripts/run_release_gate.py release
```

---

### 4. 改 `scripts/approval_manager.py`

**影响范围**:
- 审批流程
- 审批历史
- 控制平面
- 处置记录

**必跑命令**:
```bash
python scripts/check_repo_integrity.py --strict
python scripts/run_release_gate.py nightly
python scripts/run_release_gate.py release
```

---

### 5. 改 `scripts/control_plane*.py`

**影响范围**:
- 控制平面状态
- 控制平面审计
- Summary 输出

**必跑命令**:
```bash
python scripts/check_repo_integrity.py --strict
```

---

### 6. 改 `core/contracts/*`

**影响范围**:
- 契约校验
- Schema 验证

**必跑命令**:
```bash
python scripts/check_json_contracts.py
python scripts/check_repo_integrity.py --strict
```

---

## 三、版本历史

- V2.0.0: 规则硬化版，简化为三列表格
- V1.0.0: 初始版本

---

**维护者**: OpenClaw 架构团队
**更新日期**: 2026-04-13
