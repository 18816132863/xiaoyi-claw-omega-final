# 平台健康巡检手册

## 版本
- V8.4.0 审计闭环版
- 日期: 2026-04-24

## 一、巡检命令

### 1.1 运行巡检

```bash
python scripts/platform_health_check.py
```

### 1.2 输出示例

```
============================================================
平台健康巡检报告
============================================================
时间: 2026-04-24T14:00:00

📊 总体统计
----------------------------------------
总调用数: 1000
Uncertain 记录: 50
未确认 Uncertain: 10

📈 24 小时统计
----------------------------------------
失败率: 2.50%
超时率: 1.80%

🔐 NOTIFICATION 授权状态
----------------------------------------
状态: configured
说明: authCode 已配置

📋 状态分布
----------------------------------------
  completed: 900 (90.0%)
  failed: 50 (5.0%)
  timeout: 50 (5.0%)

🏥 健康评估
----------------------------------------
✅ 所有指标正常

============================================================
```

## 二、巡检指标

### 2.1 核心指标

| 指标 | 说明 | 健康阈值 |
|------|------|----------|
| total_invocations | 总调用数 | - |
| uncertain_count | Uncertain 记录数 | - |
| unconfirmed_uncertain_count | 未确认 Uncertain 数 | < 10 |
| failed_rate_24h | 24 小时失败率 | < 5% |
| timeout_rate_24h | 24 小时超时率 | < 5% |
| notification_auth_status | NOTIFICATION 授权状态 | configured |

### 2.2 状态分布

| 状态 | 说明 |
|------|------|
| completed | 成功完成 |
| failed | 执行失败 |
| timeout | 请求超时 |
| result_uncertain | 结果不确定 |
| queued_for_delivery | 等待处理 |
| auth_required | 需要授权 |

## 三、健康评估

### 3.1 评估规则

| 条件 | 级别 | 说明 |
|------|------|------|
| failed_rate_24h > 10% | 严重 | 失败率过高 |
| failed_rate_24h > 5% | 警告 | 失败率偏高 |
| timeout_rate_24h > 10% | 严重 | 超时率过高 |
| timeout_rate_24h > 5% | 警告 | 超时率偏高 |
| unconfirmed_uncertain > 50 | 严重 | 待确认过多 |
| unconfirmed_uncertain > 10 | 警告 | 待确认偏多 |
| notification_auth != configured | 警告 | 授权未配置 |

### 3.2 退出码

- `0`: 健康
- `1`: 有严重问题

## 四、定时巡检

### 4.1 Crontab 配置

```bash
# 每小时巡检
0 * * * * cd /path/to/workspace && python scripts/platform_health_check.py >> logs/health_check.log 2>&1

# 每日 8:00 巡检并发送报告
0 8 * * * cd /path/to/workspace && python scripts/platform_health_check.py | mail -s "平台健康报告" admin@example.com
```

### 4.2 Systemd Timer

```ini
# /etc/systemd/system/platform-health-check.service
[Unit]
Description=Platform Health Check

[Service]
Type=oneshot
ExecStart=/usr/bin/python /path/to/workspace/scripts/platform_health_check.py
WorkingDirectory=/path/to/workspace

# /etc/systemd/system/platform-health-check.timer
[Unit]
Description=Run platform health check hourly

[Timer]
OnCalendar=hourly

[Install]
WantedBy=timers.target
```

## 五、告警集成

### 5.1 邮件告警

```bash
#!/bin/bash
# scripts/health_check_with_alert.sh

REPORT=$(python scripts/platform_health_check.py)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "$REPORT" | mail -s "⚠️ 平台健康告警" admin@example.com
fi

echo "$REPORT"
exit $EXIT_CODE
```

### 5.2 Webhook 告警

```python
#!/usr/bin/env python
# scripts/health_check_webhook.py

import requests
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.platform_health_check import run_health_check

WEBHOOK_URL = "https://hooks.example.com/alert"

report = run_health_check()

# 检查是否需要告警
if report["failed_rate_24h"] > 5 or report["timeout_rate_24h"] > 5:
    requests.post(WEBHOOK_URL, json={
        "text": f"⚠️ 平台健康告警\n\n"
                f"失败率: {report['failed_rate_24h']:.2f}%\n"
                f"超时率: {report['timeout_rate_24h']:.2f}%"
    })
```

## 六、程序化接口

### 6.1 获取健康报告

```python
from scripts.platform_health_check import run_health_check, format_health_report

# 获取报告
report = run_health_check()

# 格式化输出
print(format_health_report(report))

# 检查健康状态
if report["failed_rate_24h"] > 5:
    print("⚠️ 失败率过高")
```

### 6.2 自定义巡检

```python
from platform_adapter.invocation_ledger import get_statistics, export_recent

# 获取统计
stats = get_statistics()

# 自定义检查
if stats["uncertain_count"] > 100:
    print("⚠️ Uncertain 记录过多")

# 检查特定能力
from capabilities.audit_queries import AuditQueries
msg_records = AuditQueries.get_by_capability("MESSAGE_SENDING", limit=1000)
failed_count = sum(1 for r in msg_records if r["normalized_status"] == "failed")
failed_rate = failed_count / len(msg_records) * 100 if msg_records else 0

if failed_rate > 5:
    print(f"⚠️ MESSAGE_SENDING 失败率: {failed_rate:.2f}%")
```

## 七、巡检报告解读

### 7.1 正常报告

```
🏥 健康评估
----------------------------------------
✅ 所有指标正常
```

**解读**: 平台运行正常，无需干预。

### 7.2 警告报告

```
🏥 健康评估
----------------------------------------
⚠️ 24小时失败率过高: 6.50%
⚠️ 未确认 uncertain 记录过多: 15
```

**解读**: 需要关注，建议：
1. 检查失败原因
2. 确认 uncertain 记录
3. 优化配置

### 7.3 严重报告

```
🏥 健康评估
----------------------------------------
⚠️ 24小时失败率过高: 12.50%
⚠️ 24小时超时率过高: 15.00%
⚠️ NOTIFICATION 未正确授权
```

**解读**: 需要立即处理：
1. 检查平台连接
2. 检查网络状况
3. 配置 NOTIFICATION 授权
4. 联系技术支持

## 八、最佳实践

### 8.1 巡检频率

- 生产环境: 每小时
- 测试环境: 每 6 小时
- 开发环境: 每天

### 8.2 告警阈值

根据业务需求调整：
- 高可用系统: 失败率 < 1%
- 一般系统: 失败率 < 5%
- 测试系统: 失败率 < 10%

### 8.3 响应流程

1. 收到告警
2. 查看详细报告
3. 定位问题
4. 采取措施
5. 验证恢复
6. 记录复盘
