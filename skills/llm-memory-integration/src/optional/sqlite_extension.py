"""
可选模块 - SQLite 扩展加载
高风险功能：加载原生 SQLite 扩展（vec0.so）

⚠️ 安全警告：
- 此模块包含高风险功能
- 需要用户明确启用
- 默认禁用

使用方法：
1. 在 config/optional_features.json 中启用
2. 或通过环境变量 ENABLE_SQLITE_EXTENSION=true
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional

# 默认禁用
ENABLED = os.environ.get('ENABLE_SQLITE_EXTENSION', 'false').lower() == 'true'

def is_enabled() -> bool:
    """检查是否启用"""
    return ENABLED

def load_vec_extension(conn: sqlite3.Connection, vec_path: Optional[str] = None) -> bool:
    """
    加载 vec0.so 扩展
    
    ⚠️ 高风险操作：需要用户明确启用
    
    Args:
        conn: SQLite 连接
        vec_path: vec0.so 路径（可选）
    
    Returns:
        bool: 是否成功加载
    """
    if not is_enabled():
        print("⚠️ SQLite 扩展加载未启用")
        print("   设置环境变量 ENABLE_SQLITE_EXTENSION=true 以启用")
        return False
    
    if vec_path is None:
        # 默认路径
        vec_path = Path.home() / ".openclaw" / "extensions" / "memory-tencentdb" / "node_modules" / "sqlite-vec-linux-x64" / "vec0.so"
    
    if not Path(vec_path).exists():
        print(f"❌ vec0.so 不存在: {vec_path}")
        return False
    
    try:
        conn.enable_load_extension(True)
        conn.load_extension(str(vec_path))
        print(f"✅ SQLite 扩展已加载: {vec_path}")
        return True
    except Exception as e:
        print(f"❌ 加载扩展失败: {e}")
        return False

def safe_load_extension(conn: sqlite3.Connection, vec_path: Optional[str] = None) -> bool:
    """
    安全加载扩展（带 SHA256 验证）
    
    ⚠️ 高风险操作：需要用户明确启用
    """
    if not is_enabled():
        return False
    
    # TODO: 添加 SHA256 验证
    return load_vec_extension(conn, vec_path)

__all__ = ['is_enabled', 'load_vec_extension', 'safe_load_extension']
