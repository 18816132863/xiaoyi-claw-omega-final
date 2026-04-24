---
name: xiaoyi-podcast-gen
description: 小艺播客生成技能。支持文本内容、网页链接、本地文件三种输入方式，自动生成双人访谈式播客音频。触发词包括："生成播客"、"做一期播客"、"播客音频"、"对话式播客"、"podcast"等。
---

## 核心能力

- **内容文本生成播客**：直接传入文本内容（--content），走 collection 模式生成播客
- **本地文件生成播客**：传入本地文件路径（--content），自动读取内容后走 collection 模式生成播客
- **网页链接生成播客**：输入 URL（--uri），基于网页内容解析生成播客
- **详略程度选择**：briefs（简略）/ details（详细，更耗时但是效果更好）

## 交互指引

收到播客生成请求后，按以下流程处理：

### 第一步：判断输入类型

| 用户输入 | 模式 | 处理方式 |
|---------|------|----------|
| URL 链接 | `--uri` | 进入第三步确认 |
| 本地文件路径（.txt/.md） | `--content` | 进入第三步确认 |
| 文本内容 | `--content` | 进入第二步 |

**⚠️ 用户给 URL，直接用 `--uri`，不需要先抓取内容；用户给文件，直接用 `--content` 传文件路径，不要自己概括总结。**

### 第二步：内容长度校验（仅 `--content` 文本模式）

**目标**：传入内容控制在 **100~2000 字** 之间，太少无法生成，太多平台会进行截断。

- **内容 < 100 字（一句话/短话题）**：内容不足，自动联网搜索补全。流程：
  1. 调用网络搜索技能（xiaoyi-web-search/tavily-search 等）搜索相关内容
  2. 将搜索结果提炼总结，控制在 100~2000 字
  3. 进入第三步确认

- **100 字 ≤ 内容 ≤ 2000 字**：长度合适，进入第三步。

- **内容 > 2000 字**：内容过长，需要提炼。agent 自行对内容进行摘要/提炼，控制在 2000 字以内，然后进入第三步。提炼时保留核心观点和关键细节，不要丢失重要信息。

**内容保存文件**：校验通过后，将文本内容写入临时文件（`/tmp/podcast_content_YYYYMMDD_HHMMSS.txt`），用 `--content` 传文件路径给脚本。用户提供本地文件直接用原路径。

### 第三步：用户确认 🚫不可跳过

**每次生成都必须用户明确授权，不可跳过。** 如果用户多次修改内容，每次修改后都必须重新展示修改后的内容并等待用户明确同意。确认内容包含：

- 输入方式（文本内容 / 网页链接 / 本地文件）
- 内容摘要或来源（文本模式展示前 100 字，链接模式展示链接，文件模式展示文件路径）
- 详略程度（briefs 简略 / details 详细，默认 details）

示例：
> 📋 播客生成确认：
> - 输入：文本内容
> - 内容："荆州文物保护中心位于荆州古城外的三国公园..."（共 580 字）
> - 详略程度：details（详细）
> 
> 确认生成吗？

### 第四步：执行生成

**必须用户明确授权才可以执行，否则禁止执行。**

用户同意后，调用播客生成脚本执行生成。

### 第五步：发送结果

生成完成后，**必须立即**将结果发送给用户，格式如下：

> 🎙️ 播客生成完成！
> 
> 📌 标题：{标题}
> ⏱️ 时长：{时长}
> 📊 配额：今日已完成 {n}/{上限}
> 
> MEDIA:{音频文件路径}


## 使用示例

```bash
# 直接传入文本内容（collection 模式）
python3 scripts/generate_podcast.py --content "荆州文物保护中心位于荆州古城外的三国公园..."

# 传入本地文件路径（自动读取内容，collection 模式）
python3 scripts/generate_podcast.py --content /path/to/article.md
python3 scripts/generate_podcast.py --content ~/docs/notes.txt

# 网页链接生成播客
python3 scripts/generate_podcast.py --uri "http://xhslink.com/n/2bMrQ7n1jq4"

# 指定内容详略程度
python3 scripts/generate_podcast.py --content "深度学习发展史..." --scene details

# 完整参数
python3 scripts/generate_podcast.py --content "AI对未来工作的影响..." \
  --scene details \
  --output /path/to/output
```

## 参数说明

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `--content` | 是* | - | 播客内容文本或本地文件路径（与 `--uri` 二选一）。本地文件仅支持 .txt/.md，自动读取内容 |
| `--uri` | 否* | - | 播客来源 URL 链接（与 `--content` 二选一） |
| `--scene` | 否 | details | 播客详略程度：briefs（简略）/ details（详细，更耗时但是效果更好） |
| `--output` | 否 | 自动生成 | 输出目录路径 |

## 输出

文件保存至：`~/.openclaw/workspace/generated-podcasts/YYYYMMDD_HHMMSS/`

默认文件命名：`YYYYMMDD_HHMMSS_podcast.{ext}`

脚本输出包含：
- 🎵 音频文件（.m4a）本地路径
- 📌 播客标题
- ⏱️ 时长
- 📊 已用配额

## ⚠️ 播客生成超时设置

`generate_podcast.py` 执行时间较长，**必须**在 exec 调用中设置 `timeout=1800`（30 分钟），否则默认超时会导致中途断开。

```python
# ✅ 正确
exec(command="python3 scripts/generate_podcast.py --content 'xxx'", timeout=1800)

# ❌ 错误：未设 timeout（默认太短）
exec(command="python3 scripts/generate_podcast.py --content 'xxx'")

# ❌ 错误：timeout 过短
exec(command="python3 scripts/generate_podcast.py --content 'xxx'", timeout=600)

