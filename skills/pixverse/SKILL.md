---
name: pixverse
description: "PixVerse V6 视频生成模型（爱诗科技）。支持文生视频、图生视频。高质量AI视频生成，支持多种分辨率和时长。Triggers: 生成视频, AI视频, 文生视频, 图生视频, video generation, text to video, image to video, 视频创作"
metadata: {"openclaw":{"emoji":"🎬","primaryEnv":"PIXVERSE_API_KEY"}}
---

# PixVerse V6 视频生成

**爱诗科技** 出品的 AI 视频生成模型，支持高质量视频生成。

## 能力

- **文生视频 (Text to Video)**: 根据文字描述生成视频
- **图生视频 (Image to Video)**: 根据图片生成视频
- **多分辨率支持**: 720P, 1080P
- **时长支持**: 5-15 秒

## API 配置

### 环境变量

```bash
export PIXVERSE_API_KEY="your_api_key_here"
export PIXVERSE_BASE_URL="https://api.pixverse.ai"
```

### 获取 API Key

1. 访问 https://pixverse.ai 注册账号
2. 在控制台获取 API Key

## 使用方式

### 文生视频

```bash
python3 scripts/pixverse_generate.py text2video \
  --prompt "一只可爱的猫咪在花园里追逐蝴蝶，阳光明媚，画面温馨" \
  --duration 10 \
  --resolution "1080P"
```

### 图生视频

```bash
python3 scripts/pixverse_generate.py image2video \
  --prompt "图片中的人物开始微笑并挥手" \
  --image "https://example.com/image.png" \
  --duration 5
```

### 查询任务状态

```bash
python3 scripts/pixverse_generate.py get-task \
  --task-id "task_xxxxx"
```

## 参数说明

### text2video

| 参数 | 说明 | 默认值 |
|------|------|--------|
| --prompt | 视频描述 | 必填 |
| --duration | 视频时长(秒) | 5 |
| --resolution | 分辨率 (720P/1080P) | 1080P |
| --style | 风格 (realistic/anime/3d) | realistic |

### image2video

| 参数 | 说明 | 默认值 |
|------|------|--------|
| --prompt | 视频描述 | 必填 |
| --image | 图片URL或本地路径 | 必填 |
| --duration | 视频时长(秒) | 5 |
| --motion-level | 运动强度 (1-10) | 5 |

## 输出

生成的视频将保存到：
- `~/.openclaw/workspace/generated-videos/`

## 注意事项

1. 视频生成是异步任务，需要轮询获取结果
2. 生成时间约 1-3 分钟
3. 支持本地图片（自动上传）和远程图片URL
