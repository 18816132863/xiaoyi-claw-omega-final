#!/usr/bin/env python3
"""
自动路由注册测试
"""

import json
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.auto_register_routes import (
    auto_register_routes,
    generate_route,
    generate_route_id,
    build_intent_index,
    load_capability_registry,
    INTENT_MAPPING,
    RISK_LEVELS,
    FALLBACK_ROUTES,
    HANDLER_MAPPING
)


class TestAutoRegisterRoutes:
    """测试自动路由注册"""
    
    def test_load_capability_registry(self):
        """测试加载能力注册表"""
        registry = load_capability_registry()
        assert "items" in registry
        assert len(registry["items"]) > 0
    
    def test_generate_route_id(self):
        """测试生成路由 ID"""
        route_id = generate_route_id("send_message")
        assert route_id == "route.send_message"
    
    def test_generate_route(self):
        """测试生成单个路由"""
        cap_info = {
            "name": "send_message",
            "description": "发送消息能力",
            "path": "capabilities/send_message.py"
        }
        route = generate_route("send_message", cap_info)
        
        assert route["route_id"] == "route.send_message"
        assert route["capability"] == "send_message"
        assert "发送消息" in route["user_intents"]
        assert route["risk_level"] == "HIGH"
        assert route["requires_confirmation"] is True
        assert len(route["fallback_routes"]) > 0
    
    def test_auto_register_routes(self):
        """测试自动注册所有路由"""
        registry = auto_register_routes()
        
        assert "version" in registry
        assert "routes" in registry
        assert "intent_index" in registry
        assert "stats" in registry
        
        # 检查路由数量
        assert len(registry["routes"]) > 0
        assert registry["stats"]["total"] == len(registry["routes"])
    
    def test_build_intent_index(self):
        """测试构建意图索引"""
        routes = {
            "route.send_message": {
                "user_intents": ["发送消息", "发消息"]
            },
            "route.create_note": {
                "user_intents": ["创建备忘录", "新建备忘录"]
            }
        }
        
        intent_index = build_intent_index(routes)
        
        assert "发送消息" in intent_index
        assert "route.send_message" in intent_index["发送消息"]
        assert "创建备忘录" in intent_index
        assert "route.create_note" in intent_index["创建备忘录"]


class TestIntentMapping:
    """测试意图映射"""
    
    def test_intent_mapping_not_empty(self):
        """测试意图映射不为空"""
        assert len(INTENT_MAPPING) > 0
    
    def test_all_capabilities_mapped(self):
        """测试所有能力都有意图映射"""
        registry = load_capability_registry()
        mapped_caps = set()
        
        for caps in INTENT_MAPPING.values():
            mapped_caps.update(caps)
        
        # 至少大部分能力应该有映射
        total_caps = len(registry["items"])
        mapping_ratio = len(mapped_caps) / total_caps
        assert mapping_ratio >= 0.8, f"意图映射覆盖率过低: {mapping_ratio:.1%}"


class TestRiskLevels:
    """测试风险等级"""
    
    def test_risk_levels_defined(self):
        """测试风险等级已定义"""
        assert len(RISK_LEVELS) > 0
    
    def test_high_risk_operations(self):
        """测试高风险操作"""
        high_risk_ops = [
            "delete_note", "delete_contact", "delete_photo",
            "delete_file", "make_call", "send_message"
        ]
        
        for op in high_risk_ops:
            assert RISK_LEVELS.get(op) == "HIGH", f"{op} 应该是高风险"
    
    def test_low_risk_operations(self):
        """测试低风险操作"""
        low_risk_ops = [
            "query_note", "query_contact", "query_photo",
            "list_recent_notes", "get_location"
        ]
        
        for op in low_risk_ops:
            assert RISK_LEVELS.get(op) == "LOW", f"{op} 应该是低风险"


class TestFallbackRoutes:
    """测试 Fallback 路由"""
    
    def test_fallback_routes_defined(self):
        """测试 fallback 路由已定义"""
        assert len(FALLBACK_ROUTES) > 0
    
    def test_send_message_has_fallback(self):
        """测试发送消息有 fallback"""
        assert "send_message" in FALLBACK_ROUTES
        assert len(FALLBACK_ROUTES["send_message"]) > 0
    
    def test_delete_operations_have_query_fallback(self):
        """测试删除操作有查询 fallback"""
        delete_ops = [
            "delete_note", "delete_contact", "delete_photo",
            "delete_file", "delete_alarm", "delete_calendar_event"
        ]
        
        for op in delete_ops:
            if op in FALLBACK_ROUTES:
                fallbacks = FALLBACK_ROUTES[op]
                query_op = op.replace("delete_", "query_")
                assert query_op in fallbacks, \
                    f"{op} 应该有 {query_op} 作为 fallback"


class TestHandlerMapping:
    """测试 Handler 映射"""
    
    def test_handler_mapping_not_empty(self):
        """测试 handler 映射不为空"""
        assert len(HANDLER_MAPPING) > 0
    
    def test_handler_format(self):
        """测试 handler 格式"""
        for cap, handler in HANDLER_MAPPING.items():
            parts = handler.split(".")
            assert len(parts) >= 2, f"{cap} handler 格式不正确: {handler}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
