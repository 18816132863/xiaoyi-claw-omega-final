---
name: lock-palm
description: "智能门锁掌静脉识别设置技能。用于设置掌静脉识别相关功能，包括掌静脉开关、识别模式、语音提醒、关门静默时长等。不支持查询操作。"
---

# 门锁掌静脉识别设置功能Skill

## 1. 必读项

本技能用于**控制**门锁的掌静脉识别相关设置，包括掌静脉开关、识别模式、语音提醒、关门静默时长等。**不支持查询操作**。

### 服务ID（sid）
- **sid**: `securitySetting`

### 重要说明
- 关门静默时长功能：关门后，掌静脉识别功能在设置时间内停用，可以避免误开锁

## 2. 触发关键字

当用户提到以下关键词时，应加载本技能：
- 掌静脉
- 掌静脉识别
- 掌心识别

## 3. 用户语料示例

- "打开掌静脉识别开锁"
- "关闭掌静脉识别"
- "设置掌静脉识别模式为手动"
- "设置掌静脉识别模式为自动"
- "打开掌静脉语音提醒"
- "关闭掌静脉语音提醒"
- "设置关门静默时长为10秒"
- "设置关门静默"

## 4. 相关参数说明

### 4.1 掌静脉识别设置参数表

| 功能 | 参数 | 参数说明 | 功能作用 |
|---|---|---|---|
| 掌静脉识别开关 | `palmIdentifySwitch` | 0=关闭，1=打开 | 开启后，可使用录入的管理员或成员掌静脉识别开锁 |
| 掌静脉识别模式 | `palmDetectMode` | 0=手动模式，1=手动+自动模式 | 手动：触摸数字键盘，唤醒门锁进行掌静脉识别（可以提高门锁续航时间）；自动：举起手掌，掌心正对门锁摄像头约15厘米处，可自动进行掌静脉识别（同时支持手动触发） |
| 掌静脉语音提示 | `palmVoiceSwitch` | 0=关闭，1=打开 | 开启后，在掌静脉识别开锁时会有语音引导提示 |
| 关门静默时长 | `palmSleepTime` | 取值范围：0, 5, 10, 20, 30, 120（秒） | 关门后，掌静脉识别功能在设置时间内停用 |

### 4.2 参数取值范围

| 参数 | 取值范围 | 说明 |
|------|---------|------|
| `palmIdentifySwitch` | 0, 1 | 0=关闭，1=打开 |
| `palmDetectMode` | 0, 1 | 0=手动模式，1=手动+自动模式 |
| `palmVoiceSwitch` | 0, 1 | 0=关闭，1=打开 |
| `palmSleepTime` | 0, 5, 10, 20, 30, 120 | 关门静默时长（秒） |

## 5. 调用示例

### 5.1 掌静脉识别开关设置

#### 打开掌静脉识别
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "securitySetting" \
  --data '{"palmIdentifySwitch": 1}' \
  --verbose
```

#### 关闭掌静脉识别
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "securitySetting" \
  --data '{"palmIdentifySwitch": 0}' \
  --verbose
```

### 5.2 掌静脉识别模式设置

#### 设置掌静脉识别模式为手动模式
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "securitySetting" \
  --data '{"palmDetectMode": 0}' \
  --verbose
```

#### 设置掌静脉识别模式为手动+自动模式
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "securitySetting" \
  --data '{"palmDetectMode": 1}' \
  --verbose
```

### 5.3 掌静脉语音提醒设置

#### 打开掌静脉语音提示
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "securitySetting" \
  --data '{"palmVoiceSwitch": 1}' \
  --verbose
```

#### 关闭掌静脉语音提示
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "securitySetting" \
  --data '{"palmVoiceSwitch": 0}' \
  --verbose
```

### 5.4 关门静默时长设置

#### 设置关门静默时长为10s
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "securitySetting" \
  --data '{"palmSleepTime": 10}' \
  --verbose
```

## 6. 注意事项

- 本技能仅支持控制，不支持查询操作
- **不支持添加/删除掌静脉等成员管理操作**
