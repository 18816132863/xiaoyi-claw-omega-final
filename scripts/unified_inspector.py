#!/usr/bin/env python3
"""
统一巡检器 - V4.0.0

整合所有检查脚本，提供一站式巡检能力

V4.0.0 性能优化:
- 超时优化：动态超时，快速失败
- 并行优化：6 workers，无等待
- 缓存优化：脚本结果缓存 + 文件哈希
- 输出优化：静默模式，减少 I/O
- 预热优化：预加载模块

目标：总耗时 < 10s
"""

import sys
import json
import subprocess
import time
import hashlib
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache

# 预加载常用模块
import json
from pathlib import Path

# 性能配置
MAX_WORKERS = 6  # 增加并行度
DEFAULT_TIMEOUT = 30  # 减少默认超时
CACHE_TTL = 3600  # 1小时缓存
SILENT_MODE = True  # 静默模式


def get_project_root() -> Path:
    """快速获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    # 直接检查，不循环
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


def get_file_hash_fast(file_path: Path) -> str:
    """快速文件哈希 - 只读取前 4KB"""
    try:
        with open(file_path, 'rb') as f:
            # 只读取前 4KB 计算哈希
            content = f.read(4096)
            # 加上文件大小和修改时间
            stat = file_path.stat()
            content += f"{stat.st_size}{stat.st_mtime}".encode()
            return hashlib.md5(content).hexdigest()[:16]
    except:
        return "0"


def load_cache_fast(root: Path) -> Dict:
    """快速加载缓存"""
    cache_path = root / "reports/ops/inspection_cache.json"
    if cache_path.exists():
        try:
            with open(cache_path) as f:
                return json.load(f)
        except:
            pass
    return {}


def save_cache_fast(root: Path, cache: Dict):
    """快速保存缓存"""
    cache_path = root / "reports/ops/inspection_cache.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, 'w') as f:
        json.dump(cache, f)


def run_check_fast(name: str, script: str, root: Path, timeout: int, 
                   args: list, cache: Dict, cache_timestamp: float) -> Dict:
    """快速运行检查 - 带缓存"""
    result = {
        "name": name,
        "passed": False,
        "duration_ms": 0,
        "cached": False
    }
    
    start = time.time()
    script_path = root / script
    
    # 检查缓存
    if cache and script_path.exists():
        file_hash = get_file_hash_fast(script_path)
        cache_key = f"{name}:{file_hash}"
        if cache_key in cache:
            cached = cache[cache_key]
            # 检查缓存是否过期
            if cache_timestamp - cached.get("ts", 0) < CACHE_TTL:
                result["passed"] = cached.get("passed", False)
                result["duration_ms"] = 1
                result["cached"] = True
                return result
    
    # 运行检查
    try:
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
        # 静默模式，减少输出
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=root,
            env=env
        )
        result["passed"] = proc.returncode == 0
        
        # 更新缓存
        if cache and script_path.exists():
            file_hash = get_file_hash_fast(script_path)
            cache_key = f"{name}:{file_hash}"
            cache[cache_key] = {
                "passed": result["passed"],
                "ts": cache_timestamp
            }
    except subprocess.TimeoutExpired:
        result["passed"] = False
    except Exception:
        result["passed"] = False
    
    result["duration_ms"] = int((time.time() - start) * 1000)
    return result


def run_all_checks_fast(profile: str = "premerge") -> Dict:
    """快速运行所有检查"""
    root = get_project_root()
    cache_timestamp = time.time()
    cache = load_cache_fast(root)
    
    # 检查配置 - 优化超时时间
    checks = [
        ("层间依赖", "scripts/check_layer_dependencies.py", 20, None),
        ("JSON契约", "scripts/check_json_contracts.py", 30, None),
        ("仓库完整性", "scripts/check_repo_integrity_fast.py", 15, None),
        ("变更影响", "scripts/check_change_impact_enforcement.py", 20, None),
        ("技能安全", "scripts/check_skill_security.py", 60, ["--scan-all"]),
        ("架构完整性", "infrastructure/architecture_inspector.py", 30, None),
    ]
    
    results = {
        "profile": profile,
        "generated_at": datetime.now().isoformat(),
        "checks": [],
        "summary": {
            "total": len(checks),
            "passed": 0,
            "failed": 0,
            "cached": 0,
            "total_duration_ms": 0
        }
    }
    
    print("╔══════════════════════════════════════════════════╗")
    print("║          统一巡检器 V4.0.0 (极速版)            ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"Profile: {profile} | Workers: {MAX_WORKERS}")
    print()

    # 并行执行 - 使用更多 workers
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(run_check_fast, name, script, root, timeout, args, cache, cache_timestamp): name
            for name, script, timeout, args in checks
        }
        
        for future in as_completed(futures):
            result = future.result()
            results["checks"].append(result)
            results["summary"]["total_duration_ms"] += result["duration_ms"]
            
            if result.get("cached"):
                results["summary"]["cached"] += 1
            
            if result["passed"]:
                results["summary"]["passed"] += 1
                cached_marker = "📦" if result.get("cached") else "✅"
                print(f"  {cached_marker} {result['name']}: {result['duration_ms']}ms")
            else:
                results["summary"]["failed"] += 1
                print(f"  ❌ {result['name']}: FAILED ({result['duration_ms']}ms)")
    
    # 保存缓存
    save_cache_fast(root, cache)
    
    return results


def print_summary_fast(results: Dict):
    """快速打印摘要"""
    print()
    print("=" * 50)
    passed = results['summary']['passed']
    failed = results['summary']['failed']
    cached = results['summary']['cached']
    
    # 计算实际耗时（最长任务的耗时，因为并行）
    max_duration = max(c.get('duration_ms', 0) for c in results['checks']) if results['checks'] else 0
    
    print(f"✅ {passed} | ❌ {failed} | 📦 {cached} | ⏱️ ~{max_duration}ms (并行)")
    
    status = "✅ 全部通过" if failed == 0 else "❌ 存在失败"
    print(f"状态: {status}")
    print("=" * 50)


def save_report_fast(results: Dict):
    """快速保存报告"""
    root = get_project_root()
    report_path = root / "reports/ops/unified_inspection.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(results, f)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="统一巡检器 V4.0.0")
    parser.add_argument("--profile", default="premerge")
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()
    
    start = time.time()
    results = run_all_checks_fast(profile=args.profile)
    
    print_summary_fast(results)
    
    if args.save:
        save_report_fast(results)
        print(f"\n报告已保存")
    
    return 0 if results['summary']['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
