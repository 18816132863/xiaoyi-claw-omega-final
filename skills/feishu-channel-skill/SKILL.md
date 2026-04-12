---
name: feishu-channel-setup
description: 飞书Channel配置技能。帮助用户配置飞书机器人与OpenClaw的集成，包括创建应用、配置权限、设置事件订阅。触发词：配置飞书、飞书channel、飞书机器人、feishu配置。
license: MIT
metadata:
  author: flp516
  version: "1.0"
---

# 飞书 Channel 配置技能

帮助用户配置飞书 Channel，实现通过飞书与 OpenClaw 对话。

## 前置要求

- OpenClaw 运行环境
- 飞书企业账号（管理员权限）
- 公网可访问的服务器（或使用 ngrok）

## 配置步骤概览

1. 创建飞书企业自建应用
2. 配置应用权限
3. 获取 App ID 和 App Secret
4. 配置 OpenClaw
5. 配置事件订阅
6. 发布应用并测试

## 详细配置指南

请参阅 [GUIDE.md](./GUIDE.md) 获取完整的配置步骤。

## 配置模板

参考 `config-template.json` 获取 OpenClaw 配置模板。

## 技术说明

- 飞书 API 文档：https://open.feishu.cn/document
- 事件订阅方式：Webhook 或长链接
- 默认端口：18789

## 相关链接

- [飞书开放平台](https://open.feishu.cn/)
- [OpenClaw文档](https://docs.openclaw.ai)
