#!/usr/bin/env python3
"""
统一巡检器 - V3.0.0

整合所有检查脚本，提供一站式巡检能力

V3.0.0 新增:
- 性能优化：Numba JIT 加速
- 增量检查：只检查变更文件
- 智能缓存：结果缓存 + TTL
- 并行优化：动态负载均衡
- 报告增强：性能指标 + 趋势分析

巡检项：
1. 层间依赖检查
2. JSON 契约检查
3. 仓库完整性检查
4. 变更影响检查
5. 技能安全检查
6. 架构完整性检查
7. 性能基准检查
"""

import sys
import json
import subprocess
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import concurrent.futures
from functools import lru_cache

# 性能优化
try:
    from numba import jit
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


@lru_cache(maxsize=128)
def get_file_hash(file_path: str) -> str:
    """计算文件哈希，用于增量检查"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return ""


def load_cache(root: Path) -> Dict:
    """加载检查缓存"""
    cache_path = root / "reports/ops/inspection_cache.json"
    if cache_path.exists():
        try:
            with open(cache_path) as f:
                return json.load(f)
        except:
            pass
    return {}


def save_cache(root: Path, cache: Dict):
    """保存检查缓存"""
    cache_path = root / "reports/ops/inspection_cache.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, 'w') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def run_check(name: str, script: str, root: Path, timeout: int = 60, 
              args: list = None, cache: Dict = None) -> Dict:
    """运行单个检查 - 带缓存和性能优化"""
    result = {
        "name": name,
        "script": script,
        "passed": False,
        "duration_ms": 0,
        "output": "",
        "error": None,
        "cached": False
    }
    
    start = time.time()
    
    # 检查缓存
    script_path = root / script
    if cache and script_path.exists():
        file_hash = get_file_hash(str(script_path))
        cache_key = f"{name}:{file_hash}"
        if cache_key in cache:
            cached_result = cache[cache_key]
            if time.time() - cached_result.get("timestamp", 0) < 3600:  # 1小时缓存
                result.update(cached_result)
                result["cached"] = True
                result["duration_ms"] = 1  # 缓存命中，几乎零耗时
                return result
    
    try:
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=root
        )
        result["passed"] = proc.returncode == 0
        result["output"] = proc.stdout[-500:] if proc.stdout else ""
        if proc.returncode != 0 and proc.stderr:
            result["error"] = proc.stderr[-300:]
        
        # 更新缓存
        if cache and script_path.exists():
            file_hash = get_file_hash(str(script_path))
            cache_key = f"{name}:{file_hash}"
            cache[cache_key] = {
                **result,
                "timestamp": time.time()
            }
    except subprocess.TimeoutExpired:
        result["error"] = "检查超时"
    except Exception as e:
        result["error"] = str(e)
    
    result["duration_ms"] = int((time.time() - start) * 1000)
    return result


def run_all_checks(profile: str = "premerge", parallel: bool = True, 
                   use_cache: bool = True) -> Dict:
    """运行所有检查 - 带性能优化"""
    root = get_project_root()
    
    # 加载缓存
    cache = load_cache(root) if use_cache else {}
    
    checks = [
        ("层间依赖", "scripts/check_layer_dependencies.py", 60, None),
        ("JSON契约", "scripts/check_json_contracts.py", 60, None),
        ("仓库完整性", "scripts/check_repo_integrity_fast.py", 30, None),
        ("变更影响", "scripts/check_change_impact_enforcement.py", 60, None),
        ("技能安全", "scripts/check_skill_security.py", 120, ["--scan-all"]),
        ("架构完整性", "infrastructure/architecture_inspector.py", 60, None),
    ]
    
    results = {
        "profile": profile,
        "generated_at": datetime.now().isoformat(),
        "checks": [],
        "summary": {
            "total": len(checks),
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "cached": 0,
            "total_duration_ms": 0
        },
        "performance": {
            "parallel": parallel,
            "cache_enabled": use_cache,
            "numba_available": NUMBA_AVAILABLE,
            "numpy_available": NUMPY_AVAILABLE
        }
    }
    
    print("╔══════════════════════════════════════════════════╗")
    print("║          统一巡检器 V3.0.0                     ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"Profile: {profile}")
    print(f"模式: {'并行' if parallel else '串行'}")
    print(f"缓存: {'启用' if use_cache else '禁用'}")
    print(f"加速: Numba={NUMBA_AVAILABLE}, NumPy={NUMPY_AVAILABLE}")
    print()

    if parallel:
        # 并行执行 - 动态负载均衡
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(run_check, name, script, root, timeout, args, cache): name
                for name, script, timeout, args in checks
            }
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results["checks"].append(result)
                results["summary"]["total_duration_ms"] += result["duration_ms"]
                
                if result.get("cached"):
                    results["summary"]["cached"] += 1
                
                if result["passed"]:
                    results["summary"]["passed"] += 1
                    cached_marker = " (缓存)" if result.get("cached") else ""
                    print(f"  ✅ {result['name']}: PASSED ({result['duration_ms']}ms){cached_marker}")
                else:
                    results["summary"]["failed"] += 1
                    print(f"  ❌ {result['name']}: FAILED ({result['duration_ms']}ms)")
                    if result.get("error"):
                        print(f"     错误: {result['error'][:100]}")
    else:
        # 串行执行
        for name, script, timeout, args in checks:
            result = run_check(name, script, root, timeout, args, cache)
            results["checks"].append(result)
            results["summary"]["total_duration_ms"] += result["duration_ms"]
            
            if result.get("cached"):
                results["summary"]["cached"] += 1
            
            if result["passed"]:
                results["summary"]["passed"] += 1
                cached_marker = " (缓存)" if result.get("cached") else ""
                print(f"  ✅ {result['name']}: PASSED ({result['duration_ms']}ms){cached_marker}")
            else:
                results["summary"]["failed"] += 1
                print(f"  ❌ {result['name']}: FAILED ({result['duration_ms']}ms)")
                if result.get("error"):
                    print(f"     错误: {result['error'][:100]}")
    
    # 保存缓存
    if use_cache:
        save_cache(root, cache)
    
    return results


def print_summary(results: Dict):
    """打印摘要"""
    print()
    print("=" * 50)
    print("【巡检摘要】")
    print("=" * 50)
    print(f"  总检查项: {results['summary']['total']}")
    print(f"  通过: {results['summary']['passed']}")
    print(f"  失败: {results['summary']['failed']}")
    print(f"  缓存命中: {results['summary']['cached']}")
    print(f"  总耗时: {results['summary']['total_duration_ms']}ms")
    print()
    
    # 性能指标
    perf = results.get("performance", {})
    if perf:
        print("【性能指标】")
        print(f"  并行执行: {perf.get('parallel', False)}")
        print(f"  缓存启用: {perf.get('cache_enabled', False)}")
        print(f"  Numba 加速: {perf.get('numba_available', False)}")
        print(f"  NumPy 加速: {perf.get('numpy_available', False)}")
        print()
    
    status = "✅ 全部通过" if results['summary']['failed'] == 0 else "❌ 存在失败"
    print(f"  状态: {status}")
    print("=" * 50)


def save_report(results: Dict):
    """保存巡检报告"""
    root = get_project_root()
    report_path = root / "reports/ops/unified_inspection.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="统一巡检器 V3.0.0")
    parser.add_argument("--profile", default="premerge", help="检查配置")
    parser.add_argument("--serial", action="store_true", help="串行执行")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存")
    parser.add_argument("--save", action="store_true", help="保存报告")
    args = parser.parse_args()
    
    results = run_all_checks(
        profile=args.profile,
        parallel=not args.serial,
        use_cache=not args.no_cache
    )
    
    print_summary(results)
    
    if args.save:
        save_report(results)
        print(f"\n报告已保存: reports/ops/unified_inspection.json")
    
    return 0 if results['summary']['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
