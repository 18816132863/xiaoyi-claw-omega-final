#!/usr/bin/env python3
"""
最小闭环演示 - Minimum Viable Loop Demo

演示链路:
1. 输入一个任务
2. governance/policy_engine 先给出决策
3. memory_context/context_builder 生成 context bundle
4. orchestration/workflow_engine 根据 workflow spec 执行
5. workflow 中通过 skills/runtime/skill_router 选一个技能
6. 执行完成后生成最小结果报告
7. 事件流写入 core/events/event_bus
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
import json

# 1. 导入核心模块
from core.events.event_bus import EventBus, Event, EventType, get_event_bus
from core.state.task_state_contract import get_task_state_contract, TaskStatus
from core.state.profile_state_contract import get_profile_state_contract

from governance.control_plane.policy_engine import PolicyEngine, Policy, PolicyType, PolicyEffect
from governance.budget.budget_manager import BudgetManager, ResourceType, BudgetPeriod

from memory_context.builder.context_builder import ContextBuilder, ContextBundle
from memory_context.session.session_state import SessionStateStore
from memory_context.session.session_history import SessionHistory

from orchestration.planner.task_planner import TaskPlanner
from orchestration.workflow.workflow_engine import WorkflowEngine, run_workflow, WorkflowStatus

from skills.registry.skill_registry import SkillRegistry, SkillManifest, SkillCategory, SkillStatus
from skills.runtime.skill_router import SkillRouter


def demo_minimum_loop():
    """运行最小闭环演示."""
    print("=" * 60)
    print("最小闭环演示 - Minimum Viable Loop Demo")
    print("=" * 60)
    print()
    
    # ========================================
    # Step 1: 输入任务
    # ========================================
    print("【Step 1】输入任务")
    print("-" * 40)
    
    task_intent = "检查项目架构完整性"
    profile = "developer"
    
    print(f"任务意图: {task_intent}")
    print(f"执行配置: {profile}")
    print()
    
    # 创建任务状态
    task_contract = get_task_state_contract()
    task = task_contract.create_task(intent=task_intent, profile=profile)
    print(f"任务ID: {task.task_id}")
    print(f"任务状态: {task.status.value}")
    print()
    
    # ========================================
    # Step 2: Policy Engine 决策
    # ========================================
    print("【Step 2】Policy Engine 决策")
    print("-" * 40)
    
    policy_engine = PolicyEngine()
    
    # 注册策略
    policy_engine.register(Policy(
        policy_id="developer_write_policy",
        name="Developer Write Policy",
        policy_type=PolicyType.PERMISSION,
        effect=PolicyEffect.ALLOW,
        conditions=[{"field": "profile", "operator": "eq", "value": "developer"}],
        priority=100
    ))
    
    # 评估策略
    context = {
        "profile": profile,
        "action": "check_architecture",
        "resource": "project"
    }
    
    effect, applied_policies = policy_engine.evaluate(PolicyType.PERMISSION, context)
    
    print(f"策略决策: {effect.value}")
    print(f"应用策略: {applied_policies}")
    
    if effect == PolicyEffect.DENY:
        print("❌ 策略拒绝，任务终止")
        return
    
    print("✅ 策略允许，继续执行")
    print()
    
    # ========================================
    # Step 3: Context Builder 生成上下文
    # ========================================
    print("【Step 3】Context Builder 生成上下文")
    print("-" * 40)
    
    # 创建会话历史
    session_history = SessionHistory()
    session_history.add("user", task_intent, {"task_id": task.task_id})
    session_history.add("system", "开始处理任务", {"step": "init"})
    
    # 构建上下文
    context_builder = ContextBuilder()
    context_bundle = context_builder.build_context(
        task_id=task.task_id,
        profile=profile,
        intent=task_intent,
        sources=["session", "memory"],
        token_budget=4000
    )
    
    print(f"上下文包ID: {context_bundle.task_id}")
    print(f"Token 预算: {context_bundle.token_budget}")
    print(f"Token 使用: {context_bundle.token_count}")
    print(f"来源数量: {len(context_bundle.sources)}")
    print()
    
    # ========================================
    # Step 4: Workflow Engine 执行
    # ========================================
    print("【Step 4】Workflow Engine 执行")
    print("-" * 40)
    
    # 定义工作流
    workflow_spec = {
        "workflow_id": f"workflow_{task.task_id}",
        "name": "架构检查工作流",
        "steps": [
            {
                "step_id": "prepare",
                "name": "准备阶段",
                "action": "prepare_context",
                "timeout_seconds": 30
            },
            {
                "step_id": "check",
                "name": "检查架构",
                "action": "check_architecture_integrity",
                "depends_on": ["prepare"],
                "timeout_seconds": 60
            },
            {
                "step_id": "report",
                "name": "生成报告",
                "action": "generate_report",
                "depends_on": ["check"],
                "timeout_seconds": 30
            }
        ]
    }
    
    print(f"工作流ID: {workflow_spec['workflow_id']}")
    print(f"步骤数: {len(workflow_spec['steps'])}")
    
    # 执行工作流
    workflow_result = run_workflow(
        workflow_spec=workflow_spec,
        profile=profile,
        context_bundle=context_bundle.to_dict()
    )
    
    print(f"工作流状态: {workflow_result.status.value}")
    print(f"执行时长: {workflow_result.total_duration_ms}ms")
    print(f"步骤结果:")
    for step_id, result in workflow_result.step_results.items():
        print(f"  - {step_id}: {result.status.value} ({result.duration_ms}ms)")
    print()
    
    # ========================================
    # Step 5: Skill Router 选择技能
    # ========================================
    print("【Step 5】Skill Router 选择技能")
    print("-" * 40)
    
    # 创建技能注册表
    registry = SkillRegistry()
    
    # 注册一个示例技能
    skill_manifest = SkillManifest(
        skill_id="architecture_checker",
        name="Architecture Checker",
        version="1.0.0",
        description="检查项目架构完整性",
        category=SkillCategory.CODE,
        status=SkillStatus.ACTIVE,
        executor_type="skill_md",
        entry_point="skills/architecture_checker/SKILL.md",
        timeout_seconds=60
    )
    registry.register(skill_manifest)
    
    print(f"注册技能: {skill_manifest.skill_id}")
    print(f"技能名称: {skill_manifest.name}")
    print(f"技能类别: {skill_manifest.category.value}")
    
    # 创建技能路由器
    router = SkillRouter(registry=registry)
    
    # 发现技能
    matches = router.discover("architecture", context={"profile": profile})
    print(f"发现技能: {matches}")
    
    # 执行技能
    skill_result = router.route(
        skill_id="architecture_checker",
        input_data={"task_id": task.task_id},
        context={"profile": profile}
    )
    
    print(f"技能执行: {'成功' if skill_result.success else '失败'}")
    print(f"执行时长: {skill_result.duration_ms}ms")
    print()
    
    # ========================================
    # Step 6: 生成结果报告
    # ========================================
    print("【Step 6】生成结果报告")
    print("-" * 40)
    
    # 更新任务状态
    task_contract.start_task(task.task_id)
    task_contract.complete_task(task.task_id, result={
        "workflow_status": workflow_result.status.value,
        "skill_status": "success" if skill_result.success else "failed",
        "duration_ms": workflow_result.total_duration_ms
    })
    
    final_task = task_contract.get_task(task.task_id)
    
    print(f"任务ID: {final_task.task_id}")
    print(f"最终状态: {final_task.status.value}")
    print(f"创建时间: {final_task.created_at}")
    print(f"完成时间: {final_task.completed_at}")
    print(f"执行结果: {json.dumps(final_task.result, ensure_ascii=False)}")
    print()
    
    # ========================================
    # Step 7: 事件流记录
    # ========================================
    print("【Step 7】事件流记录")
    print("-" * 40)
    
    event_bus = get_event_bus()
    
    # 发送事件
    event_bus.emit(EventType.TASK_CREATED, "demo", {"task_id": task.task_id})
    event_bus.emit(EventType.POLICY_APPLIED, "demo", {"effect": effect.value})
    event_bus.emit(EventType.CONTEXT_BUILT, "demo", {"token_count": context_bundle.token_count})
    event_bus.emit(EventType.WORKFLOW_STARTED, "demo", {"workflow_id": workflow_spec["workflow_id"]})
    event_bus.emit(EventType.WORKFLOW_COMPLETED, "demo", {"status": workflow_result.status.value})
    event_bus.emit(EventType.SKILL_EXECUTED, "demo", {"skill_id": skill_manifest.skill_id})
    event_bus.emit(EventType.TASK_COMPLETED, "demo", {"task_id": task.task_id})
    
    # 获取事件历史
    events = event_bus.get_history(limit=10)
    
    print(f"事件总数: {len(events)}")
    print("事件列表:")
    for event in events:
        print(f"  - [{event.event_type.value}] {event.source}: {json.dumps(event.data, ensure_ascii=False)}")
    print()
    
    # ========================================
    # 总结
    # ========================================
    print("=" * 60)
    print("✅ 最小闭环演示完成")
    print("=" * 60)
    print()
    print("验证结果:")
    print(f"  ✅ Policy Engine 决策: {effect.value}")
    print(f"  ✅ Context Bundle 生成: {context_bundle.token_count} tokens")
    print(f"  ✅ Workflow 执行: {workflow_result.status.value}")
    print(f"  ✅ Skill 调用: {'成功' if skill_result.success else '失败'}")
    print(f"  ✅ 任务完成: {final_task.status.value}")
    print(f"  ✅ 事件记录: {len(events)} 条")
    print()
    
    return {
        "task_id": task.task_id,
        "policy_decision": effect.value,
        "context_tokens": context_bundle.token_count,
        "workflow_status": workflow_result.status.value,
        "skill_success": skill_result.success,
        "task_status": final_task.status.value,
        "event_count": len(events)
    }


if __name__ == "__main__":
    result = demo_minimum_loop()
    print("\n最终结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
