#!/usr/bin/env python3
from safe_extension_loader import safe_load_extension
"""
安全数据库连接模块

提供安全的 SQLite 数据库连接，替代 shell=False 调用。
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

# 数据库路径
VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"

# 向量扩展路径（动态检测）
def get_vec_extension_path() -> Path:
    """动态获取向量扩展路径"""
    possible_paths = [
        Path.home() / ".openclaw" / "extensions" / "memory-tencentdb" / "node_modules" / "sqlite-vec-linux-x64" / "vec0.so",
        Path.home() / ".openclaw" / "extensions" / "memory-tencentdb" / "node_modules" / "sqlite-vec-linux-x64" / "vec0",
    ]
    for p in possible_paths:
        if p.exists():
            return p
    return possible_paths[0]


class SafeDB:
    """安全数据库连接类"""
    
    def __init__(self, db_path: Optional[Path] = None, load_vec: bool = False):
        self.db_path = db_path or VECTORS_DB
        self.load_vec = load_vec
        self._conn = None
    
    def connect(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            
            # 尝试加载向量扩展
            if self.load_vec:
                try:
                    self._conn.enable_load_extension(True)
                    vec_ext = get_vec_extension_path()
                    if vec_ext.exists():
                        self._safe_load_extension(conn, vec_ext)
                except AttributeError:
                    # Python 的 sqlite3 可能不支持扩展加载
                    pass
                except Exception as e:
                    print(f"⚠️ 向量扩展加载失败: {e}")
        
        return self._conn
    
    def close(self):
        """关闭连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def execute(self, sql: str, params: tuple = ()) -> List[Tuple]:
        """执行查询（参数化）"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            pass  # 保持连接
    
    def execute_many(self, sql: str, params_list: List[tuple]) -> int:
        """批量执行"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.executemany(sql, params_list)
            conn.commit()
            return cursor.rowcount
        finally:
            pass
    
    def execute_script(self, script: str):
        """执行脚本"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.executescript(script)
            conn.commit()
        finally:
            pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def safe_query(sql: str, params: tuple = (), db_path: Optional[Path] = None) -> List[Tuple]:
    """安全查询快捷函数"""
    with SafeDB(db_path) as db:
        return db.execute(sql, params)


def safe_execute(sql: str, params: tuple = (), db_path: Optional[Path] = None) -> int:
    """安全执行快捷函数"""
    with SafeDB(db_path) as db:
        with db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount


def get_count(table: str, db_path: Optional[Path] = None) -> int:
    """获取表记录数"""
    # 验证表名（防止 SQL 注入）
    import re
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
        raise ValueError(f"Invalid table name: {table}")
    
    with SafeDB(db_path) as db:
        result = db.execute(f"SELECT COUNT(*) FROM {table}")
        return result[0][0] if result else 0


if __name__ == "__main__":
    print("安全数据库模块测试")
    print(f"数据库路径: {VECTORS_DB}")
    print(f"向量扩展: {get_vec_extension_path()}")
    
    # 测试连接
    with SafeDB() as db:
        try:
            result = db.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in result]
            print(f"表列表: {tables}")
        except Exception as e:
            print(f"错误: {e}")
