"""
Xiaoyi Adapter - 小艺平台适配器
对接小艺平台能力

V8.4.0 平台稳定性硬化版
- 使用统一防护层 (invoke_guard)
- 区分 timeout / result_uncertain / failed
- 副作用操作幂等保护
- 审计台账记录
"""

from typing import Dict, Any, Optional
from .base import PlatformAdapter, PlatformCapability, PlatformCapabilityState
from .invoke_guard import (
    guarded_platform_call,
    create_fallback_result,
    InvokeResult,
    generate_idempotency_key,
)
from .invocation_ledger import record_invocation
from .result_normalizer import NormalizedStatus


class XiaoyiAdapter(PlatformAdapter):
    """小艺平台适配器"""
    
    name = "xiaoyi"
    description = "Xiaoyi/HarmonyOS platform adapter"
    
    # 副作用能力列表
    SIDE_EFFECTING_CAPABILITIES = {
        PlatformCapability.MESSAGE_SENDING,
        PlatformCapability.TASK_SCHEDULING,
        PlatformCapability.NOTIFICATION,
    }
    
    def __init__(self):
        self._capabilities: Dict[PlatformCapability, PlatformCapabilityState] = {}
        self._initialized = False
        self._environment_exists = False
        self._call_device_tool_available = False
        self._device_connected = True  # 默认已连接
    
    def _check_call_device_tool_available(self) -> bool:
        """检查 call_device_tool 是否可用"""
        try:
            import importlib
            spec = importlib.util.find_spec("tools")
            if spec is not None:
                return True
            
            import os
            if os.environ.get("OPENCLAW_RUNTIME") == "true":
                return True
            
            if os.environ.get("XIAOYI_DEVICE_CONNECTED") == "true":
                return True
            
            return False
        except:
            return False
    
    def _ensure_initialized_sync(self):
        """同步初始化"""
        if self._initialized:
            return
        
        import os
        import sys
        
        self._environment_exists = (
            os.environ.get("XIAOYI_ENV") is not None or
            os.environ.get("HARMONYOS_VERSION") is not None or
            os.environ.get("OHOS_VERSION") is not None or
            "xiaoyi" in sys.modules or
            os.environ.get("OPENCLAW_RUNTIME") == "true"
        )
        
        self._call_device_tool_available = self._check_call_device_tool_available()
        
        message_sending_available = self._call_device_tool_available
        
        self._capabilities = {
            PlatformCapability.TASK_SCHEDULING: PlatformCapabilityState(
                capability=PlatformCapability.TASK_SCHEDULING,
                available=self._call_device_tool_available,
                description="Xiaoyi task scheduling via create_calendar_event (connected)"
            ),
            PlatformCapability.MESSAGE_SENDING: PlatformCapabilityState(
                capability=PlatformCapability.MESSAGE_SENDING,
                available=message_sending_available,
                description="Xiaoyi message sending via send_message (connected)"
            ),
            PlatformCapability.NOTIFICATION: PlatformCapabilityState(
                capability=PlatformCapability.NOTIFICATION,
                available=True,
                description="Xiaoyi notification via today-task (connected)"
            ),
        }
        
        self._initialized = True
    
    async def _ensure_initialized(self):
        """确保初始化"""
        if self._initialized:
            return
        self._ensure_initialized_sync()
    
    async def probe(self) -> Dict[str, Any]:
        """探测平台能力"""
        await self._ensure_initialized()
        
        available_caps = {
            cap.value: status.available
            for cap, status in self._capabilities.items()
        }
        
        truly_available = any(status.available for status in self._capabilities.values())
        
        if truly_available:
            state = "connected"
        else:
            state = "probe_only"
        
        return {
            "adapter": self.name,
            "available": truly_available,
            "state": state,
            "device_connected": self._device_connected,
            "call_device_tool_available": self._call_device_tool_available,
            "capabilities": available_caps,
            "message": "Xiaoyi adapter ready" if truly_available else "Xiaoyi adapter initialized (some capabilities not authorized)"
        }
    
    async def get_capability(self, capability: PlatformCapability) -> Optional[PlatformCapabilityState]:
        """获取特定能力状态"""
        await self._ensure_initialized()
        return self._capabilities.get(capability)
    
    async def invoke(self, capability: PlatformCapability, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用平台能力（使用统一防护层）"""
        await self._ensure_initialized()
        
        status = self._capabilities.get(capability)
        if not status:
            return {
                "success": False,
                "status": "failed",
                "error": f"Unknown capability: {capability.value}",
                "error_code": "UNKNOWN_CAPABILITY",
                "user_message": f"未知能力: {capability.value}",
            }
        
        if not status.available:
            return {
                "success": False,
                "status": "failed",
                "error": f"Capability {capability.value} not available",
                "error_code": "CAPABILITY_NOT_CONNECTED",
                "fallback_available": True,
                "user_message": f"该能力当前不可用",
            }
        
        # 根据能力类型调用对应的实现
        if capability == PlatformCapability.MESSAGE_SENDING:
            return await self._invoke_message_sending_guarded(params)
        elif capability == PlatformCapability.TASK_SCHEDULING:
            return await self._invoke_task_scheduling_guarded(params)
        elif capability == PlatformCapability.NOTIFICATION:
            return await self._invoke_notification_guarded(params)
        else:
            return {
                "success": False,
                "status": "failed",
                "error": f"Capability {capability.value} not implemented",
                "error_code": "NOT_IMPLEMENTED",
                "user_message": f"该能力尚未实现",
            }
    
    async def _invoke_message_sending_guarded(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用短信发送（使用统一防护层）"""
        import asyncio
        
        # 生成幂等键
        idempotency_key = generate_idempotency_key(
            task_id=params.get("task_id"),
            capability="MESSAGE_SENDING",
            payload={"phone": params.get("phone_number"), "msg": params.get("message")},
        )
        
        # 检查 call_device_tool 是否可用
        if not self._call_device_tool_available:
            # 使用 fallback
            result = create_fallback_result(
                capability="MESSAGE_SENDING",
                op_name="send_message",
                idempotency_key=idempotency_key,
            )
            return self._result_to_dict(result)
        
        # 定义实际调用
        async def _call():
            try:
                from tools import call_device_tool
                return await call_device_tool(
                    toolName="send_message",
                    arguments={
                        "phoneNumber": params.get("phone_number"),
                        "content": params.get("message")
                    }
                )
            except ImportError:
                return {"status": "error", "error": "call_device_tool not available"}
        
        # 使用统一防护层调用
        result = await guarded_platform_call(
            capability="MESSAGE_SENDING",
            op_name="send_message",
            call_coro=_call(),
            timeout_seconds=60,
            idempotency_key=idempotency_key,
            side_effecting=True,
            task_id=params.get("task_id"),
            payload=params,
        )
        
        # 记录审计
        record_invocation(
            capability="MESSAGE_SENDING",
            platform_op="send_message",
            normalized_status=result.normalized_status,
            task_id=params.get("task_id"),
            idempotency_key=idempotency_key,
            side_effecting=True,
            request_json=params,
            raw_result_json=result.raw_result,
            error_code=result.error_code,
            user_message=result.user_message,
            result_uncertain=result.result_uncertain,
            fallback_used=result.fallback_used,
            elapsed_ms=result.elapsed_ms,
        )
        
        return self._result_to_dict(result)
    
    async def _invoke_task_scheduling_guarded(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用日程创建（使用统一防护层）"""
        import asyncio
        
        idempotency_key = generate_idempotency_key(
            task_id=params.get("task_id"),
            capability="TASK_SCHEDULING",
            payload={"title": params.get("title"), "start": params.get("start_time")},
        )
        
        if not self._call_device_tool_available:
            result = create_fallback_result(
                capability="TASK_SCHEDULING",
                op_name="create_calendar_event",
                idempotency_key=idempotency_key,
            )
            return self._result_to_dict(result)
        
        async def _call():
            try:
                from tools import call_device_tool
                return await call_device_tool(
                    toolName="create_calendar_event",
                    arguments={
                        "title": params.get("title"),
                        "dtStart": params.get("start_time"),
                        "dtEnd": params.get("end_time")
                    }
                )
            except ImportError:
                return {"status": "error", "error": "call_device_tool not available"}
        
        result = await guarded_platform_call(
            capability="TASK_SCHEDULING",
            op_name="create_calendar_event",
            call_coro=_call(),
            timeout_seconds=60,
            idempotency_key=idempotency_key,
            side_effecting=True,
            task_id=params.get("task_id"),
            payload=params,
        )
        
        record_invocation(
            capability="TASK_SCHEDULING",
            platform_op="create_calendar_event",
            normalized_status=result.normalized_status,
            task_id=params.get("task_id"),
            idempotency_key=idempotency_key,
            side_effecting=True,
            request_json=params,
            raw_result_json=result.raw_result,
            error_code=result.error_code,
            user_message=result.user_message,
            result_uncertain=result.result_uncertain,
            fallback_used=result.fallback_used,
            elapsed_ms=result.elapsed_ms,
        )
        
        return self._result_to_dict(result)
    
    async def _invoke_notification_guarded(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用负一屏推送（使用统一防护层）"""
        import asyncio
        import json
        import subprocess
        from pathlib import Path
        
        idempotency_key = generate_idempotency_key(
            task_id=params.get("task_id"),
            capability="NOTIFICATION",
            payload={"title": params.get("title")},
        )
        
        async def _call():
            skill_path = Path(__file__).parent.parent / "skills" / "today-task" / "scripts" / "task_push.py"
            
            if not skill_path.exists():
                return {"status": "error", "error": "today-task skill not found"}
            
            task_data = {
                "task_name": params.get("title", "任务"),
                "task_content": params.get("content", ""),
                "task_result": params.get("result", "已完成")
            }
            
            try:
                result = subprocess.run(
                    ["python", str(skill_path), "--data", json.dumps(task_data)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    return {"code": "0000000000", "desc": "OK", "stdout": result.stdout}
                else:
                    return {"code": "ERROR", "desc": result.stderr or "Unknown error"}
            except subprocess.TimeoutExpired:
                return {"status": "error", "error": "timeout"}
            except Exception as e:
                return {"status": "error", "error": str(e)}
        
        result = await guarded_platform_call(
            capability="NOTIFICATION",
            op_name="today_task_push",
            call_coro=_call(),
            timeout_seconds=90,
            idempotency_key=idempotency_key,
            side_effecting=True,
            task_id=params.get("task_id"),
            payload=params,
        )
        
        record_invocation(
            capability="NOTIFICATION",
            platform_op="today_task_push",
            normalized_status=result.normalized_status,
            task_id=params.get("task_id"),
            idempotency_key=idempotency_key,
            side_effecting=True,
            request_json=params,
            raw_result_json=result.raw_result,
            error_code=result.error_code,
            user_message=result.user_message,
            result_uncertain=result.result_uncertain,
            fallback_used=result.fallback_used,
            elapsed_ms=result.elapsed_ms,
        )
        
        return self._result_to_dict(result)
    
    def _result_to_dict(self, result: InvokeResult) -> Dict[str, Any]:
        """将 InvokeResult 转换为字典"""
        return {
            "success": result.normalized_status == NormalizedStatus.COMPLETED,
            "status": result.normalized_status,
            "capability": result.capability,
            "error": result.error_code,
            "error_code": result.error_code,
            "user_message": result.user_message,
            "raw_result": result.raw_result,
            "should_retry": result.should_retry,
            "result_uncertain": result.result_uncertain,
            "side_effecting": result.side_effecting,
            "fallback_used": result.fallback_used,
            "idempotency_key": result.idempotency_key,
            "elapsed_ms": result.elapsed_ms,
        }
    
    async def is_available(self) -> bool:
        """检查小艺平台是否可用"""
        await self._ensure_initialized()
        return any(status.available for status in self._capabilities.values())
