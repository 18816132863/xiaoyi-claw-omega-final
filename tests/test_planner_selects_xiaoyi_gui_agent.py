"""
Test: Planner Selects xiaoyi_gui_agent

验证 Planner 能正确选择 route.xiaoyi_gui_agent
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from autonomous_planner.route_selector import RouteSelector, get_route_selector


class TestPlannerSelectsXiaoyiGuiAgent:
    """Planner 选择 xiaoyi_gui_agent 测试"""
    
    @pytest.fixture
    def selector(self):
        return get_route_selector()
    
    def test_select_xiaoyi_gui_agent_by_intent_手机操作(self, selector):
        """测试: '手机操作' 能选中 route.xiaoyi_gui_agent"""
        result = selector.select_route("手机操作")
        
        assert result is not None, "应该能选中 route"
        assert result.selected_route_id == "route.xiaoyi_gui_agent", \
            f"应该选中 route.xiaoyi_gui_agent，实际选中 {result.selected_route_id}"
        assert result.risk_level == "L4", f"风险等级应该是 L4，实际是 {result.risk_level}"
        assert result.policy == "strong_confirm", f"策略应该是 strong_confirm，实际是 {result.policy}"
    
    def test_select_xiaoyi_gui_agent_by_intent_GUI操作(self, selector):
        """测试: 'GUI操作' 能选中 route.xiaoyi_gui_agent"""
        result = selector.select_route("GUI操作")
        
        assert result is not None, "应该能选中 route"
        assert result.selected_route_id == "route.xiaoyi_gui_agent", \
            f"应该选中 route.xiaoyi_gui_agent，实际选中 {result.selected_route_id}"
    
    def test_select_xiaoyi_gui_agent_by_intent_小艺帮帮忙(self, selector):
        """测试: '小艺帮帮忙' 能选中 route.xiaoyi_gui_agent"""
        result = selector.select_route("小艺帮帮忙")
        
        assert result is not None, "应该能选中 route"
        assert result.selected_route_id == "route.xiaoyi_gui_agent", \
            f"应该选中 route.xiaoyi_gui_agent，实际选中 {result.selected_route_id}"
    
    def test_select_xiaoyi_gui_agent_by_intent_视觉操作(self, selector):
        """测试: '视觉操作' 能选中 route.xiaoyi_gui_agent"""
        result = selector.select_route("视觉操作")
        
        assert result is not None, "应该能选中 route"
        assert result.selected_route_id == "route.xiaoyi_gui_agent", \
            f"应该选中 route.xiaoyi_gui_agent，实际选中 {result.selected_route_id}"
    
    def test_select_xiaoyi_gui_agent_by_intent_操作手机(self, selector):
        """测试: '操作手机' 能选中 route.xiaoyi_gui_agent"""
        result = selector.select_route("操作手机")
        
        assert result is not None, "应该能选中 route"
        assert result.selected_route_id == "route.xiaoyi_gui_agent", \
            f"应该选中 route.xiaoyi_gui_agent，实际选中 {result.selected_route_id}"
    
    def test_select_xiaoyi_gui_agent_requires_confirmation(self, selector):
        """测试: xiaoyi_gui_agent 需要确认"""
        result = selector.select_route("手机操作")
        
        assert result is not None
        assert result.requires_confirmation is True, "L4 route 必须需要确认"
    
    def test_select_xiaoyi_gui_agent_has_fallback(self, selector):
        """测试: xiaoyi_gui_agent 的 fallback 信息"""
        result = selector.select_route("手机操作")
        
        assert result is not None
        # fallback_routes 可能是空列表，但字段必须存在
        assert hasattr(result, 'fallback_routes'), "必须有 fallback_routes 字段"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
