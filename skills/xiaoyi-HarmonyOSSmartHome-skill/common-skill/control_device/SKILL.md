# 全屋设备控制技能

## ⚠️ 重要说明：GET vs POST 操作

> **GET 操作：主动查询设备实时状态**
> - **数据来源**：主动向设备发起查询请求
> - **时效性**：实时/近实时的设备状态
> - **设备要求**：设备必须在线
> - **适用场景**：需要获取设备的精确实时状态
>
> **POST 操作：向设备发送控制命令**
> - **功能**：控制设备开关、调节参数等
> - **响应**：实时返回控制结果
> - **适用场景**：远程控制设备、调节参数、执行场景

## 核心能力
1. 向指定设备发送控制命令（POST）
2. 主动查询设备实时状态（GET）
3. 支持多种操作类型（开关、调节、场景等）
4. 实时返回控制结果和查询结果
5. 支持调试模式查看详细请求和响应

## 适用设备范围
- 灯光、开关、插座等通用设备
- 传感器、窗帘等智能家居设备
- **不包含智慧屏（devType='09C'）设备**

## 调用方式
### 1. 获取设备信息（获取devId和prodId）
```bash
node smarthome-claw.js get_devices_info
```

### 2. 控制设备
```bash
# 基本格式
node common-skill/bin/smarthome-claw.js control_device --dev-id <设备ID> --prod-id <产品ID> --operation <操作类型> --sid <服务ID> --data <{cid: value}>

# 示例：开关灯
node common-skill/bin/smarthome-claw.js control_device --dev-id "xxx" --prod-id "xxx" --operation "POST" --sid "switch" --data '{\"on\":1}'

# 示例：查询状态
node common-skill/bin/smarthome-claw.js control_device --dev-id "xxx" --prod-id "xxx" --operation "GET" --sid "switch" --data '{}'

# 调试模式
node common-skill/bin/smarthome-claw.js control_device --dev-id "xxx" --prod-id "xxx" --operation "POST" --sid "switch" --data '{\"on\":1}' --verbose
```

## 参数说明
- `--dev-id`: 设备ID（必填），从 get_devices_info 获取
- `--prod-id`: 产品ID（必填），从 get_devices_info 获取
- `--operation`: 操作类型（必填），如 "GET"、"POST" 等
- `--sid`: 服务ID（必填），如 "switch"、"brightness" 等
- `--data`: 控制数据JSON字符串（必填），如 `{\"cid\":value}` "GET" 类型传'{}'即可

在profile定义中定义了设备对外开放的服务能力，介绍，参数和参数类型，可选范围的介绍，可以参考查询到的设备状态和profile定义来组装控制报文，
https://smartlife-sandbox-drcn.things.dbankcloud.cn/device/guide/<产品ID>/<产品ID>.json

#示例
https://smartlife-sandbox-drcn.things.dbankcloud.cn/device/guide/V0FW/V0FW.json

## 适用场景
### POST 操作（控制）
1. 远程控制设备开关
2. 调节设备参数（亮度、温度等）

### GET 操作（查询）
1. 获取设备的实时精确状态
2. 确认设备是否在线并响应
3. 查询设备当前属性值（实时）

## 与 get_device_detail 的区别

| 对比项 | get_device_detail | control_device (GET) |
|--------|-------------------|---------------------|
| **数据来源** | 云端缓存 | 主动查询设备 |
| **时效性** | 可能有延迟 | 实时/近实时 |
| **响应速度** | 快 | 较慢（需要设备响应） |
| **设备在线要求** | 不需要 | 需要 |
| **适用场景** | 快速查看信息 | 获取精确实时状态 |

> **选择建议**：
> - 快速查看设备信息、了解设备能力 → 使用 `get_device_detail`
> - 需要精确的实时状态、确认设备在线 → 使用 `control_device` 的 GET 操作