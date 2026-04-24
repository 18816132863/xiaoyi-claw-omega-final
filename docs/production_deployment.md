# 生产部署文档

## 环境要求

- Python 3.12+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (可选)

## 快速开始

### 本地开发环境

```bash
# 1. 复制配置文件
cp .env.local.example .env

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
bash scripts/start_services.sh
```

### Docker 部署

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f task-daemon
```

### 生产环境

```bash
# 1. 复制生产配置
cp .env.prod.example .env

# 2. 修改配置
vim .env

# 3. 启动服务
docker-compose -f docker-compose.yml up -d
```

## 配置说明

### 数据库配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DATABASE_URL | 数据库 URL | sqlite:///data/tasks.db |
| DB_HOST | 数据库主机 | localhost |
| DB_PORT | 数据库端口 | 5432 |
| DB_NAME | 数据库名称 | openclaw |
| DB_USER | 数据库用户 | openclaw |
| DB_PASSWORD | 数据库密码 | |

### Redis 配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| REDIS_HOST | Redis 主机 | (空，禁用) |
| REDIS_PORT | Redis 端口 | 6379 |

### 服务配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| MESSAGE_SERVER_PORT | 消息服务端口 | 18790 |
| DAEMON_CHECK_INTERVAL | 守护进程检查间隔 | 5.0 |

## 健康检查

### 消息服务

```bash
# 健康检查
curl http://localhost:18790/health

# 就绪检查
curl http://localhost:18790/ready

# 指标
curl http://localhost:18790/metrics
```

### 任务守护进程

```bash
# 检查进程
pgrep -f task_daemon.py

# 查看日志
tail -f logs/task_daemon.log
```

## 监控

### 日志位置

- 消息服务: `logs/message_server_*.jsonl`
- 任务守护进程: `logs/task_daemon_*.jsonl`

### 指标位置

- 指标文件: `reports/metrics/metrics.json`

## 故障排查

### 任务不执行

1. 检查守护进程是否运行
2. 检查任务队列 `data/task_queue.jsonl`
3. 查看日志中的错误信息

### 消息发送失败

1. 检查消息服务是否运行
2. 检查健康检查接口
3. 查看 `reports/ops/delivered_messages.jsonl`

### 数据库连接失败

1. 检查 PostgreSQL 是否运行
2. 检查连接字符串
3. 检查网络连通性
