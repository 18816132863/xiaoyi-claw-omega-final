---
# 固定元数据头（必须，AI 优先读取）
name: router-claw
description: 路由器信息查询与儿童上网控制技能
version: 1.0.2
permissions: 发送get请求和post请求的权限、以及儿童上网保护操作权限,路由器信息查询
---

# router diag Skill（技能名称，可自定义）

## 1. Description（技能详细说明）
当用户反馈儿童上网保护使用问题时，使用此技能查询路由器的实时状态，执行儿童上网保护相关配置操作，以清晰、友好的中文格式返回结果，帮助用户了解路由当前儿童上网保护的配置状态、网络状态，并完成设备管控、上网时段设置、应用管理、断网控制等操作。

## 2. When to use（触发场景：明确 AI 何时调用此技能）
用户说：“儿童上网保护”
用户说：“上网时间太长了，需要休息一下”
用户说：“不要再玩游戏了”
用户说：“不能长时间看电视”
用户说：“让手机断网”
用户说：“控制孩子上网”
用户说：“查询路由器状态”
用户说：“查询家里连接的设备”
用户说：“设置儿童上网时段”

## 3. How to use（调用逻辑：教 AI 如何使用技能）
3.1 回复规则
（1）当答复用户时，首先简短一句话告知用户，例如 “好的，已收到”“请稍等，正在帮您处理”，无需告知底层请求流程；
（2）最终结果以简洁清晰的 checklist 形式统一展示给用户，不要对用户答复详细过程数据和过于专业的内部参数；
（3）【强制】在用户有多个家庭、多个路由场景下，需要明确询问用户具体选择，禁止随机、默认选择；
（4）若设备未加入儿童保护，先询问用户是否添加，确认后执行操作；
（5）若不能明确理解用户意图或指令，请详细追问用户，不要用没有依据的假设条件或编造参数去执行。
（6）【强制】禁止在回复中展示命令执行过程/CLI调用/API请求等技术细节；

3.2 前置必要条件（强制：不能跳过该步骤）
# 【强制】【重要】【注意】获取家庭信息和设备device id，将获取的路由devid和prodid分别配置到ROUTER_DEVID和ROUTER_PRODID环境变量中，用于后续发送请求；
（1）获取用户要控制的家庭信息，若有多个家庭，都列举出家庭名称，追问用户，让用户自己选择具体的家庭信息；
（2）在用户选择家庭后，将该家庭下的所有路由名称列出来，追问用户，让用户选择具体要对接的路由，并获取该路由的device id，用于具体对接配置；
（3）若用户说选择"XX路由"，但实际未找到路由，请根据在家庭中获取的设备prodid在router_device_info.js中进行查找对应路由；

3.3 儿童上网保护具体操作逻辑
# 管理儿童上网保护设备
（1）当用户需要对XX设备（例如：nova 6手机）进行断网、设置上网时长、时段、禁止特定应用或特定种类应用上网操作时，首先查询儿童上网保护设备列表，看对应设备是否在列表中；
（2）若设备不在列表中，请先告知用户当前情况并询问用户是否需要帮忙将对应设备添加到儿童上网保护列表中，若用户同意，就执行”添加儿童上网保护设备“的步骤，执行成功或失败请以实际查询到的配置结果为准；
（3）若设备已在列表中，可以直接执行断网、设置上网时长、时段、禁止特定应用或特定种类应用上网等操作；
（4）执行命令请严格按照“3.3 命令行调用方式”中规定的命令和参数来使用，不要编造或漏掉任何参数；

# 添加儿童上网保护设备
当用户需要将XX设备（例如：nova 6手机）加入儿童上网保护，先需要通过get_host_info查询到对应设备名称和mac地址，然后将该设备的MAC地址和名称分别作为device字段和name字段传入add_child_device接口中;

# 删除儿童上网保护设备
当用户需要将XX设备（例如：nova 6手机）从儿童上网保护列表中删除，先通过get_child_protect查询到对应设备devceid，并在调用对应设置接口时将devceid赋值给"device"，例如"device": "2"；

3.4 命令行调用方式（与 skill 中枢统一规范）
（0）前置信息查询：确认家庭和路由信息
# 获取家庭信息和homeId
node common-skill/bin/smarthome-claw.js get_homes_info

# 获取所有设备信息，包括device id和prodid
node common-skill/bin/smarthome-claw.js get_devices_info

# 查询设备详细信息
node common-skill/bin/smarthome-claw.js get_device_detail --dev-id "xxx"

# 根据prodid查找本地映射的路由设备信息
# 本功能仅使用本地的router_device_info.js映射表进行设备识别
node router-skill/bin/router-claw.js get_router_device_by_prodid --prodid K1AP

（1）路由相关状态、配置信息查询
# 查询儿童上网保护信息
node router-skill/bin/router-claw.js get_child_protect

**【关键判断逻辑 - 必须遵守】**
判断某类应用是否真正被禁止，必须同时看两个字段：
- `denyXxx = 1`：表示该类应用的限制开关已开启
- `xxxDenyCount > 0`：表示实际被禁止的应用数量

| denyXxx | xxxDenyCount | 实际状态                                   |
|---------|--------------|----------------------------------------|
| 1       | > 0          | ✅ 已禁止（如 gameDenyCount=153 表示153款游戏被禁止） |
| 1       | = 0          | ❌ 未实际禁止（开关开启但无具体应用被拦截）                 |
| 0       | 任意           | ❌ 未禁止                                  |

**【强制】向用户展示应用管控状态时，必须使用上述判断逻辑，不能仅凭 denyXxx=1 就说"已开启"。**
**【强制】若查询到具体应用使用情况，可以通过应用id查询到具体应用名称并返回给用户实际应用名称，方法用get_app_info；**

# 查询路由下挂设备信息（自动解码gzip+base64）
node router-skill/bin/router-claw.js get_host_info
注1：可用于判断某家庭成员是否到家（示例：女儿几点到家，可以以女儿手机连接路由wifi的时间为准）
注2：用户在查询下挂设备时，需要告诉用户各个设备的名称/品牌型号/IP/MAC/在线状态等信息

# 查询当前上网方式
node router-skill/bin/router-claw.js get_wan_status

# 查询上行网络连接状态
node router-skill/bin/router-claw.js get_wandetect

# 查询自动优化信道开关状态
node router-skill/bin/router-claw.js get_channel_info

# 查询5G优选开关状态
node router-skill/bin/router-claw.js get_5g_optimize

# 查询ipv6开关状态
node router-skill/bin/router-claw.js get_ipv6

# 查询用户体验改进计划开关状态
node router-skill/bin/router-claw.js get_user_behavior

# 查询路由器状态
node router-skill/bin/router-claw.js get_router_status

# 查询WiFi配置
node router-skill/bin/router-claw.js get_wifi_config

（2）允许上网的时段设置
**【重要】action 参数说明：**
| action 值 | 功能 | 必须完全匹配 |
|-----------|------|-------------|
| `newCreate` | 创建新的上网时段规则 | ✅ 是 |
| `newUpdate` | 更新已有的上网时段规则 | ✅ 是 |
| `newDelete` | 删除已有的上网时段规则 | ✅ 是 |
**⚠️ 注意：action 参数必须完全匹配上述值，使用 `delete`、`create`、`update` 等错误值会导致操作无效但返回成功！**

# 添加允许上网时段（例如：周一到周五，每天早上8点到23点允许上网，周六周日不允许上网）
node router-skill/bin/router-claw.js set_net_time --device-id 1 --action newCreate --data '{"id":"","enable":1,"timeFrom":"08:00","timeTo":"23:00","today":0,"device":"1","monday":1,"saturday":0,"sunday":0,"thursday":1,"friday":1,"tuesday":1,"wednesday":1}'

# 关闭允许上网时段（例如：关闭周一到周五的上网时段设置，那周一到周五就默认允许上网）
node router-skill/bin/router-claw.js set_net_time --device-id 1 --action newUpdate --data '{"id":"1","enable":0,"timeFrom":"08:00","timeTo":"23:00","today":1,"device":"1","monday":1,"saturday":0,"sunday":0,"thursday":1,"friday":1,"tuesday":1,"wednesday":1}'

# 删除上网时段配置（若出现上网时段规则冲突或重复的情况，可以执行该命令删除重复时段或冲突时段）
node router-skill/bin/router-claw.js set_net_time --device-id 1 --action newDelete --data '{"id":"1","enable":0,"timeFrom":"08:00","timeTo":"10:30","today":1,"device":"1","monday":1,"saturday":1,"sunday":1,"thursday":1,"friday":1,"tuesday":1,"wednesday":1}'

（3）不允许上网时段设置
**⚠️ 注意：若需要设置不允许上网时段，请把除不允许时段以外，其他时段均设置为允许上网时段，反过来使用set_net_time**
**【重要】需要将设备所有上网时段设置整体考虑,包括:新设置时段和已有配置，可以删除冲突的时段设置，避免实际不生效**

（3）允许上网的时长设置
# 添加允许上网时长（例如：从周一到周五，每天允许上网6小时）
node router-skill/bin/router-claw.js set_net_duration --device-id 1 --action update --data '{"daily":{"monday":21600,"tuesday":21600,"wednesday":21600,"thursday":21600,"friday":21600,"saturday":90000,"sunday":90000},"device":"1"}‘

# 添加允许上网时长（例如：周末每天允许上网3小时）
node router-skill/bin/router-claw.js set_net_duration --device-id 1 --action update --data '{"daily":{"monday":18000,"tuesday":18000,"wednesday":18000,"thursday":18000,"friday":18000,"saturday":10800,"sunday":10800},"device":"1"}'

# 删除上网时长（例如：删除周一到周五（工作日）允许上网时长的设置）
node router-skill/bin/router-claw.js set_net_duration --device-id 1 --action update --data '{"daily":{"monday":90000,"tuesday":90000,"wednesday":90000,"thursday":90000,"friday":90000,"saturday":10800,"sunday":10800},"device":"1"}'

# 删除上网时长（例如：删除周末允许上网时长的设置）
node router-skill/bin/router-claw.js set_net_duration --device-id 1 --action update --data '{"daily":{"monday":90000,"tuesday":90000,"wednesday":90000,"thursday":90000,"friday":90000,"saturday":90000,"sunday":90000},"device":"1"}'
**【重要】时长单位说明：**
- `timeSummary.allowed` 字段单位为**秒**，表示**每天**的允许上网时长
- 示例：`allowed: 21600` = 21600秒 = 6小时/天
- 示例：`allowed: 90000` = 90000秒 = 25小时/天（相当于无限制，因为一天只有24小时）
**【强制】25小时就相当于无上网时长限制，不要给用户展示25小时，直接展示“无时长限制”**

（3）精细应用管理（禁止特定类型应用）
# 禁止设备玩游戏（包括王者荣耀、和平精英等153款游戏）
node router-skill/bin/router-claw.js deny_games --device-id 1

# 禁止设备看视频（包括爱奇艺、腾讯视频、抖音等43款视频应用）
node router-skill/bin/router-claw.js deny_videos --device-id 1

# 禁止设备社交通讯（包括微信、QQ、知乎、微博等5款社交应用）
node router-skill/bin/router-claw.js deny_social --device-id 1

# 禁止设备购物支付（包括支付宝、微信支付、淘宝、京东等9款购物应用）
node router-skill/bin/router-claw.js deny_shopping --device-id 1

# 禁止设备安装应用（包括华为应用市场、小米应用商店等8款应用商店）
node router-skill/bin/router-claw.js deny_install --device-id 1

（4）取消应用限制（恢复特定类型应用使用权限）
# 恢复设备游戏使用权限
node router-skill/bin/router-claw.js allow_games --device-id 1

# 恢复设备视频使用权限
node router-skill/bin/router-claw.js allow_videos --device-id 1

# 恢复设备社交通讯使用权限
node router-skill/bin/router-claw.js allow_social --device-id 1

# 恢复设备购物支付使用权限
node router-skill/bin/router-claw.js allow_shopping --device-id 1

# 恢复设备安装应用使用权限
node router-skill/bin/router-claw.js allow_install --device-id 1

（5）一键断网 / 延时断网
# 立即断网 delayEnable=1，allow=0
node router-skill/bin/router-claw.js set_net_off --data '{"device":"1","game":0,"video":0,"social":0,"payEnable":0,"appDownload":0,"urlEnable":0,"denyEnable":0,"delayEnable":1,"allow":0,"increaseTime":0}'

# 延时10分钟断网 allow=600,allow单位是秒，可以根据用户指令修改实际延时断网时长
node router-skill/bin/router-claw.js set_net_off --data '{"device":"1","game":0,"video":0,"social":0,"payEnable":0,"appDownload":0,"urlEnable":0,"denyEnable":0,"delayEnable":1,"allow":600,"increaseTime":0}'

# 恢复上网 delayEnable=0
node router-skill/bin/router-claw.js set_net_off --data '{"device":"1","game":0,"video":0,"social":0,"payEnable":0,"appDownload":0,"urlEnable":0,"denyEnable":0,"delayEnable":0,"allow":0,"increaseTime":0}'

（6）应用信息查询
# 根据应用id查询具体应用信息
node router-skill/bin/router-claw.js get_app_info --app-id 1

# 查询所有可用的应用列表
node router-skill/bin/router-claw.js get_all_apps

（7）添加、删除儿童上网保护设备
# 添加儿童上网保护设备
node router-skill/bin/router-claw.js add_child_device --data '{"devices" : ["A2:61:62:A9:69:2E"],"names" : ["nova 13"]}'

# 删除儿童上网保护设备
node router-skill/bin/router-claw.js del_child_device --data '{"device":"2"}'

（8）查询设备具体上网时长
# 查询当前在线时长：根据设备名称或者设备MAC地址找到对应设备信息，AccessRecords是接入时间，当前时间减去接入时间，就是在线时长
node router-skill/bin/router-claw.js get_host_info

# 通过get_child_protect获取下列具体类别使用时长：
# 查询设备当天玩游戏时长：”today“->"time"->"game"的值代表游戏时长，单位：s
# 查询设备看视频娱乐时长：”today“->"time"->"video"
# 查询设备学习时长：”today“->"time"->"study"
# 查询设备进行社交资讯时长：”today“->"time"->"social"
node router-skill/bin/router-claw.js get_child_protect

3.5 数据展示格式
开头固定：当前您家路由儿童上网配置如下：
展示受儿童保护的设备列表
展示上网时段规则
展示应用管控状态
展示网络与设备基础信息

4. Edge cases（边缘场景）
模糊描述：当用户问其他网络问题时，使用通用网络知识回答；
设备未添加保护：提示用户是否需要将设备加入儿童上网保护；
请求失败：告知用户 “操作失败，请稍后重试”。

5. 支持查询 SID 清单
下挂设备：.sys/gateway/system/HostInfo?filterAndroid=true&isSupportHostZip=true
儿童保护：.sys/gateway/ntwk/childHomepage
上网方式：.sys/gateway/ntwk/wan?type=active
上行网络：.sys/gateway/ntwk/wandetect
信道优化：.sys/gateway/ntwk/channelinfo
5G 优选：.sys/gateway/ntwk/wlandbho
IPv6：.sys/gateway/ntwk/ipv6_enable
用户体验计划：.sys/gateway/system/userbehavior
路由状态：.sys/gateway/system/processstatus
WiFi 配置：.sys/gateway/ntwk/wlanradio

6. 应用管理接口 SID 清单
禁止/允许游戏应用：.sys/gateway/ntwk/childModelApps
禁止/允许视频应用：.sys/gateway/ntwk/childModelApps
禁止/允许社交通讯：.sys/gateway/ntwk/childModelApps
禁止/允许购物支付：.sys/gateway/ntwk/childModelApps
禁止/允许安装应用：.sys/gateway/ntwk/childModelApps
取消应用限制操作：.sys/gateway/ntwk/childHomepage
应用上网时长设置：.sys/gateway/ntwk/childDailyUpdate