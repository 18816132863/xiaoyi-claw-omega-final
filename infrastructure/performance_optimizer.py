#!/usr/bin/env python3
"""
性能优化模块 - V1.0.0

职责：
1. 规则引擎缓存
2. 技能注册表缓存
3. 记忆索引懒加载
4. 并行检查支持
"""

import os
import sys
import json
import hashlib
import pickle
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from functools import lru_cache
import concurrent.futures

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


class RuleEngineCache:
    """规则引擎缓存"""
    
    def __init__(self, root: Path):
        self.root = root
        self.cache_dir = root / "cache" / "rule_engine"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.registry_cache = None
        self.exceptions_cache = None
    
    def _file_hash(self, filepath: Path) -> str:
        """计算文件哈希"""
        if not filepath.exists():
            return ""
        return hashlib.md5(filepath.read_bytes()).hexdigest()[:8]
    
    def _cache_valid(self, cache_file: Path, source_files: List[Path]) -> bool:
        """检查缓存是否有效"""
        if not cache_file.exists():
            return False
        
        try:
            cache_data = pickle.load(open(cache_file, 'rb'))
            cached_hashes = cache_data.get('source_hashes', {})
            
            for source in source_files:
                if source.exists():
                    current_hash = self._file_hash(source)
                    if cached_hashes.get(str(source)) != current_hash:
                        return False
            return True
        except:
            return False
    
    def get_registry(self) -> Dict:
        """获取规则注册表（带缓存）"""
        if self.registry_cache is not None:
            return self.registry_cache
        
        registry_path = self.root / "core/RULE_REGISTRY.json"
        cache_file = self.cache_dir / "registry.cache"
        
        if self._cache_valid(cache_file, [registry_path]):
            try:
                self.registry_cache = pickle.load(open(cache_file, 'rb'))['data']
                return self.registry_cache
            except:
                pass
        
        # 加载并缓存
        self.registry_cache = json.load(open(registry_path, encoding='utf-8'))
        
        cache_data = {
            'data': self.registry_cache,
            'source_hashes': {str(registry_path): self._file_hash(registry_path)},
            'cached_at': datetime.now().isoformat()
        }
        pickle.dump(cache_data, open(cache_file, 'wb'))
        
        return self.registry_cache
    
    def get_exceptions(self) -> Dict:
        """获取规则例外（带缓存）"""
        if self.exceptions_cache is not None:
            return self.exceptions_cache
        
        exceptions_path = self.root / "core/RULE_EXCEPTIONS.json"
        cache_file = self.cache_dir / "exceptions.cache"
        
        if exceptions_path.exists():
            if self._cache_valid(cache_file, [exceptions_path]):
                try:
                    self.exceptions_cache = pickle.load(open(cache_file, 'rb'))['data']
                    return self.exceptions_cache
                except:
                    pass
            
            self.exceptions_cache = json.load(open(exceptions_path, encoding='utf-8'))
            
            cache_data = {
                'data': self.exceptions_cache,
                'source_hashes': {str(exceptions_path): self._file_hash(exceptions_path)},
                'cached_at': datetime.now().isoformat()
            }
            pickle.dump(cache_data, open(cache_file, 'wb'))
        else:
            self.exceptions_cache = {"exceptions": []}
        
        return self.exceptions_cache
    
    def invalidate(self):
        """清除缓存"""
        self.registry_cache = None
        self.exceptions_cache = None
        for f in self.cache_dir.glob("*.cache"):
            f.unlink()


class SkillRegistryCache:
    """技能注册表缓存"""
    
    def __init__(self, root: Path):
        self.root = root
        self.cache_dir = root / "cache" / "skills"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache = None
    
    def scan_skills(self, force_refresh: bool = False) -> List[Dict]:
        """扫描技能（带缓存）"""
        cache_file = self.cache_dir / "skill_registry.cache"
        skills_dir = self.root / "skills"
        
        # 检查缓存
        if not force_refresh and cache_file.exists():
            try:
                cache_data = pickle.load(open(cache_file, 'rb'))
                # 检查缓存时间（1小时内有效）
                cached_time = datetime.fromisoformat(cache_data.get('cached_at', '2000-01-01'))
                if (datetime.now() - cached_time).total_seconds() < 3600:
                    return cache_data['skills']
            except:
                pass
        
        # 扫描技能
        skills = []
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            
            skill_info = {
                'name': skill_dir.name,
                'path': str(skill_dir),
                'skill_md': str(skill_md)
            }
            
            # 读取 SKILL.md 元信息
            try:
                content = skill_md.read_text(encoding='utf-8')
                for line in content.split('\n')[:20]:
                    if line.startswith('name:'):
                        skill_info['display_name'] = line.split(':', 1)[1].strip()
                    elif line.startswith('version:'):
                        skill_info['version'] = line.split(':', 1)[1].strip()
            except:
                pass
            
            skills.append(skill_info)
        
        # 缓存结果
        cache_data = {
            'skills': skills,
            'count': len(skills),
            'cached_at': datetime.now().isoformat()
        }
        pickle.dump(cache_data, open(cache_file, 'wb'))
        
        return skills
    
    def get_skill_count(self) -> int:
        """获取技能数量"""
        skills = self.scan_skills()
        return len(skills)


class ParallelChecker:
    """并行检查器"""
    
    def __init__(self, root: Path, max_workers: int = 4):
        self.root = root
        self.max_workers = max_workers
    
    def run_checkers_parallel(self, checkers: List[Dict]) -> Dict:
        """并行运行检查器"""
        results = {
            'passed': [],
            'failed': [],
            'errors': []
        }
        
        def run_checker(checker):
            import subprocess
            script = checker['script']
            try:
                proc = subprocess.run(
                    [sys.executable, str(self.root / script)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=self.root
                )
                return {
                    'name': checker['name'],
                    'script': script,
                    'passed': proc.returncode == 0,
                    'output': proc.stdout[-500:] if proc.stdout else ''
                }
            except Exception as e:
                return {
                    'name': checker['name'],
                    'script': script,
                    'passed': False,
                    'error': str(e)
                }
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(run_checker, c): c for c in checkers}
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result['passed']:
                    results['passed'].append(result['name'])
                else:
                    results['failed'].append(result['name'])
                    if result.get('error'):
                        results['errors'].append({
                            'name': result['name'],
                            'error': result['error']
                        })
        
        return results


class MemoryIndexLazyLoader:
    """记忆索引懒加载器"""
    
    def __init__(self, root: Path):
        self.root = root
        self.index_dir = root / "memory_context" / "index"
        self._fts_index = None
        self._keyword_index = None
    
    def _load_gzipped_json(self, filepath: Path) -> Dict:
        """加载 gzip 压缩的 JSON"""
        import gzip
        if not filepath.exists():
            return {}
        try:
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def get_fts_index(self) -> Dict:
        """获取全文索引（懒加载）"""
        if self._fts_index is None:
            fts_path = self.index_dir / "fts_index.json.gz"
            self._fts_index = self._load_gzipped_json(fts_path)
        return self._fts_index
    
    def get_keyword_index(self) -> Dict:
        """获取关键词索引（懒加载）"""
        if self._keyword_index is None:
            keyword_path = self.index_dir / "keyword_index.json.gz"
            self._keyword_index = self._load_gzipped_json(keyword_path)
        return self._keyword_index
    
    def clear_cache(self):
        """清除内存缓存"""
        self._fts_index = None
        self._keyword_index = None


def benchmark():
    """性能基准测试"""
    import time
    
    root = get_project_root()
    
    print("╔══════════════════════════════════════════════════╗")
    print("║          性能优化模块 V1.0.0                   ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    # 1. 规则引擎缓存测试
    print("【规则引擎缓存】")
    cache = RuleEngineCache(root)
    
    start = time.time()
    registry1 = cache.get_registry()
    first_load = time.time() - start
    print(f"  首次加载: {first_load*1000:.2f}ms")
    
    start = time.time()
    registry2 = cache.get_registry()
    cached_load = time.time() - start
    print(f"  缓存加载: {cached_load*1000:.2f}ms")
    print(f"  性能提升: {first_load/cached_load:.1f}x")
    print()
    
    # 2. 技能注册表缓存测试
    print("【技能注册表缓存】")
    skill_cache = SkillRegistryCache(root)
    
    start = time.time()
    skills1 = skill_cache.scan_skills(force_refresh=True)
    first_scan = time.time() - start
    print(f"  首次扫描: {first_scan*1000:.2f}ms ({len(skills1)} 个技能)")
    
    start = time.time()
    skills2 = skill_cache.scan_skills()
    cached_scan = time.time() - start
    print(f"  缓存扫描: {cached_scan*1000:.2f}ms")
    print(f"  性能提升: {first_scan/cached_scan:.1f}x")
    print()
    
    # 3. 记忆索引懒加载测试
    print("【记忆索引懒加载】")
    lazy_loader = MemoryIndexLazyLoader(root)
    
    start = time.time()
    fts = lazy_loader.get_fts_index()
    fts_load = time.time() - start
    print(f"  FTS 索引加载: {fts_load*1000:.2f}ms ({len(fts)} 条)")
    
    start = time.time()
    fts2 = lazy_loader.get_fts_index()
    fts_cached = time.time() - start
    print(f"  FTS 索引缓存: {fts_cached*1000:.2f}ms")
    print()
    
    print("✅ 性能优化模块就绪")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="性能优化模块 V1.0.0")
    parser.add_argument("--benchmark", action="store_true", help="运行性能基准测试")
    parser.add_argument("--clear-cache", action="store_true", help="清除所有缓存")
    args = parser.parse_args()
    
    if args.benchmark:
        benchmark()
    elif args.clear_cache:
        root = get_project_root()
        cache_dir = root / "cache"
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
        print("✅ 缓存已清除")
    else:
        benchmark()
