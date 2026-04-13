#!/usr/bin/env python3
"""快速搜索模块 V1.0.0

优化策略：
1. 预加载索引到内存
2. 使用字典快速查找
3. 结果缓存
"""

import json
import time
from pathlib import Path
from functools import lru_cache

class FastSearch:
    """快速搜索器"""
    
    _instance = None
    _keyword_index = None
    _loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def _load_index(self):
        """延迟加载索引"""
        if self._loaded:
            return
        
        kw_path = Path('memory_context/index/keyword_index.json')
        if kw_path.exists():
            with open(kw_path) as f:
                self._keyword_index = json.load(f)
        
        self._loaded = True
    
    @lru_cache(maxsize=100)
    def search(self, query: str, limit: int = 10) -> list:
        """搜索关键词"""
        self._load_index()
        
        if not self._keyword_index:
            return []
        
        query_lower = query.lower()
        results = []
        
        for keyword, files in self._keyword_index.items():
            if query_lower in keyword.lower():
                results.append({
                    'keyword': keyword,
                    'files': files[:limit]
                })
                if len(results) >= limit:
                    break
        
        return results
    
    def benchmark(self) -> dict:
        """性能基准测试"""
        # 预热
        self.search('skill')
        
        # 测试
        start = time.time()
        for _ in range(100):
            self.search('skill')
        elapsed = (time.time() - start) * 1000 / 100
        
        return {
            'avg_search_time_ms': round(elapsed, 2),
            'cache_info': str(self.search.cache_info())
        }

if __name__ == '__main__':
    searcher = FastSearch()
    
    print("快速搜索模块测试")
    print("=" * 40)
    
    # 搜索测试
    results = searcher.search('skill')
    print(f"搜索 'skill': {len(results)} 结果")
    
    # 性能测试
    bench = searcher.benchmark()
    print(f"平均搜索时间: {bench['avg_search_time_ms']}ms")
    print(f"缓存信息: {bench['cache_info']}")
