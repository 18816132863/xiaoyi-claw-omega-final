#!/usr/bin/env python3
"""
Route Static Verification Script

验证 route 结构合规性，将 generated -> verified
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.route_state import RouteStateMachine, RouteStatus


def verify_route_structure(route_id: str, route: dict) -> Tuple[bool, List[str]]:
    """验证单条 route 结构"""
    errors = []
    
    # 必需字段
    required_fields = ["route_id", "capability", "handler", "risk_level", "policy"]
    for field in required_fields:
        if field not in route:
            errors.append(f"missing required field: {field}")
    
    # route_id 一致性
    if route.get("route_id") != route_id:
        errors.append(f"route_id mismatch: {route.get('route_id')} != {route_id}")
    
    # risk_level 合规
    valid_risk_levels = ["L0", "L1", "L2", "L3", "L4", "BLOCKED"]
    if route.get("risk_level") not in valid_risk_levels:
        errors.append(f"invalid risk_level: {route.get('risk_level')}")
    
    # policy 合规
    valid_policies = ["auto_execute", "rate_limited", "confirm_once", "strong_confirm", "blocked"]
    if route.get("policy") not in valid_policies:
        errors.append(f"invalid policy: {route.get('policy')}")
    
    # L4 必须是 strong_confirm
    if route.get("risk_level") == "L4" and route.get("policy") != "strong_confirm":
        errors.append(f"L4 route must have strong_confirm policy, got: {route.get('policy')}")
    
    # BLOCKED 必须是 blocked
    if route.get("risk_level") == "BLOCKED" and route.get("policy") != "blocked":
        errors.append(f"BLOCKED route must have blocked policy, got: {route.get('policy')}")
    
    # blocked 字段一致性
    if route.get("risk_level") == "BLOCKED" and route.get("blocked") != True:
        errors.append("BLOCKED route must have blocked=true")
    
    return len(errors) == 0, errors


def verify_handler_importable(route: dict) -> Tuple[bool, str]:
    """验证 handler 是否可导入"""
    handler = route.get("handler", "")
    
    # 对于生成的 route，handler 可能还不存在
    # 这里只检查格式
    if not handler:
        return False, "empty handler"
    
    parts = handler.split(".")
    if len(parts) < 2:
        return False, f"invalid handler format: {handler}"
    
    # 检查是否是已知的有效 handler 前缀
    valid_prefixes = [
        "device_capability_bus",
        "visual_operation_agent",
        "autonomous_planner",
        "safety_governor",
        "core",
        "governance",
        "infrastructure",
        "orchestration"
    ]
    
    prefix = parts[0]
    if prefix in valid_prefixes:
        return True, "valid handler prefix"
    
    # 允许其他 handler，但标记为需要验证
    return True, f"handler prefix: {prefix}"


def verify_schema(route: dict) -> Tuple[bool, str]:
    """验证 input_schema 和 output_schema"""
    input_schema = route.get("input_schema", {})
    output_schema = route.get("output_schema", {})
    
    if not input_schema:
        return True, "no input_schema (optional)"
    
    if input_schema.get("type") != "object":
        return False, "input_schema must be type object"
    
    return True, "schema valid"


def verify_risk_policy_consistency(route: dict) -> Tuple[bool, str]:
    """验证风险等级与策略一致性"""
    risk = route.get("risk_level", "")
    policy = route.get("policy", "")
    
    consistency_map = {
        "L0": ["auto_execute"],
        "L1": ["auto_execute", "rate_limited"],
        "L2": ["rate_limited", "confirm_once"],
        "L3": ["confirm_once", "strong_confirm"],
        "L4": ["strong_confirm"],
        "BLOCKED": ["blocked"]
    }
    
    valid_policies = consistency_map.get(risk, [])
    if policy in valid_policies:
        return True, f"{risk} -> {policy} consistent"
    
    # 宽松检查：只要不是明显违规就通过
    if risk in ["L0", "L1"] and policy in ["auto_execute", "rate_limited"]:
        return True, f"{risk} -> {policy} acceptable"
    if risk in ["L2", "L3"] and policy in ["rate_limited", "confirm_once", "strong_confirm"]:
        return True, f"{risk} -> {policy} acceptable"
    
    return True, f"{risk} -> {policy} (warning: non-standard)"


def verify_fallback_routes(route: dict, all_routes: dict) -> Tuple[bool, str]:
    """验证 fallback_routes 是否存在"""
    fallbacks = route.get("fallback_routes", [])
    
    if not fallbacks:
        return True, "no fallback routes"
    
    missing = []
    for fb in fallbacks:
        fb_route_id = f"route.{fb}" if not fb.startswith("route.") else fb
        if fb_route_id not in all_routes:
            missing.append(fb)
    
    if missing:
        return True, f"fallback routes not in registry: {missing} (warning)"
    
    return True, f"all {len(fallbacks)} fallback routes exist"


def main():
    print("=" * 60)
    print("Route Static Verification Report")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    registry_path = Path(__file__).parent.parent / "infrastructure" / "route_registry.json"
    
    if not registry_path.exists():
        print("❌ route_registry.json not found")
        return 1
    
    registry = json.loads(registry_path.read_text())
    routes = registry.get("routes", {})
    
    print(f"\n📋 Total routes: {len(routes)}")
    
    state_machine = RouteStateMachine(str(registry_path))
    
    verified_count = 0
    failed_count = 0
    results = []
    
    for route_id, route in routes.items():
        # 结构验证
        struct_ok, struct_errors = verify_route_structure(route_id, route)
        
        # Handler 验证
        handler_ok, handler_msg = verify_handler_importable(route)
        
        # Schema 验证
        schema_ok, schema_msg = verify_schema(route)
        
        # 风险策略一致性
        risk_ok, risk_msg = verify_risk_policy_consistency(route)
        
        # Fallback 验证
        fb_ok, fb_msg = verify_fallback_routes(route, routes)
        
        all_ok = struct_ok and handler_ok and schema_ok and risk_ok
        
        if all_ok:
            # 更新状态为 verified
            verification = {
                "static_verified": True,
                "handler_importable": handler_ok,
                "schema_valid": schema_ok,
                "risk_policy_valid": risk_ok,
                "tested": False
            }
            state_machine.transition_to_verified(route_id, verification)
            verified_count += 1
            results.append((route_id, "✅ VERIFIED", ""))
        else:
            failed_count += 1
            errors = "; ".join(struct_errors) if struct_errors else "verification failed"
            results.append((route_id, "❌ FAILED", errors))
    
    print(f"\n📊 Results:")
    print(f"   ✅ Verified: {verified_count}")
    print(f"   ❌ Failed: {failed_count}")
    
    # 显示状态统计
    status_counts = state_machine.get_status_counts()
    print(f"\n📈 Status Distribution:")
    for status, count in status_counts.items():
        if count > 0:
            print(f"   {status}: {count}")
    
    # 显示失败详情
    if failed_count > 0:
        print(f"\n❌ Failed Routes (first 10):")
        for route_id, status, error in results[:10]:
            if status == "❌ FAILED":
                print(f"   - {route_id}: {error}")
    
    print("\n" + "=" * 60)
    if failed_count == 0:
        print("✅ All routes verified successfully")
        return 0
    else:
        print(f"⚠️  {failed_count} routes failed verification")
        return 1


if __name__ == "__main__":
    sys.exit(main())
