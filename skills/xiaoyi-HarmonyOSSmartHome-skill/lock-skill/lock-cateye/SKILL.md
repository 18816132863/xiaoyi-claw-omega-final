---
name: lock-cateye
description: "智能门锁猫眼设置技能。用于设置智慧猫眼相关功能，包括猫眼开关、逗留抓拍、实时视频、畸变矫正等。不支持查询操作。"
---

# 门锁猫眼设置功能Skill

## 1. 必读项

本技能用于**控制**门锁的猫眼相关设置，包括猫眼开关、逗留抓拍、实时视频、畸变矫正等。**不支持查询操作**。

### 服务ID（sid）
- **sid**: `catEyeSetting`

## 2. 触发关键字

当用户提到以下关键词时，应加载本技能：
- 猫眼
- 抓拍
- 逗留
- 实时视频
- 畸变矫正
- 按门铃亮屏
- 内屏
- 逗留录像

## 3. 用户语料示例

- "打开猫眼开关"
- "关闭猫眼"
- "打开逗留抓拍"
- "关闭逗留抓拍"
- "打开实时视频"
- "关闭实时视频"
- "打开畸变矫正"
- "关闭畸变矫正"
- "按门铃亮内屏"
- "设置逗留录像时长"

## 4. 相关参数说明

### 4.1 猫眼设置参数表

| 功能 | 参数 | 参数说明 | 功能作用 |
|---|---|---|---|
| 智慧猫眼开关 | `peepholeEnableSwitch`| 0=关闭，1=打开| 当发生安全事件或有人按门铃，门锁会进行录像或拍照 |
| 逗留抓拍开关   | `staySnapshotSwitch` | 0=关闭，1=打开| 当检测到门外有人逗留会录像 |
| 实时视频 | `liveVideoSwitch`,`liveVideoDuration`,`callValidPeriod` | liveVideoSwitch：功能开关，2=关闭，1=打开<br/> liveVideoDuration：实时视频开启时间，0-全天，1-自定义时间。不支持自定义修改。<br/>callValidPeriod：呼叫有效期：0-1分钟，1-2分钟，2-3分钟，3-4分钟，4-5分钟。不支持自定义修改。 | 开启后，门锁首页可随时查看实时画面，但会相应减少门锁续航 |
| 畸变矫正  | `distortionCorrectionSwitch` | 0=关闭，1=打开 | 开启后画面更接近真实场景 |
| 按门铃亮内屏开关 | `autoPowerScreen` | 0=关闭，1=打开 | 开启后，按门铃门锁内屏自动显示门外情况 |
| 逗留多久开始录像   | `stayDuration` | 取值范围0、3、6、12、17、27、57，（0=立即录像，1=3s，3=6s...57=60s） | 当检测到门外有人逗留时，过多长时间开始录像 |
| 录像最大时长   | `shootingDuration` | 取值范围0-2，对应6-30秒（0=6s，1=15s，2=30s） | 逗留录像的最大时长 |
| 开门中断逗留抓拍   | `openDoorStopShooting` | 0-关闭，1-打开 | 开启后，在抓拍逗留视频期间开门，抓拍的视频将不保存;关闭后，可以提升逗留抓拍的有效性和灵敏度 |
| 抓拍灵敏度   | `shootingDuration` | 取值范围0、2，（0：灵敏度低，识别距离1m；2：灵敏度高，识别距离2m） | 逗留抓拍的灵敏度 |
| 抓拍录像分辨率   | `resolution` | 0=1080p，1=2k | 逗留抓拍录像的分辨率 |

### 4.2 参数取值范围

| 参数 | 取值范围 | 说明 |
|------|---------|------|
| `stayDuration` | 0-27 | 逗留时长，对应3-30秒（0=3s，1=4s，2=5s...27=30s） |

## 5. 调用示例

### 5.1 猫眼开关设置

#### 打开猫眼开关
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "catEyeSetting" \
  --data '{"peepholeEnableSwitch": 1}' \
  --verbose
```

#### 关闭猫眼开关
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "catEyeSetting" \
  --data '{"peepholeEnableSwitch": 0}' \
  --verbose
```

### 5.2 逗留抓拍设置

#### 打开逗留抓拍
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "catEyeSetting" \
  --data '{"staySnapshotSwitch": 1}' \
  --verbose
```

#### 关闭逗留抓拍
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "catEyeSetting" \
  --data '{"staySnapshotSwitch": 0}' \
  --verbose
```

### 5.3 实时视频设置

#### 打开实时视频
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "catEyeSetting" \
  --data '{"liveVideoSwitch": 1, "liveVideoDuration":0, "callValidPeriod":	0}' \
  --verbose
```

#### 关闭实时视频
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "catEyeSetting" \
  --data '{"liveVideoSwitch": 2}' \
  --verbose
```

### 5.4 畸变矫正设置

#### 打开畸变矫正
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "catEyeSetting" \
  --data '{"distortionCorrectionSwitch": 1}' \
  --verbose
```

#### 关闭畸变矫正
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "catEyeSetting" \
  --data '{"distortionCorrectionSwitch": 0}' \
  --verbose
```

### 5.5 按门铃亮内屏设置

#### 打开按门铃亮内屏开关
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "catEyeSetting" \
  --data '{"autoPowerScreen": 1}' \
  --verbose
```

#### 关闭按门铃亮内屏开关
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "catEyeSetting" \
  --data '{"autoPowerScreen": 0}' \
  --verbose
```

### 5.6 逗留时长设置

#### 设置逗留时长为6s
```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "catEyeSetting" \
  --data '{"stayDuration": 6}' \
  --verbose
```

## 6. 注意事项

- 本技能仅支持控制，不支持查询操作
- **不支持查询逗留视频、查询按门铃抓拍等操作**
