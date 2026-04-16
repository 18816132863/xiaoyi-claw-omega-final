"""集成测试 - 最小闭环完整链路测试"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import unittest
from datetime import datetime
import json

# 导入所有核心模块
from core.events.event_bus import EventBus, EventType, get_event_bus
from core.state.task_state_contract import get_task_state_contract, TaskStatus
from core.state.profile_state_contract import get_profile_state_contract, ProfileType

from governance.control_plane.policy_engine import PolicyEngine, Policy, PolicyType, PolicyEffect
from governance.budget.budget_manager import BudgetManager, ResourceType, BudgetPeriod
from governance.risk.risk_manager import RiskManager, RiskLevel

from memory_context.builder.context_builder import ContextBuilder, ContextBundle
from memory_context.session.session_state import SessionStateStore
from memory_context.session.session_history import SessionHistory

from orchestration.planner.task_planner import TaskPlanner, TaskComplexity
from orchestration.workflow.workflow_engine import WorkflowEngine, run_workflow, WorkflowStatus
from orchestration.workflow.dag_builder import DAGBuilder

# 真实导入 skills 模块
from skills.registry.skill_registry import SkillRegistry, SkillManifest, SkillCategory, SkillStatus
from skills.runtime.skill_router import SkillRouter
from skills.lifecycle.lifecycle_manager import LifecycleManager, LifecycleState


class TestMinimumLoop(unittest.TestCase):
    """最小闭环集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.event_bus = get_event_bus()
        self.event_bus.clear_history()
        
        self.task_contract = get_task_state_contract()
        self.profile_contract = get_profile_state_contract()
        
        self.policy_engine = PolicyEngine()
        self.budget_manager = BudgetManager()
        self.risk_manager = RiskManager()
        
        self.registry = SkillRegistry()
        self.router = SkillRouter(registry=self.registry)
    
    def test_01_task_creation(self):
        """测试任务创建"""
        task = self.task_contract.create_task(
            intent="测试任务",
            profile="developer"
        )
        
        self.assertIsNotNone(task.task_id)
        self.assertEqual(task.status, TaskStatus.CREATED)
        self.assertEqual(task.profile, "developer")
    
    def test_02_policy_evaluation(self):
        """测试策略评估"""
        # 注册策略
        self.policy_engine.register(Policy(
            policy_id="test_policy",
            name="Test Policy",
            policy_type=PolicyType.PERMISSION,
            effect=PolicyEffect.ALLOW,
            conditions=[{"field": "profile", "operator": "eq", "value": "developer"}]
        ))
        
        # 评估
        effect, applied = self.policy_engine.evaluate(
            PolicyType.PERMISSION,
            {"profile": "developer"}
        )
        
        self.assertEqual(effect, PolicyEffect.ALLOW)
    
    def test_03_policy_evaluate_policy_facade(self):
        """测试 evaluate_policy façade"""
        result = self.policy_engine.evaluate_policy(
            task_meta={"intent": "测试", "risk_level": "low"},
            profile="developer",
            requested_capabilities=["read", "write"]
        )
        
        self.assertIn("allowed", result)
        self.assertIn("effect", result)
        self.assertIn("reason", result)
    
    def test_04_context_building(self):
        """测试上下文构建"""
        builder = ContextBuilder()
        bundle = builder.build_context(
            task_id="test_task",
            profile="developer",
            intent="测试意图",
            token_budget=4000
        )
        
        self.assertIsNotNone(bundle)
        self.assertEqual(bundle.task_id, "test_task")
        self.assertEqual(bundle.profile, "developer")
        # 上下文不应为空
        self.assertGreater(len(bundle.sources), 0)
        # Token 数量应大于 0
        self.assertGreater(bundle.token_count, 0)
    
    def test_05_workflow_execution(self):
        """测试工作流执行"""
        # 创建引擎并注册处理器
        engine = WorkflowEngine()
        
        # 注册测试处理器
        def test_handler(action, step_input):
            return {"executed": True, "action": action}
        
        engine.register_action_handler("test_action", test_handler)
        
        workflow_spec = {
            "workflow_id": "test_workflow",
            "steps": [
                {"step_id": "step1", "action": "test_action"}
            ]
        }
        
        result = engine.run_workflow(workflow_spec, profile="developer")
        
        self.assertEqual(result.status, WorkflowStatus.COMPLETED)
        self.assertIn("step1", result.step_results)
    
    def test_06_skill_registration_and_routing(self):
        """测试技能注册和路由"""
        # 注册技能
        manifest = SkillManifest(
            skill_id="test_skill",
            name="Test Skill",
            version="1.0.0",
            description="测试技能",
            category=SkillCategory.UTILITY,
            status=SkillStatus.STABLE,
            executor_type="skill_md"
        )
        self.registry.register(manifest)
        
        # 获取技能
        retrieved = self.registry.get("test_skill")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test Skill")
        
        # 路由技能
        result = self.router.route("test_skill", {"input": "test"})
        self.assertTrue(result.success)
    
    def test_07_skill_select_skill_facade(self):
        """测试 select_skill façade"""
        # 注册技能
        manifest = SkillManifest(
            skill_id="test_selector",
            name="Test Selector Skill",
            version="1.0.0",
            description="用于测试选择的技能",
            category=SkillCategory.UTILITY,
            status=SkillStatus.STABLE,
            executor_type="skill_md",
            tags=["test", "selector"]
        )
        self.registry.register(manifest)
        
        # 使用 select_skill
        result = self.router.select_skill(
            intent="测试选择",
            profile="developer"
        )
        
        self.assertIn("success", result)
        self.assertIn("skill_id", result)
        self.assertIn("confidence", result)
    
    def test_08_dag_building(self):
        """测试 DAG 构建"""
        builder = DAGBuilder()
        dag = builder.build_from_steps([
            {"step_id": "a", "depends_on": []},
            {"step_id": "b", "depends_on": ["a"]},
            {"step_id": "c", "depends_on": ["a"]},
            {"step_id": "d", "depends_on": ["b", "c"]}
        ])
        
        # 验证拓扑排序
        order = dag.topological_sort()
        self.assertEqual(len(order), 4)
        self.assertIn("a", order)
        
        # 验证并行组
        groups = dag.get_parallel_groups()
        self.assertEqual(len(groups), 3)
    
    def test_09_event_flow(self):
        """测试事件流"""
        # 发送事件
        self.event_bus.emit(EventType.TASK_CREATED, "test", {"task_id": "test_123"})
        self.event_bus.emit(EventType.TASK_COMPLETED, "test", {"task_id": "test_123"})
        
        # 获取历史
        events = self.event_bus.get_history()
        
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].event_type, EventType.TASK_CREATED)
        self.assertEqual(events[1].event_type, EventType.TASK_COMPLETED)
    
    def test_10_budget_management(self):
        """测试预算管理"""
        # 创建预算
        budget = self.budget_manager.create_budget(
            budget_id="test_budget",
            resource_type=ResourceType.TOKENS,
            period=BudgetPeriod.DAILY,
            limit=10000
        )
        
        self.assertEqual(budget.limit, 10000)
        
        # 使用预算
        allowed, remaining = self.budget_manager.use_budget("test_budget", 1000)
        self.assertTrue(allowed)
        self.assertEqual(remaining, 9000)
    
    def test_11_risk_assessment(self):
        """测试风险评估"""
        assessment = self.risk_manager.assess(
            "file_delete",
            {"path": "/test/file.txt"}
        )
        
        self.assertIsNotNone(assessment)
        self.assertIn(assessment.level, [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL])
    
    def test_12_full_loop(self):
        """测试完整闭环"""
        # 1. 创建任务
        task = self.task_contract.create_task(intent="完整闭环测试", profile="developer")
        
        # 2. 策略评估
        effect, _ = self.policy_engine.evaluate(
            PolicyType.PERMISSION,
            {"profile": "developer"}
        )
        self.assertEqual(effect, PolicyEffect.ALLOW)
        
        # 3. 构建上下文
        builder = ContextBuilder()
        bundle = builder.build_context(
            task_id=task.task_id,
            profile="developer",
            intent="完整闭环测试",
            token_budget=4000
        )
        self.assertIsNotNone(bundle)
        self.assertGreater(len(bundle.sources), 0)
        self.assertGreater(bundle.token_count, 0)
        
        # 4. 执行工作流
        engine = WorkflowEngine()
        engine.register_action_handler("test", lambda a, i: {"ok": True})
        
        result = engine.run_workflow({
            "workflow_id": f"loop_{task.task_id}",
            "steps": [{"step_id": "main", "action": "test"}]
        })
        self.assertEqual(result.status, WorkflowStatus.COMPLETED)
        
        # 5. 完成任务
        self.task_contract.complete_task(task.task_id, result={"status": "ok"})
        final_task = self.task_contract.get_task(task.task_id)
        self.assertEqual(final_task.status, TaskStatus.COMPLETED)
        
        # 6. 验证事件
        self.event_bus.emit(EventType.TASK_COMPLETED, "test", {"task_id": task.task_id})
        events = self.event_bus.get_history()
        self.assertGreater(len(events), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
