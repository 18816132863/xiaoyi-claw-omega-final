# OpenClaw 运行手册

## 启动

```bash
bash scripts/start_services.sh
```

## 停止

```bash
bash scripts/stop_services.sh
```

## 状态

```bash
bash scripts/status_services.sh
```

## 依赖安装

```bash
pip install -r requirements.txt
pip install croniter aiohttp pydantic
```

## 健康检查

```bash
curl http://localhost:18790/health
```

## 日志位置

- 消息服务: `logs/message_server.log`
- 任务守护进程: `logs/task_daemon.log`

## 严格验收

```bash
# 1. 清环境
rm -f data/tasks.db data/task_queue.jsonl
rm -f reports/ops/pending_sends.jsonl reports/ops/delivered_messages.jsonl
pkill -f message_server.py || true
pkill -f task_daemon.py || true

# 2. 启动
bash scripts/start_services.sh

# 3. 测试
pytest tests/ -q

# 4. 验收
curl http://localhost:18790/health
```

## 验收通过标准

1. once 任务最终状态为 `succeeded`
2. `delivery_pending` 状态可正常读取
3. recurring 至少连续执行 2 次
4. `message_server /health` 返回 200
5. `pytest tests -q` 结果为 `90 passed`

## 常见故障

### 消息服务未响应

检查端口占用：
```bash
lsof -i :18790
```

### 任务不执行

检查守护进程：
```bash
pgrep -f task_daemon.py
```

检查任务队列：
```bash
cat data/task_queue.jsonl
```
