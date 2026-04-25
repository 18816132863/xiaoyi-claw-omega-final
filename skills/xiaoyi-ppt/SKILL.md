---
name: xiaoyi-ppt
description: "Generate and edit professional PPT presentations. Generation uses a 3-stage workflow: gather information & confirm writing approach, generate structured outline, generate PPT via cloud service & deliver. Editing operates directly on existing PPTX files via XML-level manipulation (unpack, modify, repack). TRIGGER when user asks to: generate PPT, create slides, make presentation, edit/modify PPT, adjust slide content/layout, delete/add/reorder slides, use PPT as template, 生成PPT, 做PPT, 制作幻灯片, 做演示文稿, 编辑/修改PPT, 基于模板修改. Supports both document-based and web-search-based content sourcing for generation."
metadata:
  openclaw:
    requires:
      bins:
        - python3
---

# PPT 生成&编辑 Skill

信息整理（文档解析 / 网络搜索）+ 结构化大纲生成 + 云端 PPT 生成的完整流程；也支持对已有 PPTX 文件进行直接编辑修改。

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
| `$PPT_SESSION_DIR` | `/tmp/xiaoyi_ppt/$PPT_SESSION_ID/` |
| `/tmp/xiaoyi_ppt/$PPT_SESSION_ID/outline.md` | 大纲文件 |
| `/tmp/xiaoyi_ppt/$PPT_SESSION_ID/generate.log` | 运行日志 |
| `{baseDir}/edit.md` | PPT 编辑提示词 |

---

## 任务分流

环境和会话初始化完成后，根据用户意图选择对应流程：

| 用户意图 | 判断依据 | 执行流程 |
|---------|---------|---------|
| **新建 PPT** | 用户要求从零生成 PPT，提供文档或主题 | → 进入「生成流程」（子流程一 ~ 三） |
| **编辑已有 PPT** | 用户提供了 PPTX 文件并要求修改，或要求以某个 PPTX 为模板填入新内容 | → 进入「编辑流程」（步骤 E1 ~ E3） |

---

## 生成流程

按顺序执行以下三个子流程。**每个子流程开始前，必须先完整阅读对应的 MD 文件，再执行任何操作。**

### 子流程一：信息搜索 & 确认写作思路

> **必须先阅读 `{baseDir}/step1_search_confirm.md`，再执行此子流程。**

覆盖范围：
- 从文档或网络搜索收集信息
- 梳理写作思路并与用户对齐确认

完成标志：用户确认写作思路，输出 `✅ 写作思路已确认`

---

### 子流程二：生成大纲

> **必须先阅读 `{baseDir}/step2_outline.md`，再执行此子流程。**

覆盖范围：
- 基于已确认的写作思路生成完整大纲
- 保存大纲到本地文件

完成标志：大纲保存完成，输出 `✅ 大纲生成完成`

---

### 子流程三：调用云服务 & 监控 & 交付

> **必须先阅读 `{baseDir}/step3_generate_monitor.md`，再执行此子流程。**

覆盖范围：
- 调用 `generate_ppt.py` 在后台启动 PPT 生成任务
- 每 10 秒轮询日志，实时汇报进展（最多 60 次）
- 任务完成后向用户交付文件

完成标志：PPT 生成完成，输出 `✅ PPT 生成完成！`

---

## 编辑流程

当用户提供已有 PPTX 文件并要求修改，或以某个 PPTX 为模板填入新内容时，进入编辑流程。

### 步骤 E1：读取编辑指导并执行

> **必须先阅读 `{baseDir}/edit.md`，再执行任何编辑操作。**

edit.md 是编辑流程的**唯一权威参考**，包含完整的操作规范（模板分析、XML 解包/打包、幻灯片增删改序、内容编辑、格式规则、常见陷阱等）。读取后，严格按照其中的步骤和约束执行全部编辑操作。

**每完成一张幻灯片的编辑，向用户汇报进展。**

---

### 步骤 E2：AIGC 水印标记

编辑完成、打包出最终 PPTX 后，**必须调用水印脚本**为文件添加 AIGC 标识：

```bash
$PYTHON_CMD {baseDir}/scripts/ppt_aigc_mark.py $PPT_SESSION_DIR/input.pptx
```

脚本自动完成：提取全文 → 生成 AIGC 签名 → 添加首页可见水印 + 隐式 custom property → 覆盖写入原文件。

---

### 步骤 E3：交付

**将标记完成的 `{原文件名}_edited.pptx` 文件发送给用户。**

完成标志：输出 `✅ PPT 编辑完成！`

---

## 依赖

- **Python 3.8+**（必需）— `python3` / `python` 必须在 PATH 中
- **requests 库** — 环境检查步骤自动安装
- **已安装的文档解析 skill** — 当用户提供文档时使用
- **已安装的网络搜索 skill** — 当需要在线搜索信息时使用
- **`~/.openclaw/.xiaoyienv`** — OSMS 服务配置文件，必须包含 `SERVICE_URL`