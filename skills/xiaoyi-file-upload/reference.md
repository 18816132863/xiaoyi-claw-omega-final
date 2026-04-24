# acp2service-upload 参考手册

## 环境变量配置

环境变量通过 `~/.openclaw/.xiaoyienv`（默认）或 `ACP2SERVICE_ENV` 指定的 .env 文件加载。

### OSMS 配置

| 变量 | 说明 |
|------|------|
| `OSMS_BASE_URL` | OSMS 服务基础地址，设置后启用 OSMS |
| `REQUEST_FROM` | 鉴权 header，默认 `openclaw` |
| `PERSONAL_UID` | 鉴权 header |
| `PERSONAL_API_KEY` | 鉴权 header |

## 问题排查

| 现象 | 原因 | 解决 |
|------|------|------|
| "未配置文件上传后端" | 没有设置 OSMS 环境变量 | 检查 `~/.openclaw/.xiaoyienv` 或手动 export |
| "文件不存在" | 路径错误 | 检查文件路径，支持相对和绝对路径 |
| "OSMS 客户端创建失败" | 配置不完整或服务不可达 | 检查网络和环境变量完整性 |
