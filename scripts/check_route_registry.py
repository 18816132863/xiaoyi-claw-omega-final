#!/usr/bin/env python3
"""
路由注册表检查器
验证 route_registry.json 的完整性和正确性
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime


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
        
        # 7. 风险策略检查
        self._check_risk_policy(registry)
        
        return len(self.errors) == 0
    
    def _check_structure(self, registry: Dict):
        """检查基本结构"""
        required_fields = ["version", "updated", "routes", "intent_index", "stats"]
        
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
            "input_schema", "output_schema", "risk_level",
            "requires_confirmation", "fallback_routes"
        ]
        
        for route_id, route in routes.items():
            # 检查必需字段
            for field in required_route_fields:
                if field not in route:
                    self.errors.append(f"路由 {route_id} 缺少字段: {field}")
            
            # 检查 route_id 一致性
            if route.get("route_id") != route_id:
                self.errors.append(f"路由 ID 不一致: {route_id} vs {route.get('route_id')}")
            
            # 检查风险等级有效性
            valid_risk_levels = ["LOW", "MEDIUM", "HIGH", "SYSTEM"]
            if route.get("risk_level") not in valid_risk_levels:
                self.errors.append(f"路由 {route_id} 无效风险等级: {route.get('risk_level')}")
            
            # 检查高风险路由是否需要确认
            if route.get("risk_level") in ["HIGH", "SYSTEM"] and not route.get("requires_confirmation"):
                self.warnings.append(f"路由 {route_id} 高风险但未设置 requires_confirmation")
    
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
    
    def _check_risk_policy(self, registry: Dict):
        """检查风险策略"""
        routes = registry.get("routes", {})
        stats = registry.get("stats", {})
        
        # 统计实际的风险等级分布
        actual_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "SYSTEM": 0}
        for route in routes.values():
            risk = route.get("risk_level", "LOW")
            if risk in actual_counts:
                actual_counts[risk] += 1
        
        # 与 stats 对比
        recorded_counts = stats.get("by_risk_level", {})
        for level in ["LOW", "MEDIUM", "HIGH", "SYSTEM"]:
            if actual_counts[level] != recorded_counts.get(level, 0):
                self.warnings.append(
                    f"风险等级统计不一致 {level}: "
                    f"实际 {actual_counts[level]} vs 记录 {recorded_counts.get(level, 0)}"
                )
    
    def print_report(self):
        """打印检查报告"""
        print("\n" + "=" * 60)
        print("路由注册表检查报告")
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
