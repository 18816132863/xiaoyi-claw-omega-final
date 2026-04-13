---
name: hunyuan-image
description: "腾讯混元图像 3.0 (Hunyuan-Image)。腾讯自研的文生图大模型，支持高质量图像生成、图像编辑、图像超分。Triggers: 生成图片, AI绘画, 文生图, 图像生成, 腾讯混元, Hunyuan, image generation, text to image, AI art"
metadata: {"openclaw":{"emoji":"🎨","primaryEnv":"TENCENT_SECRET_KEY"}}
---

# 腾讯混元图像 3.0 (Hunyuan-Image)

腾讯自研的文生图大模型，支持高质量图像生成。

## 能力

- **文生图 (Text to Image)**: 根据文字描述生成高质量图像
- **图像编辑 (Image Edit)**: 根据文字指令编辑图像
- **图像超分 (Image Super Resolution)**: 提升图像分辨率
- **多风格支持**: 写实、动漫、3D、油画等

## API 配置

### 环境变量

```bash
export TENCENT_SECRET_ID="your_secret_id"
export TENCENT_SECRET_KEY="your_secret_key"
```

### 获取密钥

1. 访问 https://cloud.tencent.com 注册账号
2. 开通混元大模型服务
3. 在访问管理 > API密钥管理中创建密钥

## 使用方式

### 文生图

```bash
python3 scripts/hunyuan_generate.py text2image \
  --prompt "一只可爱的橘猫躺在窗台上晒太阳，阳光温暖，画面温馨治愈" \
  --style "realistic" \
  --size "1024x1024" \
  --quantity 1
```

### 图像编辑

```bash
python3 scripts/hunyuan_generate.py image-edit \
  --prompt "将背景替换为海边日落场景" \
  --image "https://example.com/image.png"
```

### 图像超分

```bash
python3 scripts/hunyuan_generate.py super-resolution \
  --image "https://example.com/low_res.png" \
  --scale 4
```

## 参数说明

### text2image

| 参数 | 说明 | 默认值 |
|------|------|--------|
| --prompt | 图像描述 | 必填 |
| --negative-prompt | 负面提示词 | "" |
| --style | 风格 (realistic/anime/3d/oil_painting) | realistic |
| --size | 尺寸 (1024x1024/1280x720/720x1280) | 1024x1024 |
| --quantity | 生成数量 (1-4) | 1 |
| --seed | 随机种子 | 随机 |

### image-edit

| 参数 | 说明 | 默认值 |
|------|------|--------|
| --prompt | 编辑指令 | 必填 |
| --image | 图片URL或本地路径 | 必填 |
| --strength | 编辑强度 (0-1) | 0.8 |

### super-resolution

| 参数 | 说明 | 默认值 |
|------|------|--------|
| --image | 图片URL或本地路径 | 必填 |
| --scale | 放大倍数 (2/4) | 4 |

## 输出

生成的图像将保存到：
- `~/.openclaw/workspace/generated-images/`

## 风格说明

| 风格 | 说明 |
|------|------|
| realistic | 写实风格，适合人物、风景 |
| anime | 动漫风格，适合二次元创作 |
| 3d | 3D渲染风格 |
| oil_painting | 油画风格 |
| watercolor | 水彩风格 |
| sketch | 素描风格 |

## 注意事项

1. 图像生成通常需要 10-30 秒
2. 支持本地图片（自动上传）和远程图片URL
3. 建议使用详细的提示词以获得更好的效果
