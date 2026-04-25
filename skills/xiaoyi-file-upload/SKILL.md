---
name: xiaoyi-file-upload
description: 通过 upload 命令上传本地文件到对象存储（OSMS/NSP），获取可共享的下载 URL。适用于需要将本地文件分享、传递给其他服务、或生成临时下载链接的场景。当用户提到"上传文件"、"获取下载链接"、"文件分享链接"、"把文件传到云上"等需求时使用此 skill。
---

# xiaoyi-file-upload：文件上传与下载链接生成

## 适用场景

- **生成文件分享链接** — 上传文件后将 URL 发给同事或粘贴到文档中
- **与 xiaoyi-office 配合** — 先上传文件获取 URL，再在 prompt 中通过 URL 引用
- **脚本集成** — 在自动化流程中上传产物并记录下载地址

> 注意：xiaoyi-office 支持 `@file_path` 语法直接引用本地文件，通常不需要手动上传。

## 前置条件

1. **acp2service 二进制**：已编译的 `acp2service` 可执行文件（位于 `bin/` 目录）
2. **环境变量**：配置 OSMS 或 NSP 其中一种对象存储后端，详见 [reference.md](./reference.md)
3. **不需要** `SERVICE_URL`，也不需要 `acpx`

## 调用方式

### 基本用法

```bash
# 上传单个文件，download URL 输出到 stdout
/path/to/bin/acp2service upload /path/to/file.pdf

# 在脚本中捕获 URL
URL=$(/path/to/bin/acp2service upload ./report.pdf)
echo "下载地址: $URL"
```

### 批量上传

```bash
for f in /path/to/docs/*.pdf; do
  url=$(/path/to/bin/acp2service upload "$f")
  echo "$f -> $url"
done
```

### 输出说明

- download URL 输出到 **stdout**（一行纯文本）
- 日志和错误信息输出到 **stderr**
- 退出码：0 成功，非 0 失败
