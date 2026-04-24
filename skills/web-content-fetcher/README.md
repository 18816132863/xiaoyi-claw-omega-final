<div align="center">

# Web Content Fetcher

**网页正文提取 · 永久免费 · 支持微信公众号**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-purple)](https://github.com/shirenchuang/web-content-fetcher)

</div>

---

## 简介

Web Content Fetcher 是一个轻量级的网页正文提取工具，能够自动将任意网页转换为干净的 Markdown 格式，保留标题、链接、图片和列表结构。

**核心优势：**
- 支持 Jina Reader / Scrapling / web_fetch 三级降级策略
- 完美支持微信公众号文章（Jina 无法读取的场景）
- 返回标准 Markdown 格式，便于后续处理
- 零配置，开箱即用

---

## 安装

### 方式一：作为 OpenClaw Skill 安装（推荐）

```bash
npx skills add shirenchuang/web-content-fetcher
```

### 方式二：手动安装

1. 将整个目录复制到 OpenClaw skills 目录：
   ```bash
   cp -r web-content-fetcher ~/.openclaw/workspace/skills/
   ```

2. 安装 Python 依赖：
   ```bash
   cd ~/.openclaw/workspace/skills/web-content-fetcher
   pip install -r requirements.txt
   ```

   > **注意**：首次安装后需要运行 `scrapling install` 下载浏览器依赖

3. 重启 OpenClaw，skill 自动生效

### 依赖说明

本工具基于 [Scrapling](https://github.com/D4Vinci/Scrapling) 构建，使用 fetchers 功能需要额外安装浏览器依赖：

```bash
# 安装完成后执行
scrapling install
```

---

## 使用方式

### 在 OpenClaw 中使用

直接告诉 AI 你要读取的 URL，会自动选择最佳方案：

```
帮我读取这篇文章：[https://example.com/article](https://mp.weixin.qq.com/s/EwVItQH4JUsONqv_Fmi4wQ)
用 Scrapling 读取这篇公众号：https://mp.weixin.qq.com/s/EwVItQH4JUsONqv_Fmi4wQ
```

### 命令行单独使用

```bash
# 基础用法
python3 scripts/fetch.py <url> [max_chars]

# 示例：读取微信公众号文章
python3 scripts/fetch.py https://mp.weixin.qq.com/s/EwVItQH4JUsONqv_Fmi4wQ 30000

# 输出到文件
python3 scripts/fetch.py https://example.com/article > output.md
```

---

## 提取策略

```
URL 输入
    │
    ▼
┌─────────────────────────────────────┐
│  1. Jina Reader（首选）              │
│     · 速度快（~1.5s），格式干净      │
│     · 免费额度：200次/天             │
│     · 不支持：微信公众号、部分国内站  │
└─────────────────────────────────────┘
    │ 失败/超限
    ▼
┌─────────────────────────────────────┐
│  2. Scrapling + html2text           │
│     · 无限制，效果与 Jina 相当       │
│     · 支持：公众号、Substack、Medium  │
│     · 反爬平台友好                   │
└─────────────────────────────────────┘
    │ 失败
    ▼
┌─────────────────────────────────────┐
│  3. web_fetch（兜底）                │
│     · 静态页面兜底方案               │
│     · 适合：GitHub README、技术文档   │
└─────────────────────────────────────┘
```

### 域名快捷路由

为节省 Jina 配额，以下域名直接使用 Scrapling：

| 域名 | 路由策略 |
|------|---------|
| `mp.weixin.qq.com` | 直跳 Scrapling |
| `zhuanlan.zhihu.com` | 优先 Scrapling |
| `juejin.cn` | 优先 Scrapling |
| `csdn.net` | 优先 Scrapling |

---

## 支持平台

| 平台 | 状态 | 备注 |
|------|:----:|------|
| 微信公众号 | ✅ | Jina 无法读取，Scrapling 完美支持 |
| Substack | ✅ | |
| Medium | ✅ | |
| 知乎专栏 | ✅ | |
| 掘金 | ✅ | |
| CSDN | ✅ | |
| GitHub | ✅ | web_fetch 亦可 |
| 小红书 | ❌ | 需要登录态 |

---

## 输出格式

返回标准 Markdown，自动保留：

- **标题层级**：`# ## ###`
- **超链接**：`[文字](url)`
- **图片**：`![alt](url)`（data-src 懒加载自动处理）
- **列表、代码块、引用块**

---

## 相关项目

### [Kuaifa（快发）](https://github.com/shirenchuang/kuaifa) - 公众号一键排版发布

如果你需要将 Markdown 文章发布到微信公众号，推荐使用 **Kuaifa**：

- 一键 Markdown 排版，支持多种主题
- 自动上传图片到 CDN
- 一键创建公众号草稿
- 支持预览和发布

```bash
pip install kuaifa
kuaifa publish your-article.md
```

**Star**: [github.com/shirenchuang/kuaifa](https://github.com/shirenchuang/kuaifa)

---

## 作者

<div align="center">

**石臻说AI**

AI科技博主 · 10+年大厂AI提效专家

专注于个人提效、超级个体、AI 资讯

<img src="qrcode_for_shizhen.jpg" width="200" alt="公众号二维码"/>

*扫码关注公众号*

</div>

---

## License

MIT License
