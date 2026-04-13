---
name: xiaoyi-ppt
description: "Generate professional PPT presentations using a 3-stage workflow: gather information & confirm writing approach, generate structured outline & upload, generate PPT via cloud service & deliver. TRIGGER when user asks to: generate PPT, create slides, make presentation, 生成PPT, 做PPT, 制作幻灯片, 做演示文稿. Supports both document-based and web-search-based content sourcing. DO NOT TRIGGER for: editing existing PPT files, modifying slides, adjusting layout or content of an existing presentation — those are edit operations not covered by this skill."
metadata:
  openclaw:
    requires:
      bins:
        - python3
---

# PPT 生成技能

信息整理（文档解析 / 网络搜索）+ 结构化大纲生成 + 云端 PPT 生成的完整流程，分为三个子流程。

---

## 环境初始化（始终最先执行此步骤）

**此技能需要 Python 3 (>=3.8)。在运行任何脚本之前，执行以下命令定位有效的 Python 可执行文件并安装依赖。**

```bash
PYTHON_CMD=""
for cmd in python3 python python3.13 python3.12 python3.11 python3.10 python3.9 python3.8; do
  if command -v "$cmd" &>/dev/null && "$cmd" -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" 2>/dev/null; then
    PYTHON_CMD="$cmd"
    break
  fi
done

if [ -z "$PYTHON_CMD" ]; then
  echo "错误：未找到 Python 3.8+"
  exit 1
fi

echo "已找到 Python：$PYTHON_CMD ($($PYTHON_CMD --version))"

$PYTHON_CMD -m pip install -q --break-system-packages requests
echo "依赖已就绪。"
```

> 检查完成后，在后续所有命令中使用发现的 `$PYTHON_CMD` 替代 `python`。

---

## 会话初始化（环境检查完成后立即执行）

```bash
PPT_SESSION_ID="${PPT_SESSION_ID:-$(uuidgen 2>/dev/null || $PYTHON_CMD -c 'import uuid; print(uuid.uuid4())')}"
PPT_SESSION_DIR="/tmp/xiaoyi_ppt/$PPT_SESSION_ID"
mkdir -p "$PPT_SESSION_DIR"
echo "会话 ID：$PPT_SESSION_ID"
echo "会话目录：$PPT_SESSION_DIR"
```

| 变量 | 路径 |
|------|------|
| `{baseDir}` | 本 skill 根目录（由运行环境注入） |
| `{baseDir}/scripts/` | 脚本目录 |
| `$PPT_SESSION_DIR` | `/tmp/xiaoyi_ppt/<session_id>/` |
| `/tmp/xiaoyi_ppt/<session_id>/outline.md` | 大纲文件 |
| `/tmp/xiaoyi_ppt/<session_id>/generate.log` | 运行日志 |

---

## 三个子流程

环境和会话初始化完成后，按顺序执行以下三个子流程。**每个子流程开始前，必须先完整阅读对应的 MD 文件，再执行任何操作。**

### 子流程一：信息搜索 & 确认写作思路

> **必须先阅读 `{baseDir}/step1_search_confirm.md`，再执行此子流程。**

覆盖范围：
- 从文档或网络搜索收集信息
- 梳理写作思路并与用户对齐确认

完成标志：用户确认写作思路，输出 `✅ 写作思路已确认`

---

### 子流程二：生成大纲 & 上传

> **必须先阅读 `{baseDir}/step2_outline_upload.md`，再执行此子流程。**

覆盖范围：
- 基于已确认的写作思路生成完整大纲
- 保存大纲到本地文件
- 上传大纲到云端获取 URL

完成标志：大纲上传成功，获取到 `$OUTLINE_URL`，输出 `✅ 大纲文件上传成功`

---

### 子流程三：调用云服务 & 监控 & 交付

> **必须先阅读 `{baseDir}/step3_generate_monitor.md`，再执行此子流程。**

覆盖范围：
- 调用 `generate_ppt.py` 在后台启动 PPT 生成任务
- 每 10 秒轮询日志，实时汇报进展（最多 60 次）
- 任务完成后向用户交付本地路径和下载链接

完成标志：PPT 生成完成，输出 `✅ PPT 生成完成！`

---

## 依赖

- **Python 3.8+**（必需）— `python3` / `python` 必须在 PATH 中
- **requests 库** — 环境检查步骤自动安装
- **已安装的文档解析 skill** — 当用户提供文档时使用
- **已安装的网络搜索 skill** — 当需要在线搜索信息时使用
- **`~/.openclaw/.xiaoyienv`** — OSMS 服务配置文件，必须包含 `SERVICE_URL`
