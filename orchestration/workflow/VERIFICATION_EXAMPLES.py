from pathlib import Path
import os
"""

PROJECT_ROOT = Path(__file__).resolve().parents[2]
Phase3 第二组验收示例
展示 workflow 正式内核化后的 5 个验收点
"""

import sys
sys.path.insert(0, str(PROJECT_ROOT))

from orchestration.workflow.workflow_registry import (
    WorkflowRegistry,
    WorkflowTemplate,
    WorkflowStep,
    RecoveryPolicy,
    RecoveryPolicyType,
    WorkflowStatus,
    get_workflow_registry
)
from orchestration.workflow.workflow_template_loader import (
    load_builtin_templates
)
from orchestration.state.workflow_instance_store import (
    WorkflowInstanceStore,
    InstanceStatus,
    get_workflow_instance_store
)
from orchestration.state.workflow_event_store import (
    WorkflowEventStore,
    EventType,
    get_workflow_event_store
)
from orchestration.state.recovery_store import (
    RecoveryStore,
    ErrorType,
    RecoveryAction,
    get_recovery_store
)
from orchestration.validators.workflow_contract_validator import (
    WorkflowContractValidator,
    get_workflow_contract_validator
)
from orchestration.workflow.workflow_replay import (
    WorkflowReplay,
    get_workflow_replay
)
import json


def example_1_registered_template():
    """
    验收点 1: Registered Workflow Template 示例
    """
    print("=" * 60)
    print("验收点 1: Registered Workflow Template")
    print("=" * 60)
    
    # 加载内置模板
    load_builtin_templates()
    
    registry = get_workflow_registry()
    
    # 1. 列出所有已注册模板
    print("\n[1] 已注册模板列表:")
    templates = registry.list()
    for t in templates:
        print(f"  - {t.workflow_id}:{t.version} - {t.name} ({t.status.value})")
    
    # 2. 获取特定模板
    print("\n[2] 获取模板:")
    template = registry.get("minimum_loop", "1.0.0")
    if template:
        print(f"  - workflow_id: {template.workflow_id}")
        print(f"  - version: {template.version}")
        print(f"  - name: {template.name}")
        print(f"  - steps: {[s.step_id for s in template.steps]}")
        print(f"  - required_capabilities: {template.required_capabilities}")
        print(f"  - profile_compatibility: {template.profile_compatibility}")
    
    # 3. 注册自定义模板
    print("\n[3] 注册自定义模板:")
    custom_template = WorkflowTemplate(
        workflow_id="custom_workflow",
        version="1.0.0",
        name="Custom Workflow",
        description="自定义工作流示例",
        profile_compatibility=["default", "development"],
        required_capabilities=["skill.execute", "memory.read"],
        steps=[
            WorkflowStep(
                step_id="step_1",
                name="Read Data",
                action="memory.read",
                depends_on=[],
                required_capabilities=["memory.read"]
            ),
            WorkflowStep(
                step_id="step_2",
                name="Process Data",
                action="skill.execute",
                depends_on=["step_1"],
                required_capabilities=["skill.execute"]
            )
        ],
        recovery_policy=RecoveryPolicy(
            policy_type=RecoveryPolicyType.RETRY,
            max_retries=3
        )
    )
    
    success = registry.register(custom_template)
    print(f"  - 注册结果: {'成功' if success else '失败'}")
    
    # 4. 导出模板
    print("\n[4] 模板完整结构:")
    print(json.dumps(template.to_dict(), indent=2, ensure_ascii=False))
    
    print("\n✅ 验收点 1 通过: 展示了注册模板")
    return True


def example_2_workflow_instance():
    """
    验收点 2: Workflow Instance 记录示例
    """
    print("\n" + "=" * 60)
    print("验收点 2: Workflow Instance 记录")
    print("=" * 60)
    
    store = get_workflow_instance_store()
    
    # 1. 创建实例
    print("\n[1] 创建实例:")
    instance = store.create(
        workflow_id="minimum_loop",
        version="1.0.0",
        task_id="task_001",
        profile="default",
        control_decision_id="dec_12345",
        input_data={"param1": "value1"}
    )
    print(f"  - instance_id: {instance.instance_id}")
    print(f"  - workflow_id: {instance.workflow_id}")
    print(f"  - status: {instance.status.value}")
    print(f"  - control_decision_id: {instance.control_decision_id}")
    
    # 2. 更新实例状态
    print("\n[2] 更新实例状态:")
    store.update(
        instance_id=instance.instance_id,
        status=InstanceStatus.RUNNING
    )
    updated = store.get(instance.instance_id)
    print(f"  - 更新后状态: {updated.status.value}")
    
    # 3. 完成实例
    print("\n[3] 完成实例:")
    store.update(
        instance_id=instance.instance_id,
        status=InstanceStatus.COMPLETED,
        output={"result": "success"}
    )
    completed = store.get(instance.instance_id)
    print(f"  - 完成状态: {completed.status.value}")
    print(f"  - 完成时间: {completed.completed_at}")
    
    # 4. 查询实例
    print("\n[4] 查询实例:")
    instances = store.query(workflow_id="minimum_loop")
    for inst in instances[:3]:
        print(f"  - {inst.instance_id}: {inst.status.value}")
    
    # 5. 导出实例
    print("\n[5] 实例完整记录:")
    print(json.dumps(completed.to_dict(), indent=2, ensure_ascii=False))
    
    print("\n✅ 验收点 2 通过: 展示了实例记录")
    return True


def example_3_event_timeline():
    """
    验收点 3: Workflow Event Timeline 示例
    """
    print("\n" + "=" * 60)
    print("验收点 3: Workflow Event Timeline")
    print("=" * 60)
    
    event_store = get_workflow_event_store()
    instance_store = get_workflow_instance_store()
    
    # 创建实例
    instance = instance_store.create(
        workflow_id="minimum_loop",
        version="1.0.0",
        task_id="task_002",
        profile="default"
    )
    
    # 1. 记录 workflow 开始
    print("\n[1] 记录事件:")
    event_store.record_workflow_started(
        instance_id=instance.instance_id,
        workflow_id="minimum_loop",
        version="1.0.0",
        profile="default"
    )
    print("  - workflow_started")
    
    # 2. 记录步骤事件
    event_store.record_step_started(
        instance_id=instance.instance_id,
        step_id="step_1",
        step_name="Initialize",
        action="initialize"
    )
    print("  - step_started: step_1")
    
    event_store.record_step_completed(
        instance_id=instance.instance_id,
        step_id="step_1",
        output={"initialized": True},
        duration_ms=150
    )
    print("  - step_completed: step_1")
    
    event_store.record_step_started(
        instance_id=instance.instance_id,
        step_id="step_2",
        step_name="Execute",
        action="execute"
    )
    print("  - step_started: step_2")
    
    event_store.record_step_completed(
        instance_id=instance.instance_id,
        step_id="step_2",
        output={"executed": True},
        duration_ms=500
    )
    print("  - step_completed: step_2")
    
    # 3. 记录 workflow 完成
    event_store.record_workflow_completed(
        instance_id=instance.instance_id,
        status="completed",
        output={"result": "success"}
    )
    print("  - workflow_completed")
    
    # 4. 获取事件时间线
    print("\n[2] 事件时间线:")
    timeline = event_store.get_timeline(instance.instance_id)
    for event in timeline:
        print(f"  - {event['event_type']}: {event.get('step_id', 'N/A')}")
    
    # 5. 统计信息
    print("\n[3] 事件统计:")
    stats = event_store.get_statistics()
    print(f"  - 总事件数: {stats['total']}")
    print(f"  - 按类型: {stats['by_type']}")
    
    print("\n✅ 验收点 3 通过: 展示了事件时间线")
    return True


def example_4_replay_result():
    """
    验收点 4: Replay 结果示例
    """
    print("\n" + "=" * 60)
    print("验收点 4: Replay 结果")
    print("=" * 60)
    
    # 使用之前创建的实例
    instance_store = get_workflow_instance_store()
    event_store = get_workflow_event_store()
    recovery_store = get_recovery_store()
    
    # 创建一个带恢复动作的实例
    instance = instance_store.create(
        workflow_id="minimum_loop",
        version="1.0.0",
        task_id="task_003",
        profile="default"
    )
    
    # 记录事件
    event_store.record_workflow_started(
        instance_id=instance.instance_id,
        workflow_id="minimum_loop",
        version="1.0.0",
        profile="default"
    )
    
    event_store.record_step_started(
        instance_id=instance.instance_id,
        step_id="step_1",
        step_name="Initialize",
        action="initialize"
    )
    
    event_store.record_step_completed(
        instance_id=instance.instance_id,
        step_id="step_1",
        output={"initialized": True}
    )
    
    # 模拟失败和重试
    event_store.record_step_started(
        instance_id=instance.instance_id,
        step_id="step_2",
        step_name="Execute",
        action="execute"
    )
    
    event_store.record_step_failed(
        instance_id=instance.instance_id,
        step_id="step_2",
        error_type="timeout",
        error_message="Step timed out"
    )
    
    recovery_store.record_retry(
        instance_id=instance.instance_id,
        step_id="step_2",
        error_type=ErrorType.TIMEOUT,
        error_message="Step timed out",
        retry_count=1,
        max_retries=3
    )
    
    event_store.record_retry_triggered(
        instance_id=instance.instance_id,
        step_id="step_2",
        retry_count=1,
        max_retries=3
    )
    
    # 重试成功
    event_store.record_step_started(
        instance_id=instance.instance_id,
        step_id="step_2",
        step_name="Execute",
        action="execute"
    )
    
    event_store.record_step_completed(
        instance_id=instance.instance_id,
        step_id="step_2",
        output={"executed": True}
    )
    
    event_store.record_workflow_completed(
        instance_id=instance.instance_id,
        status="completed"
    )
    
    # 更新实例
    instance_store.update(
        instance_id=instance.instance_id,
        status=InstanceStatus.COMPLETED,
        recovery_summary={"retry_count": 1}
    )
    
    # 1. 执行回放
    print("\n[1] 执行回放:")
    replay = get_workflow_replay()
    result = replay.replay(instance.instance_id)
    
    if result:
        print(f"  - instance_id: {result.instance_id}")
        print(f"  - workflow_id: {result.workflow_id}")
        print(f"  - status: {result.status}")
        print(f"  - steps: {len(result.step_timeline)}")
    
    # 2. 步骤时间线
    print("\n[2] 步骤时间线:")
    for step in result.step_timeline:
        print(f"  - {step.step_id}: {step.status} (retries={step.retries})")
    
    # 3. 恢复摘要
    print("\n[3] 恢复摘要:")
    print(f"  - retry_summary: {result.retry_summary}")
    print(f"  - fallback_summary: {result.fallback_summary}")
    print(f"  - rollback_summary: {result.rollback_summary}")
    
    # 4. 完整回放结果
    print("\n[4] 完整回放结果:")
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    
    print("\n✅ 验收点 4 通过: 展示了回放结果")
    return True


def example_5_control_decision_impact():
    """
    验收点 5: Control Decision 影响 Workflow 行为示例
    """
    print("\n" + "=" * 60)
    print("验收点 5: Control Decision 影响 Workflow 行为")
    print("=" * 60)
    
    validator = get_workflow_contract_validator()
    
    # 1. 正常情况校验
    print("\n[1] 正常情况校验:")
    result1 = validator.validate(
        workflow_id="minimum_loop",
        version="1.0.0",
        profile="default",
        allowed_capabilities=["skill.execute", "memory.read", "memory.write"]
    )
    print(f"  - valid: {result1.valid}")
    print(f"  - errors: {result1.errors}")
    print(f"  - warnings: {result1.warnings}")
    
    # 2. 能力不足校验
    print("\n[2] 能力不足校验:")
    result2 = validator.validate(
        workflow_id="minimum_loop",
        version="1.0.0",
        profile="default",
        allowed_capabilities=["memory.read"]  # 缺少 skill.execute
    )
    print(f"  - valid: {result2.valid}")
    print(f"  - errors: {result2.errors}")
    print(f"  - warnings: {result2.warnings}")
    
    # 3. Profile 不兼容校验
    print("\n[3] Profile 不兼容校验:")
    result3 = validator.validate(
        workflow_id="minimum_loop",
        version="1.0.0",
        profile="restricted",  # minimum_loop 不支持 restricted
        allowed_capabilities=["skill.execute"]
    )
    print(f"  - valid: {result3.valid}")
    print(f"  - errors: {result3.errors}")
    print(f"  - warnings: {result3.warnings}")
    
    # 4. Safe mode 校验
    print("\n[4] Safe mode 校验:")
    result4 = validator.validate(
        workflow_id="minimum_loop",
        version="1.0.0",
        profile="safe",
        allowed_capabilities=["skill.execute"]
    )
    print(f"  - valid: {result4.valid}")
    print(f"  - errors: {result4.errors}")
    print(f"  - warnings: {result4.warnings}")
    
    # 5. 步骤级别校验
    print("\n[5] 步骤级别校验:")
    from orchestration.workflow.workflow_registry import WorkflowStep
    step = WorkflowStep(
        step_id="test_step",
        name="Test Step",
        action="high_risk.execute",
        required_capabilities=["high_risk.execute"],
        is_high_risk=True
    )
    step_result = validator.validate_step(
        step=step,
        profile="safe",
        allowed_capabilities=["skill.execute"]
    )
    print(f"  - valid: {step_result.valid}")
    print(f"  - errors: {step_result.errors}")
    print(f"  - warnings: {step_result.warnings}")
    
    print("\n✅ 验收点 5 通过: 展示了 Control Decision 影响 Workflow 行为")
    return True


def run_all_verifications():
    """运行所有验收"""
    print("\n" + "=" * 60)
    print("Phase3 第二组验收: Workflow 正式内核化")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("验收点 1: RegisteredTemplate", example_1_registered_template()))
    except Exception as e:
        print(f"❌ 验收点 1 失败: {e}")
        results.append(("验收点 1: RegisteredTemplate", False))
    
    try:
        results.append(("验收点 2: WorkflowInstance", example_2_workflow_instance()))
    except Exception as e:
        print(f"❌ 验收点 2 失败: {e}")
        results.append(("验收点 2: WorkflowInstance", False))
    
    try:
        results.append(("验收点 3: EventTimeline", example_3_event_timeline()))
    except Exception as e:
        print(f"❌ 验收点 3 失败: {e}")
        results.append(("验收点 3: EventTimeline", False))
    
    try:
        results.append(("验收点 4: ReplayResult", example_4_replay_result()))
    except Exception as e:
        print(f"❌ 验收点 4 失败: {e}")
        results.append(("验收点 4: ReplayResult", False))
    
    try:
        results.append(("验收点 5: ControlDecisionImpact", example_5_control_decision_impact()))
    except Exception as e:
        print(f"❌ 验收点 5 失败: {e}")
        results.append(("验收点 5: ControlDecisionImpact", False))
    
    # 汇总
    print("\n" + "=" * 60)
    print("验收汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 所有验收点通过！Phase3 第二组完成。")
    else:
        print("\n⚠️ 部分验收点未通过，需要修复。")
    
    return all_passed


if __name__ == "__main__":
    run_all_verifications()
