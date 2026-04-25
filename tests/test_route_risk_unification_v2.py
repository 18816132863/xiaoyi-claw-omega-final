#!/usr/bin/env python3
"""
测试路由风险体系统一 V2
验证：
1. 不允许 LOW/MEDIUM/HIGH/SYSTEM 出现在任何 route 或 stats 中
2. route_registry 真源只能有一个
3. 每条 route 必须有 policy
4. L4 必须是 strong_confirm
5. BLOCKED 必须是 blocked
"""

import json
import pytest
from pathlib import Path


# 正式风险等级
VALID_RISK_LEVELS = {"L0", "L1", "L2", "L3", "L4", "BLOCKED"}

# 旧风险等级 (不允许残留)
LEGACY_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "SYSTEM", "CRITICAL"}

# 有效策略
VALID_POLICIES = {
    "auto_execute",
    "rate_limited",
    "confirm_once",
    "strong_confirm",
    "blocked",
}


@pytest.fixture
def route_registry():
    """加载路由注册表"""
    registry_path = Path(__file__).parent.parent / "infrastructure" / "route_registry.json"
    with open(registry_path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestNoLegacyRiskLevels:
    """测试不允许旧风险等级残留"""
    
    def test_routes_no_legacy_risk_levels(self, route_registry):
        """单条路由不应包含旧风险等级"""
        routes = route_registry.get("routes", {})
        legacy_found = []
        
        for route_id, route in routes.items():
            risk_level = route.get("risk_level", "")
            if risk_level in LEGACY_RISK_LEVELS:
                legacy_found.append((route_id, risk_level))
        
        assert not legacy_found, f"发现旧风险等级: {legacy_found}"
    
    def test_stats_no_legacy_risk_levels(self, route_registry):
        """stats.by_risk_level 不应包含旧风险等级"""
        stats = route_registry.get("stats", {})
        by_risk_level = stats.get("by_risk_level", {})
        
        legacy_found = []
        for level in LEGACY_RISK_LEVELS:
            if level in by_risk_level:
                legacy_found.append(level)
        
        assert not legacy_found, f"stats.by_risk_level 包含旧风险等级: {legacy_found}"


class TestSingleSourceOfTruth:
    """测试路由注册表真源唯一性"""
    
    def test_inventory_registry_deleted_or_empty(self):
        """inventory/route_registry.json 应该被删除或为空"""
        workspace = Path(__file__).parent.parent
        inventory_registry = workspace / "infrastructure" / "inventory" / "route_registry.json"
        
        if inventory_registry.exists():
            with open(inventory_registry, "r", encoding="utf-8") as f:
                inv_registry = json.load(f)
            
            routes = inv_registry.get("routes", {})
            assert not routes, "inventory/route_registry.json 应该为空或被删除"


class TestRoutePolicyRequired:
    """测试每条路由必须有 policy"""
    
    def test_all_routes_have_policy(self, route_registry):
        """每条路由必须有 policy 字段"""
        routes = route_registry.get("routes", {})
        missing_policy = []
        
        for route_id, route in routes.items():
            if "policy" not in route:
                missing_policy.append(route_id)
        
        assert not missing_policy, f"缺少 policy 字段的路由: {missing_policy}"


class TestL4StrongConfirm:
    """测试 L4 必须是 strong_confirm"""
    
    def test_l4_has_strong_confirm(self, route_registry):
        """L4 路由必须有 policy=strong_confirm"""
        routes = route_registry.get("routes", {})
        violations = []
        
        for route_id, route in routes.items():
            if route.get("risk_level") == "L4":
                if route.get("policy") != "strong_confirm":
                    violations.append((route_id, route.get("policy")))
        
        assert not violations, f"L4 路由 policy 不是 strong_confirm: {violations}"
    
    def test_l4_has_required_fields(self, route_registry):
        """L4 路由必须有 requires_preview, requires_stepwise_execution, audit_required"""
        routes = route_registry.get("routes", {})
        violations = []
        
        for route_id, route in routes.items():
            if route.get("risk_level") == "L4":
                if not route.get("requires_preview"):
                    violations.append((route_id, "requires_preview"))
                if not route.get("requires_stepwise_execution"):
                    violations.append((route_id, "requires_stepwise_execution"))
                if not route.get("audit_required"):
                    violations.append((route_id, "audit_required"))
        
        assert not violations, f"L4 路由缺少必需字段: {violations}"


class TestBlockedPolicy:
    """测试 BLOCKED 必须是 blocked"""
    
    def test_blocked_has_blocked_policy(self, route_registry):
        """BLOCKED 路由必须有 policy=blocked"""
        routes = route_registry.get("routes", {})
        violations = []
        
        for route_id, route in routes.items():
            if route.get("risk_level") == "BLOCKED":
                if route.get("policy") != "blocked":
                    violations.append((route_id, route.get("policy")))
        
        assert not violations, f"BLOCKED 路由 policy 不是 blocked: {violations}"
    
    def test_blocked_has_blocked_field(self, route_registry):
        """BLOCKED 路由必须有 blocked=true"""
        routes = route_registry.get("routes", {})
        violations = []
        
        for route_id, route in routes.items():
            if route.get("risk_level") == "BLOCKED":
                if not route.get("blocked"):
                    violations.append(route_id)
        
        assert not violations, f"BLOCKED 路由 blocked 字段不是 true: {violations}"


class TestValidRiskLevels:
    """测试风险等级有效性"""
    
    def test_all_risk_levels_valid(self, route_registry):
        """所有风险等级必须是有效的"""
        routes = route_registry.get("routes", {})
        invalid = []
        
        for route_id, route in routes.items():
            risk_level = route.get("risk_level", "")
            if risk_level not in VALID_RISK_LEVELS:
                invalid.append((route_id, risk_level))
        
        assert not invalid, f"无效风险等级: {invalid}"


class TestValidPolicies:
    """测试策略有效性"""
    
    def test_all_policies_valid(self, route_registry):
        """所有策略必须是有效的"""
        routes = route_registry.get("routes", {})
        invalid = []
        
        for route_id, route in routes.items():
            policy = route.get("policy", "")
            if policy and policy not in VALID_POLICIES:
                invalid.append((route_id, policy))
        
        assert not invalid, f"无效策略: {invalid}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
