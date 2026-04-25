#!/usr/bin/env python3
"""
批量操作优化模块
支持高效的批量插入、更新、删除

安全修复：添加表名和列名验证
"""

import sqlite3
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path
from contextlib import contextmanager

from connection_pool import get_connection
from unified_logger import get_logger

logger = get_logger("batch_operations")

def _validate_identifier(name: str) -> str:
    """
    验证标识符（表名、列名）
    
    Args:
        name: 标识符名称
    
    Returns:
        str: 验证后的名称
    
    Raises:
        ValueError: 如果名称无效
    """
    # 只允许字母、数字、下划线
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        raise ValueError(f"Invalid identifier: {name}")
    return name

class BatchOperations:
    """批量操作类"""
    
    def __init__(self, db_path: str, batch_size: int = 100):
        """
        初始化
        
        Args:
            db_path: 数据库路径
            batch_size: 批量大小
        """
        self.db_path = db_path
        self.batch_size = batch_size
    
    @contextmanager
    def _get_connection(self):
        """获取连接"""
        with get_connection(self.db_path) as conn:
            yield conn
    
    def batch_insert(self, table: str, records: List[Dict], batch_size: int = None) -> int:
        """
        批量插入
        
        Args:
            table: 表名
            records: 记录列表
            batch_size: 批量大小（可选）
        
        Returns:
            插入的记录数
        """
        if not records:
            return 0
        
        batch_size = batch_size or self.batch_size
        total = 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 安全修复：验证表名和列名
            table = _validate_identifier(table)
            columns = [_validate_identifier(col) for col in records[0].keys()]
            placeholders = ', '.join(['?' for _ in columns])
            sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # 分批插入
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                values = [tuple(r[col] for col in columns) for r in batch]
                
                cursor.executemany(sql, values)
                conn.commit()
                total += len(batch)
                
                logger.debug(f"批量插入: {len(batch)} 条")
            
            logger.info(f"批量插入完成: {total} 条记录")
            return total
    
    def batch_update(self, table: str, updates: List[Tuple], 
                     key_column: str = "id", batch_size: int = None) -> int:
        """
        批量更新
        
        Args:
            table: 表名
            updates: 更新列表 [(id, {column: value}), ...]
            key_column: 键列名
            batch_size: 批量大小
        
        Returns:
            更新的记录数
        """
        if not updates:
            return 0
        
        batch_size = batch_size or self.batch_size
        total = 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 安全修复：验证表名和列名
            table = _validate_identifier(table)
            key_column = _validate_identifier(key_column)
            
            for i in range(0, len(updates), batch_size):
                batch = updates[i:i+batch_size]
                
                for key, values in batch:
                    # 验证列名
                    safe_columns = [_validate_identifier(k) for k in values.keys()]
                    set_clause = ', '.join([f"{k} = ?" for k in safe_columns])
                    sql = f"UPDATE {table} SET {set_clause} WHERE {key_column} = ?"
                    params = list(values.values()) + [key]
                    
                    cursor.execute(sql, params)
                    total += 1
                
                conn.commit()
                logger.debug(f"批量更新: {len(batch)} 条")
            
            logger.info(f"批量更新完成: {total} 条记录")
            return total
    
    def batch_delete(self, table: str, ids: List[Any], 
                     key_column: str = "id", batch_size: int = None) -> int:
        """
        批量删除
        
        Args:
            table: 表名
            ids: ID 列表
            key_column: 键列名
            batch_size: 批量大小
        
        Returns:
            删除的记录数
        """
        if not ids:
            return 0
        
        batch_size = batch_size or self.batch_size
        total = 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            for i in range(0, len(ids), batch_size):
                batch = ids[i:i+batch_size]
                placeholders = ', '.join(['?' for _ in batch])
                sql = f"DELETE FROM {table} WHERE {key_column} IN ({placeholders})"
                
                cursor.execute(sql, batch)
                total += cursor.rowcount
                conn.commit()
                
                logger.debug(f"批量删除: {len(batch)} 条")
            
            logger.info(f"批量删除完成: {total} 条记录")
            return total
    
    def batch_upsert(self, table: str, records: List[Dict], 
                     key_columns: List[str], batch_size: int = None) -> int:
        """
        批量插入或更新（UPSERT）
        
        Args:
            table: 表名
            records: 记录列表
            key_columns: 键列名列表
            batch_size: 批量大小
        
        Returns:
            处理的记录数
        """
        if not records:
            return 0
        
        batch_size = batch_size or self.batch_size
        total = 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            columns = list(records[0].keys())
            placeholders = ', '.join(['?' for _ in columns])
            
            # 构建 UPSERT SQL
            update_columns = [c for c in columns if c not in key_columns]
            update_clause = ', '.join([f"{c} = excluded.{c}" for c in update_columns])
            
            sql = f"""
                INSERT INTO {table} ({', '.join(columns)}) 
                VALUES ({placeholders})
                ON CONFLICT ({', '.join(key_columns)}) 
                DO UPDATE SET {update_clause}
            """
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                values = [tuple(r[col] for col in columns) for r in batch]
                
                cursor.executemany(sql, values)
                conn.commit()
                total += len(batch)
                
                logger.debug(f"批量 UPSERT: {len(batch)} 条")
            
            logger.info(f"批量 UPSERT 完成: {total} 条记录")
            return total

# 便捷函数
def batch_insert_memories(records: List[Dict], db_path: str = None) -> int:
    """批量插入记忆"""
    if db_path is None:
        from paths import VECTORS_DB
        db_path = str(VECTORS_DB)
    
    ops = BatchOperations(db_path)
    return ops.batch_insert("l1_records", records)

def batch_update_memories(updates: List[Tuple], db_path: str = None) -> int:
    """批量更新记忆"""
    if db_path is None:
        from paths import VECTORS_DB
        db_path = str(VECTORS_DB)
    
    ops = BatchOperations(db_path)
    return ops.batch_update("l1_records", updates, key_column="record_id")
