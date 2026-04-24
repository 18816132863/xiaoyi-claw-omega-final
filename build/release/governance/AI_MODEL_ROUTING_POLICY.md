# AI 生成模型统一调度策略

## 概述

本文档定义了多个 AI 生成模型（即梦、Wan、PixVerse、腾讯混元）的无冲突使用策略。

## 1. 环境变量隔离

所有 API Key 存储在 `~/.openclaw/.xiaoyienv` 文件中，按模型隔离：

```bash
# 即梦AI (小艺内置)
PERSONAL-API-KEY=xxx
PERSONAL-UID=xxx
SERVICE_URL=xxx

# 阿里云 Wan 万相
DASHSCOPE_API_KEY=sk-xxx

# 爱诗科技 PixVerse
PIXVERSE_API_KEY=xxx
PIXVERSE_BASE_URL=https://api.pixverse.ai

# 腾讯云混元
TENCENT_SECRET_ID=xxx
TENCENT_SECRET_KEY=xxx
```

## 2. 技能路由规则

### 2.1 按任务类型路由

| 任务类型 | 首选模型 | 备选模型 | 原因 |
|----------|----------|----------|------|
| 文生图 | 即梦AI | 腾讯混元 | 即梦中文优化，混元风格多样 |
| 图生图 | 即梦AI | Wan | 即梦主体一致性强 |
| 多图融合 | 即梦AI | Wan | 即梦专为此设计 |
| 图像编辑 | 腾讯混元 | Wan | 混元编辑能力强 |
| 图像超分 | 腾讯混元 | - | 混元专有功能 |
| 文生视频 | Wan | PixVerse | Wan 质量高，PixVerse 备选 |
| 图生视频 | Wan | PixVerse | Wan 效果好 |
| 参考视频生成 | Wan | - | Wan 专有功能 |

### 2.2 路由优先级

```
用户请求 → 任务分类 → 模型选择 → API 调用 → 结果返回
                ↓
         检查 API Key 是否配置
                ↓
         未配置 → 提示用户配置
         已配置 → 执行调用
```

## 3. 冲突避免机制

### 3.1 环境变量命名空间

每个模型使用独立的前缀，避免变量名冲突：

- `PERSONAL-*` → 即梦AI (小艺内置)
- `DASHSCOPE_*` → 阿里云 Wan
- `PIXVERSE_*` → 爱诗科技 PixVerse
- `TENCENT_*` → 腾讯云混元

### 3.2 输出目录隔离

每个模型的输出保存到独立目录：

```
~/.openclaw/workspace/
├── generated-images/          # 即梦、混元图像
│   ├── seedream_*.jpg
│   └── hunyuan_*.png
├── generated-videos/          # Wan、PixVerse 视频
│   ├── wan_*.mp4
│   └── pixverse_*.mp4
└── wan-images/                # Wan 图像
    └── wan_*.png
```

### 3.3 脚本命名空间

每个模型使用独立脚本，避免函数名冲突：

- `generate_seedream.py` → 即梦AI
- `wan-magic.py` → Wan 万相
- `pixverse_generate.py` → PixVerse
- `hunyuan_generate.py` → 腾讯混元

## 4. 降级策略

### 4.1 API 不可用时的降级

```
首选模型 API 不可用
    ↓
检查备选模型 API 是否配置
    ↓
已配置 → 使用备选模型
未配置 → 提示用户配置任一模型
```

### 4.2 示例：文生图降级

```python
def text2image(prompt):
    # 首选：即梦AI
    if has_seedream_api():
        return seedream_text2image(prompt)
    
    # 备选：腾讯混元
    if has_hunyuan_api():
        return hunyuan_text2image(prompt)
    
    # 都不可用
    return "请配置即梦AI或腾讯混元API"
```

## 5. 使用建议

### 5.1 配置优先级

1. **即梦AI** - 小艺内置，无需额外申请，优先配置
2. **Wan 万相** - 视频生成首选，阿里云账号即可申请
3. **腾讯混元** - 图像编辑/超分，腾讯云账号申请
4. **PixVerse** - 视频备选，独立申请

### 5.2 成本优化

| 模型 | 成本 | 建议 |
|------|------|------|
| 即梦AI | 小艺内置 | 日常使用首选 |
| Wan | 按量计费 | 高质量视频场景 |
| 腾讯混元 | 按量计费 | 编辑/超分场景 |
| PixVerse | 按量计费 | Wan 不可用时备选 |

## 6. 快速配置指南

### 6.1 即梦AI (已内置)

```bash
# 小艺环境自动配置，无需手动设置
```

### 6.2 阿里云 Wan

```bash
# 1. 访问 https://dashscope.console.aliyun.com/
# 2. 开通服务，获取 API Key
# 3. 添加到 ~/.openclaw/.xiaoyienv
echo "DASHSCOPE_API_KEY=sk-xxx" >> ~/.openclaw/.xiaoyienv
```

### 6.3 腾讯云混元

```bash
# 1. 访问 https://console.cloud.tencent.com/cam/capi
# 2. 创建密钥
# 3. 添加到 ~/.openclaw/.xiaoyienv
echo "TENCENT_SECRET_ID=xxx" >> ~/.openclaw/.xiaoyienv
echo "TENCENT_SECRET_KEY=xxx" >> ~/.openclaw/.xiaoyienv
```

### 6.4 PixVerse

```bash
# 1. 访问 https://pixverse.ai
# 2. 注册获取 API Key
# 3. 添加到 ~/.openclaw/.xiaoyienv
echo "PIXVERSE_API_KEY=xxx" >> ~/.openclaw/.xiaoyienv
```

## 7. 验证配置

```bash
# 检查所有 API 配置状态
python3 scripts/check_ai_apis.py
```

---

**版本**: V1.0.0
**更新时间**: 2026-04-13
