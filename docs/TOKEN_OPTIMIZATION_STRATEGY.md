# Token 优化策略 V1.0.0

## 问题分析

当前 Token 消耗估算: **~1300 万 tokens**
目标: **< 10,000 tokens** (注入限制)

主要消耗来源:
1. **技能目录 (22.71 MB)** - 3050 文件，最大消耗
2. **记忆层 (9.43 MB)** - 169 文件
3. **基础设施 (2.06 MB)** - 286 文件

---

## 策略一：懒加载 + 按需注入

### 原理
只注入当前任务需要的文件，其他文件按需加载。

### 方案
```
注入层级:
├── L1 Core (必须) - ~3000 tokens
│   ├── AGENTS.md
│   ├── SOUL.md
│   ├── USER.md
│   ├── TOOLS.md
│   └── MEMORY.md
│
├── L2 Memory (按需) - ~500 tokens
│   └── memory/YYYY-MM-DD.md (当天)
│
├── L3-L6 (不注入) - 按需读取
│
└── Skills (不注入) - 按需发现
    └── find-skills 技能发现
```

### 预期效果
- 注入 Token: **~3500 tokens**
- 减少: **99.7%**

---

## 策略二：压缩 + 摘要

### 原理
对长文件进行压缩，只保留关键信息。

### 方案
```
压缩规则:
1. JSON 文件 -> 只保留 schema 和关键字段
2. Markdown 文件 -> 只保留标题和第一段
3. 代码文件 -> 只保留函数签名和注释
4. 报告文件 -> 只保留摘要和状态
```

### 实现示例
```python
def compress_json(data, max_depth=2):
    """压缩 JSON，只保留结构"""
    if max_depth == 0:
        return "..."
    if isinstance(data, dict):
        return {k: compress_json(v, max_depth-1) for k, v in list(data.items())[:10]}
    if isinstance(data, list):
        return [compress_json(data[0], max_depth-1)] if data else []
    return data
```

### 预期效果
- 注入 Token: **~5000 tokens**
- 减少: **99.6%**

---

## 策略三：索引 + 引用

### 原理
只注入索引文件，实际内容通过引用获取。

### 方案
```
注入内容:
├── fusion_index.json (索引)
├── skill_registry.json (摘要版)
└── MEMORY.md (当天)

引用方式:
- 技能详情: 通过 find-skills 查询
- 配置详情: 通过 memory_search 查询
- 报告详情: 通过 read 按需读取
```

### 预期效果
- 注入 Token: **~2000 tokens**
- 减少: **99.98%**

---

## 推荐方案：组合策略

### 实施步骤

#### 第一阶段：精简注入 (立即)
1. 只注入 L1 核心文件
2. 技能目录改为索引注入
3. 报告目录改为摘要注入

#### 第二阶段：懒加载 (短期)
1. 实现按需加载机制
2. 添加缓存层
3. 优化查询路径

#### 第三阶段：智能压缩 (中期)
1. 实现自动摘要
2. 实现结构压缩
3. 实现增量更新

---

## 具体实施

### 1. 创建精简注入配置

```json
{
  "injection": {
    "mode": "minimal",
    "files": [
      "AGENTS.md",
      "SOUL.md", 
      "USER.md",
      "TOOLS.md",
      "MEMORY.md",
      "memory/{today}.md"
    ],
    "indexes": [
      "infrastructure/inventory/fusion_index.json",
      "infrastructure/inventory/skill_registry_summary.json"
    ],
    "exclude": [
      "skills/**",
      "reports/**",
      "docs/**",
      "tests/**",
      "repo/**"
    ]
  }
}
```

### 2. 创建技能注册表摘要

```python
# 从 skill_registry.json 生成摘要
summary = {
    "total": 275,
    "categories": {...},
    "top_skills": ["llm-memory-integration", "find-skills", ...]
}
```

### 3. 修改注入逻辑

```python
def get_injection_files():
    """获取注入文件列表"""
    files = [
        "AGENTS.md",
        "SOUL.md",
        "USER.md", 
        "TOOLS.md",
        "MEMORY.md",
    ]
    
    # 添加今天的日记
    today = datetime.now().strftime("%Y-%m-%d")
    diary = f"memory/{today}.md"
    if Path(diary).exists():
        files.append(diary)
    
    return files
```

---

## 预期效果

| 阶段 | 注入 Token | 减少比例 |
|------|-----------|----------|
| 当前 | ~1300万 | - |
| 第一阶段 | ~5000 | 99.96% |
| 第二阶段 | ~3000 | 99.98% |
| 第三阶段 | ~2000 | 99.98% |

---

## 注意事项

1. **功能完整性**: 确保按需加载不影响功能
2. **性能影响**: 懒加载可能增加响应时间
3. **缓存策略**: 合理设置缓存 TTL
4. **回退机制**: 保留完整注入选项
