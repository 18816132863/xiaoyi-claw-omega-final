#!/usr/bin/env python3
"""
异步支持模块模板
支持高并发场景
"""

import aiosqlite
import asyncio
from typing import List, Optional, AsyncGenerator
from contextlib import asynccontextmanager

class AsyncConnectionPool:
    """异步连接池"""
    
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self._semaphore = asyncio.Semaphore(max_connections)
    
    @asynccontextmanager
    async def get_connection(self):
        """获取异步连接"""
        async with self._semaphore:
            conn = await aiosqlite.connect(self.db_path)
            conn.row_factory = aiosqlite.Row
            try:
                yield conn
            finally:
                await conn.close()

async def async_vector_search(db_path: str, embedding: List[float], top_k: int = 20) -> List[dict]:
    """异步向量搜索"""
    async with AsyncConnectionPool(db_path).get_connection() as conn:
        cursor = await conn.execute(
            "SELECT * FROM l1_vec WHERE embedding MATCH ? LIMIT ?",
            (embedding, top_k)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def async_fts_search(db_path: str, query: str, top_k: int = 10) -> List[dict]:
    """异步 FTS 搜索"""
    async with AsyncConnectionPool(db_path).get_connection() as conn:
        cursor = await conn.execute(
            "SELECT * FROM l1_fts WHERE l1_fts MATCH ? LIMIT ?",
            (query, top_k)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def async_batch_insert(db_path: str, table: str, records: List[dict]) -> int:
    """异步批量插入"""
    if not records:
        return 0
    
    async with AsyncConnectionPool(db_path).get_connection() as conn:
        columns = list(records[0].keys())
        placeholders = ','.join(['?' for _ in columns])
        sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
        values = [tuple(r.values()) for r in records]
        await conn.executemany(sql, values)
        await conn.commit()
        return len(records)

async def async_query(db_path: str, sql: str, params: tuple = ()) -> List[dict]:
    """通用异步查询"""
    async with AsyncConnectionPool(db_path).get_connection() as conn:
        cursor = await conn.execute(sql, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
