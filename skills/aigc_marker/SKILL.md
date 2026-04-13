---
name: aigc_marker
description: 为已存在的 DOCX、PDF、Excel、PPT、MD 文件添加 AIGC 标识
version: 1.2.0
entry: scripts/main.py
author: celia
---

# aigc_marker

为已存在的 Word、PDF、Excel、PowerPoint 或 Markdown 文件添加 AIGC（AI生成内容）标识。

## 功能

- **DOCX**: 为 Word 文档添加自定义属性 "AIGC"
- **PDF**: 为 PDF 文档添加 AIGC 元数据
- **Excel**: 为 Excel 文件添加自定义文档属性
- **PPT**: 为 PowerPoint 演示文稿添加自定义属性 "AIGC"
- **MD**: 为 Markdown 文件添加 YAML 前置元数据

## 脚本结构

```
scripts/
├── main.py                    # 入口脚本，接收命令行参数，调用对应装饰器
├── decorators/                # AIGC 装饰器模块
│   ├── __init__.py           # 包导出
│   └── aigc_marker.py        # 五个装饰器类实现
├── docx_extend/              # DOCX 扩展功能（精简版）
│   ├── api.py                # DocumentExtend 类
│   ├── opc/                  # OPC 包处理
│   │   ├── customprops.py    # CustomProperties 类
│   │   └── parts/            # 部件定义
│   │       └── customprops.py # CustomPropertiesPart 类
│   └── oxml/                 # XML 元素定义
│       └── customprops.py    # CT_CustomProperties 等类
├── ppt_extend/               # PPT 扩展功能（精简版）
│   ├── api.py                # PresentationExtend 类
│   ├── opc/                  # OPC 包处理
│   │   ├── customprops.py    # CustomProperties 类
│   │   └── parts/            # 部件定义
│   │       └── customprops.py # CustomPropertiesPart 类
│   └── oxml/                 # XML 元素定义
│       ├── __init__.py       # 命名空间注册
│       └── customprops.py    # CT_CustomProperties 等类
└── oxml/                     # DOCX XML 元素定义
    └── customprops.py        # CT_CustomProperties 等类
```

### 核心模块

- **`scripts/main.py`** - 主入口，解析文件类型，调用对应装饰器
- **`scripts/decorators/aigc_marker.py`** - 包含四个装饰器类：
  - `DocxAigcDecorator` - Word 文档 AIGC 标记
  - `PdfAigcDecorator` - PDF 文档 AIGC 标记
  - `ExcelAigcDecorator` - Excel 文件 AIGC 标记
  - `PptAigcDecorator` - PowerPoint 演示文稿 AIGC 标记
  - `MdAigcDecorator` - Markdown 文件 AIGC 标记

### 依赖关系

```
main.py
└── decorators/aigc_marker.py
    ├── docx_extend/api.py
    │   └── docx_extend/opc/parts/customprops.py
    │       ├── docx_extend/opc/customprops.py
    │       └── docx_extend/oxml/customprops.py
    ├── ppt_extend/api.py
    │   └── ppt_extend/opc/parts/customprops.py
    │       ├── ppt_extend/opc/customprops.py
    │       └── ppt_extend/oxml/customprops.py
    ├── pypdf (第三方库)
    └── openpyxl (第三方库)
```

## 用法

### 执行命令

```bash
cd <skill_dir>/scripts && python main.py <文件路径>
```

模型会自动将 `<skill_dir>` 替换为实际的 skill 路径。

### 命令行用法

```bash
/aigc_marker <文件路径>
```

### 支持的文件格式

| 文件扩展名 | 说明 |
|-----------|------|
| `.docx` | Microsoft Word 文档 |
| `.pdf` | PDF 文档 |
| `.xlsx` | Microsoft Excel 工作簿 |
| `.pptx` | Microsoft PowerPoint 演示文稿 |
| `.md` | Markdown 文档 |

## 参数说明

| 参数 | 类型 | 是否必填 | 说明 |
|------|------|----------|------|
| `文件路径` | string | 是 | 目标文件路径（支持 `.docx`、`.pdf`、`.xlsx`、`.pptx`、`.md`） |
| `--skip-visible` | flag | 否 | 跳过添加显式标识，仅添加隐式元数据 |

## AIGC 签名格式

生成的 AIGC 签名包含以下字段（JSON 格式）：

```json
{
  "Label": "AIGC",
  "ContentProducer": "AI Assistant",
  "ProduceID": "<uuid>",
  "ReservedCode1": "<content_hash>",
  "ContentPropagator": "",
  "PropagateID": "",
  "Timestamp": "<iso_timestamp>"
}
```

## 使用示例

### 命令行风格

```bash
# 为 Word 文档添加 AIGC 标记（默认添加显式和隐式标识）
/aigc_marker document.docx

# 为 PDF 文档添加 AIGC 标记
/aigc_marker report.pdf

# 为 Excel 文件添加 AIGC 标记
/aigc_marker data.xlsx

# 为 PowerPoint 演示文稿添加 AIGC 标记
/aigc_marker presentation.pptx

# 为 Markdown 文件添加 AIGC 标记
/aigc_marker notes.md

# 仅添加隐式标识（不显示"内容由AI生成"）
/aigc_marker document.docx --skip-visible
```

### 函数调用风格

```python
from decorators import docx_aigc_decorator

# 默认：添加显式和隐式标识
docx_aigc_decorator.decorate("document.docx", "content_hash", "req123")

# 仅添加隐式标识
docx_aigc_decorator.decorate("document.docx", "content_hash", "req123", add_visible_mark=False)
```

### 自然语言风格

```
帮我把 document.docx 加上 AIGC 标记
为 report.pdf 添加 AI 生成标识
给 data.xlsx 文件打上 AIGC 标签
为 presentation.pptx 添加 AIGC 标识
给 notes.md 文件添加 AIGC 标识
```

## 输出说明

- 文件会被直接修改，添加 AIGC 元数据
- 原始文件内容保持不变
- 添加的 AIGC 隐式标记不影响文档正常显示
- 显式标记（"内容由AI生成"文字）默认添加在文档末尾或第一页底部
- 使用 `--skip-visible` 参数可仅添加隐式元数据
