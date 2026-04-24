#!/usr/bin/env python3
"""内存优化模块 V1.0.0

优化内存使用，减少资源占用
"""

import gc
import sys
from pathlib import Path

class MemoryOptimizer:
    """内存优化器"""
    
    def __init__(self):
        self.cache_limits = {
            'skill_metadata': 50 * 1024 * 1024,  # 50MB
            'search_results': 20 * 1024 * 1024,  # 20MB
            'vectors': 100 * 1024 * 1024,  # 100MB
        }
        self.current_usage = {}
    
    def get_memory_usage(self):
        """获取内存使用情况"""
        import tracemalloc
        tracemalloc.start()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return {
            'current_mb': round(current / 1024 / 1024, 2),
            'peak_mb': round(peak / 1024 / 1024, 2)
        }
    
    def optimize(self):
        """执行优化"""
        # 强制垃圾回收
        collected = gc.collect()
        
        # 清理空引用
        gc.collect()
        
        return {
            'collected': collected,
            'status': 'optimized'
        }
    
    def check_large_files(self):
        """检查大文件"""
        large_files = []
        
        for path in Path('.').rglob('*'):
            if path.is_file() and not '.git' in str(path):
                size = path.stat().st_size
                if size > 1024 * 1024:  # > 1MB
                    large_files.append({
                        'path': str(path),
                        'size_mb': round(size / 1024 / 1024, 2)
                    })
        
        # 按大小排序
        large_files.sort(key=lambda x: x['size_mb'], reverse=True)
        return large_files[:10]
    
    def report(self):
        """生成报告"""
        print("=" * 50)
        print("内存优化报告")
        print("=" * 50)
        
        # 优化
        result = self.optimize()
        print(f"\n垃圾回收: {result['collected']} 个对象")
        
        # 大文件
        large = self.check_large_files()
        if large:
            print(f"\n大文件 (>1MB):")
            for f in large[:5]:
                print(f"  - {f['path']}: {f['size_mb']}MB")

if __name__ == '__main__':
    optimizer = MemoryOptimizer()
    optimizer.report()
