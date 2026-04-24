# NOTIFICATION 授权配置指南

## 版本
- V8.4.0 可运营化版
- 日期: 2026-04-24

## 一、授权状态

| 状态 | 说明 | 后续动作 |
|------|------|----------|
| configured | authCode 已配置且有效 | 无需操作 |
| not_configured | authCode 未配置 | 需要配置 |
| invalid | authCode 已配置但无效 | 需要更新 |

## 二、配置位置

### 2.1 环境变量（推荐）

```bash
# 临时设置
export XIAOYI_AUTH_CODE="your_auth_code_here"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export XIAOYI_AUTH_CODE="your_auth_code_here"' >> ~/.bashrc
source ~/.bashrc
```

### 2.2 配置文件

**方式一：JSON 配置文件**

创建 `config/xiaoyi_config.json`：
```json
{
  "auth_code": "your_auth_code_here"
}
```

**方式二：纯文本文件**

创建 `.xiaoyi_auth`：
```
your_auth_code_here
```

**方式三：用户目录**

创建 `~/.xiaoyi/auth_code`：
```
your_auth_code_here
```

### 2.3 配置优先级

1. 环境变量 `XIAOYI_AUTH_CODE`
2. `config/xiaoyi_config.json`
3. `.xiaoyi_auth`
4. `~/.xiaoyi/auth_code`

## 三、校验方式

### 3.1 命令行检查

```bash
python scripts/check_notification_auth.py
```

**输出示例（已配置）**：
```
============================================================
NOTIFICATION 授权状态检查
============================================================

状态: configured
说明: authCode 已配置且有效

详细信息:
----------------------------------------
  authCode: 已找到
  来源: /path/to/config
  能力可用: 是

💡 NOTIFICATION 能力已就绪

============================================================
```

**输出示例（未配置）**：
```
============================================================
NOTIFICATION 授权状态检查
============================================================

状态: not_configured
说明: authCode 未配置

详细信息:
----------------------------------------
  authCode: 未找到

💡 请配置 XIAOYI_AUTH_CODE 环境变量或在 config/xiaoyi_config.json 中设置 auth_code

============================================================
```

**输出示例（无效）**：
```
============================================================
NOTIFICATION 授权状态检查
============================================================

状态: invalid
说明: authCode 已配置但无效

详细信息:
----------------------------------------
  authCode: 已找到
  来源: /path/to/config
  能力可用: 否

💡 请检查 authCode 是否正确，或是否过期

============================================================
```

### 3.2 程序化检查

```python
from scripts.check_notification_auth import check_notification_auth

result = check_notification_auth()

if result["status"] == "configured":
    print("授权有效")
elif result["status"] == "not_configured":
    print("需要配置授权")
else:
    print("授权无效，需要更新")
```

## 四、获取 authCode

### 4.1 华为开发者平台

1. 登录 [华为开发者联盟](https://developer.huawei.com/)
2. 创建应用或选择现有应用
3. 在应用详情页获取 authCode
4. 确保 NOTIFICATION 权限已开启

### 4.2 小艺开放平台

1. 登录小艺开放平台
2. 创建技能或选择现有技能
3. 在技能配置页获取 authCode
4. 确保推送权限已授权

## 五、常见问题

### Q1: authCode 在哪里获取？

参见上方"获取 authCode"章节。

### Q2: authCode 会过期吗？

是的，authCode 可能会过期。如果检查结果显示 `invalid`，请重新获取。

### Q3: 如何更新 authCode？

更新配置文件或环境变量中的 authCode 值，然后重新运行检查脚本。

### Q4: 配置后仍然显示 not_configured？

检查：
1. 配置文件路径是否正确
2. 文件格式是否正确（JSON 需要 valid JSON）
3. 环境变量是否已生效（重启终端）

### Q5: 配置后显示 invalid？

检查：
1. authCode 是否正确复制（无多余空格）
2. authCode 是否已过期
3. 应用是否已开通 NOTIFICATION 权限
4. 网络是否能访问华为服务

## 六、健康巡检集成

健康巡检脚本会自动检查 NOTIFICATION 授权状态：

```bash
python scripts/platform_health_check.py
```

如果授权状态不是 `configured`，健康报告会显示警告。

## 七、定时检查

可以配置定时任务定期检查授权状态：

```bash
# 每小时检查一次
0 * * * * cd /path/to/workspace && python scripts/check_notification_auth.py >> logs/auth_check.log 2>&1
```
