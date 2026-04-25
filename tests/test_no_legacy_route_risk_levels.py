"""
测试确保没有任何旧口径风险等级残留
"""
import json
import pytest
from pathlib import Path

ROUTE_REGISTRY_PATH = Path(__file__).parent.parent / "infrastructure" / "route_registry.json"

LEGACY_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "SYSTEM", "CRITICAL"}


@pytest.fixture
def route_registry():
    """加载 route_registry.json"""
    with open(ROUTE_REGISTRY_PATH) as f:
        return json.load(f)


def test_no_legacy_in_routes(route_registry):
    """routes 中不允许有旧口径风险等级"""
    routes = route_registry.get("routes", {})
    legacy_found = []
    
    for route_id, route in routes.items():
        risk_level = route.get("risk_level", "")
        if risk_level in LEGACY_RISK_LEVELS:
            legacy_found.append((route_id, risk_level))
    
    assert len(legacy_found) == 0, f"Legacy risk levels in routes: {legacy_found}"


def test_no_legacy_in_stats(route_registry):
    """stats.by_risk_level 中不允许有旧口径风险等级"""
    stats = route_registry.get("stats", {})
    by_risk_level = stats.get("by_risk_level", {})
    
    legacy_in_stats = [level for level in by_risk_level.keys() if level in LEGACY_RISK_LEVELS]
    
    assert len(legacy_in_stats) == 0, f"Legacy risk levels in stats: {legacy_in_stats}"


def test_no_legacy_in_any_field(route_registry):
    """整个 route_registry 中不允许有任何旧口径字符串"""
    content = json.dumps(route_registry)
    
    for legacy in LEGACY_RISK_LEVELS:
        # 检查作为独立值出现（避免误判如 "LOWERCASE"）
        if f'"{legacy}"' in content or f"'{legacy}'" in content:
            pytest.fail(f"Found legacy risk level '{legacy}' in route_registry.json")


def test_valid_risk_levels_only(route_registry):
    """所有风险等级必须是有效的新口径"""
    VALID_RISK_LEVELS = {"L0", "L1", "L2", "L3", "L4", "BLOCKED"}
    routes = route_registry.get("routes", {})
    
    invalid = []
    for route_id, route in routes.items():
        risk_level = route.get("risk_level")
        if risk_level not in VALID_RISK_LEVELS:
            invalid.append((route_id, risk_level))
    
    assert len(invalid) == 0, f"Invalid risk levels: {invalid}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
