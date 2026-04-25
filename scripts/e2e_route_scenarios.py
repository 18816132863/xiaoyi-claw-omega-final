#!/usr/bin/env python3
"""
E2E Route Scenario Tests

端到端场景测试
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from autonomous_planner.route_selector import RouteSelector, get_route_selector
from skill_orchestrator.route_executor import RouteExecutor, get_route_executor
from orchestration.route_fallback import RouteFallbackExecutor, get_route_fallback_executor


# E2E 场景定义
E2E_SCENARIOS = [
    {
        "id": "scenario_01",
        "name": "查询备忘录",
        "user_goal": "查询备忘录",
        "expected_route": "route.query_note",
        "expected_risk": "L0",
        "expected_policy": "auto_execute",
        "expected_confirmation": False
    },
    {
        "id": "scenario_02",
        "name": "新建/更新/删除备忘录 dry-run",
        "user_goal": "删除备忘录",
        "expected_route": "route.delete_note",
        "expected_risk": "L3",
        "expected_policy": "confirm_once",
        "expected_confirmation": True
    },
    {
        "id": "scenario_03",
        "name": "发送消息 dry-run + fallback",
        "user_goal": "发送消息",
        "expected_route": "route.send_message",
        "expected_risk": "L3",
        "expected_policy": "confirm_once",
        "expected_confirmation": True,
        "test_fallback": True
    },
    {
        "id": "scenario_04",
        "name": "设置闹钟",
        "user_goal": "设置闹钟",
        "expected_route": "route.create_alarm",
        "expected_risk": "L2",
        "expected_policy": "rate_limited",
        "expected_confirmation": True
    },
    {
        "id": "scenario_05",
        "name": "删除闹钟 confirm_once",
        "user_goal": "删除闹钟",
        "expected_route": "route.delete_alarm",
        "expected_risk": "L3",
        "expected_policy": "confirm_once",
        "expected_confirmation": True
    },
    {
        "id": "scenario_06",
        "name": "拨打电话 confirm_once",
        "user_goal": "拨打电话",
        "expected_route": "route.make_call",
        "expected_risk": "L3",
        "expected_policy": "confirm_once",
        "expected_confirmation": True
    },
    {
        "id": "scenario_07",
        "name": "小艺 GUI 操作 L4 strong_confirm preview",
        "user_goal": "手机操作",
        "expected_route": "route.xiaoyi_gui_agent",
        "expected_risk": "L4",
        "expected_policy": "strong_confirm",
        "expected_confirmation": True,
        "expect_cancelled": True  # L4 应该被取消
    },
    {
        "id": "scenario_08",
        "name": "bootstrap L4 strong_confirm",
        "user_goal": "引导",
        "expected_route": "route.bootstrap",
        "expected_risk": "L4",
        "expected_policy": "strong_confirm",
        "expected_confirmation": True,
        "expect_cancelled": True
    }
]


class E2EScenarioRunner:
    """E2E 场景运行器"""
    
    def __init__(
        self,
        registry_path: str = "infrastructure/route_registry.json",
        dry_run: bool = True,
        fake_device: bool = True
    ):
        self.registry_path = Path(registry_path)
        self.dry_run = dry_run
        self.fake_device = fake_device
        
        self.selector = get_route_selector(str(self.registry_path))
        self.executor = get_route_executor(str(self.registry_path), dry_run)
        self.fallback_executor = get_route_fallback_executor(str(self.registry_path))
        
        self.results = []
    
    def run_scenario(self, scenario: dict) -> dict:
        """运行单个场景"""
        scenario_id = scenario["id"]
        user_goal = scenario["user_goal"]
        
        print(f"\n{'='*60}")
        print(f"Scenario: {scenario['name']}")
        print(f"Goal: {user_goal}")
        
        result = {
            "scenario_id": scenario_id,
            "scenario_name": scenario["name"],
            "user_goal": user_goal,
            "selected_route": None,
            "risk_level": None,
            "policy": None,
            "confirmation_required": None,
            "execution_status": None,
            "fallback_used": None,
            "audit_id": None,
            "final_summary": None,
            "passed": False
        }
        
        # Step 1: Planner 选择 route
        selection = self.selector.select_route(user_goal)
        
        if not selection:
            result["final_summary"] = "❌ No route selected"
            return result
        
        result["selected_route"] = selection.selected_route_id
        result["risk_level"] = selection.risk_level
        result["policy"] = selection.policy
        result["confirmation_required"] = selection.requires_confirmation
        
        print(f"Selected Route: {selection.selected_route_id}")
        print(f"Risk Level: {selection.risk_level}")
        print(f"Policy: {selection.policy}")
        
        # 验证选择是否正确
        if scenario.get("expected_route") and selection.selected_route_id != scenario["expected_route"]:
            result["final_summary"] = f"⚠️ Route mismatch: expected {scenario['expected_route']}, got {selection.selected_route_id}"
            return result
        
        # Step 2: Orchestrator 执行 route
        execution = self.executor.execute_route(
            selection.selected_route_id,
            {"goal": user_goal},
            dry_run=self.dry_run,
            user_message=f"[E2E] {scenario['name']}"
        )
        
        result["execution_status"] = execution.execution_status
        result["audit_id"] = execution.audit_id
        
        print(f"Execution Status: {execution.execution_status}")
        
        # L4 应该被取消
        if scenario.get("expect_cancelled"):
            if execution.execution_status == "cancelled":
                result["final_summary"] = "✅ L4 route correctly cancelled (requires strong_confirm)"
                result["passed"] = True
            else:
                result["final_summary"] = f"❌ L4 route should be cancelled, got {execution.execution_status}"
            return result
        
        # Step 3: 测试 fallback (如果需要)
        if scenario.get("test_fallback") and not execution.success:
            fallback = self.fallback_executor.execute_fallback(
                selection.selected_route_id,
                execution.error or "test fallback",
                {"goal": user_goal},
                dry_run=self.dry_run
            )
            result["fallback_used"] = fallback.fallback_route
            print(f"Fallback Used: {fallback.fallback_route}")
        
        # 最终结果
        if execution.success:
            result["final_summary"] = "✅ Scenario passed"
            result["passed"] = True
        else:
            result["final_summary"] = f"❌ Execution failed: {execution.error}"
        
        return result
    
    def run_all_scenarios(self, scenarios: List[dict] = None) -> dict:
        """运行所有场景"""
        scenarios = scenarios or E2E_SCENARIOS
        
        print("=" * 60)
        print("E2E Route Scenario Tests")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Dry-run: {self.dry_run}")
        print(f"Fake device: {self.fake_device}")
        print("=" * 60)
        
        for scenario in scenarios:
            result = self.run_scenario(scenario)
            self.results.append(result)
        
        # 统计
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "results": self.results
        }


def main():
    parser = argparse.ArgumentParser(description="E2E Route Scenario Tests")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry-run mode")
    parser.add_argument("--fake-device", action="store_true", default=True, help="Use fake device")
    parser.add_argument("--scenario", type=str, help="Run specific scenario by ID")
    
    args = parser.parse_args()
    
    registry_path = Path(__file__).parent.parent / "infrastructure" / "route_registry.json"
    
    runner = E2EScenarioRunner(
        registry_path=str(registry_path),
        dry_run=args.dry_run,
        fake_device=args.fake_device
    )
    
    scenarios = E2E_SCENARIOS
    if args.scenario:
        scenarios = [s for s in E2E_SCENARIOS if s["id"] == args.scenario]
    
    summary = runner.run_all_scenarios(scenarios)
    
    print("\n" + "=" * 60)
    print("📊 E2E Summary:")
    print(f"   Total: {summary['total']}")
    print(f"   Passed: {summary['passed']}")
    print(f"   Failed: {summary['failed']}")
    
    print("\n📋 Detailed Results:")
    for r in summary["results"]:
        status = "✅" if r["passed"] else "❌"
        print(f"   {status} {r['scenario_id']}: {r['scenario_name']}")
        print(f"      Route: {r['selected_route']}, Risk: {r['risk_level']}, Status: {r['execution_status']}")
    
    print("\n" + "=" * 60)
    if summary["failed"] == 0:
        print("✅ All E2E scenarios passed")
        return 0
    else:
        print(f"⚠️  {summary['failed']} scenarios failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
