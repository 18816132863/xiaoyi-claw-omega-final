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

if __name__ == "__main__":
    unittest.main()
