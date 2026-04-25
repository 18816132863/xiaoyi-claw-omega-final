# DEPRECATED - 此目录已废弃

## 迁移说明

此目录已迁移到 `config/` 作为唯一真源。

## 新路径

- 配置文件: `config/`
- 设置模块: `config/settings.py`
- JSON 配置: `config/*.json`

## 使用方式

```python
# 旧方式 (已废弃)
from infrastructure.config import get_settings

# 新方式
from config import get_settings
```

## 迁移日期

2026-04-24
