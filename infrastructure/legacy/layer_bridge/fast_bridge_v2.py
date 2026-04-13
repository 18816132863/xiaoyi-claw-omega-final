#!/usr/bin/env python3
"""
高速层间连接器 V2
继承组件基类
"""

import sys
from infrastructure.path_resolver import get_project_root
sys.path.insert(0, str(get_project_root()))

import time
from typing import Dict, Any, Optional, Callable
from functools import lru_cache
from dataclasses import dataclass
from enum import Enum

from infrastructure.component_base import ComponentBase, ComponentStatus

class Layer(Enum):
    L1_CORE = 1
    L2_MEMORY = 2
    L3_ORCHESTRATION = 3
    L4_EXECUTION = 4
    L5_GOVERNANCE = 5
    L6_INFRASTRUCTURE = 6

@dataclass
class LayerCall:
    from_layer: Layer
    to_layer: Layer
    action: str
    latency_ms: float
    cache_hit: bool

class FastBridgeV2(ComponentBase):
    """高速层间连接器 V2"""
    
    @property
    def name(self) -> str:
        return "fast_bridge"
    
    @property
    def version(self) -> str:
        return "2.7.0"
    
    @property
    def layer(self) -> int:
        return 1
    
    def __init__(self):
        super().__init__()
        self._cache: Dict[str, Any] = {}
        self._handlers: Dict[str, Callable] = {}
        self._call_history: list = []
        self._warmup_done = False
        self._direct_routes = {}
    
    def _do_init(self) -> bool:
        """初始化"""
        self._direct_routes = {
            (Layer.L1_CORE, Layer.L2_MEMORY): self._l1_to_l2,
            (Layer.L1_CORE, Layer.L3_ORCHESTRATION): self._l1_to_l3,
            (Layer.L1_CORE, Layer.L4_EXECUTION): self._l1_to_l4,
            (Layer.L2_MEMORY, Layer.L1_CORE): self._l2_to_l1,
            (Layer.L2_MEMORY, Layer.L3_ORCHESTRATION): self._l2_to_l3,
            (Layer.L3_ORCHESTRATION, Layer.L4_EXECUTION): self._l3_to_l4,
            (Layer.L3_ORCHESTRATION, Layer.L2_MEMORY): self._l3_to_l2,
            (Layer.L4_EXECUTION, Layer.L5_GOVERNANCE): self._l4_to_l5,
            (Layer.L4_EXECUTION, Layer.L6_INFRASTRUCTURE): self._l4_to_l6,
            (Layer.L5_GOVERNANCE, Layer.L6_INFRASTRUCTURE): self._l5_to_l6,
            (Layer.L6_INFRASTRUCTURE, Layer.L1_CORE): self._l6_to_l1,
        }
        return True
    
    def _do_shutdown(self) -> bool:
        """关闭"""
        self._cache.clear()
        self._handlers.clear()
        self._call_history.clear()
        return True
    
    def _do_health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "cache": {"status": "ok", "size": len(self._cache)},
            "handlers": {"status": "ok", "count": len(self._handlers)},
            "routes": {"status": "ok", "count": len(self._direct_routes)}
        }
    
    def register_handler(self, layer: Layer, action: str, handler: Callable):
        """注册处理器"""
        key = f"{layer.name}:{action}"
        self._handlers[key] = handler
    
    @lru_cache(maxsize=1000)
    def _get_route(self, from_layer: Layer, to_layer: Layer):
        return self._direct_routes.get((from_layer, to_layer))
    
    def call(self, from_layer: Layer, to_layer: Layer, action: str,
             data: Any = None, use_cache: bool = True) -> Any:
        """高速调用"""
        start = time.perf_counter()
        
        cache_key = f"{to_layer.name}:{action}:{hash(str(data))}"
        if use_cache and cache_key in self._cache:
            latency = (time.perf_counter() - start) * 1000
            self._record_call(from_layer, to_layer, action, latency, True)
            self.record_call(True, latency)
            return self._cache[cache_key]
        
        route = self._get_route(from_layer, to_layer)
        if route:
            result = route(action, data)
        else:
            handler_key = f"{to_layer.name}:{action}"
            handler = self._handlers.get(handler_key)
            result = handler(data) if handler else None
        
        if use_cache and result is not None:
            self._cache[cache_key] = result
        
        latency = (time.perf_counter() - start) * 1000
        self._record_call(from_layer, to_layer, action, latency, False)
        self.record_call(True, latency)
        
        return result
    
    def _record_call(self, from_layer, to_layer, action, latency, cache_hit):
        self._call_history.append(LayerCall(
            from_layer=from_layer,
            to_layer=to_layer,
            action=action,
            latency_ms=latency,
            cache_hit=cache_hit
        ))
        if len(self._call_history) > 1000:
            self._call_history = self._call_history[-1000:]
    
    # 路由实现
    def _l1_to_l2(self, action, data):
        return self._handlers.get("L2_MEMORY:recall", lambda x: x)(data)
    
    def _l1_to_l3(self, action, data):
        return self._handlers.get("L3_ORCHESTRATION:route", lambda x: x)(data)
    
    def _l1_to_l4(self, action, data):
        return self._handlers.get("L4_EXECUTION:execute", lambda x: x)(data)
    
    def _l2_to_l1(self, action, data):
        return self._handlers.get("L1_CORE:update_context", lambda x: x)(data)
    
    def _l2_to_l3(self, action, data):
        return self._handlers.get("L3_ORCHESTRATION:trigger", lambda x: x)(data)
    
    def _l3_to_l4(self, action, data):
        return self._handlers.get("L4_EXECUTION:run", lambda x: x)(data)
    
    def _l3_to_l2(self, action, data):
        return self._handlers.get("L2_MEMORY:query", lambda x: x)(data)
    
    def _l4_to_l5(self, action, data):
        return self._handlers.get("L5_GOVERNANCE:audit", lambda x: x)(data)
    
    def _l4_to_l6(self, action, data):
        return self._handlers.get("L6_INFRASTRUCTURE:log", lambda x: x)(data)
    
    def _l5_to_l6(self, action, data):
        return self._handlers.get("L6_INFRASTRUCTURE:backup", lambda x: x)(data)
    
    def _l6_to_l1(self, action, data):
        return self._handlers.get("L1_CORE:config", lambda x: x)(data)

# 全局实例
_bridge_v2: Optional[FastBridgeV2] = None

def get_bridge_v2() -> FastBridgeV2:
    global _bridge_v2
    if _bridge_v2 is None:
        _bridge_v2 = FastBridgeV2()
        _bridge_v2.init()
    return _bridge_v2
