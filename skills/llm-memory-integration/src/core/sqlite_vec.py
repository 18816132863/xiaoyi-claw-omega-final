#!/usr/bin/env python3
"""
sqlite-vec 扩展包装模块 (v5.2.25)
支持多种 SQLite 实现，用户可自行选择

⚠️ 重要变更 (v5.2.25)：
- 移除了内置的 sqlite-vec 扩展
- 用户需要自行安装 sqlite-vec
- 推荐使用官方版本：https://github.com/asg017/sqlite-vec

安装建议：
- 需要向量搜索：pip install pysqlite3-binary sqlite-vec
- 仅需基础功能：使用标准库 sqlite3 即可
"""

import os
from pathlib import Path
from typing import Any, Optional, Dict
import importlib


def get_sqlite_module():
    """
    获取支持扩展加载的 SQLite 模块
    
    优先级：
    1. pysqlite3-binary（推荐）
    2. pysqlite3
    3. sqlite3（标准库，不支持扩展）
    
    Returns:
        sqlite3 模块
    """
    # 尝试 pysqlite3-binary
    try:
        from pysqlite3 import dbapi2 as sqlite3
        return sqlite3, True
    except ImportError:
        pass
    
    # 尝试 pysqlite3
    try:
        from pysqlite3 import dbapi2 as sqlite3
        return sqlite3, True
    except ImportError:
        pass
    
    # 回退到标准库
    import sqlite3
    return sqlite3, False


# 获取 SQLite 模块
sqlite3, SUPPORTS_EXTENSION = get_sqlite_module()


def connect(db_path: str, load_vec: bool = True) -> Any:
    """
    连接数据库
    
    ⚠️ 注意：内置 sqlite-vec 扩展加载功能已移除
    请使用 connect_with_extension() 并提供自行安装的扩展路径
    
    Args:
        db_path: 数据库文件路径
        load_vec: 已弃用，保留参数兼容性
        
    Returns:
        数据库连接
    """
    # 展开路径
    db_path = os.path.expanduser(db_path)
    db_path = os.path.abspath(db_path)
    
    conn = sqlite3.connect(db_path)
    
    if load_vec:
        print("⚠️ 内置 sqlite-vec 扩展加载功能已移除")
        print("请自行安装 sqlite-vec：")
        print("  - pip install sqlite-vec")
        print("  - https://github.com/asg017/sqlite-vec")
    
    return conn


def connect_with_extension(db_path: str, extension_path: str = None) -> Any:
    """
    连接数据库并加载用户指定的 sqlite-vec 扩展
    
    Args:
        db_path: 数据库文件路径
        extension_path: sqlite-vec 扩展文件路径（用户自行提供）
        
    Returns:
        数据库连接
    """
    db_path = os.path.expanduser(db_path)
    db_path = os.path.abspath(db_path)
    
    conn = sqlite3.connect(db_path)
    
    if extension_path is None:
        print("⚠️ 未指定 sqlite-vec 扩展路径")
        print("请提供扩展路径，或使用以下方式安装：")
        print("  - pip install sqlite-vec")
        print("  - https://github.com/asg017/sqlite-vec")
        return conn
    
    if not os.path.exists(extension_path):
        print(f"⚠️ 扩展文件不存在: {extension_path}")
        return conn
    
    if not SUPPORTS_EXTENSION:
        print("⚠️ 当前 SQLite 实现不支持扩展加载")
        print(f"请安装: pip install pysqlite3-binary")
        return conn
    
    # 加载用户指定的扩展
    try:
        conn.enable_load_extension(True)
        conn.load_extension(extension_path)
        print(f"✅ 已加载 sqlite-vec 扩展: {extension_path}")
    except Exception as e:
        print(f"⚠️ 加载扩展失败: {e}")
    
    return conn


def get_vec_version(conn: Any) -> str:
    """获取 sqlite-vec 版本"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT vec_version()")
        return cursor.fetchone()[0]
    except Exception as e:
        return f"获取版本失败: {e}"


def is_vec_available(conn: Any) -> bool:
    """检查 sqlite-vec 是否可用"""
    try:
        version = get_vec_version(conn)
        return bool(version and not version.startswith("获取版本失败"))
    except Exception:
        return False


def get_installation_guide() -> str:
    """
    获取 sqlite-vec 安装指南
    
    Returns:
        str: 安装指南
    """
    return """
# sqlite-vec 安装指南

sqlite-vec 是一个轻量级、高性能的向量搜索 SQLite 扩展。

## 安装方式

### 1. Python pip 安装（推荐）
```bash
pip install sqlite-vec
```

### 2. 下载预编译版本
- GitHub Releases: https://github.com/asg017/sqlite-vec/releases
- 选择对应平台的版本：
  - Linux: vec0.so
  - macOS: vec0.dylib
  - Windows: vec0.dll

### 3. 从源码编译
```bash
git clone https://github.com/asg017/sqlite-vec
cd sqlite-vec
make loadable
```

## 使用示例

```python
from core.sqlite_vec import connect_with_extension

# 方式1：使用 pip 安装的 sqlite-vec
# pip install sqlite-vec
# 扩展路径通常在 site-packages/sqlite_vec/vec0.so

# 方式2：使用下载的预编译版本
conn = connect_with_extension(
    'vectors.db',
    extension_path='/path/to/vec0.so'
)

# 检查是否加载成功
from core.sqlite_vec import is_vec_available, get_vec_version
if is_vec_available(conn):
    print(f"sqlite-vec 版本: {get_vec_version(conn)}")
```

## 官方资源

- GitHub: https://github.com/asg017/sqlite-vec
- 文档: https://sqlite-vec.com
"""


def print_status():
    """打印状态"""
    print("=== SQLite 状态 ===")
    print(f"支持扩展: {'✅ 是' if SUPPORTS_EXTENSION else '❌ 否'}")
    
    print("\n📦 sqlite-vec 安装指南:")
    print("  内置扩展已移除，请自行安装 sqlite-vec")
    print("  - pip install sqlite-vec")
    print("  - https://github.com/asg017/sqlite-vec")
    print("==================")


# 测试
if __name__ == "__main__":
    print_status()
