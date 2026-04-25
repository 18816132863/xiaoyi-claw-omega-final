#!/usr/bin/env python3
"""
数据库连接池模块
支持连接复用，提升性能
"""

import sqlite3
import threading
from contextlib import contextmanager
from typing import Optional
from pathlib import Path

class ConnectionPool:
    """SQLite 连接池"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str, max_connections: int = 5):
        if hasattr(self, '_initialized'):
            return
        
        self.db_path = db_path
        self.max_connections = max_connections
        self._pool = []
        self._pool_lock = threading.Lock()
        self._initialized = True
    
    @contextmanager
    def get_connection(self):
        """获取连接（上下文管理器）"""
        conn = self._acquire()
        try:
            yield conn
        finally:
            self._release(conn)
    
    def _acquire(self) -> sqlite3.Connection:
        """获取连接"""
        with self._pool_lock:
            if self._pool:
                return self._pool.pop()
        
        # 创建新连接
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _release(self, conn: sqlite3.Connection):
        """释放连接"""
        with self._pool_lock:
            if len(self._pool) < self.max_connections:
                self._pool.append(conn)
            else:
                conn.close()
    
    def close_all(self):
        """关闭所有连接"""
        with self._pool_lock:
            for conn in self._pool:
                conn.close()
            self._pool.clear()

# 全局连接池实例
_pool_instances = {}

def get_pool(db_path: str) -> ConnectionPool:
    """获取或创建连接池"""
    if db_path not in _pool_instances:
        _pool_instances[db_path] = ConnectionPool(db_path)
    return _pool_instances[db_path]

@contextmanager
def get_connection(db_path: str):
    """便捷方法：获取连接"""
    pool = get_pool(db_path)
    with pool.get_connection() as conn:
        yield conn
