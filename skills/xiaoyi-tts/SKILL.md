---
name: xiaoyi-tts
description: 使用小艺TTS语音合成API将文本转换为语音，支持多语言、自定义发音人/语速/音量/音高，生成MP3音频文件
---

# 小艺语音合成 Skill

## 简介
通过小艺TTS语音合成 API 将文本智能转换为语音，支持中文、英文、法语、俄语等多语言，可自定义发音人、语速、音量、音高，最终生成标准MP3音频文件。

## 特性
- ✅ **开箱即用** - 配置已固化，无需手动设置
- ✅ **多语言支持** - 支持中文、英文、法语、俄语等主流语言
- ✅ **参数自定义** - 自由调整语速、音量、音高参数
- ✅ **发音人查询** - 内置发音人列表查询脚本，精准匹配语言与发音人
- ✅ **MP3输出** - 自动生成并保存标准MP3音频文件
- ✅ **文本限制** - 支持单次500字以内文本合成
- ✅ **中文优化** - 适配中文语音合成场景
- ✅ **简洁输出** - 直接打印音频保存路径供大模型读取

## 文件结构
```
xiaoyi-image-understanding/
├── SKILL.md                # 使用说明（本文档）
├── scripts                 # 程序文件夹
│ ├──  tts.py               # 主程序（文本转语音合成）
│ └── ttsList.py            # 发音人列表查询脚本（获取语言 + 发音人）
├── _meta.json              # Skill 元数据
└── package.json            # 项目配置
```

## 使用方法

### 语音合成

```bash

## 使用方法

### 步骤1：查询发音人列表（必做）
先获取支持的语言和对应发音人，用于后续语音合成参数配置

# 进入 skill 目录
cd /home/sandbox/.openclaw/workspace/skills/xiaoyi-tts

# 查询所有支持的语言和发音人列表
python ./scripts/ttsList.py

```
### 步骤 2：文本转语音合成
使用查询发音人列表得到的language和person参数，person参数对应发音人列表接口返回结果中的name参数，然后执行语音合成
```bash
# 基础使用（默认参数：language默认zh-Hans，person默认zh-Hans-st-1，语速5.0、音量5.0、音高5.0）
python ./scripts/tts.py --text "人工智能是当今世界上最热门的话题之一。"

# 基础使用（默认参数：语速5.0、音量5.0、音高5.0）
python ./scripts/tts.py --language "zh-Hans" --person "zh-Hans-st-3" --text "人工智能是当今世界上最热门的话题之一。"

# 自定义参数（语速、音量、音高，取值范围建议1.0-10.0）
python ./scripts/tts.py --language "zh-Hans" --person "zh-Hans-st-3" --text "文本内容" --speed "6.0" --volume "7.0" --pitch "4.0"

# 英文语音合成
python ./scripts/tts.py --language "en-US" --person "en-US-st-1" --text "Artificial intelligence is one of the hottest topics in the world."

# 开启调试模式
python ./scripts/tts.py --language "zh-Hans" --person "zh-Hans-st-3" --text "文本内容" --debug
```
也可以在 Python 代码中串联调用：
```python
from scripts.ttsList import get_voice_list
from scripts.tts import text_to_speech

# 1. 获取发音人列表
voice_list = get_voice_list()
print("支持的发音人：", voice_list)

# 2. 语音合成（支持自定义参数）
result = text_to_speech(
    language="zh-Hans",     # 从voice_list取language字段
    person="zh-Hans-xy-3",  # 从voice_list取name字段
    text="人工智能是当今世界上最热门的话题之一。",
    speed="5.0",
    volume="5.0",
    pitch="5.0"
)
# 输出：{"audioPath": "/home/sandbox/tts_output/20250520_123456.mp3"}
print(result)
```

## API 信息

| 项目 | 值 |
|------|-----|
| 语音合成地址 | `https://hag-drcn.op.dbankcloud.com/celia-claw/v1/api/skill/tts` |
| 发音人查询地址 | `https://hag-drcn.op.dbankcloud.com/celia-claw/v1/api/skill/tts/list` |
| 鉴权方式 | 从 `.xiaoyienv` 读取 API Key 和 UID，'.xiaoyienv文件默认存在，无需用户自行创建输入' |
| 响应格式 | 发音人查询：JSON；语音合成：二进制 MP3 流 |

### 配置说明

在 `/home/sandbox/.openclaw/.xiaoyienv` 文件中配置以下参数：

```bash
PERSONAL-API-KEY=你的API密钥
PERSONAL-UID=你的用户ID
```

**注意**：
- 语音合成和发音人查询服务地址均已固化在代码中，无需配置
- 只需配置 `PERSONAL-API-KEY` 和 `PERSONAL-UID` 即可

## 发音人查询（ttsList.py）

无额外参数，直接调用即可获取全量列表

### 查询发音人返回格式

```json
{
    "languages": [
        {
            "speakers": [
                {
                    "codec": "3",
                    "name": "zh-Hans-xy-1",
                    "sampleRate": "16000",
                    "desc": "小艺女声"
                },
                {
                    "codec": "3",
                    "name": "zh-Hans-xy-2",
                    "sampleRate": "16000",
                    "desc": "小艺少女"
                }
            ],
            "language": "zh-Hans"
        }
    ],
    "retCode": "0",
    "retMsg": "Success"
}
```
其中"name": "zh-Hans-xy-1"是后续语音合成的person字段。

## 语音合成输入参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| language | string | ✅ | - | 语言编码（从 ttsList.py 查询） |
| person | string | ✅ | - | 发音人编码（从 ttsList.py 查询） |
| text | string | ✅ | - | 待合成文本，≤500 字符 |
| speed | string | ❌ | 5.0 | 语速，建议 1.0-10.0 |
| volume | string | ❌ | 5.0 | 音量，建议 1.0-10.0 |
| pitch | string | ❌ | 5.0 | 音高，建议 1.0-10.0 |

## 何时使用

### ✅ 适合场景
1. 需要**将文本转换为语音**时
2. 需要**多语言语音合成（中 / 英 / 法 / 俄等）**时
3. 需要**自定义发音人、语速、音量、音高**时
4. 需要**生成 MP3 音频文件**时
5. 用户**明确要求文字转语音**时
6. 短文本**朗读场景**时

### ❌ 不适合场景
1. 超过 500 字的长文本合成
2. 语音识别（语音转文字）
3. 音频编辑、格式转换
4. 纯文本处理任务
5. 用户要求不使用 AI 合成

## 输出示例

```bash
python ./scripts/tts.py --language "zh-Hans" --person "zh-Hans-st-3" --text "人工智能是当今世界上最热门的话题之一。"

✅ 所有帧解析完成
📊 统计：总帧数 2，音频帧 2，音频总大小 5616 字节
✅ 纯音频已保存到：xxx\zh-Hans-20260416326.mp3
```

## 返回格式

无

## 技术细节

### 文本限制
1. 单次合成文本长度：≤500 个字符
2. 支持中英文、标点符号、特殊字符
3. 不支持违规、违法文本合成

### 参数范围建议
1. 语速（speed）：1.0（慢）~ 10.0（快），默认 5.0
2. 音量（volume）：1.0（小）~ 10.0（大），默认 5.0
3. 音高（pitch）：1.0（低）~ 10.0（高），默认 5.0
 
### 音频格式
1. 输出格式：MP3
2. 采样率：16kHz
3. 编码：标准音频编码

## 注意事项

1. **文本长度**: 单次合成文本必须≤500 字符
2. **参数匹配**: language 和 person 必须从 ttsList.py 查询获取，不可自定义
3. **参数范围**: 语速、音量、音高建议使用 1.0-10.0 的数值
4. **网络要求**: 需要稳定的网络连接访问 API
5. **内容安全**: 合成文本应符合相关法律法规
6. **文件保存**: 音频文件默认保存在工作目录的 tts_output 文件夹下
7. **配额限制**: 注意 API 调用频率限制

## 错误处理

### 常见错误及解决方案

| 错误码 | 错误信息 | 解决方案 |
|--------|---------|---------|
| 401 | Permission denied | 检查 Token 是否过期 |
| 400 | Parameter is not valid | 检查 language/person 参数是否匹配 |
| 500 | Internal Server Error | 后端服务器错误 |
| timeout | Request timeout | 增加超时时间或检查网络 |
| connection error | Failed to connect | 检查网络连接 |

## 总结

当需要文本转语音时：
1. ✅ 调用ttsList.py查询支持的语言和发音人
2. ✅ 确认文本长度≤500 字符
3. ✅ 配置语言、发音人、语速、音量、音高参数
4. ✅ 调用tts.py执行语音合成
5. ✅ 获取生成的 MP3 音频文件路径

记住：语音合成前必须先查询发音人列表，文本长度严格控制在 500 字以内，参数匹配才能成功合成。✅
