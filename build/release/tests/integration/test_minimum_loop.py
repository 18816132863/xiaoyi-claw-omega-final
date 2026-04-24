"""
最小循环集成测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest


class TestMinimumLoop:
    """最小循环测试"""
    
    def test_01_imports(self):
        """测试导入"""
        import core
        import memory_context
        import orchestration
        import execution
        import governance
        import infrastructure
        import application
        import domain
        assert True
    
    def test_02_skill_registry(self):
        """测试技能注册表"""
        from skills.registry import get_skill_registry
        registry = get_skill_registry()
        assert registry is not None
    
    def test_03_workflow_instance_store(self):
        """测试工作流实例存储"""
        from orchestration.state import get_workflow_instance_store
        store = get_workflow_instance_store()
        assert store is not None
    
    def test_04_workflow_event_store(self):
        """测试工作流事件存储"""
        from orchestration.state import get_workflow_event_store
        store = get_workflow_event_store()
        assert store is not None
    
    def test_05_workflow_execution(self):
        """测试工作流执行"""
        from orchestration.state import get_workflow_instance_store
        store = get_workflow_instance_store()
        
        # 创建实例
        instance = store.create(
            instance_id="test_instance",
            template_id="test_template"
        )
        assert instance is not None
    
    def test_06_skill_registration_and_routing(self):
        """测试技能注册和路由"""
        from skills.registry import get_skill_registry
        from skills.runtime import get_skill_router
        
        registry = get_skill_registry()
        router = get_skill_router()
        
        assert registry is not None
        assert router is not None
    
    def test_07_skill_select_skill_facade(self):
        """测试技能选择"""
        from skills.runtime import get_skill_router
        router = get_skill_router()
        
        # 选择技能
        skill_id = router.select_skill("test_task")
        # 可能返回 None，但不应该报错
        assert True
    
    def test_08_checkpoint_store(self):
        """测试检查点存储"""
        from orchestration.state import get_checkpoint_store
        store = get_checkpoint_store()
        assert store is not None
    
    def test_09_recovery_store(self):
        """测试恢复存储"""
        from orchestration.state import get_recovery_store
        store = get_recovery_store()
        assert store is not None
    
    def test_10_lifecycle_manager(self):
        """测试生命周期管理器"""
        from skills.lifecycle import get_lifecycle_manager
        manager = get_lifecycle_manager()
        assert manager is not None
    
    def test_11_health_monitor(self):
        """测试健康监控器"""
        from skills.runtime import SkillHealthMonitor
        monitor = SkillHealthMonitor()
        assert monitor is not None
    
    def test_12_full_loop(self):
        """测试完整循环"""
        from orchestration.state import (
            get_workflow_instance_store,
            get_workflow_event_store,
            get_checkpoint_store,
            get_recovery_store
        )
        
        # 创建工作流实例
        instance_store = get_workflow_instance_store()
        instance = instance_store.create(
            instance_id="full_loop_test",
            template_id="test_template"
        )
        assert instance is not None
        
        # 保存检查点
        checkpoint_store = get_checkpoint_store()
        checkpoint = checkpoint_store.save(
            instance_id="full_loop_test",
            step_id="step_1",
            state_data={"test": "data"}
        )
        assert checkpoint is not None
