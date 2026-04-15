# 记忆集成策略 - V1.0.0

## 记忆类型

| 类型 | 存储 | 生命周期 | 用途 |
|------|------|----------|------|
| 工作记忆 | 内存 | 会话内 | 当前对话上下文 |
| 短期记忆 | memory/*.md | 7天 | 近期事件 |
| 长期记忆 | MEMORY.md | 永久 | 重要决策和偏好 |
| 向量记忆 | 向量存储 | 永久 | 语义检索 |

## 记忆流程

```
用户输入
    ↓
工作记忆 (当前上下文)
    ↓
短期记忆 (日记文件)
    ↓
长期记忆 (MEMORY.md)
    ↓
向量记忆 (语义索引)
```

## 写入策略

### 1. 自动写入
- 每次会话结束写入日记
- 重要决策自动更新 MEMORY.md
- 关键信息自动索引

### 2. 手动写入
- 用户明确要求保存
- 标记为重要的内容

## 读取策略

### 1. 优先级
1. 工作记忆 (当前会话)
2. 短期记忆 (最近7天)
3. 长期记忆 (MEMORY.md)
4. 向量检索 (语义相关)

### 2. 检索顺序
```python
def retrieve_memory(query: str) -> List[Memory]:
    # 1. 检查工作记忆
    if query in working_memory:
        return working_memory[query]
    
    # 2. 搜索短期记忆
    recent = search_recent_memories(query, days=7)
    
    # 3. 检查长期记忆
    long_term = search_memory_md(query)
    
    # 4. 向量检索
    semantic = vector_search(query)
    
    return merge_and_rank([recent, long_term, semantic])
```

## 记忆更新

### 触发条件
- 用户明确更正
- 新信息与旧信息冲突
- 定期清理过期信息

### 更新规则
```python
def update_memory(key: str, new_value: Any):
    old_value = get_memory(key)
    
    if old_value != new_value:
        # 记录变更
        log_change(key, old_value, new_value)
        
        # 更新值
        set_memory(key, new_value)
        
        # 重新索引
        reindex_memory(key)
```

## 隐私保护

- 敏感信息不写入日记
- 用户可请求删除记忆
- 支持记忆导出和清除
