---
name: weibo-clawbot-setup
description: 安装和配置微博 ClawBot 插件（Weibo OpenClaw Plugin）。当用户要求安装微博插件、配置微博 ClawBot、设置微博 OpenClaw 插件时使用此技能。支持从 Gitee 安装官方插件、配置 AppId/AppSecret 凭证、验证连接状态。
---

# 微博 ClawBot 安装配置指南

## 概述

微博 ClawBot 是微博官方推出的 OpenClaw 插件，支持通过微博私信与 ClawBot 对话，以及调用微博相关工具（热搜、智搜、用户微博等）。

## 安装流程

### 步骤 1：从 Gitee 克隆插件

```bash
cd ~/.openclaw/workspace
git clone https://gitee.com/wecode-ai/openclaw-weibo.git skills/openclaw-weibo
```

**重要**：官方插件地址是 `gitee.com/wecode-ai/openclaw-weibo`，版权属于 Weibo, Inc.

### 步骤 2：安全扫描

安装任何 Skill/插件前，必须进行安全扫描：

```bash
cd ~/.openclaw/workspace/skills/skill-scope
npx tsx scripts/calculate_hash.ts ~/.openclaw/workspace/skills/openclaw-weibo
npx tsx scripts/check.ts <hash> ~/.openclaw/workspace/skills/openclaw-weibo/README.md https://gitee.com/wecode-ai/openclaw-weibo
```

确认扫描结果为 `Benign` 后继续。

### 步骤 3：通过 OpenClaw CLI 安装

```bash
openclaw plugins install @wecode-ai/weibo-openclaw-plugin
```

### 步骤 4：配置凭证

1. 打开微博客户端，私信 **@微博龙虾助手**（用户ID：6808810981）
2. 发送消息：`连接龙虾`
3. 收到回复后，获取 `AppId` 和 `AppSecret`

配置凭证：

```bash
openclaw config set 'channels.weibo.appId' '<your-appId>'
openclaw config set 'channels.weibo.appSecret' '<your-appSecret>'
```

### 步骤 5：重启 Gateway

```bash
openclaw gateway restart
```

### 步骤 6：验证安装

```bash
openclaw status
```

确认输出中 `Weibo` 显示 `ON · OK · configured`。

## 内置工具

安装成功后，以下工具可用：

| 工具名称 | 功能说明 |
|---------|---------|
| `weibo_token` | 获取微博 API 访问令牌 |
| `weibo_search` | 微博智搜，关键词搜索微博内容 |
| `weibo_status` | 获取用户发布的微博列表 |
| `weibo_hot_search` | 获取微博热搜榜 |
| `weibo_crowd` | 微博超话发帖工具 |

## API 调用示例

### 获取 Token

```javascript
const http = require('http');

const postData = JSON.stringify({
  app_id: '<appId>',
  app_secret: '<appSecret>'
});

const options = {
  hostname: 'open-im.api.weibo.com',
  port: 80,
  path: '/open/auth/ws_token',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(postData)
  }
};

// 发送请求获取 token
```

### 获取热搜榜

```javascript
const hotSearchUrl = 'http://open-im.api.weibo.com/open/weibo/hot_search?token=' + encodeURIComponent(token) + '&category=主榜&count=20';
http.get(hotSearchUrl, callback);
```

### 获取用户微博

```javascript
const statusUrl = 'http://open-im.api.weibo.com/open/weibo/user_status?token=' + encodeURIComponent(token) + '&count=10';
http.get(statusUrl, callback);
```

## 常见问题

### Q: 插件安装后显示 "unloaded"

检查凭证是否正确配置：
```bash
openclaw config get channels.weibo
```

### Q: API 返回 404 错误

确认使用正确的 API 端点：
- Token: `/open/auth/ws_token`
- 热搜: `/open/weibo/hot_search`
- 用户微博: `/open/weibo/user_status`（不是 `/open/weibo/status`）

### Q: 如何获取更多微博功能？

当前插件版本（v2.0.0）不支持以下功能：
- 获取关注的人的微博
- 发布新微博
- 评论、转发等互动功能

## 脚本资源

### scripts/test_weibo_api.js

测试微博 API 连接和功能的脚本。

使用方法：
```bash
node scripts/test_weibo_api.js --appId <appId> --appSecret <appSecret>
```

## 注意事项

1. **凭证安全**：AppId 和 AppSecret 是敏感信息，不要泄露给他人
2. **官方来源**：只从 `gitee.com/wecode-ai/openclaw-weibo` 安装官方插件
3. **API 限制**：微博 API 可能有调用频率限制，注意控制请求频率
