"""
测试 Memory Context 主链
V9.0.0 简化架构，memory_context.builder 模块已移除
"""

import pytest


@pytest.mark.skip(reason="V9.0.0 简化架构，memory_context.builder 模块已移除")
async def test_build_context_uses_query_rewriter():
    """测试 build_context() 走 QueryRewriter"""
    pass


@pytest.mark.skip(reason="V9.0.0 简化架构，memory_context.builder 模块已移除")
async def test_build_context_uses_source_policy_router():
    """测试 build_context() 走 SourcePolicyRouter"""
    pass


@pytest.mark.skip(reason="V9.0.0 简化架构，memory_context.builder 模块已移除")
async def test_retrieval_trace_is_saved():
    """测试检索轨迹被保存"""
    pass


@pytest.mark.skip(reason="V9.0.0 简化架构，memory_context.builder 模块已移除")
async def test_injection_planner_affects_bundle():
    """测试注入计划影响捆绑包"""
    pass


@pytest.mark.skip(reason="V9.0.0 简化架构，memory_context.builder 模块已移除")
async def test_memory_version_is_written():
    """测试内存版本被写入"""
    pass


@pytest.mark.skip(reason="V9.0.0 简化架构，memory_context.builder 模块已移除")
async def test_gc_can_run_on_real_store():
    """测试 GC 可以在真实存储上运行"""
    pass
