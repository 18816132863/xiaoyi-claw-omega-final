---
name: lock-power
description: "智能门锁电源管理设置技能。用于设置AI省电功能，当门锁耗电较快时，自动调节人脸、掌静脉、猫眼灵敏度，兼顾续航与体验。不支持查询操作。"
---

# 门锁电源管理设置功能Skill

## 1. 必读项

本技能用于**控制**门锁的电源管理设置，主要包括AI省电功能。**不支持查询操作**。

### 服务ID（sid）
- **sid**: `lockCommonSetting`

### 重要说明
- 当门锁耗电较快时，可以使用AI省电功能
- AI省电会自动调节人脸、掌静脉、猫眼灵敏度，兼顾续航与体验

## 2. 触发关键字

当用户提到以下关键词时，应加载本技能：
- 电源管理
- AI省电
- 省电模式
- 省电

## 3. 用户语料示例

- "打开AI省电"
- "关闭AI省电"
- "开启省电模式"
- "关闭省电模式"
- "设置电源管理"

## 4. 相关参数说明

### 4.1 电源管理设置参数表

| 功能 | sid | 参数 | 参数说明 | 功能作用 |
|---|---|---|---|---|
| AI省电 |`lockCommonSetting`|`devCfg`, `ts`, `aiEco`|`devCfg`:设备相关功能;<br/>`ts`:时间戳格式：20191226T075719Z,APP根据这个值判断设置是否已生效以及是否是新配置;<br/>`aiEco`:AI省电开关,0关闭,1打开|当门锁耗电较快时，自动调节人脸、掌静脉、猫眼灵敏度，兼顾续航与体验|

### 4.2 参数取值范围

| 参数 | 取值范围 | 说明 |
|------|---------|------|
| `aiEco` | 0, 1 | AI省电开关，0=关闭，1=打开 |
| `ts` | 时间戳 | 时间戳格式：20191226T075719Z |

## 5. 调用示例

### 5.1 打开AI省电

```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "lockCommonSetting" \
  --data '{"devCfg":"","ts":"20260408T151137Z621","aiEco":1}' \
  --verbose
```

### 5.2 关闭AI省电

```bash
node common-skill/bin/smarthome-claw.js control_device \
  --dev-id "xxx" \
  --prod-id "xxx" \
  --operation "POST" \
  --sid "lockCommonSetting" \
  --data '{"devCfg":"","ts":"20260408T151137Z621","aiEco":0}' \
  --verbose
```

## 6. 注意事项

- 本技能仅支持控制，不支持查询操作
- AI省电功能开启后会自动调节人脸、掌静脉、猫眼灵敏度，可能影响使用体验
