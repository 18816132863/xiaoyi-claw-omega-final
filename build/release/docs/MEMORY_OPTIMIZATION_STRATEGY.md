# 内存优化策略 V1.0.0

## 问题分析

当前工作空间内存占用: **5.3 GB**

### 占用分布

| 目录 | 大小 | 占比 |
|------|------|------|
| repo/lib (Python包) | 5.1 GB | **96%** |
| archive (备份) | 74 MB | 1.4% |
| skills (技能) | 34 MB | 0.6% |
| memory_context | 10 MB | 0.2% |
| 其他 | ~100 MB | 1.8% |

### Python 包占用 TOP 10

| 包 | 大小 | 必要性 |
|-----|------|--------|
| nvidia (CUDA) | 2.8 GB | ⚠️ 可选 |
| torch | 913 MB | ⚠️ 可选 |
| triton | 601 MB | ⚠️ 可选 |
| llvmlite | 159 MB | ⚠️ 可选 |
| transformers | 97 MB | ⚠️ 可选 |
| chromadb_rust | 51 MB | ⚠️ 可选 |
| kubernetes | 36 MB | ⚠️ 可选 |
| numba | 34 MB | ⚠️ 可选 |
| faiss | 27 MB | ⚠️ 可选 |
| langchain | 26 MB | ⚠️ 可选 |

---

## 策略一：精简 Python 依赖

### 原理
移除不常用的大型依赖，按需安装。

### 方案
```
保留 (核心):
- numpy, scipy, scikit-learn
- aiosqlite, requests
- cryptography, pycryptodome

移除 (大型):
- nvidia/* (2.8 GB) - CUDA 库，ARM 平台无用
- torch (913 MB) - 深度学习，按需安装
- triton (601 MB) - GPU 编译，按需安装
- numba (34 MB) - JIT 编译，按需安装
- transformers (97 MB) - NLP 模型，按需安装
```

### 预期效果
- 减少: **~4.5 GB**
- 剩余: **~800 MB**

---

## 策略二：备份压缩

### 原理
压缩旧备份，删除冗余备份。

### 方案
```
当前: 74 MB (多个备份)
优化:
- 保留最近 3 个备份
- 压缩为 xz 格式 (更高压缩率)
- 删除超过 7 天的备份
```

### 预期效果
- 减少: **~50 MB**
- 剩余: **~24 MB**

---

## 策略三：技能精简

### 原理
移除不常用技能，保留核心技能。

### 方案
```
保留 (核心技能):
- llm-memory-integration
- find-skills
- agent-chronicle
- 核心工具类技能

移除 (可选):
- 不常用技能
- 测试技能
- 示例技能
```

### 预期效果
- 减少: **~20 MB**
- 剩余: **~14 MB**

---

## 策略四：缓存清理

### 原理
清理各类缓存文件。

### 方案
```
清理:
- __pycache__ 目录
- .pyc 文件
- npm-cache
- browser 缓存
- 临时文件
```

### 预期效果
- 减少: **~50 MB**

---

## 推荐方案：组合执行

### 第一阶段：清理大型依赖 (立即)
```bash
# 移除 CUDA/NVIDIA 库 (ARM 平台无用)
rm -rf repo/lib/python3.12/site-packages/nvidia
rm -rf repo/lib/python3.12/site-packages/cuda

# 移除大型 ML 库 (按需安装)
pip uninstall torch triton numba transformers -y
```

### 第二阶段：清理缓存 (立即)
```bash
# 清理 Python 缓存
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# 清理 npm 缓存
rm -rf .openclaw/npm-cache

# 清理浏览器缓存
rm -rf .openclaw/browser
```

### 第三阶段：备份优化 (短期)
```bash
# 压缩旧备份
cd archive/backups
for f in *.tar.gz; do
    xz -9 "$f" && rm "$f"
done

# 删除超过 7 天的备份
find . -name "*.tar.xz" -mtime +7 -delete
```

---

## 预期效果

| 阶段 | 减少量 | 剩余 |
|------|--------|------|
| 当前 | - | 5.3 GB |
| 第一阶段 | 4.5 GB | 800 MB |
| 第二阶段 | 50 MB | 750 MB |
| 第三阶段 | 50 MB | 700 MB |

**最终目标: < 1 GB**

---

## 注意事项

1. **CUDA 库**: ARM 平台无法使用，安全删除
2. **ML 库**: 按需安装，不影响核心功能
3. **备份**: 保留最近 3 个即可
4. **缓存**: 可随时重建

---

## 风险评估

| 操作 | 风险 | 缓解措施 |
|------|------|----------|
| 删除 CUDA | 低 | ARM 平台无用 |
| 删除 torch | 中 | 按需重装 |
| 删除备份 | 低 | 保留最近 3 个 |
| 清理缓存 | 无 | 可重建 |
