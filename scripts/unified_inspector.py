#!/usr/bin/env python3
"""
统一巡检器 - V6.0.0

整合所有检查脚本，提供一站式巡检能力

V6.0.0 新增:
- Token 优化检查
- 注入配置验证
- 智能压缩验证
- 增量更新支持
- 完整性报告

巡检项：
1. 层间依赖检查
2. JSON 契约检查
3. 仓库完整性检查
4. 变更影响检查
5. 技能安全检查
6. 架构完整性检查
7. Token 优化检查
8. 注入配置检查
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

# 性能配置
MAX_WORKERS = 8  # 增加到 8 workers
DEFAULT_TIMEOUT = 30
CACHE_TTL = 3600


def get_project_root() -> Path:
    """快速获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


def get_file_hash_fast(file_path: Path) -> str:
    """快速文件哈希"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read(4096)
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
    """快速运行检查"""
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
            if cache_timestamp - cached.get("ts", 0) < CACHE_TTL:
                result["passed"] = cached.get("passed", False)
                result["duration_ms"] = 1
                result["cached"] = True
                return result
    
    try:
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
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


def check_token_optimization(root: Path) -> Dict:
    """检查 Token 优化状态"""
    result = {
        "name": "Token优化",
        "passed": False,
        "duration_ms": 0,
        "details": {}
    }
    
    start = time.time()
    
    try:
        # 检查必要文件
        required_files = [
            "infrastructure/inventory/skill_registry_summary.json",
            "config/injection_config.json",
            "config/injection_config_minimal.json",
            "config/injection_config_smart.json"
        ]
        
        missing = []
        for f in required_files:
            if not (root / f).exists():
                missing.append(f)
        
        if missing:
            result["details"]["missing"] = missing
        else:
            result["passed"] = True
            
            # 估算 Token
            core_files = ["SOUL.md", "USER.md", "MEMORY.md"]
            core_size = sum((root / f).stat().st_size for f in core_files if (root / f).exists())
            summary_path = root / "infrastructure/inventory/skill_registry_summary.json"
            index_size = summary_path.stat().st_size if summary_path.exists() else 0
            total_tokens = (core_size + index_size) / 3
            result["details"]["estimated_tokens"] = int(total_tokens)
            
    except Exception as e:
        result["details"]["error"] = str(e)
    
    result["duration_ms"] = int((time.time() - start) * 1000)
    return result


def check_injection_config(root: Path) -> Dict:
    """检查注入配置"""
    result = {
        "name": "注入配置",
        "passed": False,
        "duration_ms": 0,
        "details": {}
    }
    
    start = time.time()
    
    try:
        config_files = [
            ("minimal", "config/injection_config.json"),
            ("ultra_minimal", "config/injection_config_minimal.json"),
            ("smart", "config/injection_config_smart.json")
        ]
        
        modes = {}
        for mode, path in config_files:
            full_path = root / path
            if full_path.exists():
                with open(full_path) as f:
                    config = json.load(f)
                modes[mode] = {
                    "tokens": config.get("estimated_tokens", 0),
                    "files": len(config.get("inject", {}).get("core", []))
                }
        
        if len(modes) >= 2:
            result["passed"] = True
            result["details"]["modes"] = modes
        else:
            result["details"]["error"] = "缺少注入配置文件"
            
    except Exception as e:
        result["details"]["error"] = str(e)
    
    result["duration_ms"] = int((time.time() - start) * 1000)
    return result


def run_all_checks_fast(profile: str = "premerge") -> Dict:
    """快速运行所有检查"""
    root = get_project_root()
    cache_timestamp = time.time()
    cache = load_cache_fast(root)
    
    # 脚本检查
    script_checks = [
        ("层间依赖", "scripts/check_layer_dependencies.py", 20, None),
        ("JSON契约", "scripts/check_json_contracts.py", 30, None),
        ("仓库完整性", "scripts/check_repo_integrity_fast.py", 15, None),
        ("变更影响", "scripts/check_change_impact_enforcement.py", 20, None),
        ("技能安全", "scripts/check_skill_security.py", 60, ["--scan-all"]),
        ("架构完整性", "infrastructure/architecture_inspector.py", 60, None),
    ]
    
    results = {
        "profile": profile,
        "generated_at": datetime.now().isoformat(),
        "version": "5.0.0",
        "checks": [],
        "summary": {
            "total": len(script_checks) + 2,  # +2 for token and injection checks
            "passed": 0,
            "failed": 0,
            "cached": 0,
            "max_duration_ms": 0
        }
    }
    
    print("╔══════════════════════════════════════════════════╗")
    print("║          统一巡检器 V6.0.0 (融合版)            ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"Profile: {profile} | Workers: {MAX_WORKERS}")
    print()

    # 并行执行脚本检查
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(run_check_fast, name, script, root, timeout, args, cache, cache_timestamp): name
            for name, script, timeout, args in script_checks
        }
        
        for future in as_completed(futures):
            result = future.result()
            results["checks"].append(result)
            
            if result.get("cached"):
                results["summary"]["cached"] += 1
            
            if result["passed"]:
                results["summary"]["passed"] += 1
                cached_marker = "📦" if result.get("cached") else "✅"
                print(f"  {cached_marker} {result['name']}: {result['duration_ms']}ms")
            else:
                results["summary"]["failed"] += 1
                print(f"  ❌ {result['name']}: FAILED ({result['duration_ms']}ms)")
            
            if result["duration_ms"] > results["summary"]["max_duration_ms"]:
                results["summary"]["max_duration_ms"] = result["duration_ms"]
    
    # Token 优化检查
    token_result = check_token_optimization(root)
    results["checks"].append(token_result)
    if token_result["passed"]:
        results["summary"]["passed"] += 1
        tokens = token_result["details"].get("estimated_tokens", 0)
        print(f"  ✅ {token_result['name']}: ~{tokens} tokens")
    else:
        results["summary"]["failed"] += 1
        print(f"  ❌ {token_result['name']}: FAILED")
    
    # 注入配置检查
    injection_result = check_injection_config(root)
    results["checks"].append(injection_result)
    if injection_result["passed"]:
        results["summary"]["passed"] += 1
        modes = len(injection_result["details"].get("modes", {}))
        print(f"  ✅ {injection_result['name']}: {modes} modes")
    else:
        results["summary"]["failed"] += 1
        print(f"  ❌ {injection_result['name']}: FAILED")
    
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
    max_ms = results['summary']['max_duration_ms']
    
    print(f"✅ {passed} | ❌ {failed} | 📦 {cached} | ⏱️ ~{max_ms}ms")
    
    status = "✅ 全部通过" if failed == 0 else "❌ 存在失败"
    print(f"状态: {status}")
    print(f"版本: V{results.get('version', '5.0.0')}")
    print("=" * 50)


def save_report_fast(results: Dict):
    """快速保存报告"""
    root = get_project_root()
    report_path = root / "reports/ops/unified_inspection.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="统一巡检器 V6.0.0")
    parser.add_argument("--profile", default="premerge")
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()
    
    results = run_all_checks_fast(profile=args.profile)
    print_summary_fast(results)
    
    if args.save:
        save_report_fast(results)
        print(f"\n报告已保存")
    
    return 0 if results['summary']['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
