# AUDIT_POLICY.md - 审计策略

## 目的
定义系统审计的策略、范围和执行规范。

## 适用范围
所有需要审计的系统操作和决策。

## 审计范围

### 必须审计
| 类别 | 审计项 | 保留期限 |
|------|--------|----------|
| 安全 | 权限变更、访问异常 | 5年 |
| 决策 | 关键决策、策略变更 | 3年 |
| 执行 | 外部操作、高风险动作 | 3年 |
| 数据 | 数据访问、数据修改 | 3年 |
| 自主 | 自主执行、审批记录 | 3年 |

### 审计级别
| 级别 | 记录内容 | 存储方式 |
|------|----------|----------|
| basic | 操作类型、时间、用户 | 日志 |
| standard | + 参数、结果 | 数据库 |
| detailed | + 上下文、状态 | 数据库+日志 |
| comprehensive | + 全量数据 | 专用存储 |

## 审计执行

### 自动审计
```yaml
auto_audit:
  triggers:
    - operation_start
    - operation_complete
    - decision_made
    - policy_change
    - access_attempt
    
  record:
    - timestamp
    - operation_type
    - user_id
    - parameters
    - result
    - context
```

### 定期审计
```yaml
periodic_audit:
  daily:
    - 异常操作汇总
    - 权限变更检查
  weekly:
    - 策略执行审计
    - 安全事件回顾
  monthly:
    - 全面审计报告
    - 合规性检查
```

## 审计报告

### 报告结构
```yaml
audit_report:
  report_id: AUD-2024-001
  period: 2024-01
  generated_at: 2024-02-01
  
  summary:
    total_operations: 10000
    audited: 10000
    anomalies: 5
    
  findings:
    - finding_id: F001
      severity: medium
      description: "异常访问模式"
      recommendation: "加强监控"
```

## 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| 审计覆盖率 | 已审计/应审计 | <95% |
| 异常发现率 | 异常/审计 | >1% |
| 报告及时率 | 及时/应生成 | <90% |

## 引用文件
- `governance/AUDIT_LOG.md` - 审计日志规范
- `safety/RISK_POLICY.md` - 风险策略
