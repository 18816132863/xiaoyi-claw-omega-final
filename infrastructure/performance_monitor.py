#!/usr/bin/env python3
"""性能监控模块 V1.0.0

实时监控关键性能指标
"""

import time
import json
from pathlib import Path
from datetime import datetime
from functools import wraps

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {}
        self.history = []
        self.history_file = Path('reports/performance_history.json')
        self._load_history()
    
    def _load_history(self):
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    self.history = json.load(f)
            except:
                self.history = []
    
    def _save_history(self):
        """保存历史记录"""
        self.history_file.parent.mkdir(exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.history[-100:], f)  # 只保留最近 100 条
    
    def record(self, name: str, value: float, unit: str = 'ms'):
        """记录指标"""
        self.metrics[name] = {
            'value': round(value, 2),
            'unit': unit,
            'timestamp': datetime.now().isoformat()
        }
    
    def timeit(self, name: str):
        """计时装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                elapsed = (time.time() - start) * 1000
                self.record(name, elapsed, 'ms')
                return result
            return wrapper
        return decorator
    
    def snapshot(self):
        """生成快照"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics.copy()
        }
        self.history.append(snapshot)
        self._save_history()
        return snapshot
    
    def report(self):
        """生成报告"""
        print("=" * 50)
        print("性能监控报告")
        print("=" * 50)
        
        for name, data in self.metrics.items():
            print(f"  {name}: {data['value']} {data['unit']}")
        
        print(f"\n历史记录: {len(self.history)} 条")

# 全局监控器
monitor = PerformanceMonitor()

if __name__ == '__main__':
    # 测试
    @monitor.timeit('test_operation')
    def test_func():
        time.sleep(0.01)
        return 'done'
    
    test_func()
    monitor.record('custom_metric', 42.5, 'ms')
    monitor.snapshot()
    monitor.report()
