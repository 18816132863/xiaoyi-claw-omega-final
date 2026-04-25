#!/usr/bin/env python3
"""
WAL 模式优化模块 (v4.2)
SQLite WAL 模式、批量写入优化、检查点优化
"""

import sqlite3
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import time


class WALOptimizer:
    """
    WAL 模式优化器
    优化 SQLite 写入性能
    """
    
    def __init__(self, db_path: str):
        """
        初始化 WAL 优化器
        
        Args:
            db_path: 数据库路径
        """
        self.db_path = Path(db_path).expanduser()
        self.conn = None
        self.cursor = None
        
        self._connect()
        self._enable_wal()
        
        print(f"WAL 优化器初始化:")
        print(f"  数据库: {self.db_path}")
        print(f"  模式: WAL")
    
    def _connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
    
    def _enable_wal(self):
        """启用 WAL 模式"""
        # 启用 WAL
        self.cursor.execute("PRAGMA journal_mode=WAL")
        
        # 优化参数
        self.cursor.execute("PRAGMA synchronous=NORMAL")  # 减少同步
        self.cursor.execute("PRAGMA cache_size=-64000")  # 64MB 缓存
        self.cursor.execute("PRAGMA temp_store=MEMORY")  # 内存临时存储
        self.cursor.execute("PRAGMA mmap_size=268435456")  # 256MB mmap
        
        # WAL 参数
        self.cursor.execute("PRAGMA wal_autocheckpoint=1000")  # 每 1000 页检查点
        
        result = self.cursor.fetchone()
        print(f"  WAL 模式: {result[0] if result else 'enabled'}")
    
    def batch_insert(
        self,
        table: str,
        columns: List[str],
        data: List[Tuple],
        batch_size: int = 1000
    ) -> int:
        """
        批量插入数据
        
        Args:
            table: 表名
            columns: 列名列表
            data: 数据列表
            batch_size: 批量大小
        
        Returns:
            int: 插入数量
        """
        if not data:
            return 0
        
        # 构建 SQL
        placeholders = ','.join(['?' for _ in columns])
        columns_str = ','.join(columns)
        sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
        
        # 开始事务
        self.cursor.execute("BEGIN TRANSACTION")
        
        try:
            # 批量插入
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                self.cursor.executemany(sql, batch)
                
                # 定期提交
                if (i // batch_size) % 10 == 0:
                    self.conn.commit()
                    self.cursor.execute("BEGIN TRANSACTION")
            
            # 提交剩余
            self.conn.commit()
            
            print(f"✅ 批量插入完成: {len(data)} 条")
            return len(data)
        
        except Exception as e:
            self.conn.rollback()
            print(f"❌ 批量插入失败: {e}")
            return 0
    
    def batch_update(
        self,
        table: str,
        updates: List[Tuple],
        key_column: str = "id",
        batch_size: int = 1000
    ) -> int:
        """
        批量更新数据
        
        Args:
            table: 表名
            updates: 更新数据 [(id, col1, col2, ...), ...]
            key_column: 键列名
            batch_size: 批量大小
        
        Returns:
            int: 更新数量
        """
        if not updates:
            return 0
        
        # 构建更新 SQL
        n_columns = len(updates[0]) - 1
        set_clause = ','.join([f"col{i} = ?" for i in range(n_columns)])
        sql = f"UPDATE {table} SET {set_clause} WHERE {key_column} = ?"
        
        # 重新排列参数
        reordered = [(row[1:] + (row[0],)) for row in updates]
        
        # 开始事务
        self.cursor.execute("BEGIN TRANSACTION")
        
        try:
            # 批量更新
            for i in range(0, len(reordered), batch_size):
                batch = reordered[i:i + batch_size]
                self.cursor.executemany(sql, batch)
            
            self.conn.commit()
            print(f"✅ 批量更新完成: {len(updates)} 条")
            return len(updates)
        
        except Exception as e:
            self.conn.rollback()
            print(f"❌ 批量更新失败: {e}")
            return 0
    
    def checkpoint(self, mode: str = "PASSIVE"):
        """
        执行检查点
        
        Args:
            mode: 检查点模式 (PASSIVE, FULL, RESTART, TRUNCATE)
        """
        self.cursor.execute(f"PRAGMA wal_checkpoint({mode})")
        result = self.cursor.fetchone()
        print(f"检查点完成: {result}")
    
    def optimize(self):
        """优化数据库"""
        print("优化数据库...")
        
        # 分析
        self.cursor.execute("ANALYZE")
        
        # 重建索引
        self.cursor.execute("REINDEX")
        
        # 清理
        self.cursor.execute("VACUUM")
        
        print("✅ 数据库优化完成")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        stats = {}
        
        # 页面统计
        self.cursor.execute("PRAGMA page_count")
        stats['page_count'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("PRAGMA page_size")
        stats['page_size'] = self.cursor.fetchone()[0]
        
        # WAL 统计
        self.cursor.execute("PRAGMA wal_checkpoint")
        result = self.cursor.fetchone()
        stats['wal_checkpoint'] = result
        
        # 缓存统计
        self.cursor.execute("PRAGMA cache_size")
        stats['cache_size'] = self.cursor.fetchone()[0]
        
        return stats
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            print("✅ 数据库连接已关闭")


class BatchWriter:
    """
    批量写入器
    自动批量写入优化
    """
    
    def __init__(
        self,
        db_path: str,
        table: str,
        columns: List[str],
        batch_size: int = 1000,
        flush_interval: float = 1.0
    ):
        """
        初始化批量写入器
        
        Args:
            db_path: 数据库路径
            table: 表名
            columns: 列名列表
            batch_size: 批量大小
            flush_interval: 刷新间隔（秒）
        """
        self.wal_optimizer = WALOptimizer(db_path)
        self.table = table
        self.columns = columns
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        
        self.buffer = []
        self.last_flush = time.time()
        
        print(f"批量写入器初始化:")
        print(f"  表: {table}")
        print(f"  批量大小: {batch_size}")
        print(f"  刷新间隔: {flush_interval}s")
    
    def insert(self, row: Tuple):
        """
        插入一行
        
        Args:
            row: 数据行
        """
        self.buffer.append(row)
        
        # 检查是否需要刷新
        if len(self.buffer) >= self.batch_size or \
           time.time() - self.last_flush >= self.flush_interval:
            self.flush()
    
    def flush(self):
        """刷新缓冲区"""
        if not self.buffer:
            return
        
        self.wal_optimizer.batch_insert(
            self.table,
            self.columns,
            self.buffer
        )
        
        self.buffer = []
        self.last_flush = time.time()
    
    def close(self):
        """关闭写入器"""
        self.flush()
        self.wal_optimizer.close()


if __name__ == "__main__":
    # 测试
    print("=== WAL 优化器测试 ===")
    
    import tempfile
    import os
    
    # 创建临时数据库
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        
        # 创建优化器
        optimizer = WALOptimizer(db_path)
        
        # 创建测试表
        optimizer.cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_vectors (
                id INTEGER PRIMARY KEY,
                vector BLOB,
                metadata TEXT
            )
        """)
        optimizer.conn.commit()
        
        # 批量插入测试
        data = [
            (i, np.random.randn(128).astype(np.float32).tobytes(), f"meta_{i}")
            for i in range(10000)
        ]
        
        start = time.time()
        optimizer.batch_insert(
            "test_vectors",
            ["id", "vector", "metadata"],
            data,
            batch_size=1000
        )
        elapsed = time.time() - start
        print(f"插入耗时: {elapsed:.2f}s ({len(data)/elapsed:.0f} rows/s)")
        
        # 统计
        stats = optimizer.get_stats()
        print(f"统计: {stats}")
        
        # 检查点
        optimizer.checkpoint()
        
        # 优化
        optimizer.optimize()
        
        optimizer.close()
