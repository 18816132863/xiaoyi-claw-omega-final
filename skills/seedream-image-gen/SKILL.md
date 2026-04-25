---
name: seedream-image-gen
description: 小艺图像创作，基于Seedream5的AI图像生成能力，支持文本、单图、多图多种输入方式，可实现主体一致性多图融合、图像编辑、系列组图生成等创作功能。触发词：生成图片、画图、图像创作、小艺图像、text-to-image、image-to-image。
---

## 核心能力
这个技能有以下功能:
- 根据文本提示词生成图像
- 接收一张或多张图像输入
- 生成多张图像时保存编号的输出文件和URL

## 使用示例

```bash
# Text-to-image
python3 scripts/generate_seedream.py --prompt "生成一张爵士音乐节海报，风格复古，色彩鲜艳"

# Image-to-image with remote URL
python3 scripts/generate_seedream.py --prompt "图像风格转换" --image https://example.com/a.png

# Image-to-image with local file path
python3 scripts/generate_seedream.py --prompt "图像风格转换" --image /path/to/local/image.png

# Multi-image reference (mix of URLs and local paths)
python3 scripts/generate_seedream.py --prompt "参考多张图片风格" --image https://a.png --image /path/to/b.png --max-images 3

# Generate multiple images (3 images) - IMPORTANT: specify count in prompt
python3 scripts/generate_seedream.py --prompt "请生成3张不同风格的猫咪图片：第一张写实风格，第二张卡通风格，第三张油画风格" --max-images 3

# Image-to-multiple images (图生多图) - generate 3 variations based on one reference
python3 scripts/generate_seedream.py --prompt "请基于这张参考图生成3张不同光影效果的照片" --image https://example.com/photo.png --max-images 3

# Multiple-images-to-multiple images (多图生多图) - generate using multiple references
python3 scripts/generate_seedream.py --prompt "请基于提供的两张参考图，生成3张融合两种风格的艺术作品" --image https://example.com/a.png --image /path/to/b.png --max-images 3
```

## 输出

图像将保存至：`workspace/generated-images/`

默认文件命名：`YYYYMMDD_HHMMSS_SSS_2位随机字符_generated.jpg`

图像生成后将图像文件发送给用户

# Prompt通用规则

Seedream 支持文生图、图片编辑、参考图生图、组图生成等多样化任务。为了获得更理想的图像效果，编写提示词时注意：

- 建议用**简洁连贯**的语言写明 **主体 + 行为 + 环境**，若对画面美学有要求，可用自然语言补充 **风格**、**色彩**、**光影**、**构图** 等美学元素。提示词不超过300个汉字。
- 当有明确的应用场景时，在文本提示中写明图像用途和类型。  
- 如果有明确的风格需求，使用精准的 **风格词** 或提供 **参考图像**，能获得更理想的效果。
- 当画面中包含文字时，将文字内容放入**双引号**，提高文本渲染准确度。
- 使用 **简洁明确的指令**，说明需要修改或参考的对象及具体操作，避免使用指代模糊的代词；如果希望除了修改的内容都保持不变，可在 prompt 中强调。  

# 提示词秘籍

## 文生图

采用清晰明确的自然语言描述画面内容，对于细节比较丰富的图像，可通过详细的文本描述精准控制画面细节。

Seedream 可将知识与推理结果转化为高密度图像内容，如公式、图表、教学插图等。在生成时应明确使用**专业术语**，确保知识点表达准确，并写清对生成图像的具体要求，如可视化形式、版式、风格等。如：
- 在黑板上画出下列二元一次方程组及其相应的解法步骤：5x + 2y = 26；2x \- y = 5。

## 图生图

支持结合文本与图片完成图像编辑和参考生成任务，并可通过**箭头**、**线框**、**涂鸦等视觉信号**控制画面区域，实现可控生成。

### 图像编辑

支持对画面进行**增加**、**删除**、**替换**、**修改**等编辑操作。  
建议使用**简洁明确**的文字，**准确指示需要编辑的对象与变化要求**。
当画面内容比较复杂，难以通过文本准确描述编辑对象时，可采用箭头、线框、涂鸦等方式指明编辑对象和位置。

### 参考图生图

当有明确需保持的特征（如角色形象、视觉风格、产品设计）时，可上传图像作为参考，以确保生成结果与期望保持一致。在文本提示中明确两部分内容：
- **参考图中要保留的内容**：人物形象 / 风格 / 材质 / 款式 / 布局等
- **新图要生成的内容**：场景、动作、用途、成品形式等

如果有必须一致的特征，要明确写出：如家具位置与参考图一致、按照原型图的布局等。

## 多图输入

支持同时输入多张图像，完成**替换**、**组合**、**迁移**等复合编辑操作。使用该功能时，建议在文本提示中清楚指明不同图像需要编辑/参考的对象及操作，如：用**图一的人物**替换**图二的人物**，并参考**图三的风格**进行生成。

## 多图输出

支持生成角色连贯、风格统一的图像序列，适用于分镜、漫画创作，以及需要统一视觉风格的成套设计场景，如 IP 产品或表情包制作。  
当有多图生成需求时，可以通过“一系列”、“一套”、“组图”等提示词触发模型生成组图，或采用具体数字表明图片数量。强调角色一致、风格统一、配色统一、系列感。