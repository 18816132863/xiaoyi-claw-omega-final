#!/usr/bin/env python3
"""
组件验证器
V2.7.0 - 2026-04-10

验证组件是否符合规范
"""

import sys
import inspect
from pathlib import Path
from typing import Dict, List, Any

# 使用 path_resolver 获取路径
from pathlib import Path
_workspace = Path(__file__).parent.parent
sys.path.insert(0, str(_workspace))

from infrastructure.component_base import ComponentBase

class ComponentValidator:
    """组件验证器"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, component: ComponentBase) -> Dict[str, Any]:
        """验证组件"""
        self.errors = []
        self.warnings = []
        
        # 1. 验证必须属性
        self._validate_properties(component)
        
        # 2. 验证必须方法
        self._validate_methods(component)
        
        # 3. 验证性能要求
        self._validate_performance(component)
        
        # 4. 验证文档
        self._validate_documentation(component)
        
        return {
            "valid": len(self.errors) == 0,
            "name": getattr(component, 'name', 'unknown'),
            "errors": self.errors,
            "warnings": self.warnings
        }
    
    def _validate_properties(self, component: ComponentBase):
        """验证属性"""
        required_props = ['name', 'version', 'layer']
        
        for prop in required_props:
            if not hasattr(component, prop):
                self.errors.append(f"缺少必须属性: {prop}")
            else:
                value = getattr(component, prop)
                if value is None:
                    self.errors.append(f"属性 {prop} 值为空")
                
                # 验证 layer 范围
                if prop == 'layer':
                    if not (1 <= value <= 6):
                        self.errors.append(f"layer 值 {value} 不在 1-6 范围内")
    
    def _validate_methods(self, component: ComponentBase):
        """验证方法"""
        required_methods = [
            'init', 'shutdown', 'health_check', 
            'get_stats', '_do_init', '_do_shutdown', '_do_health_check'
        ]
        
        for method in required_methods:
            if not hasattr(component, method):
                self.errors.append(f"缺少必须方法: {method}")
            elif not callable(getattr(component, method)):
                self.errors.append(f"{method} 不是可调用方法")
    
    def _validate_performance(self, component: ComponentBase):
        """验证性能"""
        stats = component.get_stats()
        
        # 检查延迟
        layer = getattr(component, 'layer', 0)
        latency_limits = {
            1: 0.01,  # L1: <0.01ms
            2: 0.01,  # L2: <0.01ms
            3: 0.1,   # L3: <0.1ms
            4: 1.0,   # L4: <1ms
            5: 10.0,  # L5: <10ms
            6: 5.0,   # L6: <5ms
        }
        
        max_latency = latency_limits.get(layer, 10.0)
        avg_latency = stats.get('avg_latency_ms', 0)
        
        if avg_latency > max_latency:
            self.warnings.append(
                f"平均延迟 {avg_latency}ms 超过层级 {layer} 要求 {max_latency}ms"
            )
    
    def _validate_documentation(self, component: ComponentBase):
        """验证文档"""
        # 检查类文档
        if not component.__class__.__doc__:
            self.warnings.append("缺少类文档字符串")
        
        # 检查方法文档
        for method in ['init', 'shutdown', 'health_check', 'get_stats']:
            method_obj = getattr(component.__class__, method, None)
            if method_obj and not method_obj.__doc__:
                self.warnings.append(f"方法 {method} 缺少文档字符串")


def validate_all_components():
    """验证所有组件"""
    from infrastructure.component_base import get_registry
    from infrastructure.performance import (
        get_bridge, get_zero_copy, get_layer_cache,
        get_optimizer, get_monitor, get_router
    )
    
    # 注册组件
    registry = get_registry()
    
    # 包装现有组件
    class BridgeWrapper(ComponentBase):
        @property
        def name(self): return "fast_bridge"
        @property
        def version(self): return "2.7.0"
        @property
        def layer(self): return 1
        def _do_init(self): return True
        def _do_shutdown(self): return True
        def _do_health_check(self): return {"status": "ok"}
    
    registry.register(BridgeWrapper())
    
    # 验证
    validator = ComponentValidator()
    results = []
    
    for name, component in registry.get_all().items():
        result = validator.validate(component)
        results.append(result)
    
    return results


if __name__ == "__main__":
    print("\n" + "="*50)
    print("组件验证器")
    print("="*50 + "\n")
    
    results = validate_all_components()
    
    for r in results:
        status = "✓" if r["valid"] else "✗"
        print(f"{status} {r['name']}")
        
        if r["errors"]:
            for e in r["errors"]:
                print(f"  ❌ {e}")
        
        if r["warnings"]:
            for w in r["warnings"]:
                print(f"  ⚠️  {w}")
    
    print("\n" + "="*50)
    valid_count = sum(1 for r in results if r["valid"])
    print(f"验证完成: {valid_count}/{len(results)} 通过")
    print("="*50)
