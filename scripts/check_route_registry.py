#!/usr/bin/env python3
"""
路由注册表检查器 V2.0
验证 route_registry.json 的完整性和正确性
支持新风险体系: L0/L1/L2/L3/L4/BLOCKED
使用与 safety_governor 一致的策略名
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime


# 正式风险等级 (来自 safety_governor/risk_levels.py)
VALID_RISK_LEVELS = {"L0", "L1", "L2", "L3", "L4", "BLOCKED"}

# 旧风险等级 (不允许残留)
LEGACY_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "SYSTEM", "CRITICAL"}

# 有效策略 (来自 safety_governor/risk_levels.py RiskPolicy)
VALID_POLICIES = {
    "auto_execute",  # 自动执行 (L0, L1)
    "rate_limited",  # 限流执行 (L2)
    "confirm_once",  # 单次确认 (L3)
    "strong_confirm",  # 强确认 (L4)
    "blocked",  # 拒绝执行 (BLOCKED)
}


class RouteRegistryChecker:
    """路由注册表检查器"""
    
    def __init__(self, registry_path: str):
        self.registry_path = Path(registry_path)
        self.errors = []
        self.warnings = []
        self.info = []
        
    def load_registry(self) -> Dict:
        """加载路由注册表"""
        if not self.registry_path.exists():
            self.errors.append(f"路由注册表不存在: {self.registry_path}")
            return {}
        
        with open(self.registry_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def check_all(self) -> bool:
        """执行所有检查"""
        registry = self.load_registry()
        
        if not registry:
            return False
        
        # 1. 基本结构检查
        self._check_structure(registry)
        
        # 2. 路由完整性检查
        self._check_routes(registry)
        
        # 3. 意图索引检查
        self._check_intent_index(registry)
        
        # 4. Handler 可达性检查
        self._check_handlers(registry)
        
        # 5. Fallback 路由检查
        self._check_fallbacks(registry)
        
        # 6. Schema 检查
        self._check_schemas(registry)
        
        # 7. 风险策略检查 (新)
        self._check_risk_policy_v2(registry)
        
        # 8. 旧风险等级残留检查 (新)
        self._check_no_legacy_risk_levels(registry)
        
        # 9. L4 强确认字段检查 (新)
        self._check_l4_strong_confirm_fields(registry)
        
        # 10. BLOCKED 策略字段检查 (新)
        self._check_blocked_policy_fields(registry)
        
        # 11. 真源唯一性检查 (新)
        self._check_single_source_of_truth(registry)
        
        return len(self.errors) == 0
    
    def _check_structure(self, registry: Dict):
        """检查基本结构"""
        required_fields = ["version", "updated", "routes"]
        
        for field in required_fields:
            if field not in registry:
                self.errors.append(f"缺少必需字段: {field}")
        
        if "routes" in registry and not registry["routes"]:
            self.errors.append("routes 不能为空")
    
    def _check_routes(self, registry: Dict):
        """检查路由完整性"""
        routes = registry.get("routes", {})
        
        required_route_fields = [
            "route_id", "capability", "user_intents", "handler",
            "input_schema", "output_schema", "risk_level", "policy",
            "requires_confirmation", "requires_preview", 
            "requires_stepwise_execution", "audit_required", "blocked",
            "fallback_routes"
        ]
        
        for route_id, route in routes.items():
            # 检查必需字段
            for field in required_route_fields:
                if field not in route:
                    self.errors.append(f"路由 {route_id} 缺少字段: {field}")
            
            # 检查 route_id 一致性
            if route.get("route_id") != route_id:
                self.errors.append(f"路由 ID 不一致: {route_id} vs {route.get('route_id')}")
    
    def _check_intent_index(self, registry: Dict):
        """检查意图索引"""
        intent_index = registry.get("intent_index", {})
        routes = registry.get("routes", {})
        
        # 检查索引中的路由是否存在
        for intent, route_ids in intent_index.items():
            for route_id in route_ids:
                if route_id not in routes:
                    self.errors.append(f"意图索引中的路由不存在: {intent} -> {route_id}")
        
        # 检查路由的意图是否都在索引中
        for route_id, route in routes.items():
            for intent in route.get("user_intents", []):
                if intent not in intent_index:
                    self.warnings.append(f"路由 {route_id} 的意图未在索引中: {intent}")
                elif route_id not in intent_index.get(intent, []):
                    self.errors.append(f"意图索引不一致: {intent} 应包含 {route_id}")
    
    def _check_handlers(self, registry: Dict):
        """检查 Handler 可达性"""
        routes = registry.get("routes", {})
        
        for route_id, route in routes.items():
            handler = route.get("handler", "")
            
            # 检查 handler 格式
            if not handler:
                self.errors.append(f"路由 {route_id} handler 为空")
                continue
            
            # 检查 handler 格式 (module.path.function)
            parts = handler.split(".")
            if len(parts) < 2:
                self.warnings.append(f"路由 {route_id} handler 格式可能不正确: {handler}")
            
            # 检查 handler 文件是否存在 (简化检查)
            module_path = "/".join(parts[:-1]) + ".py"
            workspace_root = Path(__file__).parent.parent
            handler_file = workspace_root / module_path
            
            if not handler_file.exists():
                self.info.append(f"路由 {route_id} handler 文件不存在: {handler_file}")
    
    def _check_fallbacks(self, registry: Dict):
        """检查 Fallback 路由"""
        routes = registry.get("routes", {})
        
        for route_id, route in routes.items():
            fallbacks = route.get("fallback_routes", [])
            
            for fallback in fallbacks:
                # 检查 fallback 是否是有效的 capability
                fallback_route_id = f"route.{fallback}"
                if fallback_route_id not in routes:
                    self.warnings.append(f"路由 {route_id} 的 fallback 不存在: {fallback}")
    
    def _check_schemas(self, registry: Dict):
        """检查 Schema"""
        routes = registry.get("routes", {})
        
        for route_id, route in routes.items():
            input_schema = route.get("input_schema", {})
            output_schema = route.get("output_schema", {})
            
            # 检查 input schema 结构
            if "type" not in input_schema:
                self.warnings.append(f"路由 {route_id} input_schema 缺少 type")
            if "properties" not in input_schema:
                self.warnings.append(f"路由 {route_id} input_schema 缺少 properties")
            
            # 检查 output schema 结构
            if "type" not in output_schema:
                self.warnings.append(f"路由 {route_id} output_schema 缺少 type")
            if "properties" not in output_schema:
                self.warnings.append(f"路由 {route_id} output_schema 缺少 properties")
    
    def _check_risk_policy_v2(self, registry: Dict):
        """检查风险策略 V2 (新风险体系)"""
        routes = registry.get("routes", {})
        
        for route_id, route in routes.items():
            risk_level = route.get("risk_level", "")
            policy = route.get("policy", "")
            
            # 检查风险等级有效性
            if risk_level not in VALID_RISK_LEVELS:
                self.errors.append(
                    f"路由 {route_id} 无效风险等级: {risk_level} "
                    f"(必须是 L0/L1/L2/L3/L4/BLOCKED)"
                )
            
            # 检查策略有效性
            if policy not in VALID_POLICIES:
                self.errors.append(
                    f"路由 {route_id} 无效策略: {policy} "
                    f"(必须是 auto_execute/rate_limited/confirm_once/strong_confirm/blocked)"
                )
            
            # 检查风险等级与策略的一致性
            expected_policy = {
                "L0": "auto_execute",
                "L1": "auto_execute",
                "L2": "rate_limited",
                "L3": "confirm_once",
                "L4": "strong_confirm",
                "BLOCKED": "blocked",
            }
            
            if risk_level in expected_policy:
                if policy != expected_policy[risk_level]:
                    self.warnings.append(
                        f"路由 {route_id} 风险等级 {risk_level} 通常应使用策略 {expected_policy[risk_level]}, "
                        f"当前为 {policy}"
                    )
    
    def _check_no_legacy_risk_levels(self, registry: Dict):
        """检查是否有旧风险等级残留"""
        routes = registry.get("routes", {})
        
        # 检查单条路由
        for route_id, route in routes.items():
            risk_level = route.get("risk_level", "")
            
            if risk_level in LEGACY_RISK_LEVELS:
                self.errors.append(
                    f"路由 {route_id} 使用旧风险等级: {risk_level} "
                    f"(必须更新为 L0/L1/L2/L3/L4/BLOCKED)"
                )
        
        # 检查 stats.by_risk_level
        stats = registry.get("stats", {})
        by_risk_level = stats.get("by_risk_level", {})
        
        for legacy_level in LEGACY_RISK_LEVELS:
            if legacy_level in by_risk_level:
                self.errors.append(
                    f"stats.by_risk_level 包含旧风险等级: {legacy_level} "
                    f"(必须更新为 L0/L1/L2/L3/L4/BLOCKED)"
                )
    
    def _check_l4_strong_confirm_fields(self, registry: Dict):
        """检查 L4 路由是否有强确认字段"""
        routes = registry.get("routes", {})
        
        for route_id, route in routes.items():
            risk_level = route.get("risk_level", "")
            
            if risk_level == "L4":
                # L4 必须有 policy = strong_confirm
                if route.get("policy") != "strong_confirm":
                    self.errors.append(
                        f"路由 {route_id} 是 L4 但 policy 不是 strong_confirm"
                    )
                
                # L4 必须有 requires_preview = true
                if not route.get("requires_preview"):
                    self.errors.append(
                        f"路由 {route_id} 是 L4 但 requires_preview 不是 true"
                    )
                
                # L4 必须有 requires_stepwise_execution = true
                if not route.get("requires_stepwise_execution"):
                    self.errors.append(
                        f"路由 {route_id} 是 L4 但 requires_stepwise_execution 不是 true"
                    )
                
                # L4 必须有 audit_required = true
                if not route.get("audit_required"):
                    self.errors.append(
                        f"路由 {route_id} 是 L4 但 audit_required 不是 true"
                    )
    
    def _check_blocked_policy_fields(self, registry: Dict):
        """检查 BLOCKED 路由是否有正确的字段"""
        routes = registry.get("routes", {})
        
        for route_id, route in routes.items():
            risk_level = route.get("risk_level", "")
            
            if risk_level == "BLOCKED":
                # BLOCKED 必须有 policy = blocked
                if route.get("policy") != "blocked":
                    self.errors.append(
                        f"路由 {route_id} 是 BLOCKED 但 policy 不是 blocked"
                    )
                
                # BLOCKED 必须有 blocked = true
                if not route.get("blocked"):
                    self.errors.append(
                        f"路由 {route_id} 是 BLOCKED 但 blocked 不是 true"
                    )
    
    def _check_single_source_of_truth(self, registry: Dict):
        """检查路由注册表真源唯一性"""
        workspace_root = Path(__file__).parent.parent
        main_registry = workspace_root / "infrastructure" / "route_registry.json"
        inventory_registry = workspace_root / "infrastructure" / "inventory" / "route_registry.json"
        
        # 如果 inventory/route_registry.json 存在且非空，检查是否与主注册表同步
        if inventory_registry.exists():
            try:
                with open(inventory_registry, "r", encoding="utf-8") as f:
                    inv_registry = json.load(f)
                
                inv_routes = inv_registry.get("routes", {})
                main_routes = registry.get("routes", {})
                
                if inv_routes and inv_routes != main_routes:
                    self.warnings.append(
                        "存在两个不同的 route_registry.json，建议删除 inventory/route_registry.json"
                    )
            except Exception as e:
                self.warnings.append(f"无法检查 inventory/route_registry.json: {e}")
    
    def print_report(self):
        """打印检查报告"""
        print("\n" + "=" * 60)
        print("路由注册表检查报告 V2.0")
        print("=" * 60)
        
        print(f"\n📋 检查结果:")
        print(f"   ❌ 错误: {len(self.errors)}")
        print(f"   ⚠️  警告: {len(self.warnings)}")
        print(f"   ℹ️  信息: {len(self.info)}")
        
        if self.errors:
            print(f"\n❌ 错误详情:")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print(f"\n⚠️  警告详情:")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if self.info:
            print(f"\nℹ️  信息详情 (前10条):")
            for info in self.info[:10]:
                print(f"   - {info}")
        
        print("\n" + "=" * 60)
        
        if not self.errors:
            print("✅ 路由注册表检查通过")
            return True
        else:
            print("❌ 路由注册表检查失败")
            return False


def main():
    """主函数"""
    registry_path = Path(__file__).parent.parent / "infrastructure" / "route_registry.json"
    
    checker = RouteRegistryChecker(str(registry_path))
    checker.check_all()
    success = checker.print_report()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
