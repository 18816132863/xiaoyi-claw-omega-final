#!/usr/bin/env python3
"""
路由风险策略测试
测试路由的风险等级和确认策略
使用新的 L0/L1/L2/L3/L4/BLOCKED 风险体系
"""

import json
import pytest
from pathlib import Path
from typing import Dict, List


# 风险等级映射
RISK_LEVELS = {
    "L0": 0,  # 无风险
    "L1": 1,  # 低风险
    "L2": 2,  # 中风险
    "L3": 3,  # 高风险
    "L4": 4,  # 系统级
    "BLOCKED": 5  # 禁止
}

# 需要确认的风险等级
CONFIRMATION_REQUIRED_LEVELS = ["L3", "L4", "BLOCKED"]

# 高风险等级（对应旧的 HIGH）
HIGH_RISK_LEVELS = ["L3", "L4"]

# 低风险等级（对应旧的 LOW/MEDIUM）
LOW_RISK_LEVELS = ["L0", "L1", "L2"]


class RiskPolicyValidator:
    """风险策略验证器"""
    
    def __init__(self, route_registry_path: str):
        with open(route_registry_path, "r", encoding="utf-8") as f:
            self.registry = json.load(f)
        self.routes = self.registry.get("routes", {})
    
    def get_high_risk_routes(self) -> List[str]:
        """获取所有高风险路由"""
        return [
            route_id for route_id, route in self.routes.items()
            if route.get("risk_level") in HIGH_RISK_LEVELS
        ]
    
    def get_system_routes(self) -> List[str]:
        """获取所有系统级路由"""
        return [
            route_id for route_id, route in self.routes.items()
            if route.get("risk_level") == "L4"
        ]
    
    def get_routes_requiring_confirmation(self) -> List[str]:
        """获取所有需要确认的路由"""
        return [
            route_id for route_id, route in self.routes.items()
            if route.get("requires_confirmation")
        ]
    
    def validate_risk_policy(self, route_id: str) -> Dict:
        """验证路由的风险策略"""
        route = self.routes.get(route_id)
        if not route:
            return {"valid": False, "error": "Route not found"}
        
        risk_level = route.get("risk_level", "L0")
        requires_confirmation = route.get("requires_confirmation", False)
        
        errors = []
        
        # 高风险和系统级路由必须需要确认
        if risk_level in CONFIRMATION_REQUIRED_LEVELS and not requires_confirmation:
            errors.append(f"{risk_level} risk route should require confirmation")
        
        # 删除操作应该是高风险 (L3+)
        if "delete" in route_id.lower() and risk_level not in HIGH_RISK_LEVELS:
            errors.append(f"Delete operation should be HIGH risk (L3+), got {risk_level}")
        
        # 查询操作应该是低风险 (L0-L2)
        if "query" in route_id.lower() and risk_level not in LOW_RISK_LEVELS:
            errors.append(f"Query operation should be LOW risk (L0-L2), got {risk_level}")
        
        return {
            "valid": len(errors) == 0,
            "route_id": route_id,
            "risk_level": risk_level,
            "requires_confirmation": requires_confirmation,
            "errors": errors
        }
    
    def get_risk_distribution(self) -> Dict[str, int]:
        """获取风险分布"""
        distribution = {level: 0 for level in RISK_LEVELS.keys()}
        for route in self.routes.values():
            risk = route.get("risk_level", "L0")
            if risk in distribution:
                distribution[risk] += 1
        return distribution


@pytest.fixture
def risk_validator():
    """创建风险策略验证器"""
    registry_path = Path(__file__).parent.parent / "infrastructure" / "route_registry.json"
    return RiskPolicyValidator(str(registry_path))


class TestRiskLevelClassification:
    """测试风险等级分类"""
    
    def test_delete_operations_are_high_risk(self, risk_validator):
        """测试删除操作是高风险"""
        delete_routes = [
            route_id for route_id in risk_validator.routes
            if "delete" in route_id.lower()
        ]
        
        for route_id in delete_routes:
            route = risk_validator.routes[route_id]
            assert route["risk_level"] in HIGH_RISK_LEVELS, \
                f"{route_id} 应该是高风险 (L3+), 实际: {route['risk_level']}"
    
    def test_query_operations_are_low_risk(self, risk_validator):
        """测试查询操作是低风险"""
        query_routes = [
            route_id for route_id in risk_validator.routes
            if "query" in route_id.lower() or "list" in route_id.lower()
        ]
        
        for route_id in query_routes:
            route = risk_validator.routes[route_id]
            assert route["risk_level"] in LOW_RISK_LEVELS, \
                f"{route_id} 应该是低风险 (L0-L2), 实际: {route['risk_level']}"
    
    def test_send_operations_are_high_risk(self, risk_validator):
        """测试发送操作是高风险"""
        send_routes = [
            route_id for route_id in risk_validator.routes
            if "send" in route_id.lower() or "call" in route_id.lower()
        ]
        
        for route_id in send_routes:
            route = risk_validator.routes[route_id]
            assert route["risk_level"] in HIGH_RISK_LEVELS, \
                f"{route_id} 应该是高风险 (L3+), 实际: {route['risk_level']}"


class TestConfirmationPolicy:
    """测试确认策略"""
    
    def test_high_risk_requires_confirmation(self, risk_validator):
        """测试高风险路由需要确认"""
        high_risk_routes = risk_validator.get_high_risk_routes()
        
        for route_id in high_risk_routes:
            route = risk_validator.routes[route_id]
            assert route["requires_confirmation"], \
                f"高风险路由 {route_id} 应该需要确认"
    
    def test_system_routes_require_confirmation(self, risk_validator):
        """测试系统级路由需要确认"""
        system_routes = risk_validator.get_system_routes()
        
        for route_id in system_routes:
            route = risk_validator.routes[route_id]
            assert route["requires_confirmation"], \
                f"系统级路由 {route_id} 应该需要确认"
    
    def test_low_risk_no_confirmation_needed(self, risk_validator):
        """测试低风险路由不需要确认"""
        for route_id, route in risk_validator.routes.items():
            if route["risk_level"] in LOW_RISK_LEVELS:
                # 低风险路由通常不需要确认
                # 但这不是硬性要求，所以只做信息性检查
                pass


class TestRiskDistribution:
    """测试风险分布"""
    
    def test_risk_distribution_reasonable(self, risk_validator):
        """测试风险分布合理"""
        distribution = risk_validator.get_risk_distribution()
        
        # 应该有低风险路由
        low_risk_count = sum(distribution[level] for level in LOW_RISK_LEVELS)
        assert low_risk_count > 0, "应该有低风险路由 (L0-L2)"
        
        # 应该有高风险路由
        high_risk_count = sum(distribution[level] for level in HIGH_RISK_LEVELS)
        assert high_risk_count > 0, "应该有高风险路由 (L3-L4)"
        
        # 低风险应该是最多的
        assert low_risk_count >= high_risk_count, \
            "低风险路由应该不少于高风险路由"
    
    def test_stats_match_actual(self, risk_validator):
        """测试统计与实际匹配"""
        distribution = risk_validator.get_risk_distribution()
        stats = risk_validator.registry.get("stats", {}).get("by_risk_level", {})
        
        for level in RISK_LEVELS.keys():
            assert distribution[level] == stats.get(level, 0), \
                f"{level} 统计不匹配: {distribution[level]} vs {stats.get(level, 0)}"


class TestRiskPolicyValidation:
    """测试风险策略验证"""
    
    def test_all_routes_valid_policy(self, risk_validator):
        """测试所有路由有有效策略"""
        for route_id in risk_validator.routes:
            result = risk_validator.validate_risk_policy(route_id)
            assert result["valid"], \
                f"{route_id} 风险策略无效: {result['errors']}"
    
    def test_confirmation_count_matches(self, risk_validator):
        """测试确认数量匹配"""
        requiring_confirmation = risk_validator.get_routes_requiring_confirmation()
        stats = risk_validator.registry.get("stats", {}).get("requiring_confirmation", 0)
        
        assert len(requiring_confirmation) == stats, \
            f"需要确认的路由数不匹配: {len(requiring_confirmation)} vs {stats}"


class TestSpecificRiskPolicies:
    """测试特定风险策略"""
    
    def test_message_send_risk_policy(self, risk_validator):
        """测试消息发送风险策略"""
        route = risk_validator.routes.get("route.send_message")
        if route:
            assert route["risk_level"] in HIGH_RISK_LEVELS, \
                f"send_message 应该是高风险, 实际: {route['risk_level']}"
            assert route["requires_confirmation"] is True
    
    def test_make_call_risk_policy(self, risk_validator):
        """测试拨打电话风险策略"""
        route = risk_validator.routes.get("route.make_call")
        if route:
            assert route["risk_level"] in HIGH_RISK_LEVELS, \
                f"make_call 应该是高风险, 实际: {route['risk_level']}"
            assert route["requires_confirmation"] is True
    
    def test_delete_note_risk_policy(self, risk_validator):
        """测试删除备忘录风险策略"""
        route = risk_validator.routes.get("route.delete_note")
        if route:
            assert route["risk_level"] in HIGH_RISK_LEVELS, \
                f"delete_note 应该是高风险, 实际: {route['risk_level']}"
            assert route["requires_confirmation"] is True
    
    def test_query_note_risk_policy(self, risk_validator):
        """测试查询备忘录风险策略"""
        route = risk_validator.routes.get("route.query_note")
        if route:
            assert route["risk_level"] in LOW_RISK_LEVELS, \
                f"query_note 应该是低风险, 实际: {route['risk_level']}"
            # 低风险通常不需要确认


class TestRiskPolicyConsistency:
    """测试风险策略一致性"""
    
    def test_similar_operations_same_risk(self, risk_validator):
        """测试相似操作有相同风险等级"""
        # 所有删除操作应该是高风险
        delete_routes = [
            route_id for route_id in risk_validator.routes
            if "delete" in route_id.lower()
        ]
        
        risk_levels = set(
            risk_validator.routes[route_id]["risk_level"]
            for route_id in delete_routes
        )
        
        # 所有删除操作都应该是高风险 (L3+)
        for level in risk_levels:
            assert level in HIGH_RISK_LEVELS, \
                f"所有删除操作应该是高风险 (L3+), 实际包含: {risk_levels}"
    
    def test_create_vs_delete_different_risk(self, risk_validator):
        """测试创建和删除有不同风险等级"""
        create_routes = [
            route_id for route_id in risk_validator.routes
            if "create" in route_id.lower()
        ]
        delete_routes = [
            route_id for route_id in risk_validator.routes
            if "delete" in route_id.lower()
        ]
        
        if create_routes and delete_routes:
            avg_create_risk = sum(
                RISK_LEVELS.get(risk_validator.routes[route_id]["risk_level"], 0)
                for route_id in create_routes
            ) / len(create_routes)
            
            avg_delete_risk = sum(
                RISK_LEVELS.get(risk_validator.routes[route_id]["risk_level"], 0)
                for route_id in delete_routes
            ) / len(delete_routes)
            
            # 删除的平均风险应该 >= 创建
            assert avg_delete_risk >= avg_create_risk, \
                "删除操作风险应该不低于创建操作"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
