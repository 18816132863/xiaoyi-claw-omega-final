# 企业微信智能机器人快速参考

## 配置文件位置

```
~/.openclaw/openclaw.json
```

## Channel 配置模板

```json
{
  "channels": {
    "wecom": {
      "enabled": true,
      "botId": "你的Bot ID",
      "secret": "你的安全密钥",
      "dmPolicy": "pairing"
    }
  }
}
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `openclaw plugins install @wecom/wecom-openclaw-plugin` | 安装企业微信插件 |
| `openclaw gateway restart` | 重启 Gateway |
| `openclaw status` | 查看状态 |
| `openclaw pairing approve wecom <配对码>` | 完成配对 |
| `openclaw logs` | 查看日志 |

## 企业微信后台入口

- 管理后台: https://work.weixin.qq.com/wework_admin/loginpage_wx
- 开放平台: https://open.feishu.cn/

## 配置流程图

```
企业微信后台                    OpenClaw
    │                              │
    ├─ 创建智能机器人              │
    ├─ 获取 Bot ID 和密钥          │
    │                              │
    │                              ├─ 安装插件
    │                              ├─ 配置 openclaw.json
    │                              ├─ 重启 gateway
    │                              │
    ├─ 在企业微信发消息            │
    │   └─ 收到配对码              │
    │                              │
    │                              ├─ 执行配对命令
    │                              │
    └──────── 连接成功 ────────────┘
```

## 故障排查

### channel 状态异常

```bash
# 检查配置
cat ~/.openclaw/openclaw.json | grep -A 10 wecom

# 检查插件
ls ~/.openclaw/extensions/wecom-openclaw-plugin

# 重启服务
openclaw gateway restart
```

### 配对失败

```bash
# 查看日志
openclaw logs --tail 100

# 检查 Bot ID 和密钥是否正确
openclaw status
```

### 消息无响应

1. 确认配对成功
2. 检查机器人可见范围
3. 确认 OpenClaw gateway 正在运行
