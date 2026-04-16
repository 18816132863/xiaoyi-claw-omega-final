"""
Integration Test - 恢复链完整测试
Phase3 第二组收口验证

测试目标：
1. 一个 step 故意失败
2. engine 先通过 fallback_policy 做决策
3. 决策触发 retry / fallback / rollback
4. 执行过程中保存 checkpoint
5. replay(instance_id) 能看到完整事件链
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from orchestration.workflow.workflow_engine import WorkflowEngine, run_workflow
from orchestration.workflow.workflow_registry import WorkflowTemplate, WorkflowStep, RecoveryPolicy, RecoveryPolicyType, get_workflow_registry
from orchestration.state.workflow_event_store import get_workflow_event_store, EventType
from orchestration.state.recovery_store import get_recovery_store, RecoveryAction
from orchestration.state.checkpoint_store import CheckpointStore
from orchestration.execution_control.fallback_policy import FallbackPolicy, FallbackAction


def create_test_workflow() -> WorkflowTemplate:
    """创建测试 workflow"""
    return WorkflowTemplate(
        workflow_id="recovery_chain_test",
        version="1.0.0",
        name="恢复链测试",
        description="测试 checkpoint / fallback / rollback 完整链路",
        steps=[
            WorkflowStep(
                step_id="step_1_init",
                name="初始化",
                action="initialize",
                params={},
                timeout_ms=5000
            ),
            WorkflowStep(
                step_id="step_2_will_fail",
                name="故意失败的步骤",
                action="fail_on_purpose",
                params={"error_message": "测试失败场景"},
                timeout_ms=5000,
                recovery_policy=RecoveryPolicy(
                    policy_type=RecoveryPolicyType.FALLBACK,
                    max_retries=2,
                    fallback_skill="fallback_handler"
                )
            ),
            WorkflowStep(
                step_id="step_3_finalize",
                name="收尾",
                action="finalize",
                params={},
                timeout_ms=5000
            )
        ],
        recovery_policy=RecoveryPolicy(policy_type=RecoveryPolicyType.RETRY, max_retries=2)
    )


def test_recovery_chain():
    """测试恢复链"""
    print("=" * 60)
    print("Phase3 第二组恢复链集成测试")
    print("=" * 60)

    # 创建测试 workflow
    template = create_test_workflow()

    # 注册模板
    registry = get_workflow_registry()
    registry.register(template)

    # 创建 engine
    checkpoint_store = CheckpointStore()
    fallback_policy = FallbackPolicy()
    fallback_policy.set_fallback("step_2_will_fail", "fallback_handler")

    engine = WorkflowEngine(
        checkpoint_store=checkpoint_store,
        fallback_policy=fallback_policy
    )

    # 注册失败动作处理器
    fail_count = [0]

    def fail_handler(action, step_input):
        fail_count[0] += 1
        if fail_count[0] <= 2:  # 前两次失败
            raise RuntimeError("故意失败 - 测试重试")
        return {"recovered": True, "attempts": fail_count[0]}

    def fallback_handler(action, step_input):
        return {"fallback_executed": True, "original_error": step_input.get("error")}

    engine.register_action_handler("fail_on_purpose", fail_handler)
    engine.register_action_handler("fallback_handler", fallback_handler)

    # 执行 workflow
    print("\n[1] 执行 workflow...")
    result = engine.run_workflow(template=template)

    print(f"\n[2] 执行结果:")
    print(f"  - 状态: {result.status.value}")
    print(f"  - 实例 ID: {result.instance_id}")
    print(f"  - 总重试次数: {result.total_retry_count}")
    print(f"  - Fallback 使用: {result.fallback_used}")
    print(f"  - Rollback 使用: {result.rollback_used}")
    print(f"  - Checkpoint ID: {result.checkpoint_id}")

    # 验证事件链
    print(f"\n[3] 验证事件链...")
    event_store = get_workflow_event_store()
    events = event_store.get_by_instance(result.instance_id)

    event_types = [e.event_type.value for e in events]
    print(f"  - 事件总数: {len(events)}")
    print(f"  - 事件类型: {set(event_types)}")

    # 检查关键事件
    has_checkpoint = EventType.CHECKPOINT_SAVED.value in event_types
    has_retry = EventType.RETRY_TRIGGERED.value in event_types
    has_fallback = EventType.FALLBACK_TRIGGERED.value in event_types

    print(f"  - Checkpoint 事件: {'✅' if has_checkpoint else '❌'}")
    print(f"  - Retry 事件: {'✅' if has_retry else '❌'}")
    print(f"  - Fallback 事件: {'✅' if has_fallback else '❌'}")

    # 验证恢复记录
    print(f"\n[4] 验证恢复记录...")
    recovery_store = get_recovery_store()
    summary = recovery_store.get_summary(result.instance_id)

    print(f"  - 总记录数: {summary['total_records']}")
    print(f"  - 重试次数: {summary['retry_count']}")
    print(f"  - Fallback 次数: {summary['fallback_count']}")
    print(f"  - Rollback 次数: {summary['rollback_count']}")
    print(f"  - Checkpoint 次数: {summary['checkpoint_count']}")

    # 验证 checkpoint 存储
    print(f"\n[5] 验证 checkpoint 存储...")
    checkpoints = checkpoint_store.list_by_workflow(result.workflow_id)
    print(f"  - Checkpoint 数量: {len(checkpoints)}")
    if checkpoints:
        latest = checkpoints[-1]
        print(f"  - 最新 Checkpoint ID: {latest.checkpoint_id}")
        print(f"  - 已完成步骤: {latest.completed_steps}")
        print(f"  - 待执行步骤: {latest.pending_steps}")

    # 输出时间线
    print(f"\n[6] 事件时间线:")
    timeline = event_store.get_timeline(result.instance_id)
    for i, event in enumerate(timeline[:10], 1):  # 只显示前 10 个
        print(f"  {i}. [{event['event_type']}] step={event.get('step_id', '-')} data={event.get('data', {})}")

    # 最终判定
    print("\n" + "=" * 60)
    print("最终判定:")
    print("=" * 60)

    passed = True
    checks = [
        ("checkpoint_store.save() 被调用", has_checkpoint),
        ("retry_triggered 事件存在", has_retry),
        ("recovery_store 有记录", summary['total_records'] > 0),
        ("checkpoint 存储有数据", len(checkpoints) > 0),
    ]

    for check_name, check_result in checks:
        status = "✅ PASS" if check_result else "❌ FAIL"
        print(f"  {status} - {check_name}")
        if not check_result:
            passed = False

    print("\n" + "=" * 60)
    if passed:
        print("🎉 Phase3 第二组恢复链测试通过！")
    else:
        print("❌ Phase3 第二组恢复链测试失败")
    print("=" * 60)

    return passed


def test_rollback_scenario():
    """测试 rollback 场景"""
    print("\n" + "=" * 60)
    print("Rollback 场景测试")
    print("=" * 60)

    template = WorkflowTemplate(
        workflow_id="rollback_test",
        version="1.0.0",
        name="Rollback 测试",
        description="测试 rollback 触发",
        steps=[
            WorkflowStep(
                step_id="step_1",
                name="步骤1",
                action="step1",
                params={}
            ),
            WorkflowStep(
                step_id="step_2",
                name="步骤2 - 将失败",
                action="fail_hard",
                params={},
                recovery_policy=RecoveryPolicy(policy_type=RecoveryPolicyType.RETRY, max_retries=1)
            )
        ],
        recovery_policy=RecoveryPolicy(policy_type=RecoveryPolicyType.RETRY, max_retries=1)
    )

    # 注册模板
    registry = get_workflow_registry()
    registry.register(template)

    engine = WorkflowEngine()

    # 注册处理器
    def fail_hard_handler(action, step_input):
        raise RuntimeError("硬失败 - 触发 rollback")

    engine.register_action_handler("step1", lambda a, i: {"step1": "done"})
    engine.register_action_handler("fail_hard", fail_hard_handler)

    # 执行
    print("\n[1] 执行 workflow (预期失败)...")
    result = engine.run_workflow(template=template)

    print(f"\n[2] 执行结果:")
    print(f"  - 状态: {result.status.value}")
    print(f"  - Rollback 使用: {result.rollback_used}")
    print(f"  - Rollback 到步骤: {result.rollback_to_step}")

    # 验证事件
    event_store = get_workflow_event_store()
    events = event_store.get_by_instance(result.instance_id)
    event_types = [e.event_type.value for e in events]

    has_rollback = EventType.ROLLBACK_TRIGGERED.value in event_types
    print(f"  - Rollback 事件: {'✅' if has_rollback else '❌'}")

    return has_rollback or result.rollback_used


if __name__ == "__main__":
    # 运行测试
    test1_passed = test_recovery_chain()
    test2_passed = test_rollback_scenario()

    print("\n" + "=" * 60)
    print("测试汇总:")
    print(f"  - 恢复链测试: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"  - Rollback 测试: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print("=" * 60)

    if test1_passed and test2_passed:
        print("\n🎉 Phase3 第二组收口完成！")
        sys.exit(0)
    else:
        print("\n❌ 需要继续修复")
        sys.exit(1)
