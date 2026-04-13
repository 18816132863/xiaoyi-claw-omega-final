# 唯一真源清单 V2.0.0

> **唯一真源** - 定义所有核心对象的真源与派生关系

---

## 一、真源清单

### 1. 主架构真源

| 对象 | 真源路径 | 说明 |
|------|----------|------|
| 六层架构定义 | `core/ARCHITECTURE.md` | 唯一主架构定义 |
| 架构完整性规则 | `core/ARCHITECTURE_INTEGRITY.md` | 完整性校验规范 |

---

### 2. Skill Registry 真源

| 对象 | 真源路径 | 说明 |
|------|----------|------|
| 技能注册表 | `infrastructure/inventory/skill_registry.json` | 唯一真源 |
| 技能反向索引 | `infrastructure/inventory/skill_inverted_index.json` | **派生物**，不可手改 |

---

### 3. Latest Gate Reports 真源

| 对象 | 真源路径 | 说明 |
|------|----------|------|
| Runtime 完整性 | `reports/runtime_integrity.json` | 真源 |
| Quality Gate | `reports/quality_gate.json` | 真源 |
| Release Gate | `reports/release_gate.json` | 真源 |

---

### 4. Latest Alerts 真源

| 对象 | 真源路径 | 说明 |
|------|----------|------|
| 最新告警 | `reports/alerts/latest_alerts.json` | 真源 |

---

### 5. Incident 真源

| 对象 | 真源路径 | 说明 |
|------|----------|------|
| 事件追踪 | `governance/ops/incident_tracker.json` | 真源 |

---

### 6. Approval 真源

| 对象 | 真源路径 | 说明 |
|------|----------|------|
| 审批历史 | `reports/remediation/approval_history.json` | 真源 |

---

### 7. Control Plane Latest 真源

| 对象 | 真源路径 | 说明 |
|------|----------|------|
| 控制平面状态 | `reports/ops/control_plane_state.json` | 真源 |
| 控制平面审计 | `reports/ops/control_plane_audit.json` | 真源 |

---

## 二、派生物标注规范

所有派生物必须包含以下字段：

```json
{
  "derived": true,
  "source": "path/to/source.json",
  "generated_at": "2026-04-13T11:00:00Z",
  "generator": "script_name.py"
}
```

---

## 三、禁止行为

```
❌ 手动修改派生物
❌ 同一对象两套真源
❌ 真源变更不更新派生
❌ 派生物不标注 derived
```

---

## 四、版本历史

- V2.0.0: 规则硬化版，明确 9 项真源
- V1.0.0: 初始版本

---

**维护者**: OpenClaw 架构团队
**更新日期**: 2026-04-13
