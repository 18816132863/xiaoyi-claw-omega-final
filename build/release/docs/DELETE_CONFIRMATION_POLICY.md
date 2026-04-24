# 删除确认机制 V1.0.0

## 核心原则

**所有删除操作必须经过用户确认！**

## 机制说明

### 1. 删除流程

```
请求删除 → 创建待确认请求 → 用户确认 → 执行删除（移至回收站）
                ↓
            用户拒绝 → 取消删除
```

### 2. 受保护文件

以下文件禁止删除：
- `core/ARCHITECTURE.md` - 架构文档
- `core/RULE_REGISTRY.json` - 规则注册表
- `core/SOUL.md` - 身份定义
- `core/USER.md` - 用户信息
- `core/AGENTS.md` - 工作空间规则
- `core/TOOLS.md` - 工具规则
- `core/IDENTITY.md` - 身份标识
- `MEMORY.md` - 长期记忆

### 3. 回收站机制

- 删除的文件移动到 `archive/trash/`
- 支持从回收站恢复
- 自动清理超过 7 天的回收站文件

### 4. 审计日志

所有删除操作记录到 `reports/ops/delete_log.json`

## 使用方式

### 请求删除
```bash
python scripts/delete_manager.py --request "path/to/file" --reason "原因"
```

### 确认删除
```bash
python scripts/delete_manager.py --confirm <request_id>
```

### 拒绝删除
```bash
python scripts/delete_manager.py --reject <request_id>
```

### 查看待确认请求
```bash
python scripts/delete_manager.py --list
```

### 从回收站恢复
```bash
python scripts/delete_manager.py --restore "path/to/file"
```

### 清空回收站
```bash
# 清空超过 7 天的文件
python scripts/delete_manager.py --empty-trash 7
```

## 禁止操作

**禁止直接使用以下命令：**
- `rm` 命令
- `os.remove()` 
- `shutil.rmtree()` (不经过删除管理器)
- `Path.unlink()`

**正确做法：**
```python
# 错误 ❌
os.remove("file.txt")

# 正确 ✅
from scripts.delete_manager import DeleteManager
manager = DeleteManager()
result = manager.request_delete("file.txt", "清理临时文件")
# 等待用户确认...
manager.confirm_delete(result["request_id"])
```

## 文件位置

| 文件 | 说明 |
|------|------|
| `scripts/delete_manager.py` | 删除管理器 |
| `archive/trash/` | 回收站目录 |
| `reports/ops/delete_log.json` | 删除日志 |
| `reports/ops/pending_deletes.json` | 待确认请求 |
