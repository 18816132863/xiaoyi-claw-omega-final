---
name: xiaoyi-image-understanding
description: 使用小艺图像理解API进行图像内容识别和描述，获取图像的详细文本描述
---

# 小艺图像理解 Skill

## 简介
通过小艺图像理解 API 对图像进行智能分析，自动生成详细的图像描述，识别图像中的对象、场景、文字等内容。

## 特性
- ✅ **开箱即用** - 配置已固化，无需手动设置
- ✅ **流式响应** - 支持 SSE 实时流式返回
- ✅ **智能识别** - 精准识别图像内容和细节
- ✅ **文件上传** - 支持将本地图片上传到云存储，获取可访问的 URL
- ✅ **中文优化** - 适合中文描述场景
- ✅ **简洁输出** - 直接打印结果供大模型读取

## 文件结构
```
xiaoyi-image-understanding/
├── SKILL.md                # 使用说明（本文档）
├── scripts                 # 程序文件夹
│ ├── image_understanding.py # 主程序（图像理解）
│ └── file_upload.py         # 文件上传脚本（本地图片 → 云存储 URL）
├── _meta.json              # Skill 元数据
└── package.json            # 项目配置
```

## 使用方法

### 图像理解（直接使用公网 URL）

```bash
# 进入 skill 目录
cd /home/sandbox/.openclaw/workspace/skills/xiaoyi-image-understanding

# 基本使用
python ./scripts/image_understanding.py "https://example.com/image.jpg"

# 自定义提示词
python ./scripts/image_understanding.py "https://example.com/image.jpg" "详细描述这张图片"

# 开启调试模式
python ./scripts/image_understanding.py "https://example.com/image.jpg" --debug
```

### 本地图片上传 + 图像理解（两步流程）

当图片在本地、无公网 URL 时，先上传获取 URL，再执行图像理解：

```bash
# 步骤 1：上传本地图片，获取文件 URL
python ./scripts/file_upload.py "/path/to/local/image.jpg"
# 输出示例：{"objectId": "D4EV1DFka-XQFGvYdUIcIJXhg", "fileUrl": "https://obs.example.com/osms/...", "fileName": "image.jpg"}

# 步骤 2：使用返回的 fileUrl 进行图像理解
python ./scripts/image_understanding.py "https://obs.example.com/osms/..."
```

也可以在 Python 代码中串联调用：

```python
from scripts.file_upload import upload_file
from scripts.image_understanding import image_understanding

# 上传本地图片
upload_result = upload_file('/path/to/image.jpg')
if upload_result:
    # 使用返回的 fileUrl 进行图像理解
    result = image_understanding(upload_result['fileUrl'], '描述这张图片')
    print(result)
    # 输出: {"caption": "图片描述文本..."}
```

## API 信息

| 项目 | 值 |
|------|-----|
| 图像理解地址 | `https://hag-drcn.op.dbankcloud.com/celia-claw/v1/sse-api/skill/execute` |
| 文件上传地址 | `https://hag-drcn.op.dbankcloud.com` |
| 鉴权方式 | 从 `.xiaoyienv` 读取 API Key 和 UID，'.xiaoyienv文件默认存在，无需用户自行创建输入' |
| 响应格式 | 图像理解：SSE 流式响应；文件上传：JSON |

### 配置说明

在 `/home/sandbox/.openclaw/.xiaoyienv` 文件中配置以下参数：

```bash
PERSONAL-API-KEY=你的API密钥
PERSONAL-UID=你的用户ID
```

**注意**：
- 图像理解 API 和文件上传服务地址均已固化在代码中，无需配置
- 只需配置 `PERSONAL-API-KEY` 和 `PERSONAL-UID` 即可

## 文件上传参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| file_path | string | ✅ | - | 本地文件路径（绝对路径或相对路径） |
| object_type | string | ❌ | `TEMPORARY_MATERIAL_DOC` | 文件类型 |

### 文件上传返回格式

```json
{
  "objectId": "D4EV1DFka-XQFGvYdUIcIJXhg",
  "fileUrl": "https://obs.example.com/osms/9/4/.../image.jpg",
  "fileName": "image.jpg"
}
```

### 文件上传三阶段流程

1. **Prepare** - `POST {FILE-UPLOAD-URL}/osms/v1/file/manager/prepare` - 注册上传，获取 `objectId`、`draftId` 及上传地址
2. **Upload** - `PUT {uploadInfos[0].url}` - 使用预签名 URL 上传文件二进制数据
3. **Complete** - `POST {FILE-UPLOAD-URL}/osms/v1/file/manager/complete` - 通知服务端上传完成

## 图像理解请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| imageUrl | string | ✅ | - | 图片 URL（支持 HTTP/HTTPS） |
| text | string | ❌ | "图中讲了什么" | 提示文本，引导图像理解方向 |

## 何时使用

### ✅ 适合场景
1. 需要**识别图像内容**时
2. 需要**生成图像描述**时
3. 需要**理解图像中的文字**时
4. 需要**分析图像场景和对象**时
5. 用户**明确要求描述图片**时
6. 图片在本地、需要**先上传再理解**时（使用 file_upload.py）

### ❌ 不适合场景
1. 纯文本处理任务
2. 视频内容分析（当前仅支持静态图像）
3. 需要图像编辑或生成
4. 用户要求不使用 AI 分析

## 输出示例

```bash
$ python ./scripts/image_understanding.py "https://bkimg.cdn.bcebos.com/pic/8435e5dde71190ef3289998ac61b9d16fdfa6070"

✅ .xiaoyienv 文件解析成功
✅ key "PERSONAL-API-KEY" 存在：SK-XXXXXXXXXXXXXXXX
✅ key "PERSONAL-UID" 存在：420086000107623357
✅ 请求 URL：https://hag-drcn.op.dbankcloud.com/celia-claw/v1/sse-api/skill/execute

🔍 图像理解结果
🖼️  图片: https://bkimg.cdn.bcebos.com/pic/8435e5dde71190ef3289998ac61b9d16fdfa6070
================================================================================

📝 图像描述:
图片中展示了一个以黄色为主色调的正方形图标，中央用橙色立体字体清晰地显示着"WEBP"四个大写字母。字母具有轻微的阴影和浮雕效果，使其在背景上显得突出。整体设计简洁、现代，常用于表示WebP图像格式的文件图标或标识。

================================================================================
{"caption": "图片中展示了一个以黄色为主色调的正方形图标，中央用橙色立体字体清晰地显示着"WEBP"四个大写字母。字母具有轻微的阴影和浮雕效果，使其在背景上显得突出。整体设计简洁、现代，常用于表示WebP图像格式的文件图标或标识。"}
```

## 返回格式

```json
{
  "caption": "图像的详细文本描述"
}
```

## 技术细节

### SSE 流式响应
本 API 使用 Server-Sent Events (SSE) 协议返回流式数据：

1. **开始标记**: `streamType: "start"` - 表示流开始
2. **数据内容**: `streamContent` - 每帧包含完整的累加内容
3. **结束标记**: `streamType: "end"` - 表示流结束

### 数据提取
从 SSE 响应中提取图像描述的路径：

```
abilityInfos[0].actionExecutorResult.reply.streamInfo.streamContent
```

## 注意事项

1. **图片 URL**: 必须是可公开访问的 HTTP/HTTPS URL
2. **图片格式**: 支持 JPG、PNG、WEBP 等常见格式
3. **超时时间**: 默认 120 秒，复杂图片可能需要更长时间
4. **网络要求**: 需要稳定的网络连接访问 API
5. **内容安全**: 图像内容应符合相关法律法规
6. **配额限制**: 注意 API 调用频率限制

## 错误处理

### 常见错误及解决方案

| 错误码 | 错误信息 | 解决方案 |
|--------|---------|---------|
| 401 | Permission denied | 检查 Token 是否过期 |
| 400 | Parameter is not valid | 检查图片 URL 格式 |
| timeout | Request timeout | 增加超时时间或检查网络 |
| connection error | Failed to connect | 检查网络连接 |

## 总结

当需要图像理解时：
1. ✅ 确认图片 URL 可访问（若为本地文件，先用 `file_upload.py` 上传获取 URL）
2. ✅ 根据需求设置提示文本
3. ✅ 调用小艺图像理解 API
4. ✅ 接收并解析 SSE 流式响应
5. ✅ 提取最终的图像描述

记住：图像理解可以帮助你更好地理解图片内容，但要确保图片 URL 可访问且内容合法。✅
