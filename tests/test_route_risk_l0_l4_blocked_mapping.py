"""
测试 route_registry 风险等级映射 (L0-L4-BLOCKED)
"""
import json
import pytest
from pathlib import Path

ROUTE_REGISTRY_PATH = Path(__file__).parent.parent / "infrastructure" / "route_registry.json"

VALID_RISK_LEVELS = {"L0", "L1", "L2", "L3", "L4", "BLOCKED"}
LEGACY_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "SYSTEM", "CRITICAL"}


@pytest.fixture
def route_registry():
    """加载 route_registry.json"""
    with open(ROUTE_REGISTRY_PATH) as f:
        return json.load(f)


def test_route_registry_exists():
    """route_registry.json 文件存在"""
    assert ROUTE_REGISTRY_PATH.exists(), f"route_registry.json not found at {ROUTE_REGISTRY_PATH}"


def test_routes_count(route_registry):
    """routes 数量为 54 (含 xiaoyi_gui_agent)"""
    routes = route_registry.get("routes", {})
    assert len(routes) == 54, f"Expected 54 routes, got {len(routes)}"


def test_all_risk_levels_valid(route_registry):
    """所有 route 的 risk_level 必须是有效的新口径"""
    routes = route_registry.get("routes", {})
    invalid_routes = []
    
    for route_id, route in routes.items():
        risk_level = route.get("risk_level")
        if risk_level not in VALID_RISK_LEVELS:
            invalid_routes.append((route_id, risk_level))
    
    assert len(invalid_routes) == 0, f"Invalid risk levels found: {invalid_routes}"


def test_no_legacy_risk_levels(route_registry):
    """不允许旧口径风险等级残留"""
    routes = route_registry.get("routes", {})
    legacy_found = []
    
    for route_id, route in routes.items():
        risk_level = route.get("risk_level")
        if risk_level in LEGACY_RISK_LEVELS:
            legacy_found.append((route_id, risk_level))
    
    assert len(legacy_found) == 0, f"Legacy risk levels found: {legacy_found}"


def test_stats_uses_new_risk_levels(route_registry):
    """stats.by_risk_level 必须使用新口径"""
    stats = route_registry.get("stats", {})
    by_risk_level = stats.get("by_risk_level", {})
    
    for level in by_risk_level.keys():
        assert level in VALID_RISK_LEVELS, f"Legacy risk level in stats: {level}"


def test_l4_has_strong_confirm(route_registry):
    """L4 级别必须有 strong_confirm policy"""
    routes = route_registry.get("routes", {})
    l4_routes = [(rid, r) for rid, r in routes.items() if r.get("risk_level") == "L4"]
    
    for route_id, route in l4_routes:
        policy = route.get("policy")
        assert policy == "strong_confirm", f"L4 route {route_id} has policy={policy}, expected strong_confirm"


def test_blocked_has_blocked_policy(route_registry):
    """BLOCKED 级别必须有 blocked policy"""
    routes = route_registry.get("routes", {})
    blocked_routes = [(rid, r) for rid, r in routes.items() if r.get("risk_level") == "BLOCKED"]
    
    for route_id, route in blocked_routes:
        policy = route.get("policy")
        assert policy == "blocked", f"BLOCKED route {route_id} has policy={policy}, expected blocked"


def test_l2_l3_l4_requires_confirmation(route_registry):
    """L2/L3/L4 级别必须 requires_confirmation=True"""
    routes = route_registry.get("routes", {})
    high_risk = [(rid, r) for rid, r in routes.items() 
                 if r.get("risk_level") in {"L2", "L3", "L4"}]
    
    for route_id, route in high_risk:
        requires_conf = route.get("requires_confirmation")
        assert requires_conf == True, f"{route.get('risk_level')} route {route_id} has requires_confirmation={requires_conf}"


def test_l3_l4_requires_preview(route_registry):
    """L3/L4 级别必须 requires_preview=True"""
    routes = route_registry.get("routes", {})
    preview_required = [(rid, r) for rid, r in routes.items() 
                        if r.get("risk_level") in {"L3", "L4"}]
    
    for route_id, route in preview_required:
        requires_preview = route.get("requires_preview")
        assert requires_preview == True, f"{route.get('risk_level')} route {route_id} has requires_preview={requires_preview}"


def test_l4_requires_stepwise_execution(route_registry):
    """L4 级别必须 requires_stepwise_execution=True"""
    routes = route_registry.get("routes", {})
    l4_routes = [(rid, r) for rid, r in routes.items() if r.get("risk_level") == "L4"]
    
    for route_id, route in l4_routes:
        stepwise = route.get("requires_stepwise_execution")
        assert stepwise == True, f"L4 route {route_id} has requires_stepwise_execution={stepwise}"


def test_l2_l3_l4_audit_required(route_registry):
    """L2/L3/L4 级别必须 audit_required=True"""
    routes = route_registry.get("routes", {})
    audit_required = [(rid, r) for rid, r in routes.items() 
                      if r.get("risk_level") in {"L2", "L3", "L4"}]
    
    for route_id, route in audit_required:
        audit = route.get("audit_required")
        assert audit == True, f"{route.get('risk_level')} route {route_id} has audit_required={audit}"


def test_all_routes_have_policy(route_registry):
    """所有 route 必须有 policy 字段"""
    routes = route_registry.get("routes", {})
    missing_policy = []
    
    for route_id, route in routes.items():
        if "policy" not in route:
            missing_policy.append(route_id)
    
    assert len(missing_policy) == 0, f"Routes missing policy: {missing_policy}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
