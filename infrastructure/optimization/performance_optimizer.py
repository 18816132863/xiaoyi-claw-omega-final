#!/usr/bin/env python3
"""
性能优化器 V1.0.0

优化目标：
1. 索引压缩（47M → 10M）
2. 技能懒加载
3. 缓存策略
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import shutil

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent

class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self):
        self.root = get_project_root()
        self.index_dir = self.root / 'memory_context' / 'index'
        self.registry_path = self.root / 'infrastructure' / 'inventory' / 'skill_registry.json'
        self.results = {
            'index_optimization': {},
            'skill_optimization': {},
            'cache_setup': {}
        }
    
    def analyze_index(self) -> dict:
        """分析索引文件"""
        analysis = {}
        for idx_file in self.index_dir.glob('*.json'):
            if idx_file.name == 'index_metadata.json':
                continue
            size_mb = idx_file.stat().st_size / (1024 * 1024)
            analysis[idx_file.name] = {
                'size_mb': round(size_mb, 2),
                'path': str(idx_file)
            }
        return analysis
    
    def optimize_index(self) -> dict:
        """优化索引文件"""
        results = {}
        
        # 1. 清理空向量索引
        vector_index = self.index_dir / 'vector_index.json'
        if vector_index.exists():
            try:
                with open(vector_index, 'r') as f:
                    data = json.load(f)
                
                # 如果是空数组，压缩为最小格式
                if isinstance(data, list) and len(data) == 0:
                    with open(vector_index, 'w') as f:
                        json.dump([], f, separators=(',', ':'))
                    results['vector_index'] = 'compressed_empty'
                elif isinstance(data, dict) and len(data) == 0:
                    with open(vector_index, 'w') as f:
                        json.dump({}, f, separators=(',', ':'))
                    results['vector_index'] = 'compressed_empty'
            except Exception as e:
                results['vector_index'] = f'error: {e}'
        
        # 2. 压缩 keyword_index
        keyword_index = self.index_dir / 'keyword_index.json'
        if keyword_index.exists():
            try:
                with open(keyword_index, 'r') as f:
                    data = json.load(f)
                
                # 压缩存储
                with open(keyword_index, 'w') as f:
                    json.dump(data, f, separators=(',', ':'), ensure_ascii=True)
                
                new_size = keyword_index.stat().st_size / (1024 * 1024)
                results['keyword_index'] = f'compressed to {round(new_size, 2)}MB'
            except Exception as e:
                results['keyword_index'] = f'error: {e}'
        
        # 3. 压缩 fts_index
        fts_index = self.index_dir / 'fts_index.json'
        if fts_index.exists():
            try:
                with open(fts_index, 'r') as f:
                    data = json.load(f)
                
                # 压缩存储
                with open(fts_index, 'w') as f:
                    json.dump(data, f, separators=(',', ':'), ensure_ascii=True)
                
                new_size = fts_index.stat().st_size / (1024 * 1024)
                results['fts_index'] = f'compressed to {round(new_size, 2)}MB'
            except Exception as e:
                results['fts_index'] = f'error: {e}'
        
        return results
    
    def optimize_registry(self) -> dict:
        """优化技能注册表"""
        results = {}
        
        if not self.registry_path.exists():
            return {'error': 'registry not found'}
        
        try:
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
            
            skills = data.get('skills', {})
            total = len(skills)
            
            # 统计活跃技能
            active = sum(1 for s in skills.values() if s.get('callable', False))
            
            # 压缩存储
            with open(self.registry_path, 'w') as f:
                json.dump(data, f, separators=(',', ':'), ensure_ascii=True)
            
            new_size = self.registry_path.stat().st_size / 1024
            results = {
                'total_skills': total,
                'active_skills': active,
                'inactive_skills': total - active,
                'new_size_kb': round(new_size, 2)
            }
        except Exception as e:
            results = {'error': str(e)}
        
        return results
    
    def setup_cache(self) -> dict:
        """设置缓存目录"""
        results = {}
        
        cache_dir = self.root / 'cache'
        cache_dir.mkdir(exist_ok=True)
        
        # 创建缓存子目录
        (cache_dir / 'skill_metadata').mkdir(exist_ok=True)
        (cache_dir / 'search_results').mkdir(exist_ok=True)
        (cache_dir / 'vectors').mkdir(exist_ok=True)
        
        # 创建缓存配置
        cache_config = {
            'created': datetime.now().isoformat(),
            'directories': ['skill_metadata', 'search_results', 'vectors'],
            'ttl_seconds': {
                'skill_metadata': 3600,
                'search_results': 300,
                'vectors': 86400
            }
        }
        
        with open(cache_dir / 'cache_config.json', 'w') as f:
            json.dump(cache_config, f, indent=2)
        
        results['cache_dir'] = str(cache_dir)
        results['status'] = 'created'
        
        return results
    
    def run(self):
        """执行优化"""
        print("╔══════════════════════════════════════════════════╗")
        print("║          性能优化器 V1.0.0                      ║")
        print("╚══════════════════════════════════════════════════╝")
        
        # 1. 分析索引
        print("\n【索引分析】")
        analysis = self.analyze_index()
        total_size = 0
        for name, info in analysis.items():
            print(f"  {name}: {info['size_mb']} MB")
            total_size += info['size_mb']
        print(f"  总计: {round(total_size, 2)} MB")
        
        # 2. 优化索引
        print("\n【索引优化】")
        index_results = self.optimize_index()
        for name, result in index_results.items():
            print(f"  {name}: {result}")
        
        # 3. 优化注册表
        print("\n【注册表优化】")
        registry_results = self.optimize_registry()
        for key, value in registry_results.items():
            print(f"  {key}: {value}")
        
        # 4. 设置缓存
        print("\n【缓存设置】")
        cache_results = self.setup_cache()
        print(f"  缓存目录: {cache_results['cache_dir']}")
        print(f"  状态: {cache_results['status']}")
        
        # 5. 最终统计
        print("\n【优化结果】")
        new_analysis = self.analyze_index()
        new_total = sum(info['size_mb'] for info in new_analysis.values())
        saved = total_size - new_total
        print(f"  优化前: {round(total_size, 2)} MB")
        print(f"  优化后: {round(new_total, 2)} MB")
        print(f"  节省: {round(saved, 2)} MB ({round(saved/total_size*100, 1)}%)")

if __name__ == '__main__':
    optimizer = PerformanceOptimizer()
    optimizer.run()
