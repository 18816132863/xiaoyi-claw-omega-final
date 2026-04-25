---
name: xiaoyi-image-translation
description: 使用图片翻译API进行图像内容翻译，获取翻译后的图片和文本结果
---

# 图片翻译 Skill

## 简介
通过图片翻译 API 对图像中的文字进行智能识别和翻译，返回翻译后的图片及文本结果。支持JPG/PNG/BMP/WEBP格式，可选择输出Base64或下载链接。

## 特性
- ✅ **双输入支持** - 同时支持Base64和公网URL输入
- ✅ **多语言翻译** - 支持全球主流语言互译
- ✅ **输出灵活** - 可选择Base64或下载链接格式
- ✅ **文本提取** - 自动提取图像中的OCR文本
- ✅ **错误反馈** - 详细错误码和描述信息
- ✅ **结果完整** - 同时返回翻译图片和文本结果

## 文件结构
```
xiaoyi-image-translation/
├── SKILL.md                # 使用说明（本文档）
├── scripts                 # 程序文件夹
│ ├── image_translation.py # 主程序（图像翻译）
├── _meta.json              # Skill 元数据
└── package.json            # 项目配置
```

## 使用方法

### 图像翻译（直接使用Base64或URL）

```bash
# 进入 skill 目录
cd /home/sandbox/.openclaw/workspace/skills/xiaoyi-image-translation

# 基本使用（Base64输入）
python ./scripts/image_translation.py --imageBase64 "base64字符串" --targetLanguage "zh"

# 使用公网URL输入
python ./scripts/image_translation.py --imageUrl "https://example.com/image.jpg" --targetLanguage "en"

# 指定源语言和输出类型
python ./scripts/image_translation.py --imageBase64 "base64字符串" --sourceLanguage "es" --targetLanguage "zh" --outputType "imageUrl"
```

### Python代码调用示例

```python
from scripts.image_translation import translate_image

# Base64输入示例
result = translate_image(
    imageBase64="base64字符串",
    targetLanguage="zh"
)
print(result)

# URL输入示例
result = translate_image(
    imageUrl="https://example.com/image.jpg",
    targetLanguage="en"
)
print(result)
```

## API 信息

| 项目         | 值                                                                         |
|------------|---------------------------------------------------------------------------|
| 图片翻译地址 | 从 `.xiaoyienv` 读取SERVICE_URL ，拼接上`/celia-claw/v1/http-api/skill/execute`，'.xiaoyienv文件默认存在，无需用户自行创建输入' |
| 鉴权方式 | 从 `.xiaoyienv` 读取 API Key 和 UID，'.xiaoyienv文件默认存在，无需用户自行创建输入' |
| 响应格式       | JSON                                                                      |

### 配置说明

在 `/home/sandbox/.openclaw/.xiaoyienv` 文件中配置以下参数：

```bash
PERSONAL-API-KEY=你的API密钥
PERSONAL-UID=你的用户ID
SERVICE_URL=请求地址的域名
```

**注意**：
- 图像理解 API 和文件上传服务地址均已固化在代码中，无需配置
- 只需配置 `PERSONAL-API-KEY` 和 `PERSONAL-UID` 即可

## 输入参数

| 参数 | 类型 | 必填 | 默认值 | 说明                                  |
|------|------|------|--------|-------------------------------------|
| imageInfo | ImageInfo | ✅ | - | 原图片信息（必选imageId或imageUrl/imageBase64） |
| sourceLanguage | String | ❌ | auto | 原语言（不传则自动识别），支持的语种见语种列表   |
| targetLanguage | String | ✅ | - | 目标语言（必填），支持的语种见语种列表     |
| extra | JSON String | ❌ | - | 预留字段                                |
| outputType | String | ❌ | base64 | 输出类型（base64/imageUrl）               |

### ImageInfo 参数
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| imageId | String | Y | 图片唯一ID（与imageUrl/imageBase64二选一） |
| imageUrl | String | N | 公网图片地址（与imageBase64二选一） |
| imageBase64 | String | Y | 图片Base64（<=4M）（与imageUrl二选一） |

### 支持语言及编码对照表
| 语言         | 语言编码   | 说明 |
|------------|--------|------|
| 中文（简体）     | zh-CHS | 默认支持 |
| 英文         | en     | 默认支持 |
| 日文         | ja     | 默认支持 |
| 韩文         | ko     | 默认支持 |
| 俄语         | ru     | 默认支持 |
| 西班牙语       | es     | 默认支持 |
| 法语         | fr     | 默认支持 |
| 德语         | de     | 默认支持 |
| 意大利语       | it     | 默认支持 |
| 葡萄牙语       | pt     | 默认支持 |
| 菲律宾语       | tl     | 默认支持 |
| 泰语         | th     | 默认支持 |
| 土耳其语       | tr     | 默认支持 |
| 阿拉伯语       | ar     | 默认支持 |
| 波兰语        | pl     | 默认支持 |
| 马来语        | ms     | 默认支持 |
| 印尼语（印度尼西亚） | id     | 默认支持 |
| 希腊语（现代）    | el     | 默认支持 |
| 捷克语（捷克共和国） | cs     |
| 荷兰语        | nl     |
| 越南语        | vi     |

## 输出参数

| 字段 | 类型 | 说明 |
|------|------|------|
| errorCode | int | 错误码（0代表成功） |
| errorMsg | String | 错误信息描述 |
| imageResult | ImageResult | 图片信息 |
| textResult | List<TextResult> | 文本结果 |
| sourceLanguage | String | 源语言（auto表示自动识别） |
| targetLanguage | String | 目标语言 |

### ImageResult 结构
| 字段 | 类型 | 说明 |
|------|------|------|
| sourceImageId | String | 原图片ID |
| imageBase64 | String | 结果Base64（outputType=base64时） |
| imageUrl | String | 下载链接（outputType=imageUrl时） |

### TextResult 结构
| 字段 | 类型 | 说明 |
|------|------|------|
| ocrText | String | OCR识别结果 |
| translateText | String | 翻译结果 |

## 何时使用

### ✅ 适合场景
1. 需要**翻译图片中的文字**时（如多语言文档处理）
2. 需要**OCR识别+翻译一体化**时（自动提取并翻译图像文字）
3. 用户**明确要求翻译图片内容**时（如双语标识制作）
4. 需要**获取翻译后的图片和文本结果**时（支持Base64格式输出）
5. 图片在本地，需要**转换为Base64格式处理**时（当前仅支持Base64输入）

### ❌ 不适合场景
1. **纯文本翻译任务**（无需图像处理）
2. **视频内容翻译**（当前仅支持静态图像）
3. **图像生成或编辑需求**（API不处理图像生成）
4. **用户要求不使用AI翻译**（需人工翻译场景）

## 输出示例

```bash
$ python ./scripts/image_translation.py --imageBase64 "base64字符串" --targetLanguage "zh"

✅ .xiaoyienv 文件解析成功
✅ key "PERSONAL-API-KEY" 存在：SK-XXXXXXXXXXXXXXXX
✅ key "PERSONAL-UID" 存在：420086000107623357
✅ 请求 URL：https://celia-claw-drcn.ai.dbankcloud.cn/celia-claw/v1/rest-api/skill/execute

🔍 翻译结果
================================================================================

📝 返回结果:
{
  "errorCode": 0,
  "errorMsg": "Success",
  "sourceLanguage": "en",
  "targetLanguage": "zh",
  "imageResult": {
    "sourceImageId": "IMG123456",
    "imageBase64": "translated_base64_string"
  },
  
  "textResult": [
    {
      "ocrText": "Hello World",
      "translateText": "你好，世界"
    }
  ]
}
```

## 返回格式

```json
{
  "errorCode": 0,
  "errorMsg": "Success",
  "sourceLanguage": "en",
  "targetLanguage": "zh",
  "imageResult": {
    "sourceImageId": "IMG123456",
    "imageBase64": "translated_base64_string"
  },
  "textResult": [
    {
      "ocrText": "Hello World",
      "translateText": "你好，世界",
      "sourceLanguage": "en",
      "targetLanguage": "zh"
    }
  ]
}
```

## 注意事项

1. **输入限制**：
   - Base64输入大小不超过4M（原图3M）
   - URL必须可公开访问
   - 支持格式：JPG/PNG/BMP/WEBP

2. **输出限制**：
   - Base64输出适用于小文件
   - imageUrl输出需注意链接有效期

3. **文本场景**：
   - 无文字图片返回空textResult集合
   - 翻译结果保留原文本位置信息

## 错误码说明

| 错误码 | 描述                       | 解决方案            |
|--------|--------------------------|-----------------|
| 0 | 成功                       | 无需处理            |
| 401 | 鉴权失败                     | 联系小艺处理          |
| 503 | 限流                       | 稍后重试            |
| 1001 | 系统内部错误                   | 联系小艺处理          |
| 4008 | 图片拒识（图片中的语种不满足21语种，不给识别） | 更换图片输入          |
| 4009 | 图片命中风控                   | 更换图片输入       |

## 总结

当需要图像翻译时：
1. ✅ 准备图片（Base64或URL）
2. ✅ 设置目标语言
3. ✅ 调用图片翻译API
4. ✅ 解析返回结果
5. ✅ 处理可能的错误码

记住：图片翻译可同时获取翻译后的图片和文本，请把翻译后的图片以markdown形式发送给用户，但需注意输入格式和大小限制。✅