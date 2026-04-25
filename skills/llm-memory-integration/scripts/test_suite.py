#!/usr/bin/env python3
"""
单元测试模块
保证代码质量
"""

import unittest
import tempfile
import os
from pathlib import Path

class TestConnectionPool(unittest.TestCase):
    """连接池测试"""
    
    def setUp(self):
        self.test_db = tempfile.mktemp(suffix='.db')
    
    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_get_connection(self):
        from connection_pool import ConnectionPool
        pool = ConnectionPool(self.test_db)
        with pool.get_connection() as conn:
            self.assertIsNotNone(conn)
    
    def test_connection_reuse(self):
        from connection_pool import ConnectionPool
        pool = ConnectionPool(self.test_db)
        
        with pool.get_connection() as conn1:
            conn1_id = id(conn1)
        
        with pool.get_connection() as conn2:
            conn2_id = id(conn2)
        
        self.assertEqual(conn1_id, conn2_id)

class TestQueryCache(unittest.TestCase):
    """查询缓存测试"""
    
    def test_cache_hit(self):
        from query_cache import QueryCache
        cache = QueryCache()
        
        cache.set("test_query", None, "test_result")
        result = cache.get("test_query")
        
        self.assertEqual(result, "test_result")
    
    def test_cache_miss(self):
        from query_cache import QueryCache
        cache = QueryCache()
        
        result = cache.get("nonexistent")
        
        self.assertIsNone(result)
    
    def test_cache_expiry(self):
        from query_cache import QueryCache
        cache = QueryCache(ttl=1)  # 1秒过期
        
        cache.set("test_query", None, "test_result")
        
        import time
        time.sleep(1.1)
        
        result = cache.get("test_query")
        self.assertIsNone(result)

class TestConfigValidator(unittest.TestCase):
    """配置验证测试"""
    
    def test_valid_embedding_config(self):
        from config_validator import EmbeddingConfig
        
        config = EmbeddingConfig(
            api_url="https://api.example.com",
            api_key="test_key",
            model="test_model",
            dimensions=4096
        )
        
        # 不应抛出异常
        config.validate()
    
    def test_invalid_embedding_config(self):
        from config_validator import EmbeddingConfig
        
        config = EmbeddingConfig(
            api_url="",  # 空 URL
            api_key="test_key",
            model="test_model"
        )
        
        with self.assertRaises(ValueError):
            config.validate()

class TestBatchOperations(unittest.TestCase):
    """批量操作测试"""
    
    def setUp(self):
        self.test_db = tempfile.mktemp(suffix='.db')
    
    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_batch_insert(self):
        from batch_operations import BatchOperations
        import sqlite3
        
        # 创建测试表
        conn = sqlite3.connect(self.test_db)
        conn.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        conn.commit()
        conn.close()
        
        ops = BatchOperations(self.test_db)
        records = [{"id": i, "name": f"name_{i}"} for i in range(10)]
        
        count = ops.batch_insert("test", records)
        self.assertEqual(count, 10)

if __name__ == "__main__":
    unittest.main()
