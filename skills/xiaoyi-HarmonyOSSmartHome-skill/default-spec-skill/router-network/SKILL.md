---
name: router-network
description: "路由网络管理场景技能。网络状态诊断、路由器运行状态查询、下挂设备列表、上行网络及WiFi配置。当用户说'网络诊断'、'路由器状态'、'网络配置'等时加载此场景技能。"
---

# 路由网络管理场景

> **场景说明**：网络状态诊断、路由器运行状态查询、下挂设备列表、上行网络及 Wi-Fi 配置。

## 涉及子模块

本场景主要调用 **router-skill** 中的路由器管理相关功能：

* **get_router_status** - `router-skill/SKILL.md`
    * **功能:** 查询路由器整体运行状态。
* **get_host_info** - `router-skill/SKILL.md`
    * **功能:** 查询当前路由器下挂载的设备列表。
* **get_wandetect / get_wan_status** - `router-skill/SKILL.md`
    * **功能:** 查询上行网络状态及上网方式。
* **get_wifi_config** - `router-skill/SKILL.md`
    * **功能:** 查询 Wi-Fi 基础配置。
* **get_channel_info / get_5g_optimize / get_ipv6 / get_user_behavior** - `router-skill/SKILL.md`
    * **功能:** 查询各类高级网络优化开关状态。

## 相关技能

本场景依赖 `router-skill/SKILL.md`，当需要进行路由器相关操作时，必须优先加载使用该技能实现网络状态查询和配置管理。

---

## 路由说明

**触发关键词**：
- 网络诊断
- 路由器状态
- 网络配置
- 路由器管理

**用户语料示例**：
- "帮我做下网络状态诊断。"
- "路由器状态怎么样？"
- "查看网络配置"
- "路由器下挂设备列表"

**路由逻辑**：
- 当用户请求包含上述关键词时，总入口路由到此场景技能
- 本场景技能依赖 `router-skill/SKILL.md`（路由器技能），进一步调用：
  - `router-skill/SKILL.md` 中的路由器管理功能：
    - `get_router_status` - 查询路由器整体运行状态
    - `get_host_info` - 查询下挂设备列表
    - `get_wandetect/get_wan_status` - 查询上行网络状态
    - `get_wifi_config` - 查询 Wi-Fi 配置
    - `get_channel_info/get_5g_optimize/get_ipv6` - 网络优化功能

