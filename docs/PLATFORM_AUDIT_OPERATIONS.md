# 平台审计操作手册

## 版本
- V8.4.0 审计闭环版
- 日期: 2026-04-24

## 一、CLI 命令

### 1.1 查询最近记录

```bash
# 查询最近 10 条记录
python scripts/invocation_audit_cli.py query-recent

# 查询最近 50 条记录
python scripts/invocation_audit_cli.py query-recent --limit 50

# JSON 格式输出
python scripts/invocation_audit_cli.py query-recent --format json

# CSV 格式输出
python scripts/invocation_audit_cli.py query-recent --format csv

# 脱敏输出
python scripts/invocation_audit_cli.py query-recent --redact
```

### 1.2 查询 Uncertain 记录

```bash
# 查询 uncertain 记录
python scripts/invocation_audit_cli.py query-uncertain

# 限制数量
python scripts/invocation_audit_cli.py query-uncertain --limit 20

# JSON 格式
python scripts/invocation_audit_cli.py query-uncertain --format json
```

### 1.3 查询 Failed 记录

```bash
python scripts/invocation_audit_cli.py query-failed
```

### 1.4 查询 Timeout 记录

```bash
python scripts/invocation_audit_cli.py query-timeout
```

### 1.5 显示统计信息

```bash
python scripts/invocation_audit_cli.py stats
```

### 1.6 手动确认

```bash
# 确认成功
python scripts/invocation_audit_cli.py confirm --id 123 --status confirmed_success --note "用户确认短信已收到"

# 确认失败
python scripts/invocation_audit_cli.py confirm --id 124 --status confirmed_failed --note "用户确认未收到"

# 确认重复
python scripts/invocation_audit_cli.py confirm --id 125 --status confirmed_duplicate --note "与记录 #120 重复"
```

### 1.7 导出报告

```bash
# 导出 JSON
python scripts/invocation_audit_cli.py export --type uncertain --format json --output uncertain_report.json

# 导出 CSV
python scripts/invocation_audit_cli.py export --type failed --format csv --output failed_report.csv

# 脱敏导出
python scripts/invocation_audit_cli.py export --type recent --redact --output recent_redacted.json
```

### 1.8 清理旧记录

```bash
# 清理 30 天前的记录
python scripts/invocation_audit_cli.py cleanup --days 30

# 清理 90 天前的记录（包括 failed）
python scripts/invocation_audit_cli.py cleanup --days 90 --keep-failed false
```

## 二、程序化接口

### 2.1 审计查询

```python
from capabilities.audit_queries import AuditQueries

# 获取最近记录
records = AuditQueries.get_recent(10)

# 按 task_id 查询
records = AuditQueries.get_by_task_id("task_123")

# 按 capability 查询
records = AuditQueries.get_by_capability("MESSAGE_SENDING")

# 获取 uncertain 记录
records = AuditQueries.get_uncertain()

# 获取统计信息
stats = AuditQueries.get_stats()
```

### 2.2 手动确认

```python
from capabilities.confirm_invocation import ConfirmInvocation

# 确认成功
ConfirmInvocation.confirm_success(123, "用户确认短信已收到")

# 确认失败
ConfirmInvocation.confirm_failed(124, "用户确认未收到")

# 确认重复
ConfirmInvocation.confirm_duplicate(125, "与记录 #120 重复")

# 获取确认统计
stats = ConfirmInvocation.get_confirmation_stats()
```

### 2.3 解释状态

```python
from capabilities.explain_invocation_status import ExplainInvocationStatus

# 解释记录状态
explanation = ExplainInvocationStatus.explain(123)
print(ExplainInvocationStatus.format_explanation(explanation))

# 解释记录字典
record = {"id": 123, "normalized_status": "timeout", ...}
explanation = ExplainInvocationStatus.explain_record(record)
```

## 三、健康巡检

### 3.1 运行巡检

```bash
python scripts/platform_health_check.py
```

### 3.2 输出示例

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

## 四、定时任务

### 4.1 每日健康巡检

```bash
# 添加到 crontab
0 8 * * * cd /path/to/workspace && python scripts/platform_health_check.py >> logs/health_check.log 2>&1
```

### 4.2 每周清理

```bash
# 每周日凌晨 2 点清理
0 2 * * 0 cd /path/to/workspace && python scripts/invocation_audit_cli.py cleanup --days 30
```

## 五、告警阈值

| 指标 | 阈值 | 说明 |
|------|------|------|
| failed_rate_24h | > 5% | 警告 |
| failed_rate_24h | > 10% | 严重 |
| timeout_rate_24h | > 5% | 警告 |
| timeout_rate_24h | > 10% | 严重 |
| unconfirmed_uncertain | > 10 | 警告 |
| unconfirmed_uncertain | > 50 | 严重 |

## 六、最佳实践

### 6.1 每日操作

1. 运行健康巡检
2. 检查 uncertain 记录
3. 确认待确认记录
4. 导出日报（如需要）

### 6.2 每周操作

1. 运行清理脚本
2. 导出周报
3. 分析趋势

### 6.3 每月操作

1. 导出月度报告
2. 评估保留策略
3. 优化配置
