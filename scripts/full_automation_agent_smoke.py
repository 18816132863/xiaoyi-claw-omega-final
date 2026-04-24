"""全自动化智能体冒烟测试"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


def smoke_device_bus():
    """设备能力总线冒烟"""
    print("\n" + "=" * 60)
    print("1. Device Capability Bus")
    print("=" * 60)
    
    from device_capability_bus import CapabilityRegistry, CapabilityExecutor, DeviceCapabilityRequest
    
    registry = CapabilityRegistry()
    capabilities = registry.list_all()
    
    print(f"\n已注册能力: {len(capabilities)}")
    for cap in capabilities[:5]:
        print(f"  - {cap.capability_id}: {cap.name} ({cap.risk_level.value})")
    
    # 执行测试
    executor = CapabilityExecutor()
    request = DeviceCapabilityRequest(
        capability="storage.create_note",
        params={"content": "测试", "title": "测试"},
        dry_run=True,
    )
    result = executor.execute(request)
    
    print(f"\nDry run 测试:")
    print(f"  成功: {result.success}")
    print(f"  状态: {result.status}")
    print(f"  消息: {result.user_message}")
    
    return {"total_capabilities": len(capabilities), "dry_run_success": result.success}


def smoke_skill_registry():
    """技能资产注册表冒烟"""
    print("\n" + "=" * 60)
    print("2. Skill Asset Registry")
    print("=" * 60)
    
    from skill_asset_registry import SkillScanner, SkillRegistry
    
    scanner = SkillScanner()
    stats = scanner.get_stats()
    
    print(f"\n技能统计:")
    print(f"  总数: {stats['total']}")
    print(f"  分类: {stats['categories']}")
    print(f"  有副作用: {stats['side_effecting']}")
    
    # 注册表
    registry = SkillRegistry()
    skills = registry.list_all()
    
    print(f"\n注册表技能: {len(skills)}")
    
    return {"total_skills": stats['total'], "categories": stats['categories']}


def smoke_planner():
    """自主规划器冒烟"""
    print("\n" + "=" * 60)
    print("3. Autonomous Planner")
    print("=" * 60)
    
    from autonomous_planner import GoalParser, TaskDecomposer
    
    parser = GoalParser()
    parsed = parser.parse("明天提醒我开会")
    
    print(f"\n目标解析:")
    print(f"  意图: {parsed.intent}")
    print(f"  实体: {parsed.entities}")
    
    decomposer = TaskDecomposer()
    plan = decomposer.decompose(parsed)
    
    print(f"\n执行计划:")
    print(plan.get_preview())
    
    return {"intent": parsed.intent, "steps": len(plan.steps)}


def smoke_visual_agent():
    """视觉操作智能体冒烟"""
    print("\n" + "=" * 60)
    print("4. Visual Operation Agent")
    print("=" * 60)
    
    from visual_operation_agent import ScreenObserver, UIGrounding, ActionExecutor, VisualPlanner
    from visual_operation_agent.ui_grounding import UIElement
    
    # 屏幕观察
    observer = ScreenObserver()
    state = observer.observe()
    
    print(f"\n屏幕观察:")
    print(f"  时间: {state.timestamp}")
    print(f"  应用: {state.app_name}")
    
    # UI 定位
    grounding = UIGrounding()
    elements = [
        UIElement(element_id="btn1", element_type="button", text="确定", bounds={"x": 100, "y": 200, "width": 80, "height": 40}),
        UIElement(element_id="input1", element_type="input", text="请输入", bounds={"x": 100, "y": 300, "width": 200, "height": 40}),
    ]
    
    btn = grounding.locate_button("确定", elements)
    print(f"\nUI 定位:")
    print(f"  找到按钮: {btn.text if btn else 'None'}")
    
    # 动作执行
    executor = ActionExecutor()
    result = executor.tap(100, 200, dry_run=True)
    
    print(f"\n动作执行:")
    print(f"  动作: {result.action}")
    print(f"  成功: {result.success}")
    print(f"  消息: {result.message}")
    
    # 视觉规划
    planner = VisualPlanner()
    path = planner.get_visual_path("测试App", "搜索")
    
    print(f"\n视觉路径:")
    print(f"  应用: {path['app']}")
    print(f"  步骤: {len(path['steps'])}")
    
    return {"observe": True, "grounding": btn is not None, "action": result.success}


def smoke_safety_governor():
    """安全治理冒烟"""
    print("\n" + "=" * 60)
    print("5. Safety Governor")
    print("=" * 60)
    
    from safety_governor import PolicyEngine, GamePolicy
    
    engine = PolicyEngine()
    
    # L4 测试
    assessment_l4 = engine.assess("自动点击游戏内的抽卡按钮")
    print(f"\nL4 测试: 游戏抽卡")
    print(f"  等级: {assessment_l4.risk_level.value}")
    print(f"  策略: {assessment_l4.policy.value}")
    print(f"  需要确认: {assessment_l4.requires_confirmation}")
    
    # BLOCKED 测试
    assessment_blocked = engine.assess("联网竞技游戏自动代打", {"scenario": "competitive_cheating"})
    print(f"\nBLOCKED 测试: 联网竞技代打")
    print(f"  等级: {assessment_blocked.risk_level.value}")
    print(f"  策略: {assessment_blocked.policy.value}")
    print(f"  被禁止: {assessment_blocked.blocked}")
    
    # 游戏策略
    game_policy = GamePolicy()
    game_result = game_policy.assess_game_action("视觉辅助")
    
    print(f"\n游戏策略: 视觉辅助")
    print(f"  允许: {game_result.allowed}")
    print(f"  风险等级: {game_result.risk_level.value}")
    
    return {
        "l4_level": assessment_l4.risk_level.value,
        "l4_policy": assessment_l4.policy.value,
        "blocked": assessment_blocked.blocked,
    }


def smoke_learning_loop():
    """学习闭环冒烟"""
    print("\n" + "=" * 60)
    print("6. Learning Loop")
    print("=" * 60)
    
    from learning_loop import ExecutionMemory, ExecutionRecord, PlanOptimizer
    
    # 使用固定路径
    memory = ExecutionMemory(storage_path="data/smoke_learning_memory.jsonl")
    
    # 先写入一条学习记录
    print(f"\n步骤 1: 写入学习记录...")
    first_record = ExecutionRecord(
        goal="明天提醒我开会",
        plan=[{"step_id": 1, "capability": "schedule.create_calendar_event"}],
        capabilities_used=["schedule.create_calendar_event"],
        successful_steps=[1],
        failed_steps=[],
        final_result="success",
        user_satisfied=True,
    )
    memory.record(first_record)
    print(f"  记录ID: {first_record.execution_id}")
    
    # 再执行相似任务
    print(f"\n步骤 2: 执行相似任务...")
    similar = memory.find_similar("后天提醒我交报告")
    
    print(f"  找到相似记录: {len(similar)}")
    if similar:
        print(f"  匹配记录ID: {similar[0].execution_id}")
        print(f"  原始目标: {similar[0].goal}")
        print(f"  复用成功路径: {similar[0].final_result == 'success'}")
    
    # 优化计划
    optimizer = PlanOptimizer(memory=memory)
    optimization = optimizer.optimize("后天提醒我交报告", [{"step_id": 1}])
    
    print(f"\n步骤 3: 计划优化...")
    print(f"  置信度: {optimization['confidence']:.2f}")
    print(f"  优化措施: {len(optimization['optimizations'])} 项")
    
    # 获取优化说明
    explanation = optimizer.explain("后天提醒我交报告")
    print(f"\n步骤 4: 优化说明...")
    print(f"  {explanation[:100]}...")
    
    stats = memory.get_stats()
    
    print(f"\n执行记忆统计:")
    print(f"  总记录: {stats['total']}")
    print(f"  成功: {stats.get('success', 0)}")
    print(f"  成功率: {stats.get('success_rate', 0):.2f}")
    
    return {
        "memory_total": stats['total'],
        "has_optimizer": True,
        "found_similar": len(similar) > 0,
        "matched_previous_record_id": similar[0].execution_id if similar else None,
        "reused_success_path": similar[0].final_result == "success" if similar else False,
    }


def smoke_closed_loop():
    """闭环验证器冒烟"""
    print("\n" + "=" * 60)
    print("7. Closed Loop Verifier")
    print("=" * 60)
    
    from closed_loop_verifier import ResultChecker, AuditWriter, RecoveryManager, FinalSummarizer
    
    checker = ResultChecker()
    result = checker.verify_platform_result({"success": True, "status": "completed"})
    
    print(f"\n结果验证:")
    print(f"  验证通过: {result.verified}")
    print(f"  状态: {result.status}")
    
    audit = AuditWriter()
    audit.write({"event": "smoke_test", "test": "closed_loop"})
    
    print(f"\n审计写入: ✅")
    
    recovery = RecoveryManager()
    decision = recovery.decide("network timeout", {})
    
    print(f"\n恢复决策:")
    print(f"  策略: {decision.strategy.value}")
    print(f"  原因: {decision.reason}")
    
    summarizer = FinalSummarizer()
    summary = summarizer.summarize(
        "测试目标",
        [{"step_id": 1, "status": "completed"}],
        "2026-04-24T20:00:00",
        "2026-04-24T20:00:05",
    )
    
    print(f"\n执行总结:")
    print(f"  成功: {summary.success}")
    print(f"  消息: {summary.message}")
    
    return {"verified": result.verified, "recovery_strategy": decision.strategy.value}


def main():
    """主函数"""
    print("=" * 60)
    print("全自动化智能体冒烟测试")
    print("=" * 60)
    
    results = {}
    
    try:
        results["device_bus"] = smoke_device_bus()
    except Exception as e:
        results["device_bus"] = {"error": str(e)}
    
    try:
        results["skill_registry"] = smoke_skill_registry()
    except Exception as e:
        results["skill_registry"] = {"error": str(e)}
    
    try:
        results["planner"] = smoke_planner()
    except Exception as e:
        results["planner"] = {"error": str(e)}
    
    try:
        results["visual_agent"] = smoke_visual_agent()
    except Exception as e:
        results["visual_agent"] = {"error": str(e)}
    
    try:
        results["safety_governor"] = smoke_safety_governor()
    except Exception as e:
        results["safety_governor"] = {"error": str(e)}
    
    try:
        results["learning_loop"] = smoke_learning_loop()
    except Exception as e:
        results["learning_loop"] = {"error": str(e)}
    
    try:
        results["closed_loop"] = smoke_closed_loop()
    except Exception as e:
        results["closed_loop"] = {"error": str(e)}
    
    # 总结
    print("\n" + "=" * 60)
    print("冒烟测试总结")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if "error" not in v)
    total = len(results)
    
    print(f"\n通过: {passed}/{total}")
    
    for name, result in results.items():
        status = "✅" if "error" not in result else "❌"
        print(f"  {status} {name}")
    
    return results


if __name__ == "__main__":
    results = main()
