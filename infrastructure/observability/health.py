"""
健康检查模块 V1.0.0

提供服务健康状态检查。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum


class HealthStatus(str, Enum):
    """健康状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthChecker:
    """健康检查器"""
    
    def __init__(self, service: str):
        self.service = service
        self._checks: Dict[str, callable] = {}
    
    def register(self, name: str, check_func: callable):
        """注册健康检查"""
        self._checks[name] = check_func
    
    def check(self) -> Dict[str, Any]:
        """执行所有健康检查"""
        results = {}
        all_healthy = True
        any_degraded = False
        
        for name, check_func in self._checks.items():
            try:
                result = check_func()
                if result.get("status") == "unhealthy":
                    all_healthy = False
                elif result.get("status") == "degraded":
                    any_degraded = True
                results[name] = result
            except Exception as e:
                all_healthy = False
                results[name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        if all_healthy:
            overall = HealthStatus.HEALTHY
        elif any_degraded:
            overall = HealthStatus.DEGRADED
        else:
            overall = HealthStatus.UNHEALTHY
        
        return {
            "service": self.service,
            "status": overall.value,
            "timestamp": datetime.now().isoformat(),
            "checks": results
        }
    
    def check_ready(self) -> Dict[str, Any]:
        """就绪检查 - 是否可以接收流量"""
        result = self.check()
        
        # 就绪检查更严格，degraded 也算不就绪
        is_ready = result["status"] == "healthy"
        
        return {
            "service": self.service,
            "ready": is_ready,
            "timestamp": datetime.now().isoformat(),
            "checks": result["checks"]
        }
    
    def to_json(self) -> str:
        """导出为 JSON"""
        return json.dumps(self.check(), indent=2, ensure_ascii=False)
