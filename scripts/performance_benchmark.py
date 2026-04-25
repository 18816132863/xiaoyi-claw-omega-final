#!/usr/bin/env python3
"""性能基准测试 V1.0.0"""

import time
import json
from pathlib import Path

def benchmark_startup():
    """测试启动性能"""
    start = time.time()
    
    # 模拟加载核心文件
    core_files = [
        "MEMORY.md",
        "AGENTS.md", 
        "TOOLS.md",
        "core/ARCHITECTURE.md"
    ]
    
    for f in core_files:
        if Path(f).exists():
            Path(f).read_text(errors='ignore')
    
    elapsed = (time.time() - start) * 1000
    return elapsed

def benchmark_skill_registry():
    """测试技能注册表加载"""
    start = time.time()
    
    reg_path = Path("infrastructure/inventory/skill_registry.json")
    if reg_path.exists():
        data = json.loads(reg_path.read_text())
        skills = data.get("skills", {})
        count = len(skills)
    else:
        count = 0
    
    elapsed = (time.time() - start) * 1000
    return elapsed, count

def benchmark_search():
    """测试搜索性能"""
    start = time.time()
    
    # 模拟关键词搜索
    kw_path = Path("memory_context/index/keyword_index.json")
    if kw_path.exists():
        kw = json.loads(kw_path.read_text())
        results = [k for k in kw.keys() if "skill" in k.lower()][:10]
    else:
        results = []
    
    elapsed = (time.time() - start) * 1000
    return elapsed, len(results)

def main():
    print("=" * 50)
    print("性能基准测试 V1.0.0")
    print("=" * 50)
    
    # 启动性能
    startup_ms = benchmark_startup()
    print(f"\n启动加载: {startup_ms:.1f}ms {'✅' if startup_ms < 100 else '⚠️'}")
    
    # 技能注册表
    reg_ms, skill_count = benchmark_skill_registry()
    print(f"技能注册表: {reg_ms:.1f}ms ({skill_count} 技能) {'✅' if reg_ms < 50 else '⚠️'}")
    
    # 搜索性能
    search_ms, result_count = benchmark_search()
    print(f"关键词搜索: {search_ms:.1f}ms ({result_count} 结果) {'✅' if search_ms < 10 else '⚠️'}")
    
    # 总体评分
    total_score = 0
    if startup_ms < 100: total_score += 1
    if reg_ms < 50: total_score += 1
    if search_ms < 10: total_score += 1
    
    print(f"\n总体评分: {total_score}/3 {'✅ 优秀' if total_score == 3 else '⚠️ 需优化'}")

if __name__ == "__main__":
    main()
