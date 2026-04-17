"""
Phase3 Group4 验证示例
Memory Context 正式知识内核化验证
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timedelta
import json


def test_retrieval_trace():
    """测试 1: Retrieval Trace 示例"""
    print("\n" + "=" * 60)
    print("测试 1: Retrieval Trace 示例")
    print("=" * 60)

    from memory_context.retrieval.retrieval_trace_store import (
        RetrievalTraceStore, SourceResult
    )

    store = RetrievalTraceStore()

    # 创建追踪
    trace = store.create_trace(
        task_id="task_001",
        original_query="检查项目架构完整性",
        profile="developer",
        risk_level="low"
    )

    # 设置重写查询
    trace.rewritten_query = "架构 完整性 检查 architecture"
    trace.query_rewrite_reason = "同义词扩展"

    # 设置允许/拒绝来源
    trace.allowed_sources = ["session_history", "long_term_memory", "workflow_history"]
    trace.denied_sources = ["external_knowledge"]

    # 添加来源结果
    store.add_source_result(trace.trace_id, SourceResult(
        source_id="src_session_001",
        source_type="session_history",
        query_used="架构 完整性",
        hits_count=5,
        filtered_count=2,
        returned_count=3,
        tokens_used=150,
        latency_ms=10
    ))

    store.add_source_result(trace.trace_id, SourceResult(
        source_id="src_memory_001",
        source_type="long_term_memory",
        query_used="architecture integrity",
        hits_count=10,
        filtered_count=4,
        returned_count=6,
        tokens_used=300,
        latency_ms=25
    ))

    # 设置最终结果
    store.finalize_trace(trace.trace_id, {
        "injected_sources": ["session_history", "long_term_memory"],
        "total_items": 9,
        "total_tokens": 450,
        "compression_ratio": 0.85
    }, duration_ms=50)

    # 获取追踪
    result = store.get_trace(trace.trace_id)

    print(f"\n追踪结果:")
    print(f"  - Trace ID: {result.trace_id}")
    print(f"  - 原始查询: {result.original_query}")
    print(f"  - 重写查询: {result.rewritten_query}")
    print(f"  - 允许来源: {result.allowed_sources}")
    print(f"  - 拒绝来源: {result.denied_sources}")
    print(f"  - 来源结果数: {len(result.source_results)}")

    for sr in result.source_results:
        print(f"    - {sr.source_type}: hits={sr.hits_count}, filtered={sr.filtered_count}, returned={sr.returned_count}")

    print(f"  - 最终注入: {result.final_result.get('injected_sources', [])}")
    print(f"  - 总 tokens: {result.final_result.get('total_tokens', 0)}")

    return result.trace_id is not None


def test_source_policy_routing():
    """测试 2: Source Policy Routing 示例"""
    print("\n" + "=" * 60)
    print("测试 2: Source Policy Routing 示例")
    print("=" * 60)

    from memory_context.retrieval.source_policy_router import (
        SourcePolicyRouter, RiskLevel
    )

    router = SourcePolicyRouter()

    # 测试不同 profile
    profiles = ["default", "developer", "admin"]
    risk_levels = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]

    print("\n不同 profile/risk 下的允许来源:")

    for profile in profiles:
        for risk in risk_levels:
            result = router.route(
                profile=profile,
                risk_level=risk,
                capabilities=["memory.read", "report.read"]
            )

            allowed = [s.value for s in result.allowed_sources]
            denied = [s.value for s in result.denied_sources]

            print(f"\n  profile={profile}, risk={risk.value}:")
            print(f"    允许: {allowed[:3]}..." if len(allowed) > 3 else f"    允许: {allowed}")
            print(f"    拒绝: {denied[:3]}..." if len(denied) > 3 else f"    拒绝: {denied}")

    # 验证高风险限制
    low_risk = router.route(profile="developer", risk_level=RiskLevel.LOW)
    high_risk = router.route(profile="developer", risk_level=RiskLevel.HIGH)

    print(f"\n风险等级影响:")
    print(f"  LOW risk 允许来源数: {len(low_risk.allowed_sources)}")
    print(f"  HIGH risk 允许来源数: {len(high_risk.allowed_sources)}")

    return len(low_risk.allowed_sources) >= len(high_risk.allowed_sources)


def test_context_injection_planning():
    """测试 3: Context Injection Planning 示例"""
    print("\n" + "=" * 60)
    print("测试 3: Context Injection Planning 示例")
    print("=" * 60)

    from memory_context.builder.context_injection_planner import (
        ContextInjectionPlanner, get_context_injection_planner
    )

    planner = get_context_injection_planner()

    # 模拟来源
    sources = [
        {"source_id": "s1", "source_type": "session_history", "tokens": 100, "content": "最近会话"},
        {"source_id": "s2", "source_type": "user_preference", "tokens": 50, "content": "用户偏好"},
        {"source_id": "s3", "source_type": "long_term_memory", "tokens": 200, "content": "长期记忆"},
        {"source_id": "s4", "source_type": "report_memory", "tokens": 150, "content": "报告记忆"},
        {"source_id": "s5", "source_type": "external_knowledge", "tokens": 300, "content": "外部知识"},
    ]

    # 可信度分数
    confidence_scores = {
        "s1": 0.9,
        "s2": 0.95,
        "s3": 0.8,
        "s4": 0.6,
        "s5": 0.5
    }

    # 规划注入
    plan = planner.plan(
        task_id="task_002",
        sources=sources,
        token_budget=400,
        confidence_scores=confidence_scores
    )

    print(f"\n注入规划结果:")
    print(f"  - 总预算: {plan.total_budget}")
    print(f"  - 分配预算: {plan.allocated_budget}")

    print(f"\n  必需来源:")
    for s in plan.required_sources:
        print(f"    - {s.source_id} ({s.source_type}): priority={s.priority.value}, order={s.injection_order}")

    print(f"\n  可选来源:")
    for s in plan.optional_sources:
        print(f"    - {s.source_id} ({s.source_type}): priority={s.priority.value}, order={s.injection_order}")

    print(f"\n  被抑制来源:")
    for s in plan.suppressed_sources:
        print(f"    - {s.source_id} ({s.source_type}): reason={s.reason}")

    print(f"\n  最终注入顺序: {plan.final_injection_order}")

    return len(plan.required_sources) > 0 and len(plan.final_injection_order) > 0


def test_memory_version():
    """测试 4: Memory Version 示例"""
    print("\n" + "=" * 60)
    print("测试 4: Memory Version 示例")
    print("=" * 60)

    # ========== 清理旧测试文件，保证测试隔离 ==========
    import os
    for f in [
        "/tmp/test_memory_versions.json",
        "/tmp/test_memory_store.json", 
        "/tmp/test_memory_archive.json"
    ]:
        if os.path.exists(f):
            os.remove(f)
            print(f"  已清理: {f}")

    from memory_context.long_term.memory_version_store import (
        MemoryVersionStore
    )

    store = MemoryVersionStore(
        store_path="/tmp/test_memory_versions.json"
    )

    memory_id = "mem_001"

    # 创建初始版本
    v1 = store.create_version(
        memory_id=memory_id,
        content="初始记忆内容",
        change_type="create",
        change_reason="用户创建",
        source_task_id="task_001"
    )

    print(f"\n版本 1:")
    print(f"  - Version ID: {v1.version_id}")
    print(f"  - Version Number: {v1.version_number}")
    print(f"  - Change Type: {v1.change_type}")
    print(f"  - Reason: {v1.change_reason}")

    # 更新版本
    v2 = store.create_version(
        memory_id=memory_id,
        content="更新后的记忆内容",
        change_type="update",
        change_reason="用户修正",
        source_task_id="task_002"
    )

    print(f"\n版本 2:")
    print(f"  - Version ID: {v2.version_id}")
    print(f"  - Version Number: {v2.version_number}")
    print(f"  - Previous Version: {v2.previous_version_id}")
    print(f"  - Change Type: {v2.change_type}")
    print(f"  - Reason: {v2.change_reason}")

    # 获取历史
    history = store.get_history(memory_id)
    print(f"\n记忆历史:")
    print(f"  - Memory ID: {history.memory_id}")
    print(f"  - 当前版本: {history.current_version}")
    print(f"  - 版本数: {len(history.versions)}")
    print(f"  - 创建时间: {history.created_at}")
    print(f"  - 最后修改: {history.last_modified}")

    # 统计
    stats = store.get_statistics()
    print(f"\n统计:")
    print(f"  - 总记忆数: {stats['total_memories']}")
    print(f"  - 总版本数: {stats['total_versions']}")

    return history.current_version == 2


def test_memory_gc():
    """测试 5: Memory GC 示例"""
    print("\n" + "=" * 60)
    print("测试 5: Memory GC 示例")
    print("=" * 60)

    from memory_context.long_term.memory_gc import MemoryGC

    gc = MemoryGC(
        memory_store_path="/tmp/test_memory_store.json",
        archive_path="/tmp/test_memory_archive.json"
    )

    # 创建测试记忆
    now = datetime.now()
    memories = [
        {
            "memory_id": "mem_active",
            "content": "活跃记忆",
            "importance": 0.9,
            "tags": [],
            "created_at": (now - timedelta(days=10)).isoformat(),
            "last_accessed": (now - timedelta(days=1)).isoformat()
        },
        {
            "memory_id": "mem_old",
            "content": "旧记忆",
            "importance": 0.5,
            "tags": [],
            "created_at": (now - timedelta(days=100)).isoformat(),
            "last_accessed": (now - timedelta(days=50)).isoformat()
        },
        {
            "memory_id": "mem_critical",
            "content": "关键记忆",
            "importance": 1.0,
            "tags": ["critical"],
            "created_at": (now - timedelta(days=200)).isoformat(),
            "last_accessed": (now - timedelta(days=100)).isoformat()
        },
        {
            "memory_id": "mem_obsolete",
            "content": "废弃记忆",
            "importance": 0.3,
            "tags": [],
            "created_at": (now - timedelta(days=400)).isoformat(),
            "last_accessed": (now - timedelta(days=400)).isoformat()
        }
    ]

    # 保存测试记忆
    import json
    with open("/tmp/test_memory_store.json", 'w') as f:
        json.dump(memories, f)

    # 运行 GC（模拟模式）
    report = gc.run_gc(dry_run=True)

    print(f"\nGC 报告:")
    print(f"  - 处理总数: {report.total_processed}")
    print(f"  - 衰减: {report.decayed}")
    print(f"  - 归档: {report.archived}")
    print(f"  - 删除: {report.removed}")
    print(f"  - 保留: {report.kept}")

    print(f"\n各记忆处理结果:")
    for result in report.results:
        print(f"  - {result.memory_id}: {result.action.value}")
        print(f"    原因: {result.reason}")
        if result.action.value == "decay":
            print(f"    分数变化: {result.original_score:.2f} -> {result.new_score:.2f}")

    return report.total_processed == 4


def main():
    """运行所有测试"""
    print("=" * 60)
    print("Phase3 Group4 验证")
    print("Memory Context 正式知识内核化")
    print("=" * 60)

    results = []

    results.append(("Retrieval Trace 示例", test_retrieval_trace()))
    results.append(("Source Policy Routing 示例", test_source_policy_routing()))
    results.append(("Context Injection Planning 示例", test_context_injection_planning()))
    results.append(("Memory Version 示例", test_memory_version()))
    results.append(("Memory GC 示例", test_memory_gc()))

    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 Phase3 Group4 Memory Context 知识内核化验证通过！")
    else:
        print("❌ 需要继续修复")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
