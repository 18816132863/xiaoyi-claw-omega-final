#!/usr/bin/env python3
"""
生成 metrics 报告示例

运行方式：
    python scripts/generate_metrics.py
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.benchmarks.task_success_bench import TaskSuccessBench
from tests.benchmarks.skill_latency_bench import SkillLatencyBench
from tests.benchmarks.memory_retrieval_bench import MemoryRetrievalBench
from governance.evaluation.evaluation_aggregator import EvaluationAggregator


def generate_task_metrics():
    """生成任务指标"""
    bench = TaskSuccessBench()
    
    # 模拟任务结果
    test_tasks = [
        {"task_id": "task_001", "success": True, "duration_ms": 150},
        {"task_id": "task_002", "success": True, "duration_ms": 200},
        {"task_id": "task_003", "success": False, "duration_ms": 50, "error": "timeout"},
        {"task_id": "task_004", "success": True, "duration_ms": 180},
        {"task_id": "task_005", "success": True, "duration_ms": 220},
        {"task_id": "task_006", "success": False, "duration_ms": 30, "error": "skill_not_found"},
        {"task_id": "task_007", "success": True, "duration_ms": 160},
        {"task_id": "task_008", "success": True, "duration_ms": 190},
        {"task_id": "task_009", "success": True, "duration_ms": 170},
        {"task_id": "task_010", "success": False, "duration_ms": 40, "error": "permission_denied"},
    ]
    
    metrics = bench.run_benchmark(test_tasks)
    
    print(f"✅ 任务指标已生成:")
    print(f"   - 总数: {metrics.total}")
    print(f"   - 通过: {metrics.passed}")
    print(f"   - 失败: {metrics.failed}")
    print(f"   - 成功率: {metrics.success_rate:.2%}")
    print(f"   - 平均耗时: {metrics.avg_duration_ms:.1f}ms")
    
    return metrics


def generate_skill_metrics():
    """生成技能指标"""
    bench = SkillLatencyBench()
    
    # 模拟技能执行
    test_executions = [
        {"skill_id": "search", "success": True, "duration_ms": 50},
        {"skill_id": "search", "success": True, "duration_ms": 45},
        {"skill_id": "search", "success": False, "duration_ms": 10, "error": "timeout"},
        {"skill_id": "document", "success": True, "duration_ms": 80},
        {"skill_id": "document", "success": True, "duration_ms": 75},
        {"skill_id": "document", "success": True, "duration_ms": 90},
        {"skill_id": "code", "success": True, "duration_ms": 120},
        {"skill_id": "code", "success": False, "duration_ms": 20, "error": "validation_error"},
        {"skill_id": "code", "success": True, "duration_ms": 110},
        {"skill_id": "utility", "success": True, "duration_ms": 30},
    ]
    
    metrics = bench.run_benchmark(test_executions)
    aggregate = bench.compute_aggregate()
    
    print(f"\n✅ 技能指标已生成:")
    print(f"   - 总调用: {aggregate.total_calls}")
    print(f"   - 平均延迟: {aggregate.avg_latency_ms:.1f}ms")
    print(f"   - 最大延迟: {aggregate.max_latency_ms}ms")
    print(f"   - 失败率: {aggregate.failure_rate:.2%}")
    
    return metrics


def generate_memory_metrics():
    """生成记忆指标"""
    bench = MemoryRetrievalBench()
    
    # 模拟检索结果
    test_queries = [
        {"query": "项目状态", "hit": True, "token_usage": 150, "source_count": 3},
        {"query": "用户偏好", "hit": True, "token_usage": 200, "source_count": 4},
        {"query": "历史决策", "hit": True, "token_usage": 180, "source_count": 3},
        {"query": "未知主题", "hit": False, "token_usage": 50, "source_count": 0},
        {"query": "技能列表", "hit": True, "token_usage": 120, "source_count": 2},
        {"query": "配置信息", "hit": True, "token_usage": 100, "source_count": 2},
        {"query": "测试数据", "hit": False, "token_usage": 30, "source_count": 0},
        {"query": "工作流状态", "hit": True, "token_usage": 160, "source_count": 3},
    ]
    
    metrics = bench.run_benchmark(test_queries)
    
    print(f"\n✅ 记忆指标已生成:")
    print(f"   - 总查询: {metrics.total_queries}")
    print(f"   - 命中: {metrics.hits}")
    print(f"   - 未命中: {metrics.misses}")
    print(f"   - 命中率: {metrics.hit_rate:.2%}")
    print(f"   - 平均 token: {metrics.avg_token_usage:.1f}")
    print(f"   - 平均源数: {metrics.avg_source_count:.1f}")
    
    return metrics


def generate_aggregated_report():
    """生成聚合报告"""
    aggregator = EvaluationAggregator()
    report = aggregator.generate_report()
    
    print(f"\n✅ 聚合报告已生成:")
    print(f"   - 路径: {report['report_path']}")
    print(f"   - 健康状态: {report['summary']['overall_health']}")
    print(f"   - 任务成功率: {report['summary']['task_success_rate']:.2%}")
    print(f"   - 技能失败率: {report['summary']['skill_failure_rate']:.2%}")
    print(f"   - 记忆命中率: {report['summary']['memory_hit_rate']:.2%}")
    
    return report


def main():
    print("=" * 60)
    print("生成 Metrics 报告")
    print("=" * 60)
    
    # 生成三类指标
    generate_task_metrics()
    generate_skill_metrics()
    generate_memory_metrics()
    
    # 生成聚合报告
    generate_aggregated_report()
    
    print("\n" + "=" * 60)
    print("✅ 所有 Metrics 报告已生成")
    print("=" * 60)
    
    # 显示文件列表
    metrics_dir = "reports/metrics"
    if os.path.exists(metrics_dir):
        print(f"\n生成的文件:")
        for filename in os.listdir(metrics_dir):
            if filename.endswith(".json"):
                path = os.path.join(metrics_dir, filename)
                size = os.path.getsize(path)
                print(f"   - {filename} ({size} bytes)")


if __name__ == "__main__":
    main()
