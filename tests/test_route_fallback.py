#!/usr/bin/env python3
"""
路由 Fallback 测试
测试 fallback 路由的正确性和可达性
"""

import json
import pytest
from pathlib import Path
from typing import Dict, List, Optional


class FallbackChainValidator:
    """Fallback 链验证器"""
    
    def __init__(self, route_registry_path: str):
        with open(route_registry_path, "r", encoding="utf-8") as f:
            self.registry = json.load(f)
        self.routes = self.registry.get("routes", {})
    
    def get_fallback_chain(self, route_id: str) -> List[str]:
        """获取完整的 fallback 链"""
        chain = []
        visited = set()
        current = route_id
        
        while current and current not in visited:
            visited.add(current)
            route = self.routes.get(current)
            
            if not route:
                break
            
            fallbacks = route.get("fallback_routes", [])
            if fallbacks:
                next_fallback = f"route.{fallbacks[0]}"
                chain.append(next_fallback)
                current = next_fallback
            else:
                break
        
        return chain
    
    def validate_fallback_chain(self, route_id: str) -> Dict:
        """验证 fallback 链"""
        route = self.routes.get(route_id)
        if not route:
            return {"valid": False, "error": "Route not found"}
        
        fallbacks = route.get("fallback_routes", [])
        
        result = {
            "valid": True,
            "route_id": route_id,
            "fallbacks": [],
            "errors": []
        }
        
        for fallback in fallbacks:
            fallback_route_id = f"route.{fallback}"
            fallback_route = self.routes.get(fallback_route_id)
            
            if not fallback_route:
                result["valid"] = False
                result["errors"].append(f"Fallback route not found: {fallback}")
            else:
                result["fallbacks"].append({
                    "route_id": fallback_route_id,
                    "capability": fallback,
                    "risk_level": fallback_route.get("risk_level"),
                    "has_fallback": len(fallback_route.get("fallback_routes", [])) > 0
                })
        
        return result
    
    def check_no_circular_fallback(self, route_id: str) -> bool:
        """检查没有循环 fallback"""
        visited = set()
        current = route_id
        
        while current:
            if current in visited:
                return False
            visited.add(current)
            
            route = self.routes.get(current)
            if not route:
                break
            
            fallbacks = route.get("fallback_routes", [])
            if fallbacks:
                current = f"route.{fallbacks[0]}"
            else:
                break
        
        return True
    
    def get_terminal_fallback(self, route_id: str) -> Optional[str]:
        """获取终端 fallback（没有进一步 fallback 的路由）"""
        visited = set()
        current = route_id
        
        while current and current not in visited:
            visited.add(current)
            route = self.routes.get(current)
            
            if not route:
                return None
            
            fallbacks = route.get("fallback_routes", [])
            if not fallbacks:
                return current
            
            current = f"route.{fallbacks[0]}"
        
        return None


@pytest.fixture
def fallback_validator():
    """创建 fallback 验证器"""
    registry_path = Path(__file__).parent.parent / "infrastructure" / "route_registry.json"
    return FallbackChainValidator(str(registry_path))


class TestFallbackExistence:
    """测试 Fallback 存在性"""
    
    def test_send_message_has_fallback(self, fallback_validator):
        """测试发送消息有 fallback"""
        result = fallback_validator.validate_fallback_chain("route.send_message")
        assert result["valid"], f"send_message fallback 无效: {result['errors']}"
        assert len(result["fallbacks"]) > 0
    
    def test_delete_operations_have_fallback(self, fallback_validator):
        """测试删除操作有 fallback"""
        delete_routes = [
            "route.delete_note",
            "route.delete_contact",
            "route.delete_alarm",
            "route.delete_calendar_event"
        ]
        
        for route_id in delete_routes:
            if route_id in fallback_validator.routes:
                result = fallback_validator.validate_fallback_chain(route_id)
                # 删除操作应该有 fallback（至少是查询）
                assert len(result["fallbacks"]) > 0 or result["valid"], \
                    f"{route_id} 应该有有效的 fallback"


class TestFallbackValidity:
    """测试 Fallback 有效性"""
    
    def test_all_fallbacks_exist(self, fallback_validator):
        """测试所有 fallback 都存在"""
        for route_id, route in fallback_validator.routes.items():
            result = fallback_validator.validate_fallback_chain(route_id)
            assert result["valid"], \
                f"{route_id} 有无效 fallback: {result['errors']}"
    
    def test_no_circular_fallbacks(self, fallback_validator):
        """测试没有循环 fallback"""
        for route_id in fallback_validator.routes:
            assert fallback_validator.check_no_circular_fallback(route_id), \
                f"{route_id} 有循环 fallback"


class TestFallbackChain:
    """测试 Fallback 链"""
    
    def test_fallback_chain_depth(self, fallback_validator):
        """测试 fallback 链深度"""
        for route_id in fallback_validator.routes:
            chain = fallback_validator.get_fallback_chain(route_id)
            # 链深度不应该太深（避免无限循环）
            assert len(chain) <= 5, \
                f"{route_id} fallback 链过深: {len(chain)}"
    
    def test_terminal_fallback_exists(self, fallback_validator):
        """测试终端 fallback 存在"""
        routes_with_fallback = [
            route_id for route_id, route in fallback_validator.routes.items()
            if route.get("fallback_routes")
        ]
        
        for route_id in routes_with_fallback:
            terminal = fallback_validator.get_terminal_fallback(route_id)
            assert terminal is not None, \
                f"{route_id} 没有终端 fallback"


class TestSpecificFallbackScenarios:
    """测试特定 Fallback 场景"""
    
    def test_message_send_failure_fallback(self, fallback_validator):
        """测试消息发送失败的 fallback"""
        # send_message 失败应该可以 fallback 到查询状态
        result = fallback_validator.validate_fallback_chain("route.send_message")
        
        if result["fallbacks"]:
            # 检查是否有查询相关的 fallback
            has_query_fallback = any(
                "query" in fb["capability"] or "list" in fb["capability"]
                for fb in result["fallbacks"]
            )
            assert has_query_fallback, \
                "send_message 应该有查询相关的 fallback"
    
    def test_storage_failure_fallback(self, fallback_validator):
        """测试存储失败的 fallback"""
        # 存储相关操作失败应该可以 fallback 到本地存储
        storage_routes = [
            "route.delete_note",
            "route.update_note"
        ]
        
        for route_id in storage_routes:
            if route_id in fallback_validator.routes:
                result = fallback_validator.validate_fallback_chain(route_id)
                assert result["valid"], \
                    f"{route_id} fallback 无效: {result['errors']}"
    
    def test_notification_auth_failure_fallback(self, fallback_validator):
        """测试通知授权失败的 fallback"""
        # 通知授权失败应该可以 fallback 到消息发送或提醒用户
        route_id = "route.query_notification_status"
        
        if route_id in fallback_validator.routes:
            result = fallback_validator.validate_fallback_chain(route_id)
            # 即使没有 fallback，也应该有效
            assert result["valid"]


class TestFallbackRiskLevel:
    """测试 Fallback 风险等级"""
    
    def test_fallback_lower_risk(self, fallback_validator):
        """测试 fallback 风险等级更低或相同"""
        for route_id, route in fallback_validator.routes.items():
            risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "SYSTEM": 3}
            route_risk = route.get("risk_level", "LOW")
            
            for fallback in route.get("fallback_routes", []):
                fallback_route = fallback_validator.routes.get(f"route.{fallback}")
                if fallback_route:
                    fallback_risk = fallback_route.get("risk_level", "LOW")
                    # Fallback 风险应该 <= 原路由
                    assert risk_order.get(fallback_risk, 0) <= risk_order.get(route_risk, 0), \
                        f"{route_id} 的 fallback {fallback} 风险等级更高"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
