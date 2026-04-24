# SQLite 时间字段硬规范

## 背景

Python 3.12 开始，SQLite 的默认 datetime adapter 被标记为弃用（DeprecationWarning）。
为了避免未来版本兼容性问题，项目统一采用手动序列化方式处理时间字段。

## 硬规范

### 1. 禁止裸 datetime 直接入库

**错误写法**：
```python
cursor.execute(
    "INSERT INTO tasks (id, created_at) VALUES (?, ?)",
    (task_id, datetime.now())  # ❌ 禁止
)
```

**正确写法**：
```python
from infrastructure.storage.sqlite_utils import serialize_datetime

cursor.execute(
    "INSERT INTO tasks (id, created_at) VALUES (?, ?)",
    (task_id, serialize_datetime(datetime.now()))  # ✅ 正确
)
```

### 2. SQLite 层只接受三种值

时间字段只允许：
- `None`
- ISO 8601 字符串（如 `"2026-04-23T10:00:00"`）
- `datetime` 对象（但必须先经过 `serialize_datetime()`）

其他任何类型都会抛出 `TypeError`。

### 3. 统一使用工具函数

**入库前**：
```python
from infrastructure.storage.sqlite_utils import serialize_datetime

# datetime -> ISO 字符串
iso_str = serialize_datetime(datetime.now())

# 字符串原样返回
iso_str = serialize_datetime("2026-04-23T10:00:00")

# None -> None
value = serialize_datetime(None)
```

**出库后**：
```python
from infrastructure.storage.sqlite_utils import deserialize_datetime

# ISO 字符串 -> datetime
dt = deserialize_datetime(row["created_at"])

# None -> None
dt = deserialize_datetime(None)
```

### 4. Repository 层强制序列化

所有 SQLite Repository 的 `update()` 方法对时间字段强制序列化：

```python
TIME_FIELDS = {
    "run_at",
    "next_run_at",
    "last_run_at",
    "created_at",
    "updated_at",
    "delivered_at",
}

for key, value in updates.items():
    if key in TIME_FIELDS:
        values.append(serialize_datetime(value))  # 强制序列化
    else:
        values.append(value)
```

### 5. 发现绕过算不合规范

任何新代码如果绕过 `serialize_datetime()` 直接传递 datetime 给 SQLite，
视为不合规范，必须修改。

## 工具函数位置

- `infrastructure/storage/sqlite_utils.py`
  - `serialize_datetime(value)` - 入库前
  - `deserialize_datetime(value)` - 出库后

## 测试覆盖

- `tests/test_sqlite_datetime.py`
  - 测试序列化/反序列化
  - 测试 update() 强制序列化
  - 测试非法类型报错
  - 测试无 DeprecationWarning

## 违规后果

- 代码审查不通过
- CI 测试失败
- 必须修改后才能合并

---

# 任务系统资源管理规范

## 1. SQLite 时间字段统一入口

- 任务系统相关时间字段统一走 `serialize_datetime()`
- 任务系统相关 SQLite 写入不允许绕过 repository / sqlite_utils
- 所有 SQLite 连接统一使用 `detect_types=sqlite3.PARSE_DECLTYPES`

**统一入口位置**：
- `infrastructure/storage/sqlite_utils.py`
  - `serialize_datetime(value)` - 入库前
  - `deserialize_datetime(value)` - 出库后

**禁止写法**：
```python
# ❌ 禁止直接使用 .isoformat()
delivered_at = datetime.now().isoformat()
next_run_at = next_run.isoformat() if next_run else None

# ❌ 禁止绕过 repository 直接操作 SQLite
cursor.execute("INSERT INTO tasks ...", (..., datetime.now()))
```

**正确写法**：
```python
# ✅ 使用统一序列化函数
from infrastructure.storage.sqlite_utils import serialize_datetime

delivered_at = serialize_datetime(datetime.now())
next_run_at = serialize_datetime(next_run) if next_run else None
```

## 2. asyncio event loop 管理

- 自己创建的 asyncio event loop 必须负责 close
- 不允许留下未关闭 loop 的资源警告
- 使用 `created_loop` 标记区分获取/创建的 loop

**正确写法**：
```python
created_loop = False
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    created_loop = True

try:
    result = loop.run_until_complete(coro())
finally:
    if created_loop:
        loop.close()
```

## 3. 资源警告处理

- `ResourceWarning: unclosed event loop` 必须修复
- `DeprecationWarning: datetime adapter` 必须修复
- 其他资源泄漏警告必须修复

## 4. 第三方插件 ResourceWarning 说明

如果 ResourceWarning 来自第三方测试插件（如 pytest-asyncio），要在文档中注明：

**当前已知第三方 ResourceWarning**：
- pytest-asyncio 0.23.0 在某些 Python 版本下会产生 `AttributeError: 'Package' object has no attribute 'obj'`
- 解决方案：固定使用 pytest-asyncio==0.21.0

**判断方法**：
1. 使用 `-W error::ResourceWarning` 运行测试
2. 如果测试通过，说明 ResourceWarning 来自 pytest 内部清理，不是业务代码问题
3. 如果测试失败，定位具体测试并修复

## 5. 测试依赖版本

固定版本，避免兼容性问题：
- pytest-asyncio==0.23.6（已验证通过，无 ResourceWarning）
- pytest>=8.0.0
- pytest-cov>=4.1.0
