---
name: xiaoyi-image-search
description: 图片搜索技能。返回图链接（OSMS预签名URL）、缩略图、图片尺寸等信息。适用于为文档、PPT、报告等场景查找配图素材。
---

# Image-Search: 多引擎图片搜索器

## 简介

图片搜索工具，返回原图链接（OSMS 预签名 URL）、缩略图、标题、尺寸等信息。

## 触发条件

当用户表达以下意图时，请激活此技能：

### 1. 直接指令型 (Direct Commands)

- "搜索一张关于XXX的图片"
- "帮我找几张XXX的图"
- "搜图 XXX"
- "执行 image-search"
- "运行图片搜索技能"

### 2. 素材需求型 (Asset Gathering)

- "帮我找一些配图素材"
- "我需要几张关于XXX的图片用于PPT"
- "给报告找些插图"
- "搜索一些XXX相关的图片素材"

### 3. 自然语言型 (Natural Language Intent)

- "有没有XXX的图片？"
- "能不能帮我搜一下XXX的图？"
- "我想要一些XXX的图片"

## 文件结构

```
xiaoyi-image-search/
    ├── scripts            # 程序文件夹
    │ ├── index.js         # 主程序（CLI入口）
    │ ├── env_loader.js    # 加载环境变量
    │ ├── image_search.js  # 请求服务（执行搜索逻辑）
    │ └── package.json     # node依赖
    └── SKILL.md           # 使用说明（本文档）
```

## 参数说明

| 参数 | 必填 | 默认值 | 说明 |
|:-----|:-----|:------|:-----|
| `query` | 是 | - | 搜索关键词 |
| `num_results` | 否 | 5 | 返回结果数量 |
| `store` | 否 | `osms` | 图片存储方式 |

## 输出格式

每条搜索结果包含以下字段：

| 字段 | 说明 |
|:-----|:-----|
| `engine` | 搜索引擎来源（bing/baidu） |
| `img_title` | 图片标题 |
| `img_from_url` | 图片来源页面 URL |
| `img_ori_url` | 原图 URL（OSMS 预签名链接，可直接下载） |
| `img_thumb_url` | 缩略图 URL |
| `img_height` | 图片高度（像素） |
| `img_width` | 图片宽度（像素） |

## 核心逻辑

1. **接收参数**：解析搜索关键词及可选参数。
2. **发送请求**：调用内部 ImageSearch 接口（`mcp_server_name: browser-use`, `mcp_function_name: image_search`）。
3. **解析响应**：`result` 字段为 JSON 字符串，需二次解析获取图片列表。
4. **格式化输出**：将结果以结构化方式输出到 stdout。

## 使用方法

### 命令行调用

```bash
# 基本用法：node index.js <query> [num_results] [engines] [store]

# 示例：搜索5张图片（默认参数）
node /path/to/current/skill/scripts/index.js "湄洲岛风景"

# 示例：搜索2张图片
node /path/to/current/skill/scripts/index.js "人工智能" 2

```

### 环境变量要求

需要在 `~/.xiaoyienv` 或系统环境变量中配置：

- `SERVICE_URL` — 服务基础地址
- `PERSONAL_UID` — 鉴权 UID
- `PERSONAL_API_KEY` — 鉴权 API Key
