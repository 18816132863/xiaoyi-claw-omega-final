# 告警处理手册 V1.0

## 一、告警分类

| 告警类型 | 严重级别 | 处理时限 | 通知渠道 |
|----------|----------|----------|----------|
| P0_BLOCKED | 阻塞级 | 立即处理 | GitHub + 飞书 |
| STRONG_REGRESSION | 阻塞级 | 30分钟内 | GitHub + 飞书 |
| RELEASE_BLOCKED | 阻塞级 | 立即处理 | GitHub + 飞书 |
| WEAK_REGRESSION | 警告级 | 24小时内 | GitHub |

## 二、处理流程

### 2.1 收到告警后

1. **查看告警详情**
   ```bash
   cat reports/alerts/latest_alerts.json
   ```

2. **查看 Dashboard**
   ```bash
   cat reports/dashboard/ops_dashboard.md
   ```

3. **确认 Incident**
   ```bash
   python scripts/incident_cli.py acknowledge <incident_id> <your_name>
   ```

### 2.2 定位问题

| 告警类型 | 首先查看 |
|----------|----------|
| P0_BLOCKED | reports/runtime_integrity.json → failure_reasons |
| STRONG_REGRESSION | reports/nightly_audit.json → strong_regressions |
| RELEASE_BLOCKED | reports/release_gate.json → blocked_reasons |
| WEAK_REGRESSION | reports/nightly_audit.json → weak_regressions |

### 2.3 修复问题

1. 根据告警类型定位代码
2. 修复问题
3. 本地验证
   ```bash
   python scripts/run_release_gate.py premerge
   ```
4. 提交代码

### 2.4 关闭 Incident

```bash
python scripts/incident_cli.py resolve <incident_id> "修复说明"
```

## 三、升级规则

| 情况 | 升级动作 |
|------|----------|
| 30分钟未确认 | 重复发送通知 |
| 60分钟未处理 | 升级到二级负责人 |
| 120分钟未解决 | 创建紧急 Incident |

## 四、通知渠道配置

### 4.1 飞书 Webhook

```bash
export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
```

### 4.2 通用 Webhook

```bash
export ALERT_WEBHOOK_URL="https://your-webhook-url"
```

### 4.3 未配置时

自动降级为：
- GitHub Summary（总是可用）
- 本地 alerts.json

## 五、常见问题

### Q: 告警一直重复发送？

检查冷却机制：
```bash
cat reports/alerts/notification_history.json
```

### Q: 外部通知发送失败？

1. 检查环境变量是否配置
2. 检查网络连接
3. 查看 notification_result.json

### Q: 如何查看历史告警？

```bash
ls reports/alerts/history/
cat reports/alerts/history/<timestamp>_alerts.json
```

## 六、值班表

| 时间段 | 负责人 | 联系方式 |
|--------|--------|----------|
| 工作日 9:00-18:00 | [待填写] | [待填写] |
| 非工作时间 | [待填写] | [待填写] |

---

**版本**: V1.0  
**更新时间**: 2026-04-12
