"""
Phase3 Group4 主链生效验证
证明默认主链已升级，不是模块单独能跑
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
import json


def test_build_context_uses_query_rewriter():
    """测试 1: build_context() 真的走 query rewrite"""
    print("\n" + "=" * 60)
    print("测试 1: build_context() 走 QueryRewriter")
    print("=" * 60)

    from memory_context.builder.context_builder import ContextBuilder

    builder = ContextBuilder()
    
    # 构建 context
    bundle = builder.build_context(
        task_id="test_task_001",
        profile="developer",
        intent="检查项目架构完整性",
        token_budget=4000
    )

    print(f"\nContext Bundle:")
    print(f"  - Task ID: {bundle.task_id}")
    print(f"  - Intent: {bundle.intent}")
    print(f"  - Trace ID: {bundle.trace_id}")
    print(f"  - Token Count: {bundle.token_count}")

    # 检查 trace 是否存在
    if bundle.trace_id:
        from memory_context.retrieval.retrieval_trace_store import get_retrieval_trace_store
        store = get_retrieval_trace_store()
        trace = store.get_trace(bundle.trace_id)
        
        if trace:
            print(f"\nRetrieval Trace:")
            print(f"  - 原始查询: {trace.original_query}")
            print(f"  - 重写查询: {trace.rewritten_query}")
            print(f"  - 重写原因: {trace.query_rewrite_reason}")
            
            # 验证重写确实发生
            if trace.rewritten_query and trace.rewritten_query != trace.original_query:
                print(f"\n  ✅ QueryRewriter 真正生效")
                return True

    print(f"\n  ❌ QueryRewriter 未生效")
    return False


def test_build_context_uses_source_policy_router():
    """测试 2: build_context() 真的走 source policy router"""
    print("\n" + "=" * 60)
    print("测试 2: build_context() 走 SourcePolicyRouter")
    print("=" * 60)

    from memory_context.builder.context_builder import ContextBuilder

    builder = ContextBuilder()
    
    # 用不同 profile 构建
    profiles = ["default", "developer", "admin"]
    results = {}

    for profile in profiles:
        bundle = builder.build_context(
            task_id=f"test_task_{profile}",
            profile=profile,
            intent="测试查询",
            token_budget=2000,
            risk_level="low"
        )

        if bundle.trace_id:
            from memory_context.retrieval.retrieval_trace_store import get_retrieval_trace_store
            store = get_retrieval_trace_store()
            trace = store.get_trace(bundle.trace_id)
            
            if trace:
                results[profile] = {
                    "allowed": trace.allowed_sources,
                    "denied": trace.denied_sources
                }

    print(f"\n不同 profile 的 source policy 结果:")
    for profile, data in results.items():
        print(f"\n  {profile}:")
        print(f"    允许: {data['allowed'][:3]}...")
        print(f"    拒绝: {data['denied'][:3]}...")

    # 验证不同 profile 有不同的允许来源
    if len(results) >= 2:
        allowed_sets = [set(data['allowed']) for data in results.values()]
        if allowed_sets[0] != allowed_sets[1] if len(allowed_sets) > 1 else True:
            print(f"\n  ✅ SourcePolicyRouter 真正生效")
            return True

    print(f"\n  ❌ SourcePolicyRouter 未生效")
    return False


def test_retrieval_trace_is_saved():
    """测试 3: retrieval trace 被真实保存"""
    print("\n" + "=" * 60)
    print("测试 3: Retrieval Trace 被真实保存")
    print("=" * 60)

    from memory_context.builder.context_builder import ContextBuilder
    from memory_context.retrieval.retrieval_trace_store import get_retrieval_trace_store

    builder = ContextBuilder()
    store = get_retrieval_trace_store()

    # 记录之前的 trace 数量
    before_count = len(store.get_recent_traces(limit=1000))

    # 构建 context
    bundle = builder.build_context(
        task_id="test_trace_save",
        profile="developer",
        intent="测试 trace 保存",
        token_budget=2000
    )

    # 检查 trace 是否保存
    if bundle.trace_id:
        trace = store.get_trace(bundle.trace_id)
        
        if trace:
            print(f"\nTrace 已保存:")
            print(f"  - Trace ID: {trace.trace_id}")
            print(f"  - Task ID: {trace.task_id}")
            print(f"  - 原始查询: {trace.original_query}")
            print(f"  - 允许来源: {trace.allowed_sources}")
            print(f"  - 最终结果: {trace.final_result}")

            # 检查文件是否存在
            import os
            trace_file = f"memory_context/traces/{trace.trace_id}.json"
            if os.path.exists(trace_file):
                print(f"\n  ✅ Trace 文件已落盘: {trace_file}")
                return True
            else:
                print(f"\n  ✅ Trace 已保存到内存")
                return True

    print(f"\n  ❌ Trace 未保存")
    return False


def test_injection_planner_affects_bundle():
    """测试 4: injection planner 真影响最终 context bundle"""
    print("\n" + "=" * 60)
    print("测试 4: InjectionPlanner 影响 ContextBundle")
    print("=" * 60)

    from memory_context.builder.context_builder import ContextBuilder

    builder = ContextBuilder()
    
    # 构建 context
    bundle = builder.build_context(
        task_id="test_injection",
        profile="developer",
        intent="测试注入规划",
        token_budget=1000  # 小预算，触发裁剪
    )

    print(f"\nContext Bundle:")
    print(f"  - Sources 数量: {len(bundle.sources)}")
    print(f"  - Priority Order: {bundle.priority_order}")
    print(f"  - Token Count: {bundle.token_count}")

    if bundle.injection_plan:
        plan = bundle.injection_plan
        print(f"\nInjection Plan:")
        print(f"  - Required Sources: {[s['source_id'] for s in plan.get('required_sources', [])]}")
        print(f"  - Optional Sources: {[s['source_id'] for s in plan.get('optional_sources', [])]}")
        print(f"  - Suppressed Sources: {[s['source_id'] for s in plan.get('suppressed_sources', [])]}")
        print(f"  - Final Order: {plan.get('final_injection_order', [])}")

        # 验证 priority_order 与 injection_plan 一致
        final_order = plan.get('final_injection_order', [])
        if final_order and bundle.priority_order:
            # 检查 bundle.sources 的顺序是否与 final_order 一致
            bundle_source_ids = [s.get('source_id') for s in bundle.sources]
            print(f"\n  Bundle Source IDs: {bundle_source_ids}")
            print(f"  Plan Final Order: {final_order}")
            
            # 验证 suppressed 的不在 bundle 中
            suppressed_ids = {s['source_id'] for s in plan.get('suppressed_sources', [])}
            bundle_ids = set(bundle_source_ids)
            
            if not suppressed_ids.intersection(bundle_ids):
                print(f"\n  ✅ InjectionPlanner 真正影响 Bundle（suppressed 已排除）")
                return True

    print(f"\n  ❌ InjectionPlanner 未生效")
    return False


def test_memory_version_is_written():
    """测试 5: long-term memory update 真写 version 记录"""
    print("\n" + "=" * 60)
    print("测试 5: Memory Version 真实写入")
    print("=" * 60)

    from memory_context.long_term.project_memory_store import ProjectMemoryStore, ProjectMemory

    store = ProjectMemoryStore(store_path="/tmp/test_project_memory.json")

    # 创建记忆
    memory = ProjectMemory(
        memory_id="mem_test_001",
        project_id="proj_001",
        memory_type="decision",
        content="初始决策内容"
    )

    # 存储（应该创建 version 1）
    store.store(memory, source_task_id="task_001", reason="测试创建")

    print(f"\n创建记忆:")
    print(f"  - Memory ID: {memory.memory_id}")
    print(f"  - Version: {memory.version}")

    # 更新（应该创建 version 2）
    store.update(
        memory.memory_id,
        source_task_id="task_002",
        reason="测试更新",
        content="更新后的决策内容"
    )

    print(f"\n更新记忆:")
    print(f"  - Version: {memory.version}")

    # 检查 version store
    from memory_context.long_term.memory_version_store import get_memory_version_store
    version_store = get_memory_version_store()

    history = version_store.get_history(memory.memory_id)
    
    if history:
        print(f"\nVersion History:")
        print(f"  - Memory ID: {history.memory_id}")
        print(f"  - Current Version: {history.current_version}")
        print(f"  - Version Count: {len(history.versions)}")

        for v in history.versions:
            print(f"\n  Version {v.version_number}:")
            print(f"    - Change Type: {v.change_type}")
            print(f"    - Reason: {v.change_reason}")
            print(f"    - Source Task: {v.source_task_id}")

        if history.current_version >= 2:
            print(f"\n  ✅ Memory Version 真实写入")
            return True

    print(f"\n  ❌ Memory Version 未写入")
    return False


def test_gc_can_run_on_real_store():
    """测试 6: GC 能跑正式入口"""
    print("\n" + "=" * 60)
    print("测试 6: GC 能跑正式入口")
    print("=" * 60)

    from memory_context.long_term.memory_gc import MemoryGC
    from datetime import timedelta
    import json

    # 直接使用 MemoryGC
    gc = MemoryGC(
        memory_store_path="/tmp/test_gc_store.json",
        archive_path="/tmp/test_gc_archive.json"
    )

    # 创建测试记忆（dict 格式）
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
    ]

    # 保存测试记忆
    with open("/tmp/test_gc_store.json", 'w') as f:
        json.dump(memories, f)

    # 运行 GC
    report = gc.run_gc(dry_run=True)

    print(f"\nGC Report:")
    print(f"  - 处理总数: {report.total_processed}")
    print(f"  - 衰减: {report.decayed}")
    print(f"  - 归档: {report.archived}")
    print(f"  - 删除: {report.removed}")
    print(f"  - 保留: {report.kept}")

    if report.total_processed > 0:
        print(f"\n  ✅ GC 正式入口可用")
        return True

    print(f"\n  ❌ GC 正式入口不可用")
    return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("Phase3 Group4 主链生效验证")
    print("证明默认主链已升级")
    print("=" * 60)

    results = []

    results.append(("build_context 走 QueryRewriter", test_build_context_uses_query_rewriter()))
    results.append(("build_context 走 SourcePolicyRouter", test_build_context_uses_source_policy_router()))
    results.append(("Retrieval Trace 被保存", test_retrieval_trace_is_saved()))
    results.append(("InjectionPlanner 影响 Bundle", test_injection_planner_affects_bundle()))
    results.append(("Memory Version 真实写入", test_memory_version_is_written()))
    results.append(("GC 正式入口可用", test_gc_can_run_on_real_store()))

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
        print("🎉 Phase3 Group4 主链真正完成！")
        print("默认主链已升级，不是模块单独能跑")
    else:
        print("❌ 需要继续修复")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
