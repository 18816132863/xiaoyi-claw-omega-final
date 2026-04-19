---
name: lock-face
description: "智能门锁人脸识别设置技能。用于设置人脸识别相关功能，包括人脸开关、识别模式、语音提醒、回头防误开时长等。不支持查询操作。"
---

# 门锁人脸识别设置功能Skill

## 1. 必读项

本技能用于**控制**门锁的人脸识别相关设置，包括人脸开关、识别模式、语音提醒、回头防误开时长等。**不支持查询操作**。

### 服务ID（sid）
- **sid**: `securitySetting`

### 重要说明
- 当人脸识别开锁开关（faceIdentifySwitch）关闭时，其他人脸识别设置不可修改
- 回头防误开功能：关门后，人脸识别功能在设置时间内停用，可以避免出门后等电梯时回头误开锁；但在对应时间内无法自动唤醒人脸开锁，需要触摸键盘手动唤醒

## 2. 触发关键字

当用户提到以下关键词时，应加载本技能：
- 人脸
- 人脸识别
- 面部识别
- 刷脸
- 回头防误开

## 3. 用户语料示例

- "打开人脸识别开锁"
- "关闭人脸识别"
- "设置人脸识别模式为手动"
- "设置人脸识别模式为自动"
- "打开人脸语音提醒"
- "关闭人脸语音提醒"
- "设置回头防误开时长为30秒"
- "设置回头防误开"

## 4. 相关参数说明

### 4.1 人脸识别设置参数表

| 功能 | 参数 | 参数说明 | 功能作用 |
|---|---|---|---|
| 人脸识别开锁开关 | `faceIdentifySwitch` | 0=关闭，1=打开 | 开启后，可使用录入的管理员或成员面部识别开锁；当该开关关闭时，其他人脸识别设置不可修改 |
| 人脸识别模式   | `faceDetectMode` | 0=手动模式，1=自动模式（自动模式下同时支持手动模式触发） | 手动模式：触摸数字键盘，唤醒门锁进行人脸识别，可以提高门锁续航时间；自动模式：走进门锁0.5-1米处，可自动进行人脸识别，同时支持手动触发 |
| 人脸语音提醒   | `faceVoiceSwitch` | 0=关闭，1=打开 | 开启后，在人脸识别开锁时会有语音引导提示 |
| 回头防误开时长  | `faceSleepTime` | 取值范围：0, 5, 10, 20, 30, 120（秒） | 优点：关门后，人脸识别功能在设置时间内停用，可以避免出门后等电梯时，回头误开锁；缺点：关门后，在对应时间内无法自动唤醒人脸开锁，需要触摸键盘手动唤醒人脸识别 |

### 4.2 参数取值范围

| 参数 | 取值范围 | 说明 |
|------|---------|------|
| `faceIdentifySwitch` | 0, 1 | 0=关闭，1=打开 |
| `faceDetectMode` | 0, 1 | 0=手动模式，1=自动模式 |
| `faceVoiceSwitch` | 0, 1 | 0=关闭，1=打开 |
| `faceSleepTime` | 0, 5, 10, 20, 30, 120 | 回头防误开时长（秒） |

## 5. 调用示例

### 5.1 人脸识别开锁设置

#### 打开人脸识别开锁
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "securitySetting" \
  --data '{"faceIdentifySwitch": 1}' \
  --verbose
```

#### 关闭人脸识别开锁
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "securitySetting" \
  --data '{"faceIdentifySwitch": 0}' \
  --verbose
```

### 5.2 人脸识别模式设置

#### 设置人脸识别模式为手动模式
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "securitySetting" \
  --data '{"faceDetectMode": 0}' \
  --verbose
```

#### 设置人脸识别模式为自动模式
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "securitySetting" \
  --data '{"faceDetectMode": 1}' \
  --verbose
```

### 5.3 人脸语音提醒设置

#### 打开人脸语音提醒
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "securitySetting" \
  --data '{"faceVoiceSwitch": 1}' \
  --verbose
```

#### 关闭人脸语音提醒
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "securitySetting" \
  --data '{"faceVoiceSwitch": 0}' \
  --verbose
```

### 5.4 回头防误开时长设置

#### 设置回头防误开时长为30s
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "securitySetting" \
  --data '{"faceSleepTime": 30}' \
  --verbose
```

## 6. 注意事项

- 本技能仅支持控制，不支持查询操作
- 当人脸识别开锁开关关闭时，其他人脸识别设置不可修改
- **不支持添加/删除人脸等成员管理操作**
