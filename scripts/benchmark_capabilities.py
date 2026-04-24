"""能力级 Benchmark"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import time
import statistics


def benchmark_capabilities(
    capabilities: Optional[List[str]] = None,
    iterations: int = 10,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    对能力进行基准测试
    
    Args:
        capabilities: 要测试的能力列表（默认测试四大能力）
        iterations: 每个能力的迭代次数
        dry_run: 是否使用 dry_run 模式
        
    Returns:
        基准测试结果
    """
    if not capabilities:
        capabilities = ["MESSAGE_SENDING", "TASK_SCHEDULING", "STORAGE", "NOTIFICATION"]
    
    results = {}
    
    for capability in capabilities:
        cap_result = _benchmark_single_capability(capability, iterations, dry_run)
        results[capability] = cap_result
    
    # 汇总
    summary = {
        "total_capabilities": len(capabilities),
        "total_iterations": len(capabilities) * iterations,
        "fastest": min(results.items(), key=lambda x: x[1].get("avg_latency_ms", float("inf")))[0],
        "slowest": max(results.items(), key=lambda x: x[1].get("avg_latency_ms", 0))[0],
        "tested_at": datetime.now().isoformat()
    }
    
    return {
        "success": True,
        "dry_run": dry_run,
        "iterations": iterations,
        "results": results,
        "summary": summary
    }


def _benchmark_single_capability(
    capability: str,
    iterations: int,
    dry_run: bool,
) -> Dict[str, Any]:
    """对单个能力进行基准测试"""
    latencies = []
    successes = 0
    failures = 0
    timeouts = 0
    uncertains = 0
    
    # 模拟测试参数
    test_params = {
        "MESSAGE_SENDING": {"to": "test", "message": "benchmark test", "dry_run": dry_run},
        "TASK_SCHEDULING": {"title": "benchmark test", "start_time": "2026-04-25T10:00:00", "dry_run": dry_run},
        "STORAGE": {"title": "benchmark test", "content": "test content", "dry_run": dry_run},
        "NOTIFICATION": {"title": "benchmark test", "content": "test content", "dry_run": dry_run}
    }
    
    capability_module_map = {
        "MESSAGE_SENDING": "send_message",
        "TASK_SCHEDULING": "schedule_task",
        "STORAGE": "create_note",
        "NOTIFICATION": "send_notification"
    }
    
    module_name = capability_module_map.get(capability)
    params = test_params.get(capability, {})
    
    for i in range(iterations):
        start_time = time.time()
        
        try:
            import importlib
            module = importlib.import_module(f"capabilities.{module_name}")
            
            if hasattr(module, "run"):
                result = module.run(**params)
                
                # 统计状态
                status = result.get("normalized_status", "unknown")
                if status == "completed":
                    successes += 1
                elif status == "failed":
                    failures += 1
                elif status == "timeout":
                    timeouts += 1
                elif status == "result_uncertain":
                    uncertains += 1
                elif result.get("success", False):
                    successes += 1
                else:
                    failures += 1
            else:
                failures += 1
        
        except Exception as e:
            failures += 1
        
        elapsed = (time.time() - start_time) * 1000  # ms
        latencies.append(elapsed)
    
    # 计算统计
    if latencies:
        avg_latency = statistics.mean(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 5 else max(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
    else:
        avg_latency = p95_latency = min_latency = max_latency = 0
    
    return {
        "capability": capability,
        "iterations": iterations,
        "avg_latency_ms": round(avg_latency, 2),
        "p95_latency_ms": round(p95_latency, 2),
        "min_latency_ms": round(min_latency, 2),
        "max_latency_ms": round(max_latency, 2),
        "success_count": successes,
        "failed_count": failures,
        "timeout_count": timeouts,
        "uncertain_count": uncertains,
        "success_rate": round(successes / iterations * 100, 2) if iterations > 0 else 0
    }


def stress_test_capability(
    capability: str,
    duration_seconds: int = 10,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    对单个能力进行压力测试
    
    Args:
        capability: 能力名称
        duration_seconds: 持续时间（秒）
        dry_run: 是否使用 dry_run 模式
        
    Returns:
        压力测试结果
    """
    start_time = time.time()
    iterations = 0
    successes = 0
    failures = 0
    latencies = []
    
    capability_module_map = {
        "MESSAGE_SENDING": "send_message",
        "TASK_SCHEDULING": "schedule_task",
        "STORAGE": "create_note",
        "NOTIFICATION": "send_notification"
    }
    
    module_name = capability_module_map.get(capability)
    
    while time.time() - start_time < duration_seconds:
        iter_start = time.time()
        
        try:
            import importlib
            module = importlib.import_module(f"capabilities.{module_name}")
            
            if hasattr(module, "run"):
                result = module.run(dry_run=dry_run)
                if result.get("success", False):
                    successes += 1
                else:
                    failures += 1
            else:
                failures += 1
        
        except:
            failures += 1
        
        latencies.append((time.time() - iter_start) * 1000)
        iterations += 1
    
    return {
        "success": True,
        "capability": capability,
        "duration_seconds": duration_seconds,
        "total_iterations": iterations,
        "iterations_per_second": round(iterations / duration_seconds, 2),
        "success_count": successes,
        "failure_count": failures,
        "avg_latency_ms": round(statistics.mean(latencies), 2) if latencies else 0,
        "dry_run": dry_run
    }


def run(**kwargs):
    """入口"""
    return benchmark_capabilities(**kwargs)
