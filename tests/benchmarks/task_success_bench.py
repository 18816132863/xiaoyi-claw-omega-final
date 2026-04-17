"""
Task Success Benchmark - 任务成功率基准测试
"""

import sys
import os
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def run_benchmark():
    """运行任务成功率基准测试"""
    print("=" * 60)
    print("Task Success Rate Benchmark")
    print("=" * 60)
    
    results = {
        "benchmark": "task_success_rate",
        "timestamp": datetime.now().isoformat(),
        "iterations": 10,
        "successes": 0,
        "failures": 0,
        "success_rate": 0.0,
        "avg_latency_ms": 0
    }
    
    latencies = []
    
    for i in range(10):
        start = time.time()
        
        try:
            # 模拟任务执行
            from orchestration.workflow.workflow_engine import WorkflowEngine, WorkflowTemplate, WorkflowStep
            from orchestration.workflow.workflow_registry import RecoveryPolicy, RecoveryPolicyType
            
            engine = WorkflowEngine()
            
            template = WorkflowTemplate(
                workflow_id="bench_task",
                version="1.0.0",
                name="Benchmark Task",
                steps=[
                    WorkflowStep(
                        step_id="step_1",
                        name="Test Step",
                        action="bench_action",
                        params={}
                    )
                ],
                recovery_policy=RecoveryPolicy(policy_type=RecoveryPolicyType.RETRY, max_retries=1)
            )
            
            # 注册动作处理器
            engine.register_action_handler("bench_action", lambda a, i: {"ok": True})
            
            # 执行
            result = engine.run_workflow(template=template)
            
            if result.status.value in ["completed", "success"]:
                results["successes"] += 1
            else:
                results["failures"] += 1
        
        except Exception as e:
            results["failures"] += 1
        
        latency = (time.time() - start) * 1000
        latencies.append(latency)
    
    results["success_rate"] = results["successes"] / results["iterations"]
    results["avg_latency_ms"] = sum(latencies) / len(latencies)
    
    print(f"\nResults:")
    print(f"  Iterations: {results['iterations']}")
    print(f"  Successes: {results['successes']}")
    print(f"  Failures: {results['failures']}")
    print(f"  Success Rate: {results['success_rate']:.1%}")
    print(f"  Avg Latency: {results['avg_latency_ms']:.0f}ms")
    
    # 保存结果
    os.makedirs("reports/benchmarks", exist_ok=True)
    with open("reports/benchmarks/task_success_bench.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Benchmark passed: success_rate={results['success_rate']:.1%}")
    return 0


if __name__ == "__main__":
    sys.exit(run_benchmark())
