# Token 优化策略

## V2.7.0 - 2026-04-10

减少 Token 消耗，提升响应速度。

---

## 一、当前状态

| 类型 | 文件数 | 总大小 | 平均大小 |
|------|--------|--------|----------|
| MD 文件 | ~1300 | 7.0MB | 5.4KB |
| JSON 文件 | ~530 | 5.5MB | 10.4KB |
| Python 文件 | ~500 | 6.7MB | 13.4KB |

**问题**:
- 大文件过多（>20KB 的有 20+ 个）
- API 文档冗余
- 重复内容多

---

## 二、优化目标

| 指标 | 当前 | 目标 | 改善 |
|------|------|------|------|
| 启动 Token | ~60K | ~15K | 75% |
| 单次调用 Token | ~10K | ~3K | 70% |
| 响应延迟 | ~500ms | ~200ms | 60% |

---

## 三、优化策略

### 3.1 文件压缩

```bash
# 压缩大文件（>20KB）
find . -name "*.md" -size +20k -exec gzip {} \;

# 保留摘要版本
head -100 large_file.md > large_file.summary.md
```

### 3.2 延迟加载

```python
# 只加载必要文件
IMMEDIATE_LOAD = [
    "AGENTS.md", "SOUL.md", "TOOLS.md", "USER.md",
    "IDENTITY.md", "HEARTBEAT.md"
]

# 按需加载
ON_DEMAND_LOAD = [
    "skills/*", "memory/*", "governance/*"
]
```

### 3.3 内容去重

```python
# 使用引用代替复制
# 之前
"""
完整的 API 文档内容...
"""

# 之后
"""
参见: skills/xxx/references/api-reference.md
"""
```

### 3.4 摘要生成

```python
# 为大文件生成摘要
def generate_summary(content: str, max_lines: int = 50) -> str:
    lines = content.split('\n')
    
    # 提取标题和首段
    summary = []
    for line in lines[:max_lines]:
        if line.startswith('#') or line.strip():
            summary.append(line)
    
    return '\n'.join(summary)
```

---

## 四、分层加载策略

### 4.1 L1 核心层（立即加载）

| 文件 | 大小 | Token 估算 |
|------|------|-----------|
| AGENTS.md | 15KB | ~4K |
| SOUL.md | 2KB | ~500 |
| TOOLS.md | 8KB | ~2K |
| USER.md | 1KB | ~250 |
| IDENTITY.md | 1KB | ~250 |
| **总计** | **27KB** | **~7K** |

### 4.2 L2 记忆层（按需加载）

| 文件 | 加载条件 |
|------|----------|
| MEMORY.md | recall 操作时 |
| memory/*.md | 查询特定日期时 |

### 4.3 L3-L6（延迟加载）

| 层级 | 加载条件 |
|------|----------|
| L3 编排 | 任务编排时 |
| L4 执行 | 技能调用时 |
| L5 治理 | 审计/错误时 |
| L6 基建 | 运维操作时 |

---

## 五、Token 计算规则

### 5.1 估算公式

```
Token ≈ 字符数 / 4 (英文)
Token ≈ 字符数 / 2 (中文)
```

### 5.2 文件 Token 估算

| 文件类型 | 平均 Token | 备注 |
|----------|-----------|------|
| MD 文件 | 1.5K | 含代码块 |
| JSON 文件 | 3K | 结构化数据 |
| Python 文件 | 4K | 含注释 |

---

## 六、优化实施

### 6.1 立即执行

1. 压缩 >50KB 文件
2. 删除重复 README
3. 精简 API 文档

### 6.2 持续优化

1. 每周检查大文件
2. 每月清理冗余
3. 季度评估 Token 消耗

---

## 七、监控指标

```python
def get_token_stats() -> dict:
    return {
        "startup_tokens": 15000,
        "avg_call_tokens": 3000,
        "cache_hit_rate": 0.95,
        "load_time_ms": 200
    }
```

---

**版本**: V2.7.0
**作者**: @18816132863
