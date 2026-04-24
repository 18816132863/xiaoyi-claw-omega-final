# 告警路由策略 V1.0

## 一、告警路由规则

| 告警类型 | 严重级别 | 通知渠道 | 冷却窗口 |
|----------|----------|----------|----------|
| P0_BLOCKED | 阻塞级 | github_summary + feishu | 30 分钟 |
| STRONG_REGRESSION | 阻塞级 | github_summary + feishu | 30 分钟 |
| RELEASE_BLOCKED | 阻塞级 | github_summary + feishu | 15 分钟 |
| WEAK_REGRESSION | 警告级 | github_summary | 60 分钟 |

## 二、冷却机制

### 2.1 冷却规则

- 相同 `alert_type` + 相同 `blocked_reasons` 在冷却窗口内不重复发送
- 冷却窗口：默认 30 分钟，可按告警类型配置
- 最大通知频率：每小时最多 10 条

### 2.2 冷却例外

- **恢复通知不受冷却限制**：告警恢复时总是发送 RESOLVED 通知
- **告警升级时允许重发**：严重程度提升时可重发

## 三、升级规则

| 时间 | 动作 |
|------|------|
| 30 分钟未确认 | 重复发送通知 |
| 60 分钟未处理 | 升级到二级负责人 |
| 120 分钟未解决 | 创建紧急 Incident |

## 四、通知渠道配置

### 4.1 GitHub Summary

- **状态**：始终可用
- **用途**：GitHub Actions Step Summary
- **降级**：无（总是成功）

### 4.2 飞书 Webhook

- **环境变量**：`FEISHU_WEBHOOK_URL`
- **格式**：`https://open.feishu.cn/open-apis/bot/v2/hook/xxx`
- **降级**：未配置时自动跳过，不影响主流程

### 4.3 通用 Webhook

- **环境变量**：`ALERT_WEBHOOK_URL`
- **格式**：任意 HTTP POST 端点
- **降级**：未配置时自动跳过

## 五、OPEN / RESOLVED 通知

### 5.1 OPEN 通知

触发条件：
- 阻塞级告警首次出现
- 自动创建 Incident

通知内容：
- incident_id
- alert_type
- severity
- blocked_reasons
- recommended_actions

### 5.2 RESOLVED 通知

触发条件：
- 阻塞级告警消失
- 自动关闭 Incident

通知内容：
- incident_id
- resolved_at
- resolution_note

## 六、降级策略

| 情况 | 降级动作 |
|------|----------|
| 飞书未配置 | 仅 GitHub Summary |
| 飞书发送失败 | 记录错误，继续其他渠道 |
| 所有外部渠道失败 | 仅本地 alerts.json |

## 七、通知历史

### 7.1 存储位置

- `reports/alerts/notification_result.json` - 最新通知结果
- `reports/alerts/notification_history.json` - 历史记录（保留 100 条）

### 7.2 历史记录字段

```json
{
  "timestamp": "2026-04-12T20:00:00",
  "alert_type": "P0_BLOCKED",
  "severity": "blocking",
  "blocked_reasons": ["..."],
  "channels": ["github_summary", "feishu"],
  "incident_id": "INC-xxx"
}
```

## 八、配置文件

详细配置见：`infrastructure/alerting/alert_routing.json`

---

**版本**: V1.0  
**更新时间**: 2026-04-12
