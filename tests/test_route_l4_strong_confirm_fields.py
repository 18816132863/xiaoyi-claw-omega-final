"""
测试 L4 级别 route 的 strong_confirm 字段完整性
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


def test_l4_routes_exist(route_registry):
    """至少有一条 L4 级别 route"""
    routes = route_registry.get("routes", {})
    l4_routes = [r for r in routes.values() if r.get("risk_level") == "L4"]
    assert len(l4_routes) >= 1, "Expected at least 1 L4 route"


def test_l4_complete_field_set(route_registry):
    """L4 route 必须有完整的字段集"""
    routes = route_registry.get("routes", {})
    l4_routes = [(rid, r) for rid, r in routes.items() if r.get("risk_level") == "L4"]
    
    required_fields = [
        "route_id", "capability", "user_intents", "handler",
        "input_schema", "output_schema", "risk_level", "policy",
        "requires_confirmation", "requires_preview", 
        "requires_stepwise_execution", "audit_required", "blocked"
    ]
    
    for route_id, route in l4_routes:
        missing = [f for f in required_fields if f not in route]
        assert len(missing) == 0, f"L4 route {route_id} missing fields: {missing}"


def test_l4_policy_is_strong_confirm(route_registry):
    """L4 policy 必须是 strong_confirm"""
    routes = route_registry.get("routes", {})
    l4_routes = [(rid, r) for rid, r in routes.items() if r.get("risk_level") == "L4"]
    
    for route_id, route in l4_routes:
        assert route.get("policy") == "strong_confirm", \
            f"L4 route {route_id} policy is {route.get('policy')}, expected strong_confirm"


def test_l4_blocked_is_false(route_registry):
    """L4 route 的 blocked 字段必须是 False（不是 BLOCKED 级别）"""
    routes = route_registry.get("routes", {})
    l4_routes = [(rid, r) for rid, r in routes.items() if r.get("risk_level") == "L4"]
    
    for route_id, route in l4_routes:
        assert route.get("blocked") == False, \
            f"L4 route {route_id} has blocked=True, should be False"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
