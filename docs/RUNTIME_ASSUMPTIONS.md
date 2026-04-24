# 运行时假设

## 明确依赖

以下能力是**必须**的：

| 依赖 | 说明 | 默认值 |
|------|------|--------|
| Python | 运行环境 | 3.10+ |
| SQLite | 本地存储 | 自动创建 |
| 文件系统 | 持久化 | data/ 目录 |

## 可选增强

以下能力是**可选**的，不可用时自动降级：

| 能力 | 增强效果 | 降级方案 |
|------|----------|----------|
| PostgreSQL | 高性能存储 | SQLite |
| Redis | 分布式缓存 | 内存缓存 |
| Docker | 容器化部署 | 直接运行 |
| 小艺平台 | 平台调度 | 本地调度 |
| 鸿蒙平台 | 平台通知 | 本地日志 |

## 禁止的假设

以下假设**不允许**：

❌ 假设用户有 PostgreSQL
❌ 假设用户有 Redis
❌ 假设用户有 Docker
❌ 假设用户有 sudo 权限
❌ 假设用户有外网访问
❌ 假设用户有云服务账号

## 环境检测

```python
from platform_adapter.runtime_probe import RuntimeProbe

env = RuntimeProbe.detect_environment()

# 返回:
{
    "is_xiaoyi": False,
    "is_harmonyos": False,
    "is_web": False,
    "is_cli": True,
    "has_database": True,
    "has_redis": False,
    "has_docker": False,
    "runtime_mode": "skill_default"
}
```

## 最小运行环境

技能可以在以下最小环境中运行：

- Python 3.10+
- 10MB 磁盘空间
- 无网络访问
- 无特殊权限
