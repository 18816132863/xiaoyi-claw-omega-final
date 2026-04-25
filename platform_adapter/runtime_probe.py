"""
Runtime Probe - 运行时探测器
探测当前运行环境和平台能力
"""

import os
import sys
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path


class RuntimeProbe:
    """运行时探测器"""
    
    @staticmethod
    def detect_environment() -> Dict[str, Any]:
        """检测运行环境"""
        env = {
            "is_xiaoyi": RuntimeProbe._detect_xiaoyi(),
            "is_harmonyos": RuntimeProbe._detect_harmonyos(),
            "is_web": RuntimeProbe._detect_web(),
            "is_cli": RuntimeProbe._detect_cli(),
            "has_local_sqlite": RuntimeProbe._detect_local_sqlite(),
            "has_external_database": RuntimeProbe._detect_external_database(),
            "has_redis": RuntimeProbe._detect_redis(),
            "has_docker": RuntimeProbe._detect_docker(),
        }
        
        # 统一字段：has_database 给上层使用
        env["has_database"] = env["has_local_sqlite"] or env["has_external_database"]
        
        env["runtime_mode"] = RuntimeProbe._determine_mode(env)
        
        return env
    
    @staticmethod
    def _detect_xiaoyi() -> bool:
        """检测是否在小艺环境"""
        return (
            os.environ.get("XIAOYI_ENV") is not None or
            "xiaoyi" in sys.modules
        )
    
    @staticmethod
    def _detect_harmonyos() -> bool:
        """检测是否在鸿蒙环境"""
        return (
            os.environ.get("HARMONYOS_VERSION") is not None or
            os.environ.get("OHOS_VERSION") is not None
        )
    
    @staticmethod
    def _detect_web() -> bool:
        """检测是否在Web环境"""
        return (
            os.environ.get("WEB_ENV") is not None or
            os.environ.get("HTTP_HOST") is not None
        )
    
    @staticmethod
    def _detect_cli() -> bool:
        """检测是否在CLI环境"""
        return sys.stdin is not None and sys.stdin.isatty()
    
    @staticmethod
    def _detect_local_sqlite() -> bool:
        """检测是否有本地SQLite"""
        return Path("data/tasks.db").exists()
    
    @staticmethod
    def _detect_external_database() -> bool:
        """检测是否有外部数据库"""
        return os.environ.get("DATABASE_URL") is not None
    
    @staticmethod
    def _detect_redis() -> bool:
        """检测是否有Redis"""
        return os.environ.get("REDIS_URL") is not None or os.environ.get("REDIS_HOST") is not None
    
    @staticmethod
    def _detect_docker() -> bool:
        """检测是否在Docker环境"""
        return (
            Path("/.dockerenv").exists() or
            os.environ.get("KUBERNETES_SERVICE_HOST") is not None
        )
    
    @staticmethod
    def _determine_mode(env: Dict[str, Any]) -> str:
        """
        确定运行模式
        
        规则：
        1. 如果推荐适配器返回 xiaoyi 且真的可用，使用 platform_enhanced
        2. 如果有外部数据库 + Redis，使用 self_hosted_enhanced
        3. 否则使用 skill_default
        """
        # 检查平台增强模式 - 使用同步方式检查
        adapter_name = RuntimeProbe.get_recommended_adapter()
        if adapter_name != "null":
            # 验证适配器真的可用（同步检查）
            probe_result = RuntimeProbe.probe_adapter_sync(adapter_name)
            if probe_result.get("available") == True:
                return "platform_enhanced"
        
        # 检查自托管增强模式
        if env["has_external_database"] and env["has_redis"]:
            return "self_hosted_enhanced"
        
        # 默认模式
        return "skill_default"
    
    @staticmethod
    def get_recommended_adapter() -> str:
        """
        获取推荐的适配器
        
        使用同步方式检查，避免异步警告
        """
        # 检查小艺环境
        if RuntimeProbe._detect_xiaoyi() or RuntimeProbe._detect_harmonyos():
            # 同步检查适配器是否可用
            try:
                from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
                adapter = XiaoyiAdapter()
                
                # 同步检查：环境存在 + 至少一个能力已接通
                # 由于当前能力都是 available=False，所以会返回 null
                adapter._ensure_initialized_sync()
                
                if adapter._environment_exists:
                    # 检查是否有任何能力已接通
                    has_capability = any(
                        status.available 
                        for status in adapter._capabilities.values()
                    )
                    if has_capability:
                        return "xiaoyi"
            except Exception:
                pass
        
        # 无可用适配器
        return "null"
    
    @staticmethod
    def probe_adapter(adapter_name: str) -> Dict[str, Any]:
        """探测适配器能力（异步版本）"""
        if adapter_name == "null":
            return {
                "adapter": "null",
                "available": False,
                "capabilities": {}
            }
        
        if adapter_name == "xiaoyi":
            try:
                from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
                adapter = XiaoyiAdapter()
                
                # 尝试在现有事件循环中运行
                try:
                    loop = asyncio.get_running_loop()
                    # 如果已有事件循环，创建任务
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run, 
                            adapter.probe()
                        )
                        return future.result()
                except RuntimeError:
                    # 没有运行中的事件循环
                    return asyncio.run(adapter.probe())
            except Exception as e:
                return {
                    "adapter": "xiaoyi",
                    "available": False,
                    "error": str(e)
                }
        
        return {
            "adapter": adapter_name,
            "available": False,
            "error": f"Unknown adapter: {adapter_name}"
        }
    
    @staticmethod
    def probe_adapter_sync(adapter_name: str) -> Dict[str, Any]:
        """探测适配器能力（同步版本）"""
        if adapter_name == "null":
            return {
                "adapter": "null",
                "available": False,
                "capabilities": {}
            }
        
        if adapter_name == "xiaoyi":
            try:
                from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
                adapter = XiaoyiAdapter()
                adapter._ensure_initialized_sync()
                
                # 同步检查
                truly_available = (
                    adapter._environment_exists and 
                    any(status.available for status in adapter._capabilities.values())
                )
                
                available_caps = {
                    cap.value: status.available
                    for cap, status in adapter._capabilities.items()
                }
                
                return {
                    "adapter": "xiaoyi",
                    "available": truly_available,
                    "environment_exists": adapter._environment_exists,
                    "capabilities": available_caps
                }
            except Exception as e:
                return {
                    "adapter": "xiaoyi",
                    "available": False,
                    "error": str(e)
                }
        
        return {
            "adapter": adapter_name,
            "available": False,
            "error": f"Unknown adapter: {adapter_name}"
        }
