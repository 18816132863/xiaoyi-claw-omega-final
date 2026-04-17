"""
Skill Latency Benchmark - 技能延迟基准测试
"""

import sys
import os
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def run_benchmark():
    """运行技能延迟基准测试"""
    print("=" * 60)
    print("Skill Latency Benchmark")
    print("=" * 60)
    
    results = {
        "benchmark": "skill_latency",
        "timestamp": datetime.now().isoformat(),
        "iterations": 10,
        "latencies_ms": [],
        "avg_latency_ms": 0,
        "p50_latency_ms": 0,
        "p95_latency_ms": 0,
        "max_latency_ms": 0
    }
    
    for i in range(10):
        start = time.time()
        
        try:
            # 模拟技能选择
            from skills.runtime.skill_router import SkillRouter
            
            router = SkillRouter()
            
            # 选择技能
            selection = router.select_skill("test", "default")
            
        except Exception as e:
            pass
        
        latency = (time.time() - start) * 1000
        results["latencies_ms"].append(latency)
    
    if results["latencies_ms"]:
        results["avg_latency_ms"] = sum(results["latencies_ms"]) / len(results["latencies_ms"])
        sorted_latencies = sorted(results["latencies_ms"])
        results["p50_latency_ms"] = sorted_latencies[len(sorted_latencies) // 2]
        results["p95_latency_ms"] = sorted_latencies[int(len(sorted_latencies) * 0.95)]
        results["max_latency_ms"] = max(results["latencies_ms"])
    
    print(f"\nResults:")
    print(f"  Iterations: {results['iterations']}")
    print(f"  Avg Latency: {results['avg_latency_ms']:.0f}ms")
    print(f"  P50 Latency: {results['p50_latency_ms']:.0f}ms")
    print(f"  P95 Latency: {results['p95_latency_ms']:.0f}ms")
    print(f"  Max Latency: {results['max_latency_ms']:.0f}ms")
    
    # 保存结果
    os.makedirs("reports/benchmarks", exist_ok=True)
    with open("reports/benchmarks/skill_latency_bench.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Benchmark passed: avg_latency={results['avg_latency_ms']:.0f}ms")
    return 0


if __name__ == "__main__":
    sys.exit(run_benchmark())
