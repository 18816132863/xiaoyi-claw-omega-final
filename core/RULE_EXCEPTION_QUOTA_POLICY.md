# 规则例外配额策略 V1.0.0

## 概述

定义例外配额规则，限制每个 owner 和 rule 的例外数量，防止例外滥用。

---

## 一、Owner 级配额

### 配额定义

| Owner 类型 | max_active_exceptions | max_high_debt_exceptions |
|------------|----------------------|--------------------------|
| architecture | 5 | 2 |
| governance | 5 | 2 |
| infrastructure | 3 | 1 |
| 其他 | 2 | 1 |

### 说明

- `max_active_exceptions`: 该 owner 同时存在的活跃例外上限
- `max_high_debt_exceptions`: 该 owner 同时存在的高债务例外上限

---

## 二、Rule 级配额

### 配额定义

| 规则类型 | max_active_exceptions_per_rule |
|----------|-------------------------------|
| R004 | 2 |
| R006 | 2 |
| R007 | 3 |
| 其他 | 2 |

### 说明

- 同一规则同时存在的活跃例外上限
- 防止同一规则被多个例外绕过

---

## 三、Create 拒绝规则

### 拒绝条件

1. **Owner 活跃例外超限**
   - owner 当前 active exception 数 >= max_active_exceptions
   - 拒绝 create，返回错误

2. **Owner 高债务例外超限**
   - owner 当前 high debt active exception 数 >= max_high_debt_exceptions
   - 新例外 debt_level = high 时拒绝

3. **Rule 活跃例外超限**
   - 同一 rule 当前 active exception 数 >= max_active_exceptions_per_rule
   - 拒绝 create

### 示例

```bash
$ python scripts/exception_manager.py create --rule-id R004 --owner test --reason "test"
{
  "status": "error",
  "message": "Owner 'test' 配额已满: 2/2"
}
```

---

## 四、Renew 拒绝规则

### 拒绝条件

1. **续期次数超限**
   - renewal_count >= max_renewals
   - 拒绝 renew

2. **Owner 配额超限**
   - 续期后会导致 owner quota 超限
   - 拒绝 renew

3. **Rule 配额超限**
   - 续期后会导致 rule quota 超限
   - 拒绝 renew

### 示例

```bash
$ python scripts/exception_manager.py renew --exception-id EX001 --approved-by admin
{
  "status": "error",
  "message": "已达到最大续期次数 (2)"
}
```

---

## 五、Release 阻断规则

### 阻断条件

Release 在以下情况会被阻断：

1. **高风险例外**
   - high debt + overused + blocking rule exception

2. **Owner 配额违规**
   - owner quota violation 且对应 exception 为 active

3. **Rule 配额违规**
   - rule quota violation 且对应 rule 为 blocking

### 示例

```
❌ Release blocked by quota violations
  - Owner 'test' quota exceeded: 3/2
  - Rule 'R004' quota exceeded: 3/2
```

---

## 六、配额快照

### 文件位置

`reports/ops/rule_exception_quota.json`

### 内容

| 字段 | 说明 |
|------|------|
| `owners` | 所有 owner 配额定义 |
| `rules` | 所有 rule 配额定义 |
| `owner_usage` | 每个 owner 当前用量 |
| `rule_usage` | 每个 rule 当前用量 |
| `violations` | 超限列表 |
| `generated_at` | 生成时间 |

---

## 七、Summary 显示

### Exception Quota 区块

```
Exception Quota
- Owner Quota Violations: <count>
- Rule Quota Violations: <count>
```

---

**维护者**: OpenClaw 架构团队
**更新日期**: 2026-04-15
