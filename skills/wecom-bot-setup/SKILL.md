---
name: wecom-bot-setup
description: 企业微信智能机器人接入 OpenClaw 的配置指南。当用户需要配置企业微信智能机器人连接到 OpenClaw 时使用此技能。触发词：企业微信机器人配置、wecom bot setup、企业微信接入、配置企业微信channel。
---

# 企业微信智能机器人接入 OpenClaw 配置指南

本技能指导用户将企业微信智能机器人接入 OpenClaw，实现通过企业微信与 AI 助手对话。

## 前置条件

- 企业微信管理员权限
- OpenClaw 已安装并运行

## 配置步骤

### 第一步：在企业微信后台创建智能机器人

1. 登录 [企业微信管理后台](https://work.weixin.qq.com/wework_admin/loginpage_wx)
2. 点击顶部菜单 **「应用管理」**
3. 点击 **「创建应用」**
4. 选择 **「智能机器人」**（注意：不是自建应用）
5. 填写机器人名称、描述、头像
6. **选择「API模式」**（关键步骤）
7. 点击创建

### 第二步：获取机器人凭证

创建成功后，在机器人详情页获取：
- **Bot ID**（类似 `aibbaASmjPf24FGucaXD1FL-YHc3zOSbcWI`）
- **安全密钥**（类似 `otrlrVTviRiDuW1m4adtio8RAvbzMsHPGtz5tymvVVa`）

**重要**：妥善保管密钥，不要泄露。

### 第三步：配置机器人可见范围

1. 在机器人详情页，找到 **「可见范围」** 设置
2. 添加需要使用机器人的成员或部门
3. 建议先添加自己进行测试

### 第四步：在 OpenClaw 安装企业微信插件

```bash
openclaw plugins install @wecom/wecom-openclash-plugin
```

安装依赖：
```bash
cd ~/.openclaw/extensions/wecom-openclash-plugin
npm install @wecom/aibot-node-sdk --save
```

### 第五步：配置 OpenClaw

编辑 `~/.openclaw/openclaw.json`，在 `channels` 下添加：

```json
"wecom": {
  "enabled": true,
  "botId": "你的Bot ID",
  "secret": "你的安全密钥",
  "dmPolicy": "pairing"
}
```

### 第六步：重启 OpenClaw Gateway

```bash
openclaw gateway restart
```

检查状态：
```bash
openclaw status
```

确认 `wecom` channel 显示 `OK` 或 `configured`。

### 第七步：完成配对

1. 打开企业微信 App
2. 在「工作台」或搜索框找到你的智能机器人
3. 给机器人发送任意消息
4. 机器人会返回配对提示，包含：
   - 你的企业微信用户ID
   - 配对码（如 `RA8ATMH4`）
5. 在 OpenClaw 终端执行：
   ```bash
   openclaw pairing approve wecom <配对码>
   ```

### 第八步：验证连接

配对成功后，在企业微信中给机器人发送消息测试：
- 发送 "你好"
- 确认收到 AI 助手的回复

## 常见问题

### 找不到智能机器人

- 确认已在「可见范围」中添加自己
- 在企业微信 App 顶部搜索框搜索机器人名称
- 检查机器人是否已发布

### 配对失败

- 确认 Bot ID 和密钥正确
- 检查 OpenClaw gateway 是否正常运行
- 查看 `openclaw status` 确认 channel 状态

### 消息无响应

- 确认配对已成功
- 检查 OpenClaw 日志：`openclaw logs`
- 确认机器人事件订阅已开启

## 相关资源

- [企业微信开放平台文档](https://developer.work.weixin.qq.com/document/)
- [OpenClaw 官方文档](https://docs.openclaw.ai)
