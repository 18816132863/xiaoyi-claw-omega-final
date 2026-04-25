#!/usr/bin/env python3
"""
路由注册表测试
"""

import json
import pytest
from pathlib import Path


@pytest.fixture
def route_registry():
    """加载路由注册表"""
    registry_path = Path(__file__).parent.parent / "infrastructure" / "route_registry.json"
    with open(registry_path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestRouteRegistryStructure:
    """测试路由注册表结构"""
    
    def test_registry_exists(self):
        """测试注册表文件存在"""
        registry_path = Path(__file__).parent.parent / "infrastructure" / "route_registry.json"
        assert registry_path.exists(), "route_registry.json 不存在"
    
    def test_registry_has_required_fields(self, route_registry):
        """测试注册表有必需字段"""
        required_fields = ["version", "updated", "routes", "intent_index", "stats"]
        for field in required_fields:
            assert field in route_registry, f"缺少必需字段: {field}"
    
    def test_routes_not_empty(self, route_registry):
        """测试路由不为空"""
        assert len(route_registry["routes"]) > 0, "routes 不能为空"
    
    def test_stats_total_matches(self, route_registry):
        """测试统计总数匹配"""
        actual_count = len(route_registry["routes"])
        recorded_count = route_registry["stats"]["total"]
        assert actual_count == recorded_count, f"路由数不匹配: {actual_count} vs {recorded_count}"


class TestRouteIntegrity:
    """测试路由完整性"""
    
    def test_all_routes_have_required_fields(self, route_registry):
        """测试所有路由有必需字段"""
        required_fields = [
            "route_id", "capability", "user_intents", "handler",
            "input_schema", "output_schema", "risk_level",
            "requires_confirmation", "fallback_routes"
        ]
        
        for route_id, route in route_registry["routes"].items():
            for field in required_fields:
                assert field in route, f"路由 {route_id} 缺少字段: {field}"
    
    def test_route_id_consistency(self, route_registry):
        """测试路由 ID 一致性"""
        for route_id, route in route_registry["routes"].items():
            assert route["route_id"] == route_id, f"路由 ID 不一致: {route_id}"
    
    def test_valid_risk_levels(self, route_registry):
        """测试有效的风险等级"""
        valid_levels = ["L0", "L1", "L2", "L3", "L4", "BLOCKED"]
        for route_id, route in route_registry["routes"].items():
            assert route["risk_level"] in valid_levels, \
                f"路由 {route_id} 无效风险等级: {route['risk_level']}"
    
    def test_high_risk_requires_confirmation(self, route_registry):
        """测试高风险路由需要确认"""
        for route_id, route in route_registry["routes"].items():
            if route["risk_level"] in ["L3", "L4", "BLOCKED"]:
                assert route["requires_confirmation"], \
                    f"高风险路由 {route_id} 应该需要确认"


class TestIntentIndex:
    """测试意图索引"""
    
    def test_intent_index_not_empty(self, route_registry):
        """测试意图索引不为空"""
        assert len(route_registry["intent_index"]) > 0, "意图索引不能为空"
    
    def test_intent_routes_exist(self, route_registry):
        """测试意图索引中的路由存在"""
        routes = route_registry["routes"]
        for intent, route_ids in route_registry["intent_index"].items():
            for route_id in route_ids:
                assert route_id in routes, \
                    f"意图 {intent} 的路由不存在: {route_id}"
    
    def test_route_intents_in_index(self, route_registry):
        """测试路由的意图在索引中"""
        intent_index = route_registry["intent_index"]
        for route_id, route in route_registry["routes"].items():
            for intent in route.get("user_intents", []):
                assert intent in intent_index, \
                    f"路由 {route_id} 的意图未在索引中: {intent}"
                assert route_id in intent_index[intent], \
                    f"意图索引不一致: {intent} 应包含 {route_id}"


class TestFallbackRoutes:
    """测试 Fallback 路由"""
    
    def test_fallback_routes_exist(self, route_registry):
        """测试 fallback 路由存在"""
        routes = route_registry["routes"]
        for route_id, route in routes.items():
            for fallback in route.get("fallback_routes", []):
                fallback_route_id = f"route.{fallback}"
                assert fallback_route_id in routes, \
                    f"路由 {route_id} 的 fallback 不存在: {fallback}"
    
    def test_message_send_has_fallback(self, route_registry):
        """测试消息发送有 fallback"""
        route = route_registry["routes"].get("route.send_message")
        if route:
            assert len(route["fallback_routes"]) > 0, \
                "send_message 应该有 fallback"


class TestSchemaIntegrity:
    """测试 Schema 完整性"""
    
    def test_input_schemas_have_type(self, route_registry):
        """测试 input schema 有 type"""
        for route_id, route in route_registry["routes"].items():
            assert "type" in route["input_schema"], \
                f"路由 {route_id} input_schema 缺少 type"
    
    def test_output_schemas_have_type(self, route_registry):
        """测试 output schema 有 type"""
        for route_id, route in route_registry["routes"].items():
            assert "type" in route["output_schema"], \
                f"路由 {route_id} output_schema 缺少 type"
    
    def test_schemas_have_properties(self, route_registry):
        """测试 schema 有 properties"""
        for route_id, route in route_registry["routes"].items():
            assert "properties" in route["input_schema"], \
                f"路由 {route_id} input_schema 缺少 properties"
            assert "properties" in route["output_schema"], \
                f"路由 {route_id} output_schema 缺少 properties"


class TestRiskStatistics:
    """测试风险统计"""
    
    def test_risk_statistics_match(self, route_registry):
        """测试风险统计匹配"""
        routes = route_registry["routes"]
        stats = route_registry["stats"]
        
        actual_counts = {"L0": 0, "L1": 0, "L2": 0, "L3": 0, "L4": 0, "BLOCKED": 0}
        for route in routes.values():
            risk = route.get("risk_level", "L0")
            if risk in actual_counts:
                actual_counts[risk] += 1
        
        recorded_counts = stats.get("by_risk_level", {})
        for level in ["L0", "L1", "L2", "L3", "L4", "BLOCKED"]:
            assert actual_counts[level] == recorded_counts.get(level, 0), \
                f"风险等级统计不一致 {level}: {actual_counts[level]} vs {recorded_counts.get(level, 0)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
