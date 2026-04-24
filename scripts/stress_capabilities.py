"""能力压测脚本"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import time
import argparse


def stress_capabilities(
    capabilities: Optional[List[str]] = None,
    duration_seconds: int = 10,
    requests_per_second: int = 5,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    对能力进行压力测试
    
    Args:
        capabilities: 要测试的能力列表
        duration_seconds: 持续时间（秒）
        requests_per_second: 每秒请求数
        dry_run: 是否使用 dry_run 模式
        
    Returns:
        压测结果
    """
    if not capabilities:
        capabilities = ["MESSAGE_SENDING", "TASK_SCHEDULING", "STORAGE", "NOTIFICATION"]
    
    results = {}
    
    for capability in capabilities:
        print(f"压测 {capability}...")
        result = _stress_single_capability(
            capability=capability,
            duration_seconds=duration_seconds,
            requests_per_second=requests_per_second,
            dry_run=dry_run
        )
        results[capability] = result
    
    # 汇总
    total_requests = sum(r["total_requests"] for r in results.values())
    total_successes = sum(r["successes"] for r in results.values())
    total_failures = sum(r["failures"] for r in results.values())
    
    return {
        "success": True,
        "dry_run": dry_run,
        "duration_seconds": duration_seconds,
        "requests_per_second": requests_per_second,
        "total_requests": total_requests,
        "total_successes": total_successes,
        "total_failures": total_failures,
        "overall_success_rate": round(total_successes / total_requests * 100, 2) if total_requests > 0 else 0,
        "by_capability": results,
        "tested_at": datetime.now().isoformat()
    }


def _stress_single_capability(
    capability: str,
    duration_seconds: int,
    requests_per_second: int,
    dry_run: bool,
) -> Dict[str, Any]:
    """对单个能力进行压力测试"""
    
    capability_module_map = {
        "MESSAGE_SENDING": "send_message",
        "TASK_SCHEDULING": "schedule_task",
        "STORAGE": "create_note",
        "NOTIFICATION": "send_notification"
    }
    
    module_name = capability_module_map.get(capability)
    
    start_time = time.time()
    total_requests = 0
    successes = 0
    failures = 0
    latencies = []
    
    interval = 1.0 / requests_per_second
    
    while time.time() - start_time < duration_seconds:
        iter_start = time.time()
        
        try:
            import importlib
            module = importlib.import_module(f"capabilities.{module_name}")
            
            if hasattr(module, "run"):
                result = module.run(dry_run=dry_run)
                if result.get("success", False) or result.get("dry_run"):
                    successes += 1
                else:
                    failures += 1
            else:
                failures += 1
        
        except Exception as e:
            failures += 1
        
        latencies.append((time.time() - iter_start) * 1000)
        total_requests += 1
        
        # 控制速率
        elapsed = time.time() - iter_start
        if elapsed < interval:
            time.sleep(interval - elapsed)
    
    import statistics
    
    return {
        "capability": capability,
        "total_requests": total_requests,
        "successes": successes,
        "failures": failures,
        "success_rate": round(successes / total_requests * 100, 2) if total_requests > 0 else 0,
        "avg_latency_ms": round(statistics.mean(latencies), 2) if latencies else 0,
        "max_latency_ms": round(max(latencies), 2) if latencies else 0,
        "actual_rps": round(total_requests / duration_seconds, 2)
    }


def main():
    parser = argparse.ArgumentParser(description="能力压测脚本")
    parser.add_argument("--capabilities", nargs="+", help="要测试的能力")
    parser.add_argument("--duration", type=int, default=10, help="持续时间（秒）")
    parser.add_argument("--rps", type=int, default=5, help="每秒请求数")
    parser.add_argument("--dry-run", action="store_true", help="使用 dry_run 模式")
    
    args = parser.parse_args()
    
    result = stress_capabilities(
        capabilities=args.capabilities,
        duration_seconds=args.duration,
        requests_per_second=args.rps,
        dry_run=args.dry_run
    )
    
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
