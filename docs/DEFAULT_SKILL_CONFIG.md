# 默认技能配置

## 配置文件

配置通过 `config/default_skill_config.py` 管理。

## 默认值

```python
from config.default_skill_config import DefaultSkillConfig

config = DefaultSkillConfig()
```

### 存储配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| type | sqlite | 存储类型 |
| database_url | data/tasks.db | 数据库路径 |
| pool_size | 5 | 连接池大小 |
| timeout_seconds | 30 | 超时时间 |

### 执行配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| max_concurrent_tasks | 10 | 最大并发任务 |
| default_timeout_seconds | 300 | 默认超时 |
| max_retry_attempts | 3 | 最大重试次数 |
| retry_backoff_seconds | 60 | 重试间隔 |

### 调度配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| enabled | true | 是否启用调度 |
| check_interval_seconds | 60 | 检查间隔 |
| max_scheduled_tasks | 1000 | 最大调度任务数 |

### 日志配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| level | INFO | 日志级别 |
| format | ... | 日志格式 |
| file | logs/skill.log | 日志文件 |

## 自定义配置

```python
# 从字典创建
config = DefaultSkillConfig.from_dict({
    "storage": {
        "database_url": "custom/path/tasks.db"
    },
    "execution": {
        "max_retry_attempts": 5
    }
})

# 转换为字典
data = config.to_dict()
```

## 环境变量覆盖

| 环境变量 | 配置项 |
|----------|--------|
| DATABASE_URL | storage.database_url |
| MAX_RETRY_ATTEMPTS | execution.max_retry_attempts |
| LOG_LEVEL | logging.level |

## 功能开关

```python
from config.feature_flags import get_feature_flags, Feature

flags = get_feature_flags()

# 检查功能是否启用
if flags.is_enabled(Feature.DIAGNOSTICS):
    # 执行诊断
    pass

# 启用/禁用功能
flags.enable(Feature.BATCH_TASKS)
flags.disable(Feature.PLATFORM_SCHEDULING)
```
