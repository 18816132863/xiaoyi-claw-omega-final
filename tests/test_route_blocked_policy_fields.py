"""
测试 BLOCKED 级别 route 的字段完整性
"""
import json
import pytest
from pathlib import Path

ROUTE_REGISTRY_PATH = Path(__file__).parent.parent / "infrastructure" / "route_registry.json"


@pytest.fixture
def route_registry():
    """加载 route_registry.json"""
    with open(ROUTE_REGISTRY_PATH) as f:
        return json.load(f)


def test_blocked_policy_is_blocked(route_registry):
    """BLOCKED 级别的 policy 必须是 blocked"""
    routes = route_registry.get("routes", {})
    blocked_routes = [(rid, r) for rid, r in routes.items() if r.get("risk_level") == "BLOCKED"]
    
    for route_id, route in blocked_routes:
        assert route.get("policy") == "blocked", \
            f"BLOCKED route {route_id} policy is {route.get('policy')}, expected blocked"


def test_blocked_field_is_true(route_registry):
    """BLOCKED 级别的 blocked 字段必须是 True"""
    routes = route_registry.get("routes", {})
    blocked_routes = [(rid, r) for rid, r in routes.items() if r.get("risk_level") == "BLOCKED"]
    
    for route_id, route in blocked_routes:
        assert route.get("blocked") == True, \
            f"BLOCKED route {route_id} has blocked=False, should be True"


def test_blocked_complete_field_set(route_registry):
    """BLOCKED route 必须有完整的字段集"""
    routes = route_registry.get("routes", {})
    blocked_routes = [(rid, r) for rid, r in routes.items() if r.get("risk_level") == "BLOCKED"]
    
    required_fields = [
        "route_id", "capability", "user_intents", "handler",
        "input_schema", "output_schema", "risk_level", "policy",
        "requires_confirmation", "requires_preview", 
        "requires_stepwise_execution", "audit_required", "blocked"
    ]
    
    for route_id, route in blocked_routes:
        missing = [f for f in required_fields if f not in route]
        assert len(missing) == 0, f"BLOCKED route {route_id} missing fields: {missing}"


def test_no_blocked_routes_if_none_defined(route_registry):
    """如果没有 BLOCKED routes，stats.by_risk_level.BLOCKED 应该是 0"""
    stats = route_registry.get("stats", {})
    by_risk_level = stats.get("by_risk_level", {})
    
    routes = route_registry.get("routes", {})
    blocked_count = len([r for r in routes.values() if r.get("risk_level") == "BLOCKED"])
    
    assert by_risk_level.get("BLOCKED", 0) == blocked_count, \
        f"Stats BLOCKED count mismatch: stats={by_risk_level.get('BLOCKED')}, actual={blocked_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
