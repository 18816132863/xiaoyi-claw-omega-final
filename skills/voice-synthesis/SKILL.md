# Voice Synthesis Skill

语音合成技能，使用 edge-tts 生成语音，支持转换为飞书原生格式。

## 能力

- 文本转语音 (TTS)
- 支持多种中文语音
- 可转换为飞书原生 opus 格式

## 可用中文语音

| 语音名称 | 性别 | 风格 |
|---------|------|------|
| zh-CN-YunxiNeural | 男 | 年轻、活力 |
| zh-CN-YunyangNeural | 男 | 新闻播报 |
| zh-CN-XiaoxiaoNeural | 女 | 温柔、甜美 |
| zh-CN-XiaoyiNeural | 女 | 活泼、可爱 |
| zh-CN-JianjianNeural | 男 | 成熟、稳重 |

## 使用方法

### 1. 生成 MP3 语音

```bash
# 男声（年轻活力）
edge-tts --voice "zh-CN-YunxiNeural" --text "你好，我是小艺" --write-media /tmp/voice.mp3

# 女声（温柔甜美）
edge-tts --voice "zh-CN-XiaoxiaoNeural" --text "你好，我是小艺" --write-media /tmp/voice.mp3
```

### 2. 转换为飞书原生格式 (opus)

```bash
ffmpeg -y -i /tmp/voice.mp3 -c:a libopus -b:a 32k /tmp/voice.opus
```

### 3. 发送到飞书

上传 opus 文件获取 file_key，使用 audio 消息类型发送。

## Python 封装示例

```python
import subprocess
import os

def synthesize_voice(text: str, voice: str = "zh-CN-YunxiNeural", output_path: str = "/tmp/voice.mp3") -> str:
    """生成语音文件"""
    cmd = [
        "edge-tts",
        "--voice", voice,
        "--text", text,
        "--write-media", output_path
    ]
    subprocess.run(cmd, check=True)
    return output_path

def convert_to_opus(mp3_path: str, opus_path: str = "/tmp/voice.opus") -> str:
    """转换为飞书原生 opus 格式"""
    cmd = [
        "ffmpeg", "-y",
        "-i", mp3_path,
        "-c:a", "libopus",
        "-b:a", "32k",
        opus_path
    ]
    subprocess.run(cmd, check=True)
    return opus_path
```

## 注意事项

- edge-tts 是微软 Edge TTS，免费使用
- ffmpeg 用于格式转换
- opus 格式适合飞书语音消息
- 临时文件默认存放在 /tmp 目录
