# 配置文档

## 环境变量

### 核心配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| OPENCLAW_ENV | local | 运行环境 (local/test/prod) |
| OPENCLAW_DEBUG | false | Debug 模式 |

### 数据库配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| DATABASE_URL | sqlite:///data/tasks.db | 数据库 URL |
| DB_HOST | localhost | 数据库主机 |
| DB_PORT | 5432 | 数据库端口 |
| DB_NAME | openclaw | 数据库名称 |
| DB_USER | openclaw | 数据库用户 |
| DB_PASSWORD | | 数据库密码 |

### Redis 配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| REDIS_HOST | | Redis 主机 (为空则禁用) |
| REDIS_PORT | 6379 | Redis 端口 |

### 消息服务配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| MESSAGE_SERVER_PORT | 18790 | 消息服务端口 |

### 守护进程配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| DAEMON_CHECK_INTERVAL | 5.0 | 检查间隔 (秒) |

## 环境配置文件

### local 环境

```bash
cp .env.local.example .env
```

- 使用 SQLite
- 不使用 Redis
- Debug 模式开启

### prod 环境

```bash
cp .env.prod.example .env
```

- 使用 PostgreSQL
- 使用 Redis
- Debug 模式关闭

## 配置加载

配置按以下优先级加载：

1. 环境变量
2. .env 文件
3. 默认值

## 使用示例

```python
from infrastructure.config import get_settings

settings = get_settings()

# 获取数据库 URL
db_url = settings.get_database_url()

# 获取 Redis URL
redis_url = settings.get_redis_url()

# 检查环境
if settings.env == Environment.PROD:
    # 生产环境逻辑
    pass
```
