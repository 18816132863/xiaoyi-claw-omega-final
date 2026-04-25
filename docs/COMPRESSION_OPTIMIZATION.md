# 压缩包优化策略 V2.0.0

> 目标：从 22M 减少到 15M 以下

---

## 一、当前压缩包分析

**总大小**: 22M

### 各部分占比

| 目录 | 文件数 | 估计大小 | 占比 |
|------|--------|----------|------|
| skills/ | 4161 | ~51M | 50% |
| memory_context/ | 186 | ~9M | 9% |
| repo/ | 930 | ~12M | 12% |
| infrastructure/ | 323 | ~3M | 3% |
| 其他 | - | ~27M | 26% |

---

## 二、优化策略

### 策略 1：移除技能中的大型二进制/模型文件（预计减少 2M）

| 文件 | 大小 | 操作 |
|------|------|------|
| `alphaear-predictor/models/*.pt` | 1.3M | 移除，按需下载 |
| `canvas-design/fonts/*.ttf` | ~2M | 精简，只保留必要字体 |

### 策略 2：移除重复的 XSD Schema 文件（预计减少 0.7M）

| 文件 | 大小 | 操作 |
|------|------|------|
| `xiaoyi-xlsx/schemas/*.xsd` | 241K | 保留 |
| `pptx/schemas/*.xsd` | 237K | 移除（重复） |
| `docx/schemas/*.xsd` | 237K | 移除（重复） |
| `anthropics-skills-pptx/schemas/*.xsd` | 237K | 移除（重复） |

### 策略 3：精简 memory_context 索引（预计减少 4M）

| 文件 | 大小 | 操作 |
|------|------|------|
| `fts_index.json.gz` | 4.1M | 压缩或移除旧数据 |
| `keyword_index.json.gz` | 3.6M | 压缩或移除旧数据 |
| `vector_index.json.gz` | 975K | 保留 |

### 策略 4：精简 repo/lib（预计减少 4M）

| 内容 | 大小 | 操作 |
|------|------|------|
| `supervisor/tests/` | ~500K | 移除测试文件 |
| `docx/templates/` | ~860K | 精简模板 |
| `pypdf/_codecs/` | ~550K | 精简编码 |
| `greenlet/tests/` | ~440K | 移除测试文件 |

### 策略 5：使用更高压缩率（预计减少 2M）

| 方法 | 说明 |
|------|------|
| 使用 `xz` 压缩 | 比 gzip 压缩率高 30% |
| 排除更多缓存文件 | `__pycache__`, `.pyc` |

---

## 三、执行计划

### 第一步：移除重复文件
```bash
rm -rf skills/pptx/scripts/office/schemas
rm -rf skills/docx/scripts/office/schemas
rm -rf skills/anthropics-skills-pptx/scripts/office/schemas
```

### 第二步：移除模型文件
```bash
rm -rf skills/alphaear-predictor/scripts/predictor/exports/models
```

### 第三步：精简 repo/lib
```bash
rm -rf repo/lib/python3.12/site-packages/*/tests
rm -rf repo/lib/python3.12/site-packages/supervisor/tests
```

### 第四步：精简记忆索引
```bash
# 只保留最近 30 天的索引数据
```

### 第五步：使用 xz 压缩
```bash
tar -cJf workspace.tar.xz workspace/
```

---

## 四、预期效果

| 阶段 | 大小 | 减少 |
|------|------|------|
| 当前 | 22M | - |
| 移除重复 | 21M | 1M |
| 移除模型 | 20M | 1M |
| 精简 repo | 16M | 4M |
| xz 压缩 | **~12M** | 4M |

---

**目标**: 压缩包 **12-15M**
