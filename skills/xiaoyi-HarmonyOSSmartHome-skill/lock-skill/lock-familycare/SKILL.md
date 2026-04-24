---
name: lock-familycare
description: "智能门锁回家提醒设置技能。用于设置回家提醒功能，检测到家庭成员开门回家时推送消息通知。不支持查询操作。"
---

# 门锁回家提醒设置功能Skill

## 1. 必读项

本技能用于**控制**门锁的回家提醒设置，检测到家庭成员开门回家时推送消息通知。**不支持查询操作**。

### 服务ID（sid）
- **sid**: `familyCare`

### 重要说明
- 回家提醒和回家留言是不同的功能，执行时注意根据用户要求区分
- 可以为不同的家庭成员设置独立的开关、提醒时段、每周循环
- 需要查询用户信息获取用户id（uid）

## 2. 触发关键字

当用户提到以下关键词时，应加载本技能：
- 回家提醒
- 家人回家提醒
- 成员回家提醒

## 3. 用户语料示例

- "打开回家提醒"
- "关闭回家提醒"
- "打开xx的回家提醒"
- "关闭xx的回家提醒"
- "设置回家提醒"
- "设置成员回家提醒"

## 4. 相关参数说明

### 4.1 回家提醒设置参数表

| 功能 | sid | 参数 | 参数说明 | 功能作用 |
|---|---|---|---|---|
| 回家提醒 | `familyCare` | `bSwitch`, `uid`, `uSwitch` | bSwitch：功能总开关，0=关闭，1=打开<br/>uid：提醒所属用户id，通过查询用户信息获取<br/>uSwitch：单用户功能开关 | 1、检测到家庭成员开门回家，推送消息通知<br/>2、可以为不同的家庭成员设置独立的开关、提醒时段、每周循环（独立设置周一到周日） |

### 4.2 参数取值范围

| 参数 | 取值范围 | 说明 |
|------|---------|------|
| `bSwitch` | 0, 1 | 功能总开关，0=关闭，1=打开 |
| `uSwitch` | 0, 1 | 单用户功能开关 |
| `uid` | 用户id | 通过查询用户信息获取 |
| `rd` | 日期字符串 | 按周："1,2,3,4,5,6,7"，分别代表周一到周日 |
| `st` | 时间字符串 | 提醒开始时间，格式：HH:mm |
| `et` | 时间字符串 | 提醒结束时间，格式：HH:mm |

## 5. 调用示例

### 5.1 打开回家提醒（默认用户、默认提醒时段）

```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "familyCare" \
  --data '{"bSwitch":1,"uList":[],"ts":"20260408T150936Z905"}' \
  --verbose
```

### 5.2 打开单用户的回家提醒（uid根据查询用户信息获取）

```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "familyCare" \
  --data '{"bSwitch":0,"uList":[{"uSwitch":1,"uid":1,"rd":"1,2,3,4,5,6,7","tList":[{"st":"12:00","et":"14:00"},{"st":"06:00","et":"08:00"}]}],"ts":"20260408T150936Z905"}' \
  --verbose
```

### 5.3 关闭回家提醒

```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "familyCare" \
  --data '{"bSwitch":0,"uList":[""],"ts":"20260408T150936Z905"}' \
  --verbose
```

### 5.4 关闭单用户的回家提醒（uid根据查询用户信息获取）

```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "familyCare" \
  --data '{"bSwitch":1,"uList":["uSwitch":0,"uid":1],"ts":"20260408T150936Z905"}' \
  --verbose
```

## 6. 注意事项

- 本技能仅支持控制，不支持查询操作
- 回家提醒和回家留言是不同的功能
- 需要先查询用户信息获取用户id（uid）
