"""
测试 route_registry 与 safety_governor 风险等级定义的一致性
"""
import json
import pytest
import sys
from pathlib import Path

ROUTE_REGISTRY_PATH = Path(__file__).parent.parent / "infrastructure" / "route_registry.json"
SAFETY_GOVERNOR_PATH = Path(__file__).parent.parent / "safety_governor" / "risk_levels.py"


@pytest.fixture
def route_registry():
    """加载 route_registry.json"""
    with open(ROUTE_REGISTRY_PATH) as f:
        return json.load(f)


@pytest.fixture
def safety_governor_risk_levels():
    """从 safety_governor 加载风险等级定义"""
    # 动态导入 safety_governor.risk_levels
    sys.path.insert(0, str(SAFETY_GOVERNOR_PATH.parent.parent))
    from safety_governor.risk_levels import RiskLevel, RiskPolicy, RISK_POLICY_MAP
    
    return {
        "risk_levels": [level.value for level in RiskLevel],
        "policies": [policy.value for policy in RiskPolicy],
        "policy_map": {k.value: v.value for k, v in RISK_POLICY_MAP.items()}
    }


def test_route_risk_levels_match_safety_governor(route_registry, safety_governor_risk_levels):
    """route_registry 使用的风险等级必须与 safety_governor 定义一致"""
    valid_levels = set(safety_governor_risk_levels["risk_levels"])
    routes = route_registry.get("routes", {})
    
    mismatch = []
    for route_id, route in routes.items():
        risk_level = route.get("risk_level")
        if risk_level not in valid_levels:
            mismatch.append((route_id, risk_level))
    
    assert len(mismatch) == 0, f"Risk levels not in safety_governor: {mismatch}"


def test_route_policies_match_safety_governor(route_registry, safety_governor_risk_levels):
    """route_registry 使用的 policy 必须与 safety_governor 定义一致"""
    valid_policies = set(safety_governor_risk_levels["policies"])
    routes = route_registry.get("routes", {})
    
    mismatch = []
    for route_id, route in routes.items():
        policy = route.get("policy")
        if policy and policy not in valid_policies:
            mismatch.append((route_id, policy))
    
    assert len(mismatch) == 0, f"Policies not in safety_governor: {mismatch}"


def test_l4_policy_is_strong_confirm_per_safety_governor(route_registry, safety_governor_risk_levels):
    """L4 的 policy 必须符合 safety_governor 的 RISK_POLICY_MAP"""
    policy_map = safety_governor_risk_levels["policy_map"]
    
    # 从 policy_map 找 L4 对应的 policy
    l4_expected_policy = policy_map.get("L4")
    
    routes = route_registry.get("routes", {})
    l4_routes = [(rid, r) for rid, r in routes.items() if r.get("risk_level") == "L4"]
    
    for route_id, route in l4_routes:
        assert route.get("policy") == l4_expected_policy, \
            f"L4 route {route_id} policy={route.get('policy')}, expected {l4_expected_policy}"


def test_blocked_policy_is_blocked_per_safety_governor(route_registry, safety_governor_risk_levels):
    """BLOCKED 的 policy 必须符合 safety_governor 的 RISK_POLICY_MAP"""
    policy_map = safety_governor_risk_levels["policy_map"]
    blocked_expected_policy = policy_map.get("BLOCKED")
    
    routes = route_registry.get("routes", {})
    blocked_routes = [(rid, r) for rid, r in routes.items() if r.get("risk_level") == "BLOCKED"]
    
    for route_id, route in blocked_routes:
        assert route.get("policy") == blocked_expected_policy, \
            f"BLOCKED route {route_id} policy={route.get('policy')}, expected {blocked_expected_policy}"


def test_stats_risk_levels_match_safety_governor(route_registry, safety_governor_risk_levels):
    """stats.by_risk_level 的 key 必须与 safety_governor 定义一致"""
    valid_levels = set(safety_governor_risk_levels["risk_levels"])
    stats = route_registry.get("stats", {})
    by_risk_level = stats.get("by_risk_level", {})
    
    invalid_keys = [k for k in by_risk_level.keys() if k not in valid_levels]
    
    assert len(invalid_keys) == 0, f"Invalid keys in stats.by_risk_level: {invalid_keys}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
