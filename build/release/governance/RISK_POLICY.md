# 风险策略 - V1.0.0

## 风险级别定义

| 级别 | 描述 | 示例 |
|------|------|------|
| LOW | 低风险，可自动执行 | 读取文件、搜索记忆 |
| MEDIUM | 中风险，需记录后执行 | 写入文件、创建备忘录 |
| HIGH | 高风险，需确认后执行 | 删除文件、发送消息 |
| CRITICAL | 极高风险，需双重确认 | 拨打电话、创建子代理 |

## 风险评估规则

### 1. 操作类型评估
```python
def assess_operation_risk(operation: str) -> RiskLevel:
    if operation in ["delete", "send", "call"]:
        return RiskLevel.HIGH
    elif operation in ["write", "create", "modify"]:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW
```

### 2. 目标评估
```python
def assess_target_risk(target: str) -> RiskLevel:
    if target in PROTECTED_FILES:
        return RiskLevel.CRITICAL
    elif target in SENSITIVE_FILES:
        return RiskLevel.HIGH
    else:
        return RiskLevel.LOW
```

### 3. 综合评估
```python
def assess_risk(operation: str, target: str) -> RiskLevel:
    op_risk = assess_operation_risk(operation)
    target_risk = assess_target_risk(target)
    return max(op_risk, target_risk)
```

## 风险缓解措施

| 风险级别 | 缓解措施 |
|----------|----------|
| LOW | 直接执行 |
| MEDIUM | 记录审计日志后执行 |
| HIGH | 用户确认后执行 |
| CRITICAL | 双重确认后执行 |

## 受保护文件

```
AGENTS.md
MEMORY.md
TOOLS.md
SOUL.md
USER.md
IDENTITY.md
core/ARCHITECTURE.md
infrastructure/inventory/skill_registry.json
```

## 敏感文件

```
.env
*.key
*.pem
secrets/
```

## 异常处理

当风险评估失败时：
1. 记录审计日志
2. 拒绝操作
3. 通知用户
4. 提供替代方案
