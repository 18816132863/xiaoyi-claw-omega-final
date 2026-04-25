"""场景演示：日常提醒自动化"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from autonomous_planner import GoalParser, TaskDecomposer
from device_capability_bus import CapabilityExecutor, DeviceCapabilityRequest
from closed_loop_verifier import AuditWriter, FinalSummarizer
from learning_loop import ExecutionMemory, ExecutionRecord


def demo_daily_reminder():
    """演示：明天提醒拿快递并写备忘录"""
    
    print("=" * 60)
    print("场景演示：日常提醒自动化")
    print("=" * 60)
    
    # 1. 解析目标
    goal = "明天提醒我拿快递，并写个备忘录"
    print(f"\n用户目标: {goal}")
    
    parser = GoalParser()
    parsed = parser.parse(goal)
    
    print(f"\n解析结果:")
    print(f"  意图: {parsed.intent}")
    print(f"  实体: {parsed.entities}")
    print(f"  约束: {parsed.constraints}")
    print(f"  优先级: {parsed.priority}")
    
    # 2. 分解任务
    decomposer = TaskDecomposer()
    plan = decomposer.decompose(parsed)
    
    print(f"\n执行计划:")
    print(plan.get_preview())
    
    # 3. 检查高风险步骤
    high_risk = plan.get_high_risk_steps()
    if high_risk:
        print(f"\n⚠️ 高风险步骤:")
        for step in high_risk:
            print(f"  - 步骤 {step.step_id}: {step.capability} ({step.risk_level})")
    
    # 4. 执行（dry_run）
    print(f"\n执行预演:")
    executor = CapabilityExecutor()
    
    for step in plan.steps:
        request = DeviceCapabilityRequest(
            capability=step.capability,
            params=step.params,
            dry_run=True,
        )
        result = executor.execute(request)
        print(f"  步骤 {step.step_id}: {result.user_message}")
    
    # 5. 记录执行
    memory = ExecutionMemory()
    record = ExecutionRecord(
        goal=goal,
        plan=[s.__dict__ for s in plan.steps],
        capabilities_used=[s.capability for s in plan.steps],
        skills_used=[],
        successful_steps=list(range(1, len(plan.steps) + 1)),
        failed_steps=[],
        final_result="success",
    )
    memory.record(record)
    
    print(f"\n✅ 执行记录已保存")
    print(f"   下次相似任务将复用此成功路径")
    
    return {
        "goal": goal,
        "plan": plan.to_dict(),
        "success": True,
    }


if __name__ == "__main__":
    result = demo_daily_reminder()
    print(f"\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)
