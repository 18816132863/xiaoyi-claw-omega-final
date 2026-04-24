#!/usr/bin/env python3
"""GUI Agent 智能执行器 V1.0.0

自动判断是否使用模板：
1. 首次操作 → 正常执行 + 记录
2. 二次操作 → 自动加载模板
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))

class SmartGUIExecutor:
    """智能 GUI 执行器"""
    
    def __init__(self):
        self.history_file = Path('cache/gui_operation_history.json')
        self.templates_file = Path('cache/gui_learned_templates.json')
        self.history = []
        self.templates = {}
        self._load()
    
    def _load(self):
        """加载数据"""
        self.history_file.parent.mkdir(exist_ok=True)
        
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    self.history = json.load(f)
            except:
                self.history = []
        
        if self.templates_file.exists():
            try:
                with open(self.templates_file) as f:
                    self.templates = json.load(f)
            except:
                self.templates = {}
    
    def _save(self):
        """保存数据"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history[-100:], f, indent=2)
        
        with open(self.templates_file, 'w') as f:
            json.dump(self.templates, f, indent=2)
    
    def _generate_key(self, query: str) -> str:
        """生成查询键"""
        import hashlib
        keywords = query.lower().split()
        key = '_'.join(keywords[:3])
        return hashlib.md5(key.encode()).hexdigest()[:8]
    
    def execute(self, query: str) -> Tuple[bool, str, Optional[dict]]:
        """智能执行"""
        key = self._generate_key(query)
        
        if key in self.templates:
            template = self.templates[key]
            return (
                True,
                'template',
                {
                    'operations': template['operations'],
                    'estimated_time': template['avg_duration'],
                    'usage_count': template['count']
                }
            )
        else:
            return (
                False,
                'learn',
                {
                    'message': '首次操作，将记录学习',
                    'will_create_template': True
                }
            )
    
    def after_execute(self, query: str, operations: list, success: bool, duration: float):
        """执行后记录"""
        key = self._generate_key(query)
        
        record = {
            'query': query,
            'key': key,
            'operations': operations,
            'success': success,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        
        self.history.append(record)
        
        if success and operations:
            if key in self.templates:
                existing = self.templates[key]
                existing['count'] += 1
                existing['avg_duration'] = (
                    (existing['avg_duration'] * (existing['count'] - 1) + duration)
                    / existing['count']
                )
                existing['last_used'] = record['timestamp']
            else:
                self.templates[key] = {
                    'query_pattern': query,
                    'operations': operations,
                    'count': 1,
                    'avg_duration': duration,
                    'created': record['timestamp'],
                    'last_used': record['timestamp']
                }
        
        self._save()
        
        if success:
            return f"✅ 操作成功，已学习 ({duration:.1f}秒)"
        else:
            return f"❌ 操作失败，已记录"
    
    def status(self) -> dict:
        """获取状态"""
        total = len(self.history)
        success = sum(1 for h in self.history if h['success'])
        
        return {
            'learned_templates': len(self.templates),
            'total_operations': total,
            'success_rate': success / total * 100 if total > 0 else 0
        }
    
    def report(self):
        """生成报告"""
        print("=" * 50)
        print("GUI Agent 智能执行器")
        print("=" * 50)
        
        stats = self.status()
        print(f"\n状态:")
        print(f"  已学模板: {stats['learned_templates']} 个")
        print(f"  总操作数: {stats['total_operations']}")
        print(f"  成功率: {stats['success_rate']:.1f}%")
        
        if self.templates:
            print(f"\n已学模板:")
            for key, tmpl in list(self.templates.items())[:5]:
                print(f"  - {tmpl['query_pattern'][:30]}... ({tmpl['count']}次)")

if __name__ == '__main__':
    executor = SmartGUIExecutor()
    
    # 测试1: 首次操作
    print("\n测试1: 首次操作 '打开支付宝'")
    use_template, mode, info = executor.execute("打开支付宝")
    print(f"  使用模板: {use_template}")
    print(f"  执行方式: {mode}")
    
    # 模拟执行后记录
    result = executor.after_execute("打开支付宝", ['open_app:alipay'], True, 5.2)
    print(f"  结果: {result}")
    
    # 测试2: 第二次操作
    print("\n测试2: 第二次操作 '打开支付宝'")
    use_template, mode, info = executor.execute("打开支付宝")
    print(f"  使用模板: {use_template}")
    print(f"  执行方式: {mode}")
    print(f"  模板信息: {info}")
    
    executor.report()
