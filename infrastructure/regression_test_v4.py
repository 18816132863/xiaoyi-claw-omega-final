#!/usr/bin/env python3
"""
回归测试脚本 - V1.0

固化第三阶段验收标准，避免重复修同类问题
"""

import os
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_search_quality():
    """搜索质量回归"""
    from memory_context.unified_search import UnifiedSearch
    
    search = UnifiedSearch()
    
    test_cases = [
        ("docx", 1),
        ("pdf", 1),
        ("architecture", 1),
        ("embedding", 1),
        ("skill_registry", 1),
    ]
    
    results = []
    for query, min_results in test_cases:
        result = search.search(query, limit=5)
        passed = result.get("total", 0) >= min_results
        results.append({
            "query": query,
            "total": result.get("total", 0),
            "passed": passed
        })
    
    return all(r["passed"] for r in results), results


def test_embedding_status():
    """Embedding 状态回归"""
    from memory_context.unified_search import QwenEmbeddingEngine
    
    engine = QwenEmbeddingEngine()
    config = engine.get_config_info()
    
    results = {
        "config_loaded": config["config_loaded"],
        "connection_ok": config["connection_ok"],
        "mode": config["mode"],
        "reason": config["reason"],
    }
    
    passed = (
        config["config_loaded"] and
        config["connection_ok"] and
        config["mode"] == "embedding"
    )
    
    return passed, results


def test_cold_start():
    """冷启动回归"""
    # 简化版：只测试 build_index
    from memory_context.unified_search import UnifiedSearch
    
    search = UnifiedSearch()
    result = search.build_index(force=False)
    
    passed = result["mode"] == "loaded"
    results = {
        "mode": result["mode"],
        "files_indexed": result["files_indexed"],
    }
    
    return passed, results


def run_all_tests():
    """运行所有回归测试"""
    print("╔══════════════════════════════════════════════════╗")
    print("║        回归测试 V1.0                             ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    all_passed = True
    
    # 1. 搜索质量
    print("【1】搜索质量回归")
    passed, results = test_search_quality()
    for r in results:
        status = "✅" if r["passed"] else "❌"
        print(f"  {status} {r["query"]}: {r["total"]} 结果")
    all_passed = all_passed and passed
    print()
    
    # 2. Embedding 状态
    print("【2】Embedding 状态回归")
    passed, results = test_embedding_status()
    for k, v in results.items():
        print(f"  {k}: {v}")
    all_passed = all_passed and passed
    print()
    
    # 3. 冷启动
    print("【3】冷启动回归")
    passed, results = test_cold_start()
    for k, v in results.items():
        print(f"  {k}: {v}")
    all_passed = all_passed and passed
    print()
    
    print("══════════════════════════════════════════════════")
    if all_passed:
        print("✅ 所有回归测试通过")
    else:
        print("❌ 部分回归测试失败")
    print("══════════════════════════════════════════════════")
    
    return all_passed


if __name__ == "__main__":
    passed = run_all_tests()
    sys.exit(0 if passed else 1)
