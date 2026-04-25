# 投机解码模块

使用小型草稿模型 + 大型目标模型实现 LLM 推理加速。

## 原理

```
┌─────────────┐     ┌─────────────┐
│  草稿模型    │ --> │  目标模型    │
│  (小型快速)  │     │  (大型高质量) │
└─────────────┘     └─────────────┘
       │                   │
       v                   v
  生成 K 个候选       并行验证 K 个
       │                   │
       └───────┬───────────┘
               v
        接受/拒绝/部分接受
```

## 加速效果

| 指标 | 传统解码 | 投机解码 |
|------|----------|----------|
| 推理速度 | 1x | 2-3x |
| 输出质量 | 高 | 高 (相同) |
| API 调用次数 | N | N/K |
| 成本 | 高 | 中 |

## 使用方式

### 基础用法

```python
from execution.speculative_decoding import speculative_decode

result = await speculative_decode(
    prompt="请介绍一下人工智能",
    max_tokens=100,
    draft_model="deepseek-ai/deepseek-v4-flash",
    target_model="deepseek-ai/deepseek-v4-pro"
)

print(f"生成内容: {''.join(result.tokens)}")
print(f"加速比: {result.speedup:.2f}x")
```

### 高级用法

```python
from execution.speculative_decoding import (
    SpeculativeDecodingConfig,
    SpeculativeDecoder
)

# 配置
config = SpeculativeDecodingConfig(
    draft_model_name="deepseek-ai/deepseek-v4-flash",
    target_model_name="deepseek-ai/deepseek-v4-pro",
    max_draft_tokens=4,
    max_iterations=10,
    verbose=True
)

# 创建解码器
decoder = config.create_decoder()

# 执行解码
result = await decoder.decode(
    prompt="请介绍一下人工智能",
    max_tokens=100
)

# 获取统计信息
stats = decoder.get_stats()
print(f"接受率: {stats['accept_rate']}")
```

### NVIDIA API 集成

```python
from execution.speculative_decoding import (
    NVIDIAConfig,
    NVIDIADraftModel,
    NVIDIATargetModel,
    SpeculativeDecoder
)

# 配置 NVIDIA API
config = NVIDIAConfig(
    api_key="nvapi-xxx",
    base_url="https://integrate.api.nvidia.com/v1"
)

# 创建模型
draft_model = NVIDIADraftModel(
    model_name="deepseek-ai/deepseek-v4-flash",
    max_draft_tokens=4
)

target_model = NVIDIATargetModel(
    model_name="deepseek-ai/deepseek-v4-pro"
)

# 创建解码器
decoder = SpeculativeDecoder(
    draft_model=draft_model,
    target_model=target_model
)
```

## 模块结构

```
execution/speculative_decoding/
├── __init__.py              # 模块入口
├── speculative_decoder.py   # 核心解码器
└── nvidia_adapter.py        # NVIDIA API 适配器
```

## 核心类

### SpeculativeDecoder

投机解码器，协调草稿模型和目标模型。

**参数**:
- `draft_model`: 草稿模型实例
- `target_model`: 目标模型实例
- `max_iterations`: 最大迭代次数
- `verbose`: 是否输出详细信息

**方法**:
- `decode(prompt, max_tokens)`: 执行投机解码
- `get_stats()`: 获取统计信息

### DraftModel

草稿模型，快速生成候选 token。

**参数**:
- `model_name`: 模型名称
- `max_draft_tokens`: 最大草稿 token 数
- `temperature`: 温度参数

**方法**:
- `generate_draft(prompt, context, num_tokens)`: 生成草稿 token

### TargetModel

目标模型，验证草稿 token。

**参数**:
- `model_name`: 模型名称
- `temperature`: 温度参数

**方法**:
- `verify_tokens(prompt, draft_tokens, context)`: 验证草稿 token
- `generate_next(prompt, context)`: 生成下一个 token

## 性能优化建议

1. **草稿模型选择**
   - 选择速度快的小型模型
   - 与目标模型有相似的 token 分布
   - 推荐: DeepSeek-V4-Flash

2. **目标模型选择**
   - 选择高质量的大型模型
   - 推荐: DeepSeek-V4-Pro

3. **参数调优**
   - `max_draft_tokens`: 4-8 (平衡速度和接受率)
   - `max_iterations`: 根据生成长度调整
   - `temperature`: 0.0 (确定性输出)

## 版本

- v1.0.0 - 初始版本
