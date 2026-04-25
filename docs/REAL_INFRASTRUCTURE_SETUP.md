# 真实基础设施接入指南

## 当前环境限制

- ❌ 无 root 权限
- ❌ 无 Docker
- ❌ 无预装的 PostgreSQL/Redis 服务
- ❌ 无可用的云数据库配置

## 解决方案

### 方案 1: 使用云数据库服务（推荐）

#### PostgreSQL

**免费选项：**
1. **Supabase** (https://supabase.com) - 免费 500MB
2. **Neon** (https://neon.tech) - 免费 3GB
3. **Railway** (https://railway.app) - 免费 $5/月额度
4. **Render** (https://render.com) - 免费 1GB

**配置步骤：**
```bash
# 1. 注册云服务获取连接字符串
export DATABASE_URL="postgresql://user:password@host:5432/database"

# 2. 运行迁移
python scripts/migrate_to_postgres.py
```

#### Redis

**免费选项：**
1. **Upstash** (https://upstash.com) - 免费 10,000 请求/天
2. **Redis Cloud** (https://redis.com/try-free/) - 免费 30MB
3. **Railway** (https://railway.app) - 免费 $5/月额度

**配置步骤：**
```bash
# 1. 注册云服务获取连接字符串
export REDIS_URL="redis://default:password@host:6379"

# 2. 测试连接
python scripts/test_redis_connection.py
```

### 方案 2: 本地安装（需要 root 权限）

```bash
# Ubuntu/Debian
sudo apt-get install postgresql redis-server

# CentOS/RHEL
sudo yum install postgresql-server redis

# macOS
brew install postgresql redis
```

### 方案 3: Docker（需要 Docker）

```bash
# 使用已有的 docker-compose.yml
docker-compose up -d

# 等待服务启动
docker-compose ps

# 运行迁移
python scripts/migrate_to_postgres.py
```

## 当前实现状态

由于当前环境限制，已使用以下替代方案：

| 服务 | 替代方案 | 状态 |
|------|----------|------|
| PostgreSQL | SQLite | ✅ 功能完整 |
| Redis | FakeRedis | ✅ 功能完整 |
| Celery Worker | 自定义消费循环 | ✅ 功能完整 |
| Celery Beat | 自定义调度循环 | ✅ 功能完整 |

## 迁移到生产环境

当获得真实服务后，只需修改以下配置：

### 1. 数据库连接

```python
# infrastructure/storage/repositories/postgres_repo.py

# 替换
DATABASE_URL = "sqlite:///data/tasks.db"

# 为
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://...")
```

### 2. Redis 连接

```python
# infrastructure/storage/repositories/redis_client.py

# 替换
redis_client = fakeredis.FakeStrictRedis()

# 为
redis_client = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379"))
```

### 3. Celery 配置

```python
# infrastructure/celery_config.py

# 替换
broker_url = 'redis://fake:6379/0'

# 为
broker_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
```

### 4. 启动真实 Celery

```bash
# Worker
celery -A infrastructure.celery_config worker --loglevel=info

# Beat
celery -A infrastructure.celery_config beat --loglevel=info
```

## 验证清单

迁移后需验证：

- [ ] PostgreSQL 连接成功
- [ ] Redis PING 返回 PONG
- [ ] Celery Worker 注册成功
- [ ] Celery Beat 调度正常
- [ ] once 定时任务执行成功
- [ ] recurring 任务两次触发
- [ ] 失败重试正常
- [ ] interrupt/resume 正常
- [ ] worker 重启恢复正常
