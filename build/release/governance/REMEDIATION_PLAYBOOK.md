# 处置运维手册

## 快速参考

### 查看建议处置动作
```bash
python scripts/remediation_center.py plan
```

### 模拟执行（不落真实修改）
```bash
python scripts/remediation_center.py dry-run rebuild_dashboard
python scripts/remediation_center.py dry-run rebuild_ops_state
python scripts/remediation_center.py dry-run rebuild_bundle
python scripts/remediation_center.py dry-run retry_notifications
```

### 执行 safe_auto 动作
```bash
python scripts/remediation_center.py execute rebuild_dashboard
python scripts/remediation_center.py execute rebuild_ops_state
python scripts/remediation_center.py execute rebuild_bundle
python scripts/remediation_center.py execute retry_notifications
```

### 查看处置历史
```bash
python scripts/remediation_center.py history
python scripts/remediation_center.py history --last 10
```

## 动作详解

### rebuild_dashboard
**用途**: 重新生成运维看板

**触发条件**:
- dashboard/ops_dashboard.json 缺失
- dashboard 生成失败
- dashboard 内容过旧（超过 24 小时）

**执行内容**:
```bash
python scripts/build_ops_dashboard.py
```

**输出文件**:
- reports/dashboard/ops_dashboard.json
- reports/dashboard/ops_dashboard.md
- reports/dashboard/ops_dashboard.html

**风险等级**: 无风险，可重建

---

### rebuild_ops_state
**用途**: 重新生成统一状态

**触发条件**:
- ops/ops_state.json 缺失
- ops_state 内容过旧（超过 1 小时）
- 状态与实际报告不一致

**执行内容**:
```bash
python scripts/ops_center.py status
```

**输出文件**:
- reports/ops/ops_state.json

**风险等级**: 无风险，可重建

---

### rebuild_bundle
**用途**: 重新打包证据包

**触发条件**:
- bundles/ 目录为空
- 最新 bundle 超过 24 小时
- bundle 内容不完整

**执行内容**:
```bash
python scripts/ops_center.py bundle
```

**输出文件**:
- reports/bundles/ops_bundle_{timestamp}.zip

**风险等级**: 无风险，可重建

---

### retry_notifications
**用途**: 重试失败的通知

**触发条件**:
- notification_result.json 显示 total_failed > 0
- 部分通知渠道发送失败

**执行内容**:
- 读取 latest_alerts.json
- 重新调用 NotificationManager
- 只重试失败的渠道

**输出文件**:
- reports/alerts/notification_result.json（更新）

**风险等级**: 无风险，幂等操作

---

## 禁止自动执行的动作

以下动作只能人工处理，禁止自动执行：

| 动作 | 原因 | 人工处理方式 |
|------|------|--------------|
| runtime gate fail | 可能是代码问题 | 检查失败原因，修复代码 |
| quality gate fail | 可能是架构问题 | 检查保护文件，修复缺失 |
| release blocked | 影响发布决策 | 检查阻塞原因，人工决策 |
| strong regression | 可能是真实问题 | 分析回归原因，决定是否修复 |
| P0 > 0 | 严重问题 | 立即处理 P0 问题 |

## 处置历史

### 查看历史
```bash
# 查看最近 10 条
python scripts/remediation_center.py history --last 10

# 查看特定类型
python scripts/remediation_center.py history --type rebuild_dashboard

# 查看失败的
python scripts/remediation_center.py history --failed
```

### 历史记录格式
```json
{
  "action_id": "rem_20260412_211500_001",
  "action_type": "rebuild_dashboard",
  "mode": "execute",
  "triggered_by": "manual",
  "source_alert": null,
  "source_incident": null,
  "started_at": "2026-04-12T21:15:00",
  "finished_at": "2026-04-12T21:15:01",
  "success": true,
  "changed_files": [
    "reports/dashboard/ops_dashboard.json",
    "reports/dashboard/ops_dashboard.md"
  ],
  "error": null,
  "requires_approval": false
}
```

## 失败处理

### dry-run 失败
1. 检查错误信息
2. 确认前置条件是否满足
3. 修复问题后重新 dry-run

### execute 失败
1. 查看历史记录中的 error 字段
2. 检查是否有部分修改已生效
3. 手动修复或回滚
4. 重新执行

### 回滚方法
safe_auto 动作都是可重建的，回滚方法：
- 重新执行对应动作即可覆盖
- 从 git 恢复之前版本

## 配置说明

### 开启自动执行
```bash
# 设置环境变量
export ENABLE_SAFE_REMEDIATION=true

# 或在配置文件中设置
# infrastructure/remediation/remediation_config.json
{
  "enable_safe_remediation": true
}
```

### 限流配置
```json
{
  "max_retry_count": 3,
  "cooldown_minutes": 5,
  "max_concurrent_actions": 1
}
```

---

**版本**: V1.0.0
**更新时间**: 2026-04-12
