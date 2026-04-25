#!/usr/bin/env python3
"""
v2.0 全面升级脚本
实施所有高中低优先级优化
"""

import os
import sys
from pathlib import Path

# 使用相对路径，避免硬编码
BASE_DIR = Path(__file__).parent

print("=" * 60)
print("v2.0 全面升级脚本")
print("=" * 60)

# 1. 创建异步支持模块
ASYNC_MODULE = '''#!/usr/bin/env python3
"""
异步支持模块
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
        
        values = [tuple(r[col] for col in columns) for r in records]
        await conn.executemany(sql, values)
        await conn.commit()
        
        return len(records)
'''

# 2. 创建单元测试模块
TEST_MODULE = '''#!/usr/bin/env python3
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
'''

# 3. 创建性能基准模块
BENCHMARK_MODULE = '''#!/usr/bin/env python3
"""
性能基准测试模块
量化性能提升
"""

import time
import sqlite3
from pathlib import Path
from typing import List, Callable

class PerformanceBenchmark:
    """性能基准测试"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.results = {}
    
    def benchmark_query(self, name: str, func: Callable, iterations: int = 1000):
        """测试查询性能"""
        start = time.time()
        
        for _ in range(iterations):
            func()
        
        elapsed = time.time() - start
        avg_ms = (elapsed / iterations) * 1000
        
        self.results[name] = {
            "iterations": iterations,
            "total_time": elapsed,
            "avg_ms": avg_ms
        }
        
        return avg_ms
    
    def benchmark_cache_hit(self, name: str, func: Callable, iterations: int = 1000):
        """测试缓存命中性能"""
        # 第一次执行（缓存未命中）
        func()
        
        # 测试缓存命中
        start = time.time()
        
        for _ in range(iterations):
            func()
        
        elapsed = time.time() - start
        avg_ms = (elapsed / iterations) * 1000
        
        self.results[name + "_cache_hit"] = {
            "iterations": iterations,
            "total_time": elapsed,
            "avg_ms": avg_ms
        }
        
        return avg_ms
    
    def benchmark_batch(self, name: str, func: Callable, batch_size: int = 100):
        """测试批量操作性能"""
        start = time.time()
        
        func()
        
        elapsed = time.time() - start
        
        self.results[name] = {
            "batch_size": batch_size,
            "total_time": elapsed,
            "per_record_ms": (elapsed / batch_size) * 1000
        }
        
        return elapsed
    
    def get_report(self) -> str:
        """生成报告"""
        lines = ["=" * 60, "性能基准测试报告", "=" * 60, ""]
        
        for name, data in self.results.items():
            lines.append(f"📊 {name}:")
            if "avg_ms" in data:
                lines.append(f"   平均耗时: {data['avg_ms']:.2f}ms")
                lines.append(f"   总耗时: {data['total_time']:.2f}s ({data['iterations']} 次)")
            elif "per_record_ms" in data:
                lines.append(f"   每条记录: {data['per_record_ms']:.2f}ms")
                lines.append(f"   总耗时: {data['total_time']:.2f}s ({data['batch_size']} 条)")
            lines.append("")
        
        return "\\n".join(lines)

def run_benchmark():
    """运行基准测试"""
    print("运行性能基准测试...")
    
    # 这里需要实际的数据库路径
    benchmark = PerformanceBenchmark(":memory:")
    
    # 示例测试
    def test_query():
        conn = sqlite3.connect(":memory:")
        cursor = conn.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
    
    benchmark.benchmark_query("simple_query", test_query, 10000)
    
    print(benchmark.get_report())

if __name__ == "__main__":
    run_benchmark()
'''

# 4. 创建监控指标模块
MONITOR_MODULE = '''#!/usr/bin/env python3
"""
监控指标模块
运行时性能监控
"""

import time
import threading
from typing import Dict, List
from collections import defaultdict
from datetime import datetime

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self._lock = threading.Lock()
    
    def record_query(self, query_type: str, latency_ms: float, cache_hit: bool = False):
        """记录查询"""
        with self._lock:
            self.metrics[query_type].append({
                "timestamp": time.time(),
                "latency_ms": latency_ms,
                "cache_hit": cache_hit
            })
            self.counters[f"{query_type}_total"] += 1
            if cache_hit:
                self.counters[f"{query_type}_cache_hits"] += 1
    
    def record_error(self, error_type: str):
        """记录错误"""
        with self._lock:
            self.counters[f"errors_{error_type}"] += 1
    
    def get_stats(self, query_type: str) -> Dict:
        """获取统计"""
        with self._lock:
            records = self.metrics.get(query_type, [])
            
            if not records:
                return {}
            
            latencies = [r["latency_ms"] for r in records]
            cache_hits = sum(1 for r in records if r["cache_hit"])
            
            return {
                "total_queries": len(records),
                "cache_hits": cache_hits,
                "cache_hit_rate": cache_hits / len(records) if records else 0,
                "avg_latency_ms": sum(latencies) / len(latencies),
                "min_latency_ms": min(latencies),
                "max_latency_ms": max(latencies),
                "p50_latency_ms": sorted(latencies)[len(latencies) // 2],
                "p95_latency_ms": sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 20 else max(latencies),
                "p99_latency_ms": sorted(latencies)[int(len(latencies) * 0.99)] if len(latencies) > 100 else max(latencies)
            }
    
    def get_summary(self) -> Dict:
        """获取摘要"""
        with self._lock:
            return {
                "counters": dict(self.counters),
                "query_types": list(self.metrics.keys())
            }
    
    def reset(self):
        """重置"""
        with self._lock:
            self.metrics.clear()
            self.counters.clear()

# 全局监控实例
_monitor = PerformanceMonitor()

def get_monitor() -> PerformanceMonitor:
    """获取监控实例"""
    return _monitor
'''

# 创建所有模块
modules = {
    "async_support.py": ASYNC_MODULE,
    "test_suite.py": TEST_MODULE,
    "benchmark.py": BENCHMARK_MODULE,
    "performance_monitor.py": MONITOR_MODULE
}

print("\\n📦 创建 v2.0 新模块...")
for filename, code in modules.items():
    filepath = BASE_DIR / filename
    filepath.write_text(code, encoding='utf-8')
    print(f"  ✅ {filename}")

print("\\n" + "=" * 60)
print("✅ v2.0 模块创建完成")
print("=" * 60)
