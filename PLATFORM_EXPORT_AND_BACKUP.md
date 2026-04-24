# 平台导出与备份手册

## 版本
- V8.4.0 审计闭环版
- 日期: 2026-04-24

## 一、导出格式

### 1.1 JSON 导出

```bash
# 导出 JSON
python scripts/invocation_audit_cli.py export --type recent --format json --output recent.json

# 导出 uncertain 报告
python scripts/invocation_audit_cli.py export --type uncertain --format json --output uncertain.json

# 导出 failed 报告
python scripts/invocation_audit_cli.py export --type failed --format json --output failed.json

# 导出 timeout 报告
python scripts/invocation_audit_cli.py export --type timeout --format json --output timeout.json
```

**JSON 格式示例**:
```json
[
  {
    "id": 1,
    "task_id": "task_123",
    "capability": "MESSAGE_SENDING",
    "platform_op": "send_message",
    "normalized_status": "completed",
    "error_code": null,
    "user_message": "已完成",
    "result_uncertain": 0,
    "fallback_used": 0,
    "elapsed_ms": 1500,
    "created_at": "2026-04-24T14:00:00",
    "completed_at": "2026-04-24T14:00:01"
  }
]
```

### 1.2 CSV 导出

```bash
# 导出 CSV
python scripts/invocation_audit_cli.py export --type recent --format csv --output recent.csv
```

**CSV 格式示例**:
```csv
id,task_id,capability,platform_op,normalized_status,error_code,user_message,result_uncertain,fallback_used,elapsed_ms,created_at,completed_at
1,task_123,MESSAGE_SENDING,send_message,completed,,已完成,0,0,1500,2026-04-24T14:00:00,2026-04-24T14:00:01
```

## 二、脱敏导出

### 2.1 脱敏规则

| 字段 | 脱敏规则 |
|------|----------|
| phone_number | 保留前 3 位和后 4 位，中间用 **** 替换 |
| phoneNumber | 同上 |
| phone | 同上 |
| content | 保留前 10 个字符，后面用 ... 替换 |

**示例**:
- `13800138000` → `138****8000`
- `这是一条很长的短信内容` → `这是一条很长的短...`

### 2.2 脱敏导出命令

```bash
# 脱敏导出
python scripts/invocation_audit_cli.py export --type recent --redact --output recent_redacted.json

# 脱敏查询
python scripts/invocation_audit_cli.py query-recent --redact --format json
```

## 三、备份策略

### 3.1 清理前备份

```bash
# 备份再清理
python scripts/invocation_audit_cli.py export --type recent --format json --output backup_$(date +%Y%m%d).json
python scripts/invocation_audit_cli.py cleanup --days 30
```

### 3.2 定期备份脚本

```bash
#!/bin/bash
# scripts/backup_invocations.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 导出所有记录
python scripts/invocation_audit_cli.py export --type recent --format json --output $BACKUP_DIR/invocations_$DATE.json

# 导出 uncertain 记录
python scripts/invocation_audit_cli.py export --type uncertain --format json --output $BACKUP_DIR/uncertain_$DATE.json

# 导出 failed 记录
python scripts/invocation_audit_cli.py export --type failed --format json --output $BACKUP_DIR/failed_$DATE.json

echo "Backup completed: $DATE"
```

### 3.3 定时备份

```bash
# 每日凌晨 3 点备份
0 3 * * * cd /path/to/workspace && bash scripts/backup_invocations.sh >> logs/backup.log 2>&1
```

## 四、程序化导出

### 4.1 导出函数

```python
from capabilities.audit_queries import AuditQueries
import json

# 获取记录
records = AuditQueries.get_recent(100)

# 导出 JSON
with open("export.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

# 导出 CSV
import csv
with open("export.csv", "w", newline="", encoding="utf-8") as f:
    if records:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
```

### 4.2 脱敏函数

```python
def redact_record(record: dict) -> dict:
    """脱敏记录"""
    result = record.copy()
    
    # 脱敏手机号
    for key in ["phone_number", "phoneNumber", "phone"]:
        if key in result:
            val = str(result[key])
            if len(val) >= 7:
                result[key] = val[:3] + "****" + val[-4:]
    
    return result

# 脱敏导出
records = AuditQueries.get_recent(100)
redacted = [redact_record(r) for r in records]

with open("export_redacted.json", "w", encoding="utf-8") as f:
    json.dump(redacted, f, ensure_ascii=False, indent=2)
```

## 五、恢复与导入

### 5.1 导入 JSON

```python
import json
from platform_adapter.invocation_ledger import record_invocation

# 读取备份
with open("backup.json", "r", encoding="utf-8") as f:
    records = json.load(f)

# 导入（注意：会生成新的 ID）
for r in records:
    record_invocation(
        capability=r["capability"],
        platform_op=r["platform_op"],
        normalized_status=r["normalized_status"],
        # ... 其他字段
    )
```

### 5.2 直接恢复数据库

```bash
# 备份数据库文件
cp data/tasks.db data/tasks.db.backup

# 恢复
cp data/tasks.db.backup data/tasks.db
```

## 六、存储管理

### 6.1 存储估算

- 单条记录: ~1 KB
- 每日 1000 条: ~1 MB
- 每月: ~30 MB
- 每年: ~360 MB

### 6.2 清理策略

| 状态 | 保留期限 | 清理频率 |
|------|----------|----------|
| completed | 30 天 | 每周 |
| failed | 90 天 | 每月 |
| timeout | 90 天 | 每月 |
| uncertain | 永久 | 不清理 |

### 6.3 监控存储

```bash
# 检查数据库大小
du -h data/tasks.db

# 检查记录数
sqlite3 data/tasks.db "SELECT COUNT(*) FROM platform_invocations"
```

## 七、最佳实践

### 7.1 备份频率

- 每日增量备份
- 每周全量备份
- 每月归档备份

### 7.2 备份保留

- 每日备份保留 7 天
- 每周备份保留 4 周
- 每月备份保留 12 月

### 7.3 安全措施

- 备份文件加密
- 传输使用 HTTPS
- 存储使用安全存储
