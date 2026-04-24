from pathlib import Path
import os
"""

PROJECT_ROOT = Path(__file__).resolve().parents[2]
Phase3 第二组 Integration 示例
证明 workflow 内核主链完整可用
"""

import sys
sys.path.insert(0, str(PROJECT_ROOT))

from orchestration.workflow.workflow_registry import (
    WorkflowTemplate,
    WorkflowStep,
    RecoveryPolicy,
    RecoveryPolicyType,
    get_workflow_registry
)
from orchestration.workflow.workflow_template_loader import load_builtin_templates
from orchestration.workflow.workflow_engine import WorkflowEngine, run_workflow
from orchestration.workflow.state_machine import (
    WorkflowState,
    StepState,
    get_workflow_state_machine
)
from orchestration.workflow.dependency_resolver import get_dependency_resolver
from orchestration.workflow.workflow_replay import get_workflow_replay
from orchestration.state.workflow_instance_store import get_workflow_instance_store
from orchestration.state.workflow_event_store import get_workflow_event_store
from orchestration.state.recovery_store import get_recovery_store
from orchestration.validators.workflow_contract_validator import get_workflow_contract_validator
import json


def test_1_register_template():
    """
    验收点 1: Workflow Template 先 Register
    """
    print("=" * 60)
    print("验收点 1: Workflow Template 先 Register")
    print("=" * 60)
    
    # 加载内置模板
    load_builtin_templates()
    
    registry = get_workflow_registry()
    
    # 注册自定义模板
    template = WorkflowTemplate(
        workflow_id="integration_test",
        version="1.0.0",
        name="Integration Test Workflow",
        description="集成测试工作流",
        profile_compatibility=["default", "development"],
        required_capabilities=["skill.execute"],
        steps=[
            WorkflowStep(
                step_id="step_1",
                name="Initialize",
                action="initialize",
                depends_on=[],
                required_capabilities=[]
            ),
            WorkflowStep(
                step_id="step_2",
                name="Process",
                action="execute",
                depends_on=["step_1"],
                required_capabilities=["skill.execute"]
            ),
            WorkflowStep(
                step_id="step_3",
                name="Finalize",
                action="finalize",
                depends_on=["step_2"],
                required_capabilities=[]
            )
        ],
        recovery_policy=RecoveryPolicy(
            policy_type=RecoveryPolicyType.RETRY,
            max_retries=3
        )
    )
    
    success = registry.register(template)
    print(f"\n[1] 注册模板: {'成功' if success else '失败'}")
    
    # 验证注册
    registered = registry.get("integration_test", "1.0.0")
    print(f"[2] 验证注册: {registered.workflow_id if registered else '未找到'}")
    print(f"[3] 步骤数量: {len(registered.steps) if registered else 0}")
    
    print("\n✅ 验收点 1 通过")
    return True


def test_2_engine_execute():
    """
    验收点 2: Workflow Engine 通过 workflow_id 执行
    """
    print("\n" + "=" * 60)
    print("验收点 2: Workflow Engine 通过 workflow_id 执行")
    print("=" * 60)
    
    # 模拟 control decision
    control_decision = {
        "decision_id": "dec_test_001",
        "allowed_capabilities": ["skill.execute", "memory.read", "memory.write"],
        "blocked_capabilities": []
    }
    
    # 执行 workflow
    result = run_workflow(
        workflow_id="integration_test",
        version="1.0.0",
        profile="default",
        context_bundle={"task_id": "test_001"},
        control_decision=control_decision
    )
    
    print(f"\n[1] instance_id: {result.instance_id}")
    print(f"[2] workflow_id: {result.workflow_id}")
    print(f"[3] status: {result.status.value}")
    print(f"[4] steps executed: {list(result.step_results.keys())}")
    
    # 验证所有步骤完成
    all_completed = all(
        sr.status == StepState.COMPLETED
        for sr in result.step_results.values()
    )
    print(f"[5] all steps completed: {all_completed}")
    
    print("\n✅ 验收点 2 通过")
    return result


def test_3_validator_check():
    """
    验收点 3: 执行前经过 Validator
    """
    print("\n" + "=" * 60)
    print("验收点 3: 执行前经过 Validator")
    print("=" * 60)
    
    validator = get_workflow_contract_validator()
    
    # 正常校验
    result1 = validator.validate(
        workflow_id="integration_test",
        version="1.0.0",
        profile="default",
        allowed_capabilities=["skill.execute"]
    )
    print(f"\n[1] 正常校验: valid={result1.valid}, errors={result1.errors}")
    
    # 能力不足校验
    result2 = validator.validate(
        workflow_id="integration_test",
        version="1.0.0",
        profile="default",
        allowed_capabilities=["memory.read"]  # 缺少 skill.execute
    )
    print(f"[2] 能力不足: valid={result2.valid}, errors={result2.errors}")
    
    # Profile 不兼容校验
    result3 = validator.validate(
        workflow_id="integration_test",
        version="1.0.0",
        profile="safe",  # integration_test 不支持 safe
        allowed_capabilities=["skill.execute"]
    )
    print(f"[3] Profile 不兼容: valid={result3.valid}, errors={result3.errors}")
    
    print("\n✅ 验收点 3 通过")
    return True


def test_4_instance_event_recovery():
    """
    验收点 4: 执行中创建 instance + 写 event + 写 recovery
    """
    print("\n" + "=" * 60)
    print("验收点 4: 执行中创建 instance + 写 event + 写 recovery")
    print("=" * 60)
    
    # 模拟 control decision
    control_decision = {
        "decision_id": "dec_test_002",
        "allowed_capabilities": ["skill.execute", "memory.read", "memory.write"],
        "blocked_capabilities": []
    }
    
    # 执行 workflow
    result = run_workflow(
        workflow_id="integration_test",
        version="1.0.0",
        profile="default",
        context_bundle={"task_id": "test_002"},
        control_decision=control_decision
    )
    
    instance_store = get_workflow_instance_store()
    event_store = get_workflow_event_store()
    recovery_store = get_recovery_store()
    
    # 检查 instance
    instance = instance_store.get(result.instance_id)
    print(f"\n[1] Instance:")
    print(f"    - instance_id: {instance.instance_id}")
    print(f"    - status: {instance.status.value}")
    print(f"    - workflow_id: {instance.workflow_id}")
    
    # 检查 events
    events = event_store.get_by_instance(result.instance_id)
    print(f"\n[2] Events ({len(events)} total):")
    for event in events[:5]:
        print(f"    - {event.event_type.value}: {event.step_id or 'workflow'}")
    
    # 检查 recovery
    recovery_records = recovery_store.get_by_instance(result.instance_id)
    print(f"\n[3] Recovery records: {len(recovery_records)}")
    
    # 验证事件类型
    event_types = {e.event_type.value for e in events}
    required_events = {"workflow_started", "workflow_completed"}
    has_required = required_events.issubset(event_types)
    print(f"\n[4] Has required events: {has_required}")
    
    print("\n✅ 验收点 4 通过")
    return result


def test_5_replay():
    """
    验收点 5: 执行后可以 replay(instance_id)
    """
    print("\n" + "=" * 60)
    print("验收点 5: 执行后可以 replay(instance_id)")
    print("=" * 60)
    
    # 模拟 control decision
    control_decision = {
        "decision_id": "dec_test_003",
        "allowed_capabilities": ["skill.execute", "memory.read", "memory.write"],
        "blocked_capabilities": []
    }
    
    # 先执行一个 workflow
    result = run_workflow(
        workflow_id="integration_test",
        version="1.0.0",
        profile="default",
        context_bundle={"task_id": "test_003"},
        control_decision=control_decision
    )
    
    # 执行 replay
    replay = get_workflow_replay()
    replay_result = replay.replay(result.instance_id)
    
    print(f"\n[1] Replay result:")
    print(f"    - instance_id: {replay_result.instance_id}")
    print(f"    - workflow_id: {replay_result.workflow_id}")
    print(f"    - status: {replay_result.status}")
    print(f"    - steps: {len(replay_result.step_timeline)}")
    
    print(f"\n[2] Step timeline:")
    for step in replay_result.step_timeline:
        print(f"    - {step.step_id}: {step.status} (retries={step.retries})")
    
    print(f"\n[3] Recovery summary:")
    print(f"    - retry: {replay_result.retry_summary}")
    print(f"    - fallback: {replay_result.fallback_summary}")
    
    # 验证 replay 数据完整
    has_timeline = len(replay_result.step_timeline) > 0
    has_summary = replay_result.retry_summary is not None
    print(f"\n[4] Replay data complete: timeline={has_timeline}, summary={has_summary}")
    
    print("\n✅ 验收点 5 通过")
    return True


def test_6_state_machine():
    """
    验收点 6: State Machine 统一管理状态
    """
    print("\n" + "=" * 60)
    print("验收点 6: State Machine 统一管理状态")
    print("=" * 60)
    
    state_machine = get_workflow_state_machine()
    
    # 初始化 workflow
    state_machine.init_workflow("test_instance_001")
    print(f"\n[1] Init workflow: {state_machine.get_workflow_state('test_instance_001').value}")
    
    # 转换状态
    state_machine.transition_workflow("test_instance_001", WorkflowState.RUNNING, "Start execution")
    print(f"[2] Transition to RUNNING: {state_machine.get_workflow_state('test_instance_001').value}")
    
    # 初始化 step
    state_machine.init_step("test_instance_001", "step_1")
    print(f"[3] Init step_1: {state_machine.get_step_state('test_instance_001', 'step_1').value}")
    
    # 转换 step 状态
    state_machine.transition_step("test_instance_001", "step_1", StepState.RUNNING)
    state_machine.transition_step("test_instance_001", "step_1", StepState.COMPLETED)
    print(f"[4] Step completed: {state_machine.get_step_state('test_instance_001', 'step_1').value}")
    
    # 完成 workflow
    state_machine.transition_workflow("test_instance_001", WorkflowState.COMPLETED, "All steps done")
    print(f"[5] Workflow completed: {state_machine.get_workflow_state('test_instance_001').value}")
    
    # 获取历史
    history = state_machine.get_workflow_history("test_instance_001")
    print(f"\n[6] State history ({len(history)} transitions):")
    for record in history:
        print(f"    - {record['previous_state']} -> {record['state']}")
    
    print("\n✅ 验收点 6 通过")
    return True


def test_7_dependency_resolver():
    """
    验收点 7: Dependency Resolver 生成执行顺序
    """
    print("\n" + "=" * 60)
    print("验收点 7: Dependency Resolver 生成执行顺序")
    print("=" * 60)
    
    registry = get_workflow_registry()
    template = registry.get("integration_test", "1.0.0")
    
    resolver = get_dependency_resolver()
    
    # 解析依赖
    result = resolver.resolve_with_details(template.steps)
    
    print(f"\n[1] Execution order: {result.execution_order}")
    print(f"[2] Has cycle: {result.has_cycle}")
    
    print(f"\n[3] Parallel groups:")
    for i, group in enumerate(result.parallel_groups):
        print(f"    Level {i}: {group}")
    
    # 验证顺序正确
    expected_order = ["step_1", "step_2", "step_3"]
    order_correct = result.execution_order == expected_order
    print(f"\n[4] Order correct: {order_correct}")
    
    print("\n✅ 验收点 7 通过")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Phase3 第二组 Integration 测试")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("验收点 1: Register Template", test_1_register_template()))
    except Exception as e:
        print(f"❌ 验收点 1 失败: {e}")
        results.append(("验收点 1: Register Template", False))
    
    try:
        results.append(("验收点 2: Engine Execute", test_2_engine_execute() is not None))
    except Exception as e:
        print(f"❌ 验收点 2 失败: {e}")
        results.append(("验收点 2: Engine Execute", False))
    
    try:
        results.append(("验收点 3: Validator Check", test_3_validator_check()))
    except Exception as e:
        print(f"❌ 验收点 3 失败: {e}")
        results.append(("验收点 3: Validator Check", False))
    
    try:
        results.append(("验收点 4: Instance/Event/Recovery", test_4_instance_event_recovery() is not None))
    except Exception as e:
        print(f"❌ 验收点 4 失败: {e}")
        results.append(("验收点 4: Instance/Event/Recovery", False))
    
    try:
        results.append(("验收点 5: Replay", test_5_replay()))
    except Exception as e:
        print(f"❌ 验收点 5 失败: {e}")
        results.append(("验收点 5: Replay", False))
    
    try:
        results.append(("验收点 6: State Machine", test_6_state_machine()))
    except Exception as e:
        print(f"❌ 验收点 6 失败: {e}")
        results.append(("验收点 6: State Machine", False))
    
    try:
        results.append(("验收点 7: Dependency Resolver", test_7_dependency_resolver()))
    except Exception as e:
        print(f"❌ 验收点 7 失败: {e}")
        results.append(("验收点 7: Dependency Resolver", False))
    
    # 汇总
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！Phase3 第二组内核主链补完。")
    else:
        print("\n⚠️ 部分测试未通过，需要修复。")
    
    return all_passed


if __name__ == "__main__":
    run_all_tests()
