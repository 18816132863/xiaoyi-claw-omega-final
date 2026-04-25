"""学习闭环演示：第二次执行（复用成功路径）"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from learning_loop import ExecutionMemory, PlanOptimizer, PatternExtractor
from autonomous_planner import GoalParser, TaskDecomposer


def demo_second_run():
    """第二次执行：复用成功路径"""
    
    print("=" * 60)
    print("学习闭环演示：第二次执行（复用成功路径）")
    print("=" * 60)
    
    # 相似目标
    goal = "后天提醒我交报告"
    print(f"\n用户目标: {goal}")
    
    # 加载记忆（使用相同路径）
    memory = ExecutionMemory(storage_path="data/learning_demo_memory.jsonl")
    optimizer = PlanOptimizer(memory=memory)
    
    # 查找相似历史
    similar = memory.find_similar(goal, limit=3)
    print(f"\n找到 {len(similar)} 条相似历史记录")
    
    if similar:
        for i, record in enumerate(similar):
            print(f"  {i+1}. {record.goal} (结果: {record.final_result})")
    
    # 解析目标
    parser = GoalParser()
    parsed = parser.parse(goal)
    
    # 初始计划
    decomposer = TaskDecomposer()
    initial_plan = decomposer.decompose(parsed)
    
    print(f"\n初始计划:")
    for step in initial_plan.steps:
        print(f"  {step.step_id}. {step.capability}")
    
    # 优化计划
    optimization = optimizer.optimize(goal, [s.__dict__ for s in initial_plan.steps])
    
    print(f"\n优化结果:")
    print(f"  目标模式: {optimization['goal_pattern']}")
    print(f"  置信度: {optimization['confidence']:.2f}")
    
    if optimization['optimizations']:
        print(f"\n优化措施:")
        for opt in optimization['optimizations']:
            print(f"  - {opt['type']}: {opt}")
    
    # 获取偏好提示
    pref_hints = memory.get_preference_hints(goal)
    if pref_hints:
        print(f"\n偏好提示:")
        print(f"  首选能力: {pref_hints.get('preferred_capabilities', [])}")
        print(f"  首选技能: {pref_hints.get('preferred_skills', [])}")
    
    # 获取失败步骤
    failed_steps = memory.get_failed_steps(goal)
    if failed_steps:
        print(f"\n避开失败步骤: {failed_steps}")
    
    # 解释优化
    explanation = optimizer.explain(goal)
    print(f"\n优化说明:")
    print(f"  {explanation}")
    
    # 匹配的记录ID
    matched_id = similar[0].execution_id if similar else None
    
    return {
        "matched_previous_record_id": matched_id,
        "reused_success_path": len(similar) > 0 and similar[0].final_result == "success",
        "avoided_failed_steps": failed_steps,
        "optimized_plan": optimization['optimized_plan'],
        "reduced_questions": optimization['confidence'] > 0.7,
        "reason": explanation,
    }


if __name__ == "__main__":
    result = demo_second_run()
    print(f"\n" + "=" * 60)
    print("第二次执行完成，已复用成功路径")
    print(f"匹配记录: {result['matched_previous_record_id']}")
    print(f"复用成功路径: {result['reused_success_path']}")
    print(f"减少追问: {result['reduced_questions']}")
    print("=" * 60)
