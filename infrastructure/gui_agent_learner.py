#!/usr/bin/env python3
"""GUI Agent 自动学习模块 V1.0.0

功能：
1. 自动记录每次操作
2. 提取操作模式
3. 生成模板
4. 下次直接使用模板
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class GUIAgentLearner:
    """GUI Agent 学习器"""
    
    def __init__(self):
        self.history_file = Path('cache/gui_operation_history.json')
        self.templates_file = Path('cache/gui_learned_templates.json')
        self.history: List[dict] = []
        self.templates: Dict[str, dict] = {}
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
            json.dump(self.history[-100:], f, indent=2)  # 只保留最近100条
        
        with open(self.templates_file, 'w') as f:
            json.dump(self.templates, f, indent=2)
    
    def _generate_key(self, query: str) -> str:
        """生成查询键"""
        # 提取关键词
        keywords = query.lower().split()
        key = '_'.join(keywords[:3])  # 取前3个词
        return hashlib.md5(key.encode()).hexdigest()[:8]
    
    def record(self, query: str, operations: list, success: bool, duration: float):
        """记录操作"""
        record = {
            'query': query,
            'key': self._generate_key(query),
            'operations': operations,
            'success': success,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        
        self.history.append(record)
        
        # 如果成功，尝试学习
        if success and operations:
            self._learn(record)
        
        self._save()
        return record
    
    def _learn(self, record: dict):
        """学习操作模式"""
        key = record['key']
        query = record['query']
        operations = record['operations']
        
        # 检查是否已有类似模板
        if key in self.templates:
            # 更新模板（取平均）
            existing = self.templates[key]
            existing['count'] += 1
            existing['avg_duration'] = (
                (existing['avg_duration'] * (existing['count'] - 1) + record['duration'])
                / existing['count']
            )
            existing['last_used'] = record['timestamp']
        else:
            # 创建新模板
            self.templates[key] = {
                'query_pattern': query,
                'operations': operations,
                'count': 1,
                'avg_duration': record['duration'],
                'created': record['timestamp'],
                'last_used': record['timestamp']
            }
    
    def find_template(self, query: str) -> Optional[dict]:
        """查找匹配的模板"""
        key = self._generate_key(query)
        
        if key in self.templates:
            return self.templates[key]
        
        # 模糊匹配
        query_lower = query.lower()
        for k, tmpl in self.templates.items():
            if any(word in tmpl['query_pattern'].lower() for word in query_lower.split()):
                return tmpl
        
        return None
    
    def get_stats(self) -> dict:
        """获取统计"""
        return {
            'total_operations': len(self.history),
            'successful_operations': sum(1 for h in self.history if h['success']),
            'learned_templates': len(self.templates),
            'success_rate': sum(1 for h in self.history if h['success']) / len(self.history) * 100 if self.history else 0
        }
    
    def report(self):
        """生成报告"""
        stats = self.get_stats()
        
        print("=" * 50)
        print("GUI Agent 学习报告")
        print("=" * 50)
        
        print(f"\n操作统计:")
        print(f"  总操作数: {stats['total_operations']}")
        print(f"  成功操作: {stats['successful_operations']}")
        print(f"  成功率: {stats['success_rate']:.1f}%")
        
        print(f"\n学习成果:")
        print(f"  已学模板: {stats['learned_templates']} 个")
        
        if self.templates:
            print(f"\n模板列表:")
            for key, tmpl in list(self.templates.items())[:5]:
                print(f"  - {tmpl['query_pattern'][:30]}... ({tmpl['count']}次, {tmpl['avg_duration']:.1f}秒)")

# 全局学习器
learner = GUIAgentLearner()

if __name__ == '__main__':
    # 测试
    learner.record(
        query="打开微信发送消息给张三",
        operations=['open_app:wechat', 'click_chat', 'input:张三', 'send'],
        success=True,
        duration=15.5
    )
    
    learner.record(
        query="打开微信",
        operations=['open_app:wechat'],
        success=True,
        duration=3.2
    )
    
    learner.report()
    
    # 测试查找模板
    print("\n测试查找模板:")
    tmpl = learner.find_template("打开微信")
    if tmpl:
        print(f"  找到模板: {tmpl['operations']}")
