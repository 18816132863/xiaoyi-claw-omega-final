"""设备能力执行器"""

from typing import Optional, Dict, Any
from .registry import CapabilityRegistry, RiskLevel
from .schemas import DeviceCapabilityRequest, DeviceCapabilityResult
from platform_adapter.invocation_ledger import record_invocation


class CapabilityExecutor:
    """能力执行器"""
    
    def __init__(self, registry: Optional[CapabilityRegistry] = None):
        self.registry = registry or CapabilityRegistry()
    
    def execute(self, request: DeviceCapabilityRequest) -> DeviceCapabilityResult:
        """执行能力"""
        import time
        start_time = time.time()
        
        # 获取能力定义
        capability_def = self.registry.get(request.capability)
        if not capability_def:
            return DeviceCapabilityResult(
                success=False,
                status="failed",
                error=f"未知能力: {request.capability}",
                user_message=f"不支持的操作: {request.capability}",
            )
        
        # 检查风险等级
        if capability_def.risk_level == RiskLevel.BLOCKED:
            return DeviceCapabilityResult(
                success=False,
                status="blocked",
                error="该操作被禁止",
                user_message="该操作涉及违法/绕过平台限制/破坏公平，不能执行",
            )
        
        # L4 强确认
        if capability_def.risk_level == RiskLevel.L4:
            if not request.approval_required:
                return DeviceCapabilityResult(
                    success=False,
                    status="requires_confirmation",
                    user_message="该操作需要强确认，请先预览并确认",
                    raw_result={
                        "risk_level": "L4",
                        "policy": "strong_confirm",
                        "requires_preview": True,
                        "requires_stepwise_execution": True,
                    }
                )
        
        # L3 确认
        if capability_def.risk_level == RiskLevel.L3:
            if capability_def.requires_confirmation and not request.approval_required:
                return DeviceCapabilityResult(
                    success=False,
                    status="requires_confirmation",
                    user_message="该操作需要确认",
                )
        
        # Dry run
        if request.dry_run:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return DeviceCapabilityResult(
                success=True,
                status="completed",
                user_message=f"预演模式：{capability_def.name} 将被执行",
                raw_result={"dry_run": True, "capability": request.capability},
                elapsed_ms=elapsed_ms,
            )
        
        # 实际执行
        try:
            result = self._execute_capability(request, capability_def)
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            # 记录审计
            record_invocation(
                capability=request.capability,
                request_params=request.params,
                response=result,
                status="completed" if result.get("success") else "failed",
            )
            
            return DeviceCapabilityResult(
                success=result.get("success", False),
                status="completed" if result.get("success") else "failed",
                raw_result=result,
                user_message=result.get("message", ""),
                elapsed_ms=elapsed_ms,
            )
        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return DeviceCapabilityResult(
                success=False,
                status="failed",
                error=str(e),
                user_message=f"执行失败: {str(e)}",
                elapsed_ms=elapsed_ms,
            )
    
    def _execute_capability(self, request: DeviceCapabilityRequest, capability_def) -> Dict[str, Any]:
        """实际执行能力"""
        # 调用对应的 capabilities 模块
        capability_map = {
            "communication.send_message": "capabilities.send_message",
            "communication.call_phone": "capabilities.make_call",
            "communication.contact_lookup": "capabilities.query_contact",
            "schedule.create_calendar_event": "capabilities.schedule_task",
            "schedule.create_alarm": "capabilities.create_alarm",
            "storage.create_note": "capabilities.create_note",
            "notification.push": "capabilities.send_notification",
        }
        
        module_path = capability_map.get(request.capability)
        if module_path:
            try:
                parts = module_path.split(".")
                module = __import__(".".join(parts[:-1]))
                for part in parts[1:]:
                    module = getattr(module, part)
                
                if hasattr(module, "run"):
                    return module.run(**request.params)
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # 默认返回模拟结果
        return {
            "success": True,
            "capability": request.capability,
            "params": request.params,
            "message": f"{capability_def.name} 执行成功（模拟）",
        }
