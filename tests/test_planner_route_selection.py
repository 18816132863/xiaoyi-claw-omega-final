#!/usr/bin/env python3
"""
规划器路由选择测试
测试 autonomous_planner 能否根据用户目标找到正确的路由
"""

import json
import pytest
from pathlib import Path
from typing import Dict, List, Optional


class MockRouteSelector:
    """模拟路由选择器"""
    
    def __init__(self, route_registry_path: str):
        with open(route_registry_path, "r", encoding="utf-8") as f:
            self.registry = json.load(f)
        self.intent_index = self.registry.get("intent_index", {})
        self.routes = self.registry.get("routes", {})
    
    def find_routes_by_intent(self, intent: str) -> List[str]:
        """根据意图查找路由"""
        return self.intent_index.get(intent, [])
    
    def find_route_by_capability(self, capability: str) -> Optional[Dict]:
        """根据能力查找路由"""
        route_id = f"route.{capability}"
        return self.routes.get(route_id)
    
    def select_best_route(self, intent: str, context: Dict = None) -> Optional[Dict]:
        """选择最佳路由"""
        route_ids = self.find_routes_by_intent(intent)
        
        if not route_ids:
            return None
        
        # 简单策略：返回第一个匹配的路由
        # 实际实现可以考虑上下文、风险等级等
        return self.routes.get(route_ids[0])
    
    def get_route_handler(self, route_id: str) -> Optional[str]:
        """获取路由的 handler"""
        route = self.routes.get(route_id)
        return route.get("handler") if route else None
    
    def get_route_fallbacks(self, route_id: str) -> List[str]:
        """获取路由的 fallback"""
        route = self.routes.get(route_id)
        return route.get("fallback_routes", []) if route else []


@pytest.fixture
def route_selector():
    """创建路由选择器"""
    registry_path = Path(__file__).parent.parent / "infrastructure" / "route_registry.json"
    return MockRouteSelector(str(registry_path))


class TestIntentBasedRouting:
    """测试基于意图的路由"""
    
    def test_find_send_message_route(self, route_selector):
        """测试查找发送消息路由"""
        routes = route_selector.find_routes_by_intent("发送消息")
        assert len(routes) > 0
        assert "route.send_message" in routes
    
    def test_find_query_note_route(self, route_selector):
        """测试查找查询备忘录路由"""
        routes = route_selector.find_routes_by_intent("查询备忘录")
        assert len(routes) > 0
    
    def test_find_create_alarm_route(self, route_selector):
        """测试查找创建闹钟路由"""
        routes = route_selector.find_routes_by_intent("创建闹钟")
        assert len(routes) > 0
        assert "route.create_alarm" in routes
    
    def test_find_make_call_route(self, route_selector):
        """测试查找拨打电话路由"""
        routes = route_selector.find_routes_by_intent("拨打电话")
        assert len(routes) > 0
        assert "route.make_call" in routes
    
    def test_unknown_intent_returns_empty(self, route_selector):
        """测试未知意图返回空"""
        routes = route_selector.find_routes_by_intent("这是一个不存在的意图xyz")
        assert len(routes) == 0


class TestCapabilityBasedRouting:
    """测试基于能力的路由"""
    
    def test_find_route_by_capability(self, route_selector):
        """测试根据能力查找路由"""
        route = route_selector.find_route_by_capability("send_message")
        assert route is not None
        assert route["capability"] == "send_message"
    
    def test_find_route_handler(self, route_selector):
        """测试查找路由 handler"""
        handler = route_selector.get_route_handler("route.send_message")
        assert handler is not None
        assert "send_message" in handler
    
    def test_find_route_fallbacks(self, route_selector):
        """测试查找路由 fallback"""
        fallbacks = route_selector.get_route_fallbacks("route.send_message")
        assert len(fallbacks) > 0


class TestRouteSelection:
    """测试路由选择"""
    
    def test_select_best_route_for_messaging(self, route_selector):
        """测试消息发送的最佳路由选择"""
        route = route_selector.select_best_route("发送消息")
        assert route is not None
        assert route["capability"] == "send_message"
        # 新风险体系：L3 = 高风险
        assert route["risk_level"] in ["L3", "L4"], \
            f"send_message 应该是高风险 (L3+), 实际: {route['risk_level']}"
    
    def test_select_best_route_for_query(self, route_selector):
        """测试查询操作的最佳路由选择"""
        route = route_selector.select_best_route("查询备忘录")
        assert route is not None
        assert "query" in route["capability"]
        # 新风险体系：L0-L2 = 低风险
        assert route["risk_level"] in ["L0", "L1", "L2"], \
            f"query 应该是低风险 (L0-L2), 实际: {route['risk_level']}"
    
    def test_select_best_route_for_delete(self, route_selector):
        """测试删除操作的最佳路由选择"""
        route = route_selector.select_best_route("删除备忘录")
        assert route is not None
        assert "delete" in route["capability"]
        # 新风险体系：L3+ = 高风险
        assert route["risk_level"] in ["L3", "L4"], \
            f"delete 应该是高风险 (L3+), 实际: {route['risk_level']}"
        assert route["requires_confirmation"] is True


class TestRouteMetadata:
    """测试路由元数据"""
    
    def test_route_has_input_schema(self, route_selector):
        """测试路由有输入 schema"""
        route = route_selector.find_route_by_capability("send_message")
        assert "input_schema" in route
        assert "properties" in route["input_schema"]
    
    def test_route_has_output_schema(self, route_selector):
        """测试路由有输出 schema"""
        route = route_selector.find_route_by_capability("send_message")
        assert "output_schema" in route
        assert "properties" in route["output_schema"]
    
    def test_high_risk_route_requires_confirmation(self, route_selector):
        """测试高风险路由需要确认"""
        high_risk_caps = ["send_message", "make_call", "delete_note"]
        
        for cap in high_risk_caps:
            route = route_selector.find_route_by_capability(cap)
            if route:
                # 新风险体系：L3+ 需要确认
                if route["risk_level"] in ["L3", "L4", "BLOCKED"]:
                    assert route["requires_confirmation"], \
                        f"{cap} 应该需要确认"


class TestFallbackChain:
    """测试 Fallback 链"""
    
    def test_send_message_fallback_chain(self, route_selector):
        """测试发送消息的 fallback 链"""
        fallbacks = route_selector.get_route_fallbacks("route.send_message")
        
        # 应该有 fallback
        assert len(fallbacks) > 0
        
        # fallback 应该是有效的路由
        for fallback in fallbacks:
            fallback_route = route_selector.find_route_by_capability(fallback)
            assert fallback_route is not None, \
                f"fallback {fallback} 应该是有效的路由"
    
    def test_delete_operations_have_query_fallback(self, route_selector):
        """测试删除操作有查询 fallback"""
        delete_caps = ["delete_note", "delete_contact", "delete_alarm"]
        
        for cap in delete_caps:
            route_id = f"route.{cap}"
            fallbacks = route_selector.get_route_fallbacks(route_id)
            
            # 检查是否有对应的查询 fallback
            query_cap = cap.replace("delete_", "query_")
            if fallbacks:
                assert query_cap in fallbacks, \
                    f"{cap} 应该有 {query_cap} 作为 fallback"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
