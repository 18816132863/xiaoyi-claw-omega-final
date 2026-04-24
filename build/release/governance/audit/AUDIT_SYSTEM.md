# AUDIT_SYSTEM.md - 审计系统

## 目的
定义系统审计规则，确保关键操作可追溯、可审计。

## 适用范围
所有需要审计的系统操作。

## 审计事件

### 强制审计事件
| 事件类型 | 触发条件 | 审计级别 |
|----------|----------|----------|
| 高风险操作 | 风险等级 ≥ HIGH | CRITICAL |
| 用户确认 | 用户确认操作 | HIGH |
| 用户拒绝 | 用户拒绝操作 | HIGH |
| 安全违规 | 安全边界违规 | CRITICAL |
| 配置变更 | 系统配置修改 | HIGH |
| 技能变更 | 技能安装/卸载 | HIGH |
| 记忆删除 | 记忆删除操作 | HIGH |
| 系统错误 | 系统级错误 | MEDIUM |

### 可选审计事件
| 事件类型 | 触发条件 | 审计级别 |
|----------|----------|----------|
| 工具调用 | 工具调用 | INFO |
| 技能调用 | 技能调用 | INFO |
| 记忆读写 | 记忆操作 | INFO |
| 检索操作 | 外部检索 | INFO |

## 审计记录格式

### 标准格式
```json
{
  "auditId": "audit_20260406_111200_001",
  "timestamp": "2026-04-06T11:12:00+08:00",
  "sessionId": "session_001",
  "userId": "user_001",
  "event": {
    "type": "high_risk_operation",
    "category": "file_operation",
    "action": "file_delete",
    "target": "/path/to/file"
  },
  "context": {
    "taskId": "task_001",
    "step": 5,
    "riskLevel": "HIGH"
  },
  "decision": {
    "required": true,
    "confirmed": true,
    "confirmedAt": "2026-04-06T11:12:05+08:00",
    "confirmMethod": "user_input"
  },
  "result": {
    "status": "success",
    "duration": 150
  },
  "metadata": {
    "clientIp": "192.168.1.1",
    "userAgent": "OpenClaw/1.0"
  }
}
```

## 审计存储

### 存储配置
| 配置项 | 值 |
|--------|-----|
| 存储位置 | `audit/logs/` |
| 存储格式 | JSONL |
| 分片规则 | 按日期分文件 |
| 保留期限 | 90天 |
| 加密 | 可选AES加密 |

### 存储结构
```
audit/
├── logs/
│   ├── 2026-04-06.jsonl
│   ├── 2026-04-05.jsonl
│   └── archive/
│       └── 2026-03/
├── reports/
│   └── summary/
└── config/
    └── audit_config.json
```

## 审计查询

### 查询接口
```bash
# 按时间范围查询
audit query --from "2026-04-06T00:00:00" --to "2026-04-06T23:59:59"

# 按事件类型查询
audit query --type "high_risk_operation"

# 按用户查询
audit query --user "user_001"

# 按审计级别查询
audit query --level "CRITICAL"
```

### 查询字段
| 字段 | 说明 | 示例 |
|------|------|------|
| auditId | 审计ID | audit_20260406_001 |
| timestamp | 时间戳 | 2026-04-06T11:12:00 |
| event.type | 事件类型 | high_risk_operation |
| event.action | 操作动作 | file_delete |
| result.status | 执行状态 | success/failure |

## 审计分析

### 分析维度
| 维度 | 分析内容 |
|------|----------|
| 时间分布 | 按时间段的审计事件分布 |
| 类型分布 | 按事件类型的分布 |
| 用户分布 | 按用户的审计事件分布 |
| 结果分布 | 成功/失败比例 |

### 分析报告
```json
{
  "reportId": "report_20260406",
  "period": {
    "from": "2026-04-06T00:00:00+08:00",
    "to": "2026-04-06T23:59:59+08:00"
  },
  "summary": {
    "totalEvents": 150,
    "byLevel": {
      "CRITICAL": 5,
      "HIGH": 20,
      "MEDIUM": 30,
      "INFO": 95
    },
    "byType": {
      "high_risk_operation": 15,
      "user_confirm": 20,
      "security_violation": 2,
      "config_change": 8
    },
    "byResult": {
      "success": 140,
      "failure": 10
    }
  },
  "highlights": [
    {
      "type": "security_violation",
      "count": 2,
      "severity": "CRITICAL"
    }
  ]
}
```

## 审计告警

### 告警规则
| 条件 | 告警级别 |
|------|----------|
| 1小时内CRITICAL > 3 | CRITICAL |
| 1小时内HIGH > 10 | WARNING |
| 用户拒绝率 > 30% | WARNING |
| 安全违规 > 0 | CRITICAL |

### 告警通知
| 级别 | 通知方式 |
|------|----------|
| CRITICAL | 即时通知 + 日志 |
| WARNING | 日志 + 定期汇总 |
| INFO | 日志 |

## 审计保护

### 完整性保护
- 只追加，不修改
- 定期校验哈希
- 异地备份

### 访问控制
- 只读访问
- 需要审计权限
- 访问记录

### 数据保留
| 级别 | 保留期限 |
|------|----------|
| CRITICAL | 永久 |
| HIGH | 1年 |
| MEDIUM | 90天 |
| INFO | 30天 |

## 异常处理

| 异常 | 处理 |
|------|------|
| 写入失败 | 重试 + 告警 |
| 存储满 | 自动归档 |
| 查询失败 | 返回错误 |

## 维护方式
- 新增审计事件: 更新事件类型表
- 调整保留期限: 修改保留配置
- 新增告警规则: 更新告警规则表

## 引用文件
- `governance/AUDIT_LOG.md` - 审计日志规范
- `alert/ALERT_POLICY.md` - 告警策略
