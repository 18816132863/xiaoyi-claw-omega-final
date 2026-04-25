# 权限分离架构设计

## 📋 概述

本技能采用权限分离架构，将高风险操作与核心功能隔离，确保安全性。

## 🏗️ 架构设计

### 1. 进程分离

```
┌─────────────────────────────────────────────────────────┐
│                    主进程（普通用户权限）                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ 向量搜索    │  │ 记忆管理    │  │ LLM 集成    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │
                          │ 需要时调用
                          ▼
┌─────────────────────────────────────────────────────────┐
│              高风险进程（需要用户授权）                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ NUMA 优化   │  │ IRQ 隔离    │  │ 大页内存    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│  ┌─────────────┐                                       │
│  │ 原生扩展    │                                       │
│  └─────────────┘                                       │
└─────────────────────────────────────────────────────────┘
```

### 2. 权限级别

| 级别 | 权限 | 功能 | 默认状态 |
|------|------|------|----------|
| **Level 0** | 普通用户 | 向量搜索、记忆管理、LLM 集成 | ✅ 启用 |
| **Level 1** | 文件系统 | 读写 ~/.openclaw | ✅ 启用 |
| **Level 2** | 网络访问 | 调用 LLM/Embedding API | ✅ 启用 |
| **Level 3** | 原生扩展 | 加载 vec0.so | ❌ 禁用 |
| **Level 4** | 系统命令 | NUMA、IRQ、大页内存 | ❌ 禁用 |

### 3. 权限检查流程

```python
def check_permission(level: int, operation: str) -> bool:
    """检查权限"""
    # 1. 检查配置文件
    if not is_enabled(level):
        return False
    
    # 2. 检查用户授权
    if requires_confirmation(level):
        if not user_confirmed(operation):
            return False
    
    # 3. 记录审计日志
    log_audit(level, operation, granted=True)
    
    return True
```

## 🔒 安全措施

### 1. 默认禁用高风险功能

```json
{
  "permissions": {
    "level_0": true,   // 普通用户权限
    "level_1": true,   // 文件系统访问
    "level_2": true,   // 网络访问
    "level_3": false,  // 原生扩展（默认禁用）
    "level_4": false   // 系统命令（默认禁用）
  }
}
```

### 2. 用户确认机制

```python
def require_user_confirmation(operation: str, risk: str) -> bool:
    """需要用户确认"""
    message = f"""
    ⚠️ 高风险操作确认
    
    操作: {operation}
    风险: {risk}
    
    是否继续？(yes/no)
    """
    return input(message).lower() == 'yes'
```

### 3. 审计日志记录

```python
def log_audit(level: int, operation: str, granted: bool):
    """记录审计日志"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "operation": operation,
        "granted": granted,
        "user": get_current_user(),
        "process": get_process_id()
    }
    write_to_audit_log(log_entry)
```

## 📊 审计日志格式

### 日志文件位置
```
~/.openclaw/workspace/skills/llm-memory-integration/logs/audit.log
```

### 日志格式
```json
{
  "timestamp": "2026-04-15T21:05:00.000Z",
  "level": 4,
  "operation": "numa_bind",
  "granted": true,
  "user": "sandbox",
  "process": 12345,
  "details": {
    "node": 0,
    "pid": 12346
  }
}
```

## 🔧 配置文件

### 权限配置 (config/permissions.json)

```json
{
  "version": "1.0.0",
  "permissions": {
    "level_0": {
      "enabled": true,
      "description": "普通用户权限",
      "operations": ["vector_search", "memory_management", "llm_integration"]
    },
    "level_1": {
      "enabled": true,
      "description": "文件系统访问",
      "operations": ["read_file", "write_file"],
      "paths": ["~/.openclaw/memory-tdai", "~/.openclaw/workspace/skills/llm-memory-integration"]
    },
    "level_2": {
      "enabled": true,
      "description": "网络访问",
      "operations": ["llm_api", "embedding_api"],
      "endpoints": ["user-configured"]
    },
    "level_3": {
      "enabled": false,
      "description": "原生扩展加载",
      "operations": ["load_extension"],
      "require_confirmation": true,
      "sha256_verification": true
    },
    "level_4": {
      "enabled": false,
      "description": "系统命令执行",
      "operations": ["numa_bind", "irq_isolate", "hugepage_manage"],
      "require_confirmation": true,
      "require_root": true
    }
  }
}
```

## 🚀 使用示例

### 1. 检查权限

```python
from src.core.permission_manager import PermissionManager

pm = PermissionManager()

# 检查是否可以执行 NUMA 优化
if pm.check_permission(4, "numa_bind"):
    # 执行 NUMA 优化
    numa_optimizer.bind_to_node(0)
else:
    print("权限不足或未启用")
```

### 2. 请求权限

```python
# 请求启用 Level 3 权限
pm.request_permission(3, "load_extension", {
    "extension": "vec0.so",
    "sha256": "abc123..."
})
```

### 3. 查看审计日志

```python
# 查看最近的审计日志
logs = pm.get_audit_logs(limit=10)
for log in logs:
    print(f"{log['timestamp']}: {log['operation']} - {'通过' if log['granted'] else '拒绝'}")
```

## 📈 安全优势

1. **最小权限原则**
   - 默认只启用必要权限
   - 高风险权限需要明确启用

2. **审计追踪**
   - 记录所有权限操作
   - 可追溯问题来源

3. **用户控制**
   - 用户明确授权
   - 可随时禁用权限

4. **隔离风险**
   - 高风险操作独立进程
   - 失败不影响主进程

---

**最后更新**: 2026-04-15
**版本**: v6.3.3
