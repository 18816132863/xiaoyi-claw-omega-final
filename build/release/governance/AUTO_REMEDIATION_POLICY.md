# 自动处置策略

## 动作分类

### 1. safe_auto - 可自动执行
无需人工确认，可安全自动执行的动作：

| 动作 | 说明 | 风险 |
|------|------|------|
| rebuild_dashboard | 重新生成 dashboard | 无风险，可重建 |
| rebuild_ops_state | 重新生成 ops_state | 无风险，可重建 |
| rebuild_bundle | 重新打包证据包 | 无风险，可重建 |
| retry_notifications | 重试失败的通知 | 无风险，幂等操作 |
| regenerate_reports | 重新生成缺失的报告 | 无风险，可重建 |
| cleanup_temp_cache | 清理本轮临时缓存 | 无风险，仅清理临时文件 |

### 2. semi_auto - 需人工确认
只能 dry-run 或生成建议，需要显式 `--approve` 才能执行：

| 动作 | 说明 | 风险 |
|------|------|------|
| rerun_nightly | 重跑 nightly audit | 可能产生新告警 |
| rerun_release_gate | 重跑 release gate | 可能改变发布状态 |
| toggle_incident | 打开/关闭 incident | 影响运维记录 |
| rerun_integration | 重跑 integration 验收 | 可能产生新失败 |
| fix_config_drift | 修复配置漂移 | 修改配置文件 |

### 3. forbidden_auto - 禁止自动执行
绝对不允许自动执行，只能人工处理：

| 动作 | 说明 | 原因 |
|------|------|------|
| modify_core_arch | 修改核心架构文件 | 影响系统根基 |
| modify_skill_registry | 修改技能注册表 | 影响技能路由 |
| modify_quality_rules | 修改质量门禁规则 | 影响发布判定 |
| delete_snapshots | 删除历史快照 | 数据不可恢复 |
| modify_release_decision | 修改发布判定 | 影响生产发布 |
| clear_p2_backlog | 清理 P2 遗留 | 需人工评估 |

## 触发条件

### 可触发 safe_auto 的条件

```json
{
  "safe_auto_triggers": [
    "dashboard_missing_or_stale",
    "ops_state_missing_or_stale",
    "bundle_missing",
    "notification_failed",
    "reports_missing",
    "temp_cache_overflow"
  ]
}
```

### 只能建议，不自动修的条件

```json
{
  "suggest_only_triggers": [
    "runtime_gate_fail",
    "quality_gate_fail",
    "release_blocked",
    "strong_regression",
    "p0_count_gt_zero",
    "blocking_alerts"
  ]
}
```

## 执行模式

| 模式 | 说明 |
|------|------|
| plan | 只输出建议动作列表，不执行 |
| dry-run | 模拟执行，输出将要做什么，不落真实修改 |
| execute | 真实执行，只允许 safe_auto |

## 配置开关

```json
{
  "ENABLE_SAFE_REMEDIATION": false,
  "ENABLE_SEMI_AUTO": false,
  "REQUIRE_APPROVAL_FOR_SEMI_AUTO": true,
  "MAX_RETRY_COUNT": 3,
  "COOLDOWN_MINUTES": 5
}
```

默认关闭自动执行，必须显式配置 `ENABLE_SAFE_REMEDIATION=true` 才会执行。

## 安全约束

1. **幂等性**: 所有 safe_auto 动作必须可重复执行，结果一致
2. **可追溯**: 所有执行记录写入 history
3. **可回滚**: safe_auto 动作不删除任何不可恢复的数据
4. **限流**: 同一动作 5 分钟内不重复执行
5. **审计**: 每次执行记录触发原因和结果

---

**版本**: V1.0.0
**更新时间**: 2026-04-12
