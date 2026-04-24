#!/usr/bin/env python3
"""快速启动脚本 V1.0.0

优化启动流程，减少加载时间
"""

import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

class QuickStart:
    """快速启动器"""
    
    def __init__(self):
        self.loaded = {}
        self.start_time = time.time()
    
    def load_core_files(self):
        """并行加载核心文件"""
        core_files = [
            'MEMORY.md',
            'AGENTS.md',
            'TOOLS.md',
            'SOUL.md',
            'USER.md',
            'IDENTITY.md',
            'HEARTBEAT.md',
            'core/ARCHITECTURE.md'
        ]
        
        def load_file(path):
            if Path(path).exists():
                return path, Path(path).read_text(errors='ignore')
            return path, None
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = executor.map(load_file, core_files)
            for path, content in results:
                if content:
                    self.loaded[path] = len(content)
        
        return len(self.loaded)
    
    def load_skill_registry(self):
        """加载技能注册表"""
        reg_path = Path('infrastructure/inventory/skill_registry.json')
        if reg_path.exists():
            with open(reg_path) as f:
                data = json.load(f)
            skills = data.get('skills', {})
            active = sum(1 for s in skills.values() if s.get('callable'))
            return len(skills), active
        return 0, 0
    
    def startup(self):
        """执行启动"""
        print("=" * 50)
        print("快速启动 V1.0.0")
        print("=" * 50)
        
        # 1. 加载核心文件
        start = time.time()
        core_count = self.load_core_files()
        core_time = (time.time() - start) * 1000
        print(f"\n核心文件: {core_count} 个 ({core_time:.1f}ms)")
        
        # 2. 加载技能注册表
        start = time.time()
        total, active = self.load_skill_registry()
        reg_time = (time.time() - start) * 1000
        print(f"技能注册表: {active}/{total} 活跃 ({reg_time:.1f}ms)")
        
        # 3. 总耗时
        total_time = (time.time() - self.start_time) * 1000
        print(f"\n总启动时间: {total_time:.1f}ms")
        
        # 4. 评估
        if total_time < 50:
            print("状态: ✅ 优秀")
        elif total_time < 100:
            print("状态: ✅ 良好")
        else:
            print("状态: ⚠️ 需优化")
        
        return {
            'core_files': core_count,
            'core_time_ms': core_time,
            'registry_time_ms': reg_time,
            'total_time_ms': total_time,
            'active_skills': active,
            'total_skills': total
        }

if __name__ == '__main__':
    starter = QuickStart()
    starter.startup()
