#!/usr/bin/env python3
"""
组件基类
V2.7.0 - 2026-04-10

所有组件必须继承此基类
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class ComponentStatus(Enum):
    """组件状态"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class ComponentStats:
    """组件统计"""
    calls_total: int = 0
    calls_success: int = 0
    calls_failed: int = 0
    total_latency_ms: float = 0.0
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    last_call_time: float = 0.0
    errors: list = field(default_factory=list)

class ComponentBase(ABC):
    """组件基类"""
    
    def __init__(self):
        self._status = ComponentStatus.UNINITIALIZED
        self._stats = ComponentStats()
        self._start_time: Optional[float] = None
        self._config: Dict[str, Any] = {}
    
    @property
    @abstractmethod
    def name(self) -> str:
        """组件名称"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """组件版本"""
        pass
    
    @property
    @abstractmethod
    def layer(self) -> int:
        """归属层级 (1-6)"""
        pass
    
    @property
    def status(self) -> ComponentStatus:
        """组件状态"""
        return self._status
    
    @property
    def uptime_seconds(self) -> float:
        """运行时间"""
        if self._start_time:
            return time.time() - self._start_time
        return 0
    
    def configure(self, config: Dict[str, Any]):
        """配置组件"""
        self._config = config
    
    def init(self) -> bool:
        """初始化"""
        if self._status != ComponentStatus.UNINITIALIZED:
            return False
        
        self._status = ComponentStatus.INITIALIZING
        
        try:
            result = self._do_init()
            if result:
                self._status = ComponentStatus.ACTIVE
                self._start_time = time.time()
            else:
                self._status = ComponentStatus.ERROR
            return result
        except Exception as e:
            self._status = ComponentStatus.ERROR
            self._record_error(str(e))
            return False
    
    def shutdown(self) -> bool:
        """关闭"""
        if self._status == ComponentStatus.STOPPED:
            return True
        
        self._status = ComponentStatus.STOPPING
        
        try:
            result = self._do_shutdown()
            self._status = ComponentStatus.STOPPED
            return result
        except Exception as e:
            self._status = ComponentStatus.ERROR
            self._record_error(str(e))
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        checks = self._do_health_check()
        
        all_healthy = all(
            c.get("status") == "ok" for c in checks.values()
        )
        
        return {
            "healthy": all_healthy,
            "status": self._status.value,
            "uptime_seconds": round(self.uptime_seconds, 1),
            "checks": checks
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        stats = {
            "name": self.name,
            "version": self.version,
            "layer": self.layer,
            "status": self._status.value,
            "uptime_seconds": round(self.uptime_seconds, 1),
            "calls_total": self._stats.calls_total,
            "calls_success": self._stats.calls_success,
            "calls_failed": self._stats.calls_failed,
            "success_rate": self._get_success_rate(),
            "avg_latency_ms": self._get_avg_latency(),
            "memory_mb": round(self._stats.memory_mb, 1),
            "cpu_percent": round(self._stats.cpu_percent, 1),
        }
        
        return stats
    
    def record_call(self, success: bool, latency_ms: float):
        """记录调用"""
        self._stats.calls_total += 1
        self._stats.total_latency_ms += latency_ms
        self._stats.last_call_time = time.time()
        
        if success:
            self._stats.calls_success += 1
        else:
            self._stats.calls_failed += 1
    
    def _record_error(self, error: str):
        """记录错误"""
        self._stats.errors.append({
            "time": time.time(),
            "error": error
        })
        
        # 只保留最近100条
        if len(self._stats.errors) > 100:
            self._stats.errors = self._stats.errors[-100:]
    
    def _get_success_rate(self) -> float:
        """获取成功率"""
        if self._stats.calls_total == 0:
            return 1.0
        return self._stats.calls_success / self._stats.calls_total
    
    def _get_avg_latency(self) -> float:
        """获取平均延迟"""
        if self._stats.calls_total == 0:
            return 0.0
        return self._stats.total_latency_ms / self._stats.calls_total
    
    @abstractmethod
    def _do_init(self) -> bool:
        """实际初始化逻辑"""
        pass
    
    @abstractmethod
    def _do_shutdown(self) -> bool:
        """实际关闭逻辑"""
        pass
    
    @abstractmethod
    def _do_health_check(self) -> Dict[str, Any]:
        """实际健康检查逻辑"""
        pass


class ComponentRegistry:
    """组件注册表"""
    
    def __init__(self):
        self._components: Dict[str, ComponentBase] = {}
    
    def register(self, component: ComponentBase) -> bool:
        """注册组件"""
        if component.name in self._components:
            return False
        
        self._components[component.name] = component
        return True
    
    def unregister(self, name: str) -> bool:
        """注销组件"""
        if name not in self._components:
            return False
        
        del self._components[name]
        return True
    
    def get(self, name: str) -> Optional[ComponentBase]:
        """获取组件"""
        return self._components.get(name)
    
    def get_by_layer(self, layer: int) -> list:
        """按层级获取组件"""
        return [
            c for c in self._components.values()
            if c.layer == layer
        ]
    
    def get_all(self) -> Dict[str, ComponentBase]:
        """获取所有组件"""
        return self._components.copy()
    
    def health_check_all(self) -> Dict[str, Any]:
        """检查所有组件健康状态"""
        results = {}
        
        for name, component in self._components.items():
            results[name] = component.health_check()
        
        all_healthy = all(r["healthy"] for r in results.values())
        
        return {
            "healthy": all_healthy,
            "components": results,
            "total": len(results),
            "healthy_count": sum(1 for r in results.values() if r["healthy"])
        }
    
    def get_stats_all(self) -> Dict[str, Any]:
        """获取所有组件统计"""
        return {
            name: component.get_stats()
            for name, component in self._components.items()
        }

# 全局注册表
_registry: Optional[ComponentRegistry] = None

def get_registry() -> ComponentRegistry:
    """获取全局注册表"""
    global _registry
    if _registry is None:
        _registry = ComponentRegistry()
    return _registry
