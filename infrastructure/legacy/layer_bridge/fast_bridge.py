#!/usr/bin/env python3
"""
六层架构高速连接器
V2.7.0 - 2026-04-10
实现层间零延迟调用
"""

import time
import json
from typing import Dict, Any, Optional, Callable
from functools import lru_cache, wraps
from dataclasses import dataclass
from enum import Enum

class Layer(Enum):
    L1_CORE = 1
    L2_MEMORY = 2
    L3_ORCHESTRATION = 3
    L4_EXECUTION = 4
    L5_GOVERNANCE = 5
    L6_INFRASTRUCTURE = 6

@dataclass
class LayerCall:
    """层间调用记录"""
    from_layer: Layer
    to_layer: Layer
    action: str
    latency_ms: float
    cache_hit: bool

class FastBridge:
    """高速层间连接器"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._handlers: Dict[str, Callable] = {}
        self._call_history: list = []
        self._warmup_done = False
        
        # 层间直连路由表
        self._direct_routes = {
            # L1 -> 其他层
            (Layer.L1_CORE, Layer.L2_MEMORY): self._l1_to_l2,
            (Layer.L1_CORE, Layer.L3_ORCHESTRATION): self._l1_to_l3,
            (Layer.L1_CORE, Layer.L4_EXECUTION): self._l1_to_l4,
            
            # L2 -> 其他层
            (Layer.L2_MEMORY, Layer.L1_CORE): self._l2_to_l1,
            (Layer.L2_MEMORY, Layer.L3_ORCHESTRATION): self._l2_to_l3,
            
            # L3 -> 其他层
            (Layer.L3_ORCHESTRATION, Layer.L4_EXECUTION): self._l3_to_l4,
            (Layer.L3_ORCHESTRATION, Layer.L2_MEMORY): self._l3_to_l2,
            
            # L4 -> 其他层
            (Layer.L4_EXECUTION, Layer.L5_GOVERNANCE): self._l4_to_l5,
            (Layer.L4_EXECUTION, Layer.L6_INFRASTRUCTURE): self._l4_to_l6,
            
            # L5 -> 其他层
            (Layer.L5_GOVERNANCE, Layer.L6_INFRASTRUCTURE): self._l5_to_l6,
            
            # L6 -> 其他层
            (Layer.L6_INFRASTRUCTURE, Layer.L1_CORE): self._l6_to_l1,
        }
    
    def register_handler(self, layer: Layer, action: str, handler: Callable):
        """注册层处理器"""
        key = f"{layer.name}:{action}"
        self._handlers[key] = handler
    
    @lru_cache(maxsize=1000)
    def _get_route(self, from_layer: Layer, to_layer: Layer) -> Optional[Callable]:
        """获取直连路由（带缓存）"""
        return self._direct_routes.get((from_layer, to_layer))
    
    def call(self, from_layer: Layer, to_layer: Layer, action: str, 
             data: Any = None, use_cache: bool = True) -> Any:
        """高速层间调用"""
        start = time.perf_counter()
        
        # 1. 检查缓存
        cache_key = f"{to_layer.name}:{action}:{hash(str(data))}"
        if use_cache and cache_key in self._cache:
            latency = (time.perf_counter() - start) * 1000
            self._record_call(from_layer, to_layer, action, latency, True)
            return self._cache[cache_key]
        
        # 2. 获取直连路由
        route = self._get_route(from_layer, to_layer)
        if route:
            result = route(action, data)
        else:
            # 3. 使用通用处理器
            handler_key = f"{to_layer.name}:{action}"
            handler = self._handlers.get(handler_key)
            if handler:
                result = handler(data)
            else:
                result = None
        
        # 4. 缓存结果
        if use_cache and result is not None:
            self._cache[cache_key] = result
        
        latency = (time.perf_counter() - start) * 1000
        self._record_call(from_layer, to_layer, action, latency, False)
        
        return result
    
    def _record_call(self, from_layer: Layer, to_layer: Layer, 
                     action: str, latency: float, cache_hit: bool):
        """记录调用"""
        self._call_history.append(LayerCall(
            from_layer=from_layer,
            to_layer=to_layer,
            action=action,
            latency_ms=latency,
            cache_hit=cache_hit
        ))
        
        # 只保留最近1000条
        if len(self._call_history) > 1000:
            self._call_history = self._call_history[-1000:]
    
    def get_stats(self) -> Dict:
        """获取调用统计"""
        if not self._call_history:
            return {"total": 0, "avg_latency_ms": 0, "cache_hit_rate": 0}
        
        total = len(self._call_history)
        cache_hits = sum(1 for c in self._call_history if c.cache_hit)
        avg_latency = sum(c.latency_ms for c in self._call_history) / total
        
        return {
            "total": total,
            "avg_latency_ms": round(avg_latency, 3),
            "cache_hit_rate": round(cache_hits / total, 3),
            "cache_size": len(self._cache)
        }
    
    # === 直连路由实现 ===
    
    def _l1_to_l2(self, action: str, data: Any) -> Any:
        """L1 -> L2: 核心层访问记忆"""
        if action == "recall":
            return self._handlers.get("L2_MEMORY:recall", lambda x: x)(data)
        elif action == "store":
            return self._handlers.get("L2_MEMORY:store", lambda x: x)(data)
        return None
    
    def _l1_to_l3(self, action: str, data: Any) -> Any:
        """L1 -> L3: 核心层调度任务"""
        if action == "route":
            return self._handlers.get("L3_ORCHESTRATION:route", lambda x: x)(data)
        return None
    
    def _l1_to_l4(self, action: str, data: Any) -> Any:
        """L1 -> L4: 核心层直接执行"""
        if action == "execute":
            return self._handlers.get("L4_EXECUTION:execute", lambda x: x)(data)
        return None
    
    def _l2_to_l1(self, action: str, data: Any) -> Any:
        """L2 -> L1: 记忆层更新核心状态"""
        if action == "update_context":
            return self._handlers.get("L1_CORE:update_context", lambda x: x)(data)
        return None
    
    def _l2_to_l3(self, action: str, data: Any) -> Any:
        """L2 -> L3: 记忆层触发编排"""
        if action == "trigger":
            return self._handlers.get("L3_ORCHESTRATION:trigger", lambda x: x)(data)
        return None
    
    def _l3_to_l4(self, action: str, data: Any) -> Any:
        """L3 -> L4: 编排层执行任务"""
        if action == "run":
            return self._handlers.get("L4_EXECUTION:run", lambda x: x)(data)
        return None
    
    def _l3_to_l2(self, action: str, data: Any) -> Any:
        """L3 -> L2: 编排层查询记忆"""
        if action == "query":
            return self._handlers.get("L2_MEMORY:query", lambda x: x)(data)
        return None
    
    def _l4_to_l5(self, action: str, data: Any) -> Any:
        """L4 -> L5: 执行层审计"""
        if action == "audit":
            return self._handlers.get("L5_GOVERNANCE:audit", lambda x: x)(data)
        return None
    
    def _l4_to_l6(self, action: str, data: Any) -> Any:
        """L4 -> L6: 执行层访问基础设施"""
        if action == "log":
            return self._handlers.get("L6_INFRASTRUCTURE:log", lambda x: x)(data)
        elif action == "monitor":
            return self._handlers.get("L6_INFRASTRUCTURE:monitor", lambda x: x)(data)
        return None
    
    def _l5_to_l6(self, action: str, data: Any) -> Any:
        """L5 -> L6: 治理层运维"""
        if action == "backup":
            return self._handlers.get("L6_INFRASTRUCTURE:backup", lambda x: x)(data)
        elif action == "alert":
            return self._handlers.get("L6_INFRASTRUCTURE:alert", lambda x: x)(data)
        return None
    
    def _l6_to_l1(self, action: str, data: Any) -> Any:
        """L6 -> L1: 基础设施层更新核心配置"""
        if action == "config":
            return self._handlers.get("L1_CORE:config", lambda x: x)(data)
        return None
    
    def warmup(self):
        """预热缓存"""
        if self._warmup_done:
            return
        
        # 预加载常用路由
        for route_key in self._direct_routes:
            self._get_route(*route_key)
        
        self._warmup_done = True
    
    def clear_cache(self):
        """清理缓存"""
        self._cache.clear()
        self._get_route.cache_clear()

# 全局单例
_bridge: Optional[FastBridge] = None

def get_bridge() -> FastBridge:
    """获取全局桥接器"""
    global _bridge
    if _bridge is None:
        _bridge = FastBridge()
        _bridge.warmup()
    return _bridge

def fast_call(from_layer: Layer, to_layer: Layer, action: str, data: Any = None) -> Any:
    """快速层间调用（便捷函数）"""
    return get_bridge().call(from_layer, to_layer, action, data)
