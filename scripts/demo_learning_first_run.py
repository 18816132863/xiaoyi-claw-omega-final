"""学习闭环演示：第一次执行"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from learning_loop import ExecutionMemory, ExecutionRecord, PatternExtractor
from autonomous_planner import GoalParser, TaskDecomposer
from datetime import datetime


def demo_first_run():
    """第一次执行：记录经验"""
    
    print("=" * 60)
    print("学习闭环演示：第一次执行")
    print("=" * 60)
    
    goal = "明天提醒我开会"
    print(f"\n用户目标: {goal}")
    
    # 解析目标
    parser = GoalParser()
    parsed = parser.parse(goal)
    
    print(f"\n解析结果:")
    print(f"  意图: {parsed.intent}")
    print(f"  实体: {parsed.entities}")
    
    # 分解任务
    decomposer = TaskDecomposer()
    plan = decomposer.decompose(parsed)
    
    print(f"\n执行计划:")
    for step in plan.steps:
        print(f"  {step.step_id}. {step.capability} ({step.risk_level})")
    
    # 模拟执行
    print(f"\n执行中...")
    successful_steps = [1, 2]
    failed_steps = []
    step_timings = {1: 1200, 2: 800}
    
    # 记录经验（使用固定路径）
    memory = ExecutionMemory(storage_path="data/learning_demo_memory.jsonl")
    record = ExecutionRecord(
        goal=goal,
        plan=[{"step_id": s.step_id, "capability": s.capability, "params": s.params} for s in plan.steps],
        capabilities_used=[s.capability for s in plan.steps],
        skills_used=[],
        successful_steps=successful_steps,
        failed_steps=failed_steps,
        step_timings=step_timings,
        confirmations_needed=[],
        user_satisfied=True,
        final_result="success",
        visual_paths=[],
        fallback_occurred=False,
        result_uncertain=False,
        optimization_hints="下次可以直接创建日程，不需要额外确认",
    )
    
    memory.record(record)
    
    print(f"\n✅ 第一次执行完成")
    print(f"\n经验记录:")
    print(f"  记录ID: {record.execution_id}")
    print(f"  目标: {record.goal}")
    print(f"  计划: {len(record.plan)} 步")
    print(f"  使用能力: {record.capabilities_used}")
    print(f"  成功步骤: {record.successful_steps}")
    print(f"  失败步骤: {record.failed_steps}")
    print(f"  耗时: {sum(record.step_timings.values())}ms")
    print(f"  用户满意: {record.user_satisfied}")
    print(f"  最终结果: {record.final_result}")
    print(f"  优化建议: {record.optimization_hints}")
    
    # 提取模式
    pattern = PatternExtractor.extract_goal_pattern(goal)
    print(f"\n目标模式: {pattern}")
    
    return {
        "execution_id": record.execution_id,
        "goal": goal,
        "plan": record.plan,
        "used_capabilities": record.capabilities_used,
        "used_skills": record.skills_used,
        "successful_steps": record.successful_steps,
        "failed_steps": record.failed_steps,
        "visual_path": record.visual_paths,
        "confirmation_count": len(record.confirmations_needed),
        "final_status": record.final_result,
        "learning_record_id": record.execution_id,
    }


if __name__ == "__main__":
    result = demo_first_run()
    print(f"\n" + "=" * 60)
    print("第一次执行完成，经验已记录")
    print(f"记录ID: {result['learning_record_id']}")
    print("=" * 60)
