---
name: lock-volume
description: "智能门锁声音设置技能。用于设置门锁声音相关功能，包括门铃音量、提示音音量、告警音音量、留言音量、开关门提示音、门未关告警等。不支持查询操作。"
---

# 门锁声音设置功能Skill

## 1. 必读项

本技能用于**控制**门锁的声音相关设置，包括门铃音量、提示音音量、告警音音量、留言音量、开关门提示音、门未关告警等。**不支持查询操作**。

### 服务ID（sid）
- **sid**: `volumeSetting`（音量相关）
- **sid**: `alarmEventSetting`（告警相关）

## 2. 触发关键字

当用户提到以下关键词时，应加载本技能：
- 门锁声音
- 门铃音量
- 提示音
- 告警音
- 留言音量
- 声音大小
- 开关门提示音
- 门未关告警

## 3. 用户语料示例

- "设置门铃音量为80"
- "调大门铃音量"
- "设置提示音音量为60"
- "调小告警音音量"
- "打开开关门提示音"
- "关闭开关门提示音"
- "打开门未关告警"
- "关闭门未关告警"
- "设置出门告警时长"
- "设置留言音量为70"

## 4. 相关参数说明

### 4.1 声音设置参数表

| 功能 | sid | 参数 | 参数说明                               | 功能作用 |
|---|---|---|------------------------------------|---|
| 开关门提示音 | `volumeSetting` | `doorPromptSwitch` | 0=关闭，1=打开                          | 功能开启后，在开门时，会有"已开锁"语音提示，在关门时，会有"已上锁"语音提示 |
| 门未关告警 | `alarmEventSetting` | `doorOpenSwitch` | 0=关闭，1=打开                          | 功能开启后，当出门或进门时，门在规定时间内未成功上锁，会播报语音提示，且向手机推送门未关告警消息 |
| 出门告警时长 | `alarmEventSetting` | `outAlarmTime` | 取值范围：10，15，20，30，45，60（秒）          | 当出门时，门在多长时间内未成功上锁，会播报语音提示 |
| 进门告警时长 | `alarmEventSetting` | `inAlarmTime` | 取值范围：10，15，20，30，45，60（秒）          | 当进门时，门在多长时间内未成功上锁，会播报语音提示 |
| 手机提醒消息推送时间 | `alarmEventSetting` | `doorOpenAlarmPushTime` | 0：立即，1：1分钟后，5:5分钟后，10:10分钟后，-1：不推送 | 门未关告警产生后，经过多长时间会向手机推送门未关告警消息 |
| 门铃音量 | `volumeSetting` | `voiceVolume` | 取值范围0，30,60,100                    | 按门铃时音量 |
| 提示音音量 | `volumeSetting` | `ringVolume` | 取值范围0，30,60,100                          | 提示音音量 |
| 告警音音量 | `volumeSetting` | `warningVolume` | 取值范围0，30,60,100                          | 告警音音量 |
| 留言/天气提醒音量 | `volumeSetting` | `homeGreetVol` | 取值范围0，30,60,100                          | 出门留言、回家留言、天气提醒音量 |

### 4.2 参数取值范围

| 参数 | 取值范围 | 说明 |
|------|---------|------|
| `ringVolume` | 0，30,60,100 | 门铃音量 |
| `voiceVolume` | 0，30,60,100 | 提示音音量 |
| `warningVolume` | 0，30,60,100 | 告警音音量 |
| `homeGreetVol` | 0，30,60,100 | 留言/天气提醒音量 |
| `doorPromptSwitch` | 0, 1 | 开关门提示音开关 |
| `doorOpenSwitch` | 0, 1 | 门未关告警开关 |
| `outAlarmTime` | 10, 15, 20, 30, 45, 60 | 出门告警时长（秒） |
| `inAlarmTime` | 10, 15, 20, 30, 45, 60 | 进门告警时长（秒） |

## 5. 调用示例

### 5.1 开关门提示音设置

#### 打开开关门提示音
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "volumeSetting" \
  --data '{"doorPromptSwitch": 1}' \
  --verbose
```

#### 关闭开关门提示音
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "volumeSetting" \
  --data '{"doorPromptSwitch": 0}' \
  --verbose
```

### 5.2 门未关告警设置

#### 打开门未关告警
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "alarmEventSetting" \
  --data '{"doorOpenSwitch": 1}' \
  --verbose
```

#### 关闭门未关告警
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "alarmEventSetting" \
  --data '{"doorOpenSwitch": 0}' \
  --verbose
```

### 5.3 音量设置

#### 设置门铃音量为低
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "volumeSetting" \
  --data '{"ringVolume": 30}' \
  --verbose
```

#### 设置提示音音量为中
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "volumeSetting" \
  --data '{"voiceVolume": 60}' \
  --verbose
```

#### 设置告警音音量为静音
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "volumeSetting" \
  --data '{"warningVolume": 0}' \
  --verbose
```

#### 设置留言、天气提醒音量为最大
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "volumeSetting" \
  --data '{"homeGreetVol": 100}' \
  --verbose
```

## 6. 注意事项

- 本技能仅支持控制，不支持查询操作
- 当用户说"音量调大"或"音量调小"时，需要根据当前音量值计算新的音量值，声音只有固定值，0、30（低）、60（中）、100（高），每次只调整一级
