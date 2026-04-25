# 飞书 Channel 配置 Skill

帮助用户配置飞书 Channel，实现通过飞书与小艺对话。

## 文件结构

```
feishu-channel-setup/
├── SKILL.md              # 技能说明
├── GUIDE.md              # 详细配置指导书
├── tools.js              # 工具实现
├── config-template.json  # 配置模板
├── images/               # 截图目录（需补充）
│   ├── step-2-1.png
│   ├── step-2-2.png
│   ├── ...
│   └── step-8-2.png
└── README.md             # 本文件
```

## 使用方式

用户说：「帮我配置飞书 channel」「我想在飞书里和你对话」

## 配置步骤

1. **创建飞书应用** - 在飞书开放平台创建企业自建应用
2. **配置权限** - 添加消息、文档等权限
3. **获取凭证** - 复制 App ID 和 App Secret
4. **配置 OpenClaw** - 将凭证配置到 openclaw.json
5. **事件订阅** - 配置长链接或 Webhook
6. **发布应用** - 提交审核并发布
7. **测试对话** - 在飞书中搜索机器人并发消息

## 截图说明

`images/` 目录下的截图需要手动补充，对应 GUIDE.md 中的各个步骤：

| 截图文件 | 说明 |
|:---|:---|
| step-2-1.png | 飞书开放平台首页 |
| step-2-2.png | 创建应用按钮 |
| step-2-3.png | 填写应用信息 |
| step-3-1.png | 权限管理入口 |
| step-3-2.png | 批量添加权限 |
| step-3-3.png | 权限列表 |
| step-4-1.png | 凭证入口 |
| step-4-2.png | 凭证信息 |
| step-6-1.png | 事件订阅入口 |
| step-6-2.png | 长链接方式 |
| step-6-3.png | Webhook 配置 |
| step-6-4.png | 添加事件 |
| step-7-1.png | 版本管理入口 |
| step-7-2.png | 创建版本 |
| step-7-3.png | 发布应用 |
| step-7-4.png | 启用机器人 |
| step-8-1.png | 搜索机器人 |
| step-8-2.png | 发起对话 |

## 相关链接

- [飞书开放平台](https://open.feishu.cn)
- [OpenClaw 文档](https://docs.openclaw.ai)
