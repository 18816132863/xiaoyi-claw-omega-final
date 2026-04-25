# 飞书 Channel 配置指导书

本指导书将帮助你在飞书中与小艺对话。

---

## 目录

1. [前置准备](#1-前置准备)
2. [创建飞书应用](#2-创建飞书应用)
3. [配置应用权限](#3-配置应用权限)
4. [获取应用凭证](#4-获取应用凭证)
5. [配置 OpenClaw](#5-配置-openclaw)
6. [配置事件订阅](#6-配置事件订阅)
7. [发布应用](#7-发布应用)
8. [测试对话](#8-测试对话)
9. [常见问题](#9-常见问题)

---

## 1. 前置准备

### 1.1 环境要求

| 项目 | 要求 |
|:---|:---|
| OpenClaw | 已安装并运行 |
| 飞书账号 | 企业管理员权限 |
| 服务器 | 公网可访问（或使用 ngrok） |

### 1.2 确认 OpenClaw 状态

在小艺中发送：

```
openclaw status
```

确认 Gateway 正在运行。

---

## 2. 创建飞书应用

### 2.1 进入飞书开放平台

1. 打开浏览器，访问：**https://open.feishu.cn/app**
2. 使用飞书账号登录

![飞书开放平台首页](images/step-2-1.png)

### 2.2 创建企业自建应用

1. 点击页面上的 **「创建企业自建应用」** 按钮

![创建应用按钮](images/step-2-2.png)

2. 填写应用信息：

| 字段 | 填写内容 |
|:---|:---|
| **应用名称** | 小艺 Claw（或你喜欢的名称） |
| **应用描述** | AI 智能助手，帮你处理各种任务 |
| **应用图标** | 上传一个图标（可选） |

![填写应用信息](images/step-2-3.png)

3. 点击 **「确定」** 完成创建

---

## 3. 配置应用权限

### 3.1 进入权限管理

1. 在应用管理页面，点击左侧菜单 **「权限管理」**

![权限管理入口](images/step-3-1.png)

### 3.2 添加权限

**方式一：批量添加（推荐）**

1. 点击 **「批量添加」** 按钮
2. 粘贴以下 JSON：

```json
{
  "scopes": {
    "tenant": [
      "im:message",
      "im:message:readonly",
      "im:message:send_as_bot",
      "im:message.group_at_msg:readonly",
      "im:message.p2p_msg:readonly",
      "im:chat.members:bot_access",
      "im:resource",
      "docx:document:readonly",
      "docx:document",
      "bitable:app:readonly"
    ],
    "user": [
      "im:chat.access_event.bot_p2p_chat:read"
    ]
  }
}
```

![批量添加权限](images/step-3-2.png)

3. 点击 **「确认」**

**方式二：逐个添加**

在权限列表中搜索并开通以下权限：

| 权限名称 | 用途 |
|:---|:---|
| `im:message` | 消息权限 |
| `im:message:send_as_bot` | 以机器人身份发消息 |
| `im:message.p2p_msg:readonly` | 读取单聊消息 |
| `im:message.group_at_msg:readonly` | 读取群聊@消息 |
| `im:chat.members:bot_access` | 获取群成员信息 |
| `im:resource` | 资源权限 |
| `docx:document:readonly` | 文档只读权限 |

### 3.3 确认权限状态

添加完成后，确认所有权限状态为 **「已开通」**

![权限列表](images/step-3-3.png)

---

## 4. 获取应用凭证

### 4.1 查看凭证信息

1. 点击左侧菜单 **「凭证与基础信息」**

![凭证入口](images/step-4-1.png)

### 4.2 复制凭证

找到以下信息并复制保存：

| 凭证 | 格式示例 | 用途 |
|:---|:---|:---|
| **App ID** | `cli_xxxxxxxxxxxxxxxx` | 应用标识 |
| **App Secret** | `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` | 应用密钥 |

![凭证信息](images/step-4-2.png)

⚠️ **注意**：App Secret 只显示一次，请妥善保存！

---

## 5. 配置 OpenClaw

### 5.1 发送配置信息给小艺

将 App ID 和 App Secret 发送给小艺：

```
帮我配置飞书 channel
App ID: cli_xxxxxxxxxxxxxxxx
App Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

小艺会自动完成配置。

### 5.2 手动配置（可选）

如果需要手动配置，编辑 `~/.openclaw/openclaw.json`：

```json
{
  "channels": {
    "feishu": {
      "appId": "cli_xxxxxxxxxxxxxxxx",
      "appSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "enabled": true
    }
  }
}
```

### 5.3 启用飞书插件

```bash
openclaw plugins enable feishu
openclaw gateway restart
```

---

## 6. 配置事件订阅

### 6.1 进入事件订阅页面

1. 在飞书开放平台，点击左侧菜单 **「事件订阅」**

![事件订阅入口](images/step-6-1.png)

### 6.2 选择订阅方式

有两种方式可选：

#### 方式一：使用长链接（推荐）

1. 选择 **「使用长链接接收事件」**
2. 无需配置 URL，飞书会主动连接

![长链接方式](images/step-6-2.png)

#### 方式二：配置 Webhook URL

1. 选择 **「使用 Webhook 接收事件」**
2. 填写请求网址：

```
http://你的服务器IP:18789/webhook/feishu
```

例如：`http://1.95.104.135:18789/webhook/feishu`

![Webhook 配置](images/step-6-3.png)

### 6.3 添加事件

点击 **「添加事件」**，选择以下事件：

| 事件名称 | 用途 |
|:---|:---|
| `im.message.receive_v1` | 接收消息 |

![添加事件](images/step-6-4.png)

### 6.4 保存配置

点击 **「保存」** 完成事件订阅配置

---

## 7. 发布应用

### 7.1 进入版本管理

1. 点击左侧菜单 **「版本管理与发布」**

![版本管理入口](images/step-7-1.png)

### 7.2 创建版本

1. 点击 **「创建版本」**
2. 填写版本号（如：1.0.0）
3. 填写更新说明

![创建版本](images/step-7-2.png)

### 7.3 提交审核

1. 点击 **「提交审核」**
2. 等待审核通过（通常几分钟到几小时）

### 7.4 发布应用

审核通过后：

1. 点击 **「发布」**
2. 选择发布范围（全员可见或部分部门）

![发布应用](images/step-7-3.png)

### 7.5 启用机器人

1. 点击左侧菜单 **「应用能力」→「机器人」**
2. 开启 **「启用机器人」** 开关

![启用机器人](images/step-7-4.png)

---

## 8. 测试对话

### 8.1 在飞书中搜索机器人

1. 打开飞书 App 或网页版
2. 在搜索框输入你的机器人名称
3. 点击搜索结果中的机器人

![搜索机器人](images/step-8-1.png)

### 8.2 发起对话

1. 点击 **「发消息」**
2. 输入任意内容发送

![发起对话](images/step-8-2.png)

### 8.3 配对授权

首次对话时，小艺会返回配对码：

```
OpenClaw: access not configured.
Your Feishu user id: ou_xxxxxxxxxxxxxxxx
Pairing code: XXXXXXXX
```

将配对码发给小艺：

```
帮我批准飞书配对，配对码：XXXXXXXX
```

或让管理员执行：

```bash
openclaw pairing approve feishu XXXXXXXX
```

### 8.4 开始使用

配对成功后，你就可以在飞书中和小艺对话了！

---

## 9. 常见问题

### Q1: 消息发送失败，提示权限不足

**解决方案**：
1. 检查飞书开放平台的权限配置
2. 确认所有必要权限已开通
3. 重新发布应用版本

### Q2: 机器人不回复消息

**解决方案**：
1. 检查 OpenClaw Gateway 是否运行：`openclaw status`
2. 检查事件订阅是否配置正确
3. 查看日志：`openclaw logs`

### Q3: Webhook URL 配置失败

**解决方案**：
1. 确认服务器防火墙开放 18789 端口
2. 确认 Gateway 绑定到 0.0.0.0 而非 127.0.0.1
3. 使用 `curl http://服务器IP:18789/health` 测试连通性

### Q4: 如何获取用户的 open_id

**解决方案**：
1. 让用户先给机器人发一条消息
2. 在日志中查看用户的 open_id
3. 或使用飞书 API 查询

### Q5: 如何在群聊中使用

**解决方案**：
1. 将机器人添加到群聊
2. @机器人 发送消息
3. 机器人会回复 @你的消息

---

## 附录

### A. 飞书 API 文档

- 开放平台首页：https://open.feishu.cn
- 消息 API：https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN
- 事件订阅：https://open.feishu.cn/document/ukTMukTMukTM/uUTNxYjL1EjM24TNxYjN

### B. OpenClaw 文档

- 官方文档：https://docs.openclaw.ai
- GitHub：https://github.com/openclaw/openclaw
- 社区：https://discord.com/invite/clawd

### C. 配置文件示例

```json
{
  "channels": {
    "feishu": {
      "appId": "cli_xxxxxxxxxxxxxxxx",
      "appSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "enabled": true
    }
  },
  "gateway": {
    "mode": "local",
    "bind": "0.0.0.0",
    "auth": {
      "mode": "token",
      "token": "your-gateway-token"
    }
  }
}
```

---

*文档版本：1.0.0*
*更新时间：2026-03-19*
*作者：小艺 Claw*
