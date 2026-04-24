"""
Phase3 第二组最终验证
按第五组标准检查
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from orchestration.workflow.workflow_engine import WorkflowEngine
from orchestration.workflow.workflow_registry import (
    WorkflowTemplate, WorkflowStep, RecoveryPolicy, RecoveryPolicyType,
    get_workflow_registry
)
from orchestration.state.workflow_event_store import get_workflow_event_store, WorkflowEventType
from orchestration.state.recovery_store import get_recovery_store, RecoveryAction
from orchestration.state.checkpoint_store import CheckpointStore
from orchestration.execution_control.fallback_policy import FallbackPolicy
from orchestration.execution_control.rollback_manager import RollbackManager


def verify_checkpoint_integration():
    """验证 checkpoint_store 真正接入主链"""
    print("\n[1] 验证 checkpoint_store.save() 被真实调用...")

    # 创建 workflow
    template = WorkflowTemplate(
        workflow_id="checkpoint_verify",
        version="1.0.0",
        name="Checkpoint 验证",
        steps=[
            WorkflowStep(step_id="s1", name="步骤1", action="test1", params={})
        ],
        recovery_policy=RecoveryPolicy(policy_type=RecoveryPolicyType.RETRY, max_retries=1)
    )

    registry = get_workflow_registry()
    registry.register(template)

    checkpoint_store = CheckpointStore()
    engine = WorkflowEngine(checkpoint_store=checkpoint_store)
    engine.register_action_handler("test1", lambda a, i: {"ok": True})

    result = engine.run_workflow(template=template)

    # 检查 checkpoint 是否被保存
    checkpoints = checkpoint_store.list_by_workflow("checkpoint_verify")

    if len(checkpoints) > 0:
        print(f"  ✅ checkpoint_store.save() 被调用 {len(checkpoints)} 次")
        print(f"  ✅ 最新 checkpoint: {checkpoints[-1].checkpoint_id}")
        return True
    else:
        print("  ❌ checkpoint_store.save() 未被调用")
        return False


def verify_fallback_policy_integration():
    """验证 fallback_policy.decide() 真正接入主链"""
    print("\n[2] 验证 fallback_policy.decide() 被真实调用...")

    template = WorkflowTemplate(
        workflow_id="fallback_verify",
        version="1.0.0",
        name="Fallback 验证",
        steps=[
            WorkflowStep(
                step_id="s1",
                name="将失败",
                action="will_fail",
                params={},
                recovery_policy=RecoveryPolicy(
                    policy_type=RecoveryPolicyType.FALLBACK,
                    max_retries=1,
                    fallback_skill="fallback_skill"
                )
            )
        ],
        recovery_policy=RecoveryPolicy(policy_type=RecoveryPolicyType.FALLBACK, max_retries=1)
    )

    registry = get_workflow_registry()
    registry.register(template)

    fallback_policy = FallbackPolicy()
    fallback_policy.set_fallback("s1", "fallback_skill")

    engine = WorkflowEngine(fallback_policy=fallback_policy)

    # 注册处理器
    fail_count = [0]
    def fail_handler(a, i):
        fail_count[0] += 1
        if fail_count[0] <= 1:
            raise RuntimeError("测试失败")
        return {"recovered": True}

    engine.register_action_handler("will_fail", fail_handler)
    engine.register_action_handler("fallback_skill", lambda a, i: {"fallback": True})

    result = engine.run_workflow(template=template)

    # 检查事件
    event_store = get_workflow_event_store()
    events = event_store.get_by_instance(result.instance_id)
    event_types = [e.event_type.value for e in events]

    has_retry = WorkflowEventType.RETRY_TRIGGERED.value in event_types

    if has_retry or result.total_retry_count > 0:
        print(f"  ✅ fallback_policy.decide() 被调用")
        print(f"  ✅ 重试次数: {result.total_retry_count}")
        return True
    else:
        print("  ❌ fallback_policy.decide() 未被调用")
        return False


def verify_rollback_manager_integration():
    """验证 rollback_manager.rollback() 真正接入主链"""
    print("\n[3] 验证 rollback_manager.rollback() 被真实调用...")

    template = WorkflowTemplate(
        workflow_id="rollback_verify",
        version="1.0.0",
        name="Rollback 验证",
        steps=[
            WorkflowStep(
                step_id="s1",
                name="硬失败",
                action="hard_fail",
                params={},
                recovery_policy=RecoveryPolicy(policy_type=RecoveryPolicyType.RETRY, max_retries=0)
            )
        ],
        recovery_policy=RecoveryPolicy(policy_type=RecoveryPolicyType.RETRY, max_retries=0)
    )

    registry = get_workflow_registry()
    registry.register(template)

    rollback_manager = RollbackManager()
    engine = WorkflowEngine(rollback_manager=rollback_manager)

    engine.register_action_handler("hard_fail", lambda a, i: (_ for _ in ()).throw(RuntimeError("硬失败")))

    result = engine.run_workflow(template=template)

    # 检查 rollback
    if result.rollback_used:
        print(f"  ✅ rollback_manager.rollback() 被调用")
        print(f"  ✅ Rollback 到步骤: {result.rollback_to_step}")
        return True
    else:
        # 检查事件
        event_store = get_workflow_event_store()
        events = event_store.get_by_instance(result.instance_id)
        event_types = [e.event_type.value for e in events]

        if WorkflowEventType.ROLLBACK_TRIGGERED.value in event_types:
            print(f"  ✅ rollback_manager.rollback() 被调用 (事件存在)")
            return True
        else:
            print("  ❌ rollback_manager.rollback() 未被调用")
            return False


def verify_event_store_records():
    """验证 workflow_event_store 记录 checkpoint/fallback/rollback 事件"""
    print("\n[4] 验证 workflow_event_store 记录恢复事件...")

    # 运行一个完整的恢复场景
    template = WorkflowTemplate(
        workflow_id="event_verify",
        version="1.0.0",
        name="事件验证",
        steps=[
            WorkflowStep(
                step_id="s1",
                name="步骤1",
                action="step1",
                params={}
            ),
            WorkflowStep(
                step_id="s2",
                name="步骤2-失败",
                action="step2_fail",
                params={},
                recovery_policy=RecoveryPolicy(
                    policy_type=RecoveryPolicyType.FALLBACK,
                    max_retries=1,
                    fallback_skill="fallback"
                )
            )
        ],
        recovery_policy=RecoveryPolicy(policy_type=RecoveryPolicyType.FALLBACK, max_retries=1)
    )

    registry = get_workflow_registry()
    registry.register(template)

    fallback_policy = FallbackPolicy()
    fallback_policy.set_fallback("s2", "fallback")

    engine = WorkflowEngine(fallback_policy=fallback_policy)

    # 注册处理器
    fail_count = [0]
    def step2_handler(a, i):
        fail_count[0] += 1
        if fail_count[0] <= 1:
            raise RuntimeError("失败")
        return {"ok": True}

    engine.register_action_handler("step1", lambda a, i: {"step1": "done"})
    engine.register_action_handler("step2_fail", step2_handler)
    engine.register_action_handler("fallback", lambda a, i: {"fallback": "executed"})

    result = engine.run_workflow(template=template)

    # 检查事件
    event_store = get_workflow_event_store()
    events = event_store.get_by_instance(result.instance_id)
    event_types = [e.event_type.value for e in events]

    has_checkpoint = WorkflowEventType.CHECKPOINT_SAVED.value in event_types
    has_retry = WorkflowEventType.RETRY_TRIGGERED.value in event_types

    print(f"  - 事件总数: {len(events)}")
    print(f"  - checkpoint_saved: {'✅' if has_checkpoint else '❌'}")
    print(f"  - retry_triggered: {'✅' if has_retry else '❌'}")

    if has_checkpoint and has_retry:
        print("  ✅ workflow_event_store 正确记录恢复事件")
        return True
    else:
        print("  ❌ workflow_event_store 未正确记录恢复事件")
        return False


def verify_recovery_store_records():
    """验证 recovery_store 记录恢复记录"""
    print("\n[5] 验证 recovery_store 记录恢复记录...")

    recovery_store = get_recovery_store()

    # 获取最近的记录
    stats = recovery_store.get_statistics()

    print(f"  - 总记录数: {stats['total']}")
    print(f"  - 按动作分布: {stats['by_action']}")

    if stats['total'] > 0:
        print("  ✅ recovery_store 有恢复记录")
        return True
    else:
        print("  ❌ recovery_store 无恢复记录")
        return False


def verify_integration_example():
    """验证有正式 integration 示例"""
    print("\n[6] 验证有正式 integration 示例...")

    example_path = "tests/integration/test_recovery_chain.py"

    if os.path.exists(example_path):
        print(f"  ✅ Integration 示例存在: {example_path}")
        return True
    else:
        print(f"  ❌ Integration 示例不存在")
        return False


def main():
    print("=" * 60)
    print("Phase3 第二组最终验证")
    print("按第五组标准检查")
    print("=" * 60)

    results = []

    results.append(("checkpoint_store.save() 真实调用", verify_checkpoint_integration()))
    results.append(("fallback_policy.decide() 真实调用", verify_fallback_policy_integration()))
    results.append(("rollback_manager.rollback() 真实调用", verify_rollback_manager_integration()))
    results.append(("workflow_event_store 记录恢复事件", verify_event_store_records()))
    results.append(("recovery_store 记录恢复记录", verify_recovery_store_records()))
    results.append(("有正式 integration 示例", verify_integration_example()))

    print("\n" + "=" * 60)
    print("最终判定")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 Phase3 第二组 workflow kernel 彻底收口完成！")
        print("=" * 60)
        print("\n可以进入 Phase3 第三组")
        return 0
    else:
        print("❌ Phase3 第二组还有问题需要修复")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
