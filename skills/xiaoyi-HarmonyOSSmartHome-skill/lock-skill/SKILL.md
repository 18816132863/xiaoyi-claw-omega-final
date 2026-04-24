---
name: lock-claw
description: "智能门锁设备专用技能。当用户涉及智能门锁（deviceTypeId='A0B'）相关操作时，必须优先使用本技能。本技能作为门锁技能的总入口，负责将用户指令路由到对应的功能skill中。不支持的功能会明确告知用户。"
metadata:
  {
    "pha": {
      "emoji": "🔒",
      "category": "smarthome-skill"
    }
  }
---

# 智能门锁设备专用技能（根Skill）

> **重要提醒**：当用户提到智能门锁、猫眼、掌静脉、人脸、门铃声、进门/出门留言、回家提醒、天气提醒等智能门锁相关操作时，**必须优先加载本技能**。

> **路由原则**：本技能作为总入口，负责根据用户请求路由到具体的功能skill。**不要一次性加载所有功能skill**。

---

## 1. 技能说明

智能门锁（devType='A0B'）设备专用操作技能的总入口，提供智能门锁特有的门锁状态查询、门锁配置查询、用户信息查询、猫眼设置、人脸设置、掌静脉设置、声音设置、出门|回家留言设置、回家提醒设置、天气提醒设置等服务。

## 2. 设备识别

### 2.1 基础设备识别

- **设备类型**：智能门锁
- **devType**：`'A0B'`
- 通过 `devType` 可以从设备列表中快速筛选出智能门锁设备
- 通过 `PID` 获得设备产品ID

### 2.2 产品能力识别（重要）

> **【强制】不同型号的门锁支持的功能能力不同，在进行功能操作前必须先根据产品ID(PID)校验设备是否支持该功能**

门锁设备能力定义文件：`bin/lock_device_info.js`
#### 常见门锁型号能力对照表

门锁设备能力定义详见配置文件：`bin/lock_device_capabilities.json`

#### 设备能力校验命令

```bash
# 列出所有已定义的门锁型号
node lock-skill/bin/lock_device_info.cjs list

# 根据PID查询设备能力
node lock-skill/bin/lock_device_info.cjs get_capability --pid KW5L

# 检查是否支持特定功能
node lock-skill/bin/lock_device_info.cjs check_feature --pid KW5L --feature securitySetting:face

# 获取门锁支持的功能列表（推荐）
node lock-skill/bin/lock_device_info.cjs get_supported --pid KW5L

# 检查功能是否支持并返回友好信息
node lock-skill/bin/lock_device_info.cjs check_with_message --pid KW5L --feature securitySetting:face

# 查看配置信息
node lock-skill/bin/lock_device_info.cjs config_info

# 重新加载配置文件
node lock-skill/bin/lock_device_info.cjs reload
```
**API 说明**：

| 方法 | 用途 | 返回值 |
|------|------|--------|
| `getSupportedFeatures(pid)` | 获取门锁支持的所有功能列表 | `{ supported: [], unsupported: [], capabilities: {}, deviceName: "", model: "" }` |
| `checkFeatureWithMessage(pid, feature)` | 检查单个功能是否支持，返回友好提示 | `{ supported: boolean, message: "", featureCN: "" }` |
| `isFeatureSupported(pid, feature)` | 检查单个功能是否支持 | `true/false` |

**使用示例**：

```javascript
// 示例1：查询门锁支持的功能列表（在查询门锁信息前调用）
const pid = 'KW5L'; // 从 get_devices_info 获取的 prodId
const featureInfo = getSupportedFeatures(pid);
// 返回: { supported: ['指纹', 'NFC', '密码', '门卡', '猫眼/视频', '留言功能', '天气提醒', '回家提醒'], unsupported: ['人脸识别', '掌静脉识别'], ... }

// 示例2：检查门锁是否支持某功能
const result = checkFeatureWithMessage('KW5L', 'face');
// 返回: { supported: true, message: '华为智能门锁 Pro支持人脸识别功能', featureCN: '人脸识别' }

// 示例3：在展示门锁信息时，只输出支持的能力
const info = getSupportedFeatures(pid);
const response = `您的${info.deviceName}（${info.model}）支持以下功能：${info.supported.join('、')}`;
```

**能力校验失败的处理**：

| 场景                        | 处理方式                      |
|---------------------------|---------------------------|
| 用户请求的功能不支持                | 明确告知用户"您的门锁型号不支持XX功能"     |
| 未找到设备能力定义                 | 默认开启所有功能 |
| 多个功能中部分不支持，单用户未明确提到不支持的功能 | 仅列出支持的功能，忽略不支持的功能         |
| 多个功能中部分不支持，且用户有明确提到不支持的功能 | 列出支持的功能，并说明哪些功能不支持        |

## 3. 功能Skill路由表（精确路由）

根据用户请求的关键词，直接路由到对应的功能skill文件：

| 用户关键词                                             | 路由到 | 功能说明 |
|---------------------------------------------------|--------|----------|
| 门锁状态、门锁电量、在线状态、wifi状态、设备信息、电池                     | `lock-info/SKILL.md` | 门锁基本信息查询 |
| 开门记录、关门记录、逗留抓拍记录、门铃响铃、开锁记录、操作记录、历史记录、谁开门了、回家记录、回家 | `lock-history/SKILL.md` | 门锁历史记录查询 |
| 猫眼、抓拍、逗留、实时视频、畸变矫正、按门铃亮屏、逗留录像                     | `lock-cateye/SKILL.md` | 猫眼设置 |
| 人脸、人脸识别、面部识别、刷脸                                   | `lock-face/SKILL.md` | 人脸识别设置 |
| 掌静脉、掌静脉识别                                         | `lock-palm/SKILL.md` | 掌静脉识别设置 |
| 门锁声音、门铃音量、提示音、告警音、留言音量、声音大小、开关门提示音、门未关告警          | `lock-volume/SKILL.md` | 门锁声音设置 |
| 出门留言、回家留言、留言设置                                    | `lock-greeting/SKILL.md` | 出门/回家留言设置 |
| 天气提醒、出门天气提醒                                       | `lock-weather/SKILL.md` | 天气提醒设置 |
| 电源管理、AI省电、省电模式                                    | `lock-power/SKILL.md` | 电源管理设置 |
| 回家提醒、家人回家提醒                                       | `lock-familycare/SKILL.md` | 回家提醒设置 |

## 4. 不支持的功能清单

以下功能**当前不支持**，若用户请求这些功能，需明确告知用户：

| 操作 | 不支持原因 |
|------|-----------|
| 查询逗留视频 | 不支持 |
| 查询按门铃抓拍 | 不支持 |
| 添加访客密码 | 不支持 |
| 启动实时视频 | 不支持 |
| 修改安全配置：离家布防、双重验证、操作设备验证管理员密码等 | 不支持 |
| 紧急联系人：添加、删除等 | 不支持 |
| 远程开锁 | 不支持 |
| 添加/删除用户（成员管理） | 不支持 |
| 添加/删除密码、指纹、门卡 | 不支持 |
| 添加/删除人脸、掌静脉 | 不支持 |

## 5. 依赖的通用技能

以下通用操作由 [`common-skill`](../common-skill/SKILL.md) 提供：

| 操作 | 依赖技能 | 说明 |
|------|---------|------|
| 获取设备列表 | `get_devices_info` | 查询账号下所有设备，通过 devType='A0B' 筛选智能门锁 |
| 获取设备详情 | `get_device_detail` | 获取智能门锁的详细状态和属性信息 |
| 执行控制命令 | `control_device` | 使用功能skill提供的 sid 和参数执行控制 |
| 获取历史记录 | `get_device_histories` | 查询门锁历史记录事件 |

## 6. 使用流程

1. 使用 `get_devices_info` 获取设备列表，通过 `deviceTypeId='A0B'` 找到智能门锁
2. 根据用户请求关键词，通过路由表找到对应的功能skill
3. 加载对应功能skill获取完整的命令格式和参数说明
4. 执行对应功能skill中的操作

## 7. 注意事项

### 7.1 【强制】回复规范

> **回复用户时，只展示用户可理解的中文结果，禁止暴露任何技术细节**

- **回复内容**：最终结果以简洁清晰的 checklist 形式统一展示
- **禁止展示**：
  - 命令执行过程、CLI调用、API请求等技术细节
  - 参数名、参数值等内部参数
  - 子技能名称、技能目录结构等技术实现细节
- **多设备场景**：当用户有多个家庭或多把门锁时，必须明确询问用户具体选择，**禁止随机或默认选择**
- **意图不明**：若无法明确理解用户意图，必须详细追问，**禁止编造参数或假设条件执行**

### 7.2 【强制】敏感信息保护

> **以下信息为个人敏感数据，严禁输出给用户**

- homeId、设备 id 及各类 id
- 用户的 uid 和 api-key
- 云侧原始信息（接口名、参数名、参数值等）

### 7.3 【强制】控制类操作

1. **执行前**：重新查看功能skill中关于设置项的相关说明，确保不遗漏关键参数
2. **删除操作**：执行任何删除类操作前，必须提醒用户确认授权，**禁止未经用户同意私自执行**
3. **执行后**：必须再次查询云侧结果验证修改是否成功，避免误认为已修改成功

## 8. Profile 定义参考

如需了解智能门锁的完整服务能力定义，可参考：
```
https://smartlife-sandbox-drcn.things.dbankcloud.cn/device/guide/<产品ID>/<产品ID>.json
```

示例：
```
https://smartlife-sandbox-drcn.things.dbankcloud.cn/device/guide/KW5L/KW5L.json
```
