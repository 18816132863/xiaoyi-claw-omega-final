#!/usr/bin/env python3
"""
SQLite 扩展模块 (v5.2.25)
支持多种 SQLite 实现，用户可自行选择

支持的实现：
1. pysqlite3-binary - 支持扩展加载（推荐）
2. pysqlite3 - 纯 Python 实现
3. sqlite3 - Python 标准库（不支持扩展）

安装建议：
- 需要向量搜索：pip install pysqlite3-binary sqlite-vec
- 仅需基础功能：使用标准库 sqlite3 即可

⚠️ 重要变更 (v5.2.25)：
- 移除了内置的 sqlite-vec 扩展加载功能
- 用户需要自行安装 sqlite-vec 扩展
- 推荐使用 sqlite-vec 官方版本：https://github.com/asg017/sqlite-vec
"""

import os
import json
from pathlib import Path
from typing import Optional, Tuple, Any, List, Dict
import importlib

# 配置文件路径
CONFIG_PATH = Path.home() / ".openclaw" / "memory-tdai" / "config" / "extension_config.json"

# 默认配置
DEFAULT_CONFIG = {
    "enable_native_extension": False,
    "preferred_sqlite": "auto",
    "sqlite_vec_path": None  # 用户自定义 sqlite-vec 路径
}


def load_config() -> dict:
    """加载配置"""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                return {**DEFAULT_CONFIG, **config}
        except Exception:
            pass
    return DEFAULT_CONFIG


def save_config(config: dict):
    """保存配置"""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)


# 加载配置
_config = load_config()


def detect_sqlite_implementations() -> Dict[str, Dict]:
    """
    检测可用的 SQLite 实现
    
    Returns:
        Dict: 可用的实现及其特性
    """
    implementations = {}
    
    # 1. pysqlite3-binary（推荐，支持扩展）
    try:
        mod = importlib.import_module('pysqlite3')
        implementations['pysqlite3-binary'] = {
            'module': mod,
            'supports_extension': True,
            'description': 'pysqlite3-binary - 支持扩展加载（推荐）',
            'install': 'pip install pysqlite3-binary'
        }
    except ImportError:
        pass
    
    # 2. pysqlite3（纯 Python）
    try:
        mod = importlib.import_module('pysqlite3')
        if 'pysqlite3-binary' not in implementations:
            implementations['pysqlite3'] = {
                'module': mod,
                'supports_extension': True,
                'description': 'pysqlite3 - 纯 Python 实现',
                'install': 'pip install pysqlite3'
            }
    except ImportError:
        pass
    
    # 3. 标准库 sqlite3（不支持扩展）
    try:
        import sqlite3
        implementations['sqlite3'] = {
            'module': sqlite3,
            'supports_extension': False,
            'description': 'sqlite3 - Python 标准库（不支持扩展）',
            'install': '无需安装'
        }
    except ImportError:
        pass
    
    return implementations


def get_best_sqlite():
    """
    获取最优的 SQLite 实现
    
    优先级：
    1. pysqlite3-binary（支持扩展）
    2. pysqlite3（支持扩展）
    3. sqlite3（标准库）
    
    Returns:
        tuple: (module, info_dict)
    """
    implementations = detect_sqlite_implementations()
    
    # 按优先级选择
    for name in ['pysqlite3-binary', 'pysqlite3', 'sqlite3']:
        if name in implementations:
            return implementations[name]['module'], implementations[name]
    
    # 回退到标准库
    import sqlite3
    return sqlite3, {
        'supports_extension': False,
        'description': 'sqlite3 - Python 标准库',
        'install': '无需安装'
    }


# 自动选择最优实现
sqlite3, SQLITE_INFO = get_best_sqlite()
HAS_PYSQLITE3 = 'pysqlite3' in str(type(sqlite3).__module__)
SUPPORTS_EXTENSION = SQLITE_INFO.get('supports_extension', False)


def print_sqlite_status():
    """打印 SQLite 状态"""
    print("=== SQLite 实现状态 ===")
    print(f"当前使用: {SQLITE_INFO['description']}")
    print(f"支持扩展: {'✅ 是' if SUPPORTS_EXTENSION else '❌ 否'}")
    
    implementations = detect_sqlite_implementations()
    print(f"\n可用实现:")
    for name, info in implementations.items():
        marker = " (当前)" if info['module'] == sqlite3 else ""
        print(f"  - {info['description']}{marker}")
        print(f"    安装: {info['install']}")
    
    print("\n📦 sqlite-vec 扩展安装指南:")
    print("  sqlite-vec 是一个高性能向量搜索扩展")
    print("  安装方式:")
    print("  1. 官方文档: https://github.com/asg017/sqlite-vec")
    print("  2. Python: pip install sqlite-vec")
    print("  3. 下载预编译版本: https://github.com/asg017/sqlite-vec/releases")
    print("=====================")


def get_sqlite_module():
    """
    获取当前 SQLite 模块
    
    Returns:
        sqlite3 模块
    """
    return sqlite3


def connect(db_path: str, load_vec: bool = False) -> Any:
    """
    连接数据库
    
    Args:
        db_path: 数据库文件路径
        load_vec: 是否加载 sqlite-vec 扩展（已弃用，保留参数兼容性）
        
    Returns:
        数据库连接
    """
    # 展开路径
    db_path = os.path.expanduser(db_path)
    db_path = os.path.abspath(db_path)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    
    # load_vec 参数已弃用，不再自动加载扩展
    if load_vec:
        print("⚠️ 内置 sqlite-vec 扩展加载功能已移除")
        print("请自行安装 sqlite-vec 扩展：")
        print("  - pip install sqlite-vec")
        print("  - https://github.com/asg017/sqlite-vec")
    
    return conn


def connect_with_extension(db_path: str, extension_path: str = None) -> Any:
    """
    连接数据库并加载用户指定的扩展
    
    Args:
        db_path: 数据库文件路径
        extension_path: 扩展文件路径（用户自行提供）
        
    Returns:
        数据库连接
    """
    db_path = os.path.expanduser(db_path)
    db_path = os.path.abspath(db_path)
    
    conn = sqlite3.connect(db_path)
    
    if extension_path is None:
        print("⚠️ 未指定扩展路径")
        print("请提供 sqlite-vec 扩展的路径，或使用以下方式安装：")
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
        print(f"✅ 已加载扩展: {extension_path}")
    except Exception as e:
        print(f"⚠️ 加载扩展失败: {e}")
    
    return conn


def get_vec_installation_guide() -> str:
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
- 选择对应平台的版本（Linux/macOS/Windows）

### 3. 从源码编译
```bash
git clone https://github.com/asg017/sqlite-vec
cd sqlite-vec
make loadable
```

## 使用示例

```python
import sqlite3

# 加载扩展
conn = sqlite3.connect('vectors.db')
conn.enable_load_extension(True)
conn.load_extension('./vec0')  # 或 vec0.dll / vec0.so

# 创建向量表
conn.execute('''
    CREATE VIRTUAL TABLE vec_items USING vec0(
        embedding FLOAT[384]
    )
''')

# 插入向量
conn.execute(
    'INSERT INTO vec_items(rowid, embedding) VALUES (?, ?)',
    (1, '[0.1, 0.2, 0.3, ...]')
)

# 向量搜索
results = conn.execute('''
    SELECT rowid, distance
    FROM vec_items
    WHERE embedding MATCH '[0.1, 0.2, 0.3, ...]'
    ORDER BY distance
    LIMIT 10
''')
```

## 官方资源

- GitHub: https://github.com/asg017/sqlite-vec
- 文档: https://sqlite-vec.com
- 示例: https://github.com/asg017/sqlite-vec/tree/main/examples
"""


def is_extension_supported() -> bool:
    """检查是否支持扩展加载"""
    return SUPPORTS_EXTENSION


# 导出
__all__ = [
    'sqlite3',
    'connect',
    'connect_with_extension',
    'get_sqlite_module',
    'detect_sqlite_implementations',
    'get_best_sqlite',
    'print_sqlite_status',
    'get_vec_installation_guide',
    'is_extension_supported',
    'HAS_PYSQLITE3',
    'SUPPORTS_EXTENSION'
]


# 测试
if __name__ == "__main__":
    print_sqlite_status()
    print()
    print("=== sqlite-vec 安装指南 ===")
    print(get_vec_installation_guide())
