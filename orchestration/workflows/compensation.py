"""工作流补偿动作"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


class CompensationAction:
    """补偿动作"""
    
    def __init__(self, name: str, action: callable, params: dict):
        self.name = name
        self.action = action
        self.params = params
        self.executed = False
        self.result = None


class CompensationManager:
    """补偿管理器"""
    
    def __init__(self):
        self.compensations: List[CompensationAction] = []
        self.executed_compensations: List[Dict[str, Any]] = []
    
    def register(self, name: str, action: callable, params: dict):
        """注册补偿动作"""
        self.compensations.append(CompensationAction(name, action, params))
    
    def execute_all(self, dry_run: bool = False) -> Dict[str, Any]:
        """执行所有补偿动作"""
        results = []
        
        for comp in reversed(self.compensations):  # 逆序执行
            if comp.executed:
                continue
            
            if dry_run:
                results.append({
                    "name": comp.name,
                    "dry_run": True,
                    "skipped": True
                })
                continue
            
            try:
                result = comp.action(**comp.params)
                comp.executed = True
                comp.result = result
                
                results.append({
                    "name": comp.name,
                    "success": result.get("success", False),
                    "result": result
                })
                
                self.executed_compensations.append({
                    "name": comp.name,
                    "executed_at": datetime.now().isoformat(),
                    "result": result
                })
            
            except Exception as e:
                results.append({
                    "name": comp.name,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": all(r.get("success", False) for r in results),
            "compensations_executed": len([r for r in results if not r.get("dry_run")]),
            "results": results
        }


def execute_with_compensation(
    primary_steps: List[Dict[str, Any]],
    compensation_steps: List[Dict[str, Any]],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    执行带补偿的工作流
    
    Args:
        primary_steps: 主要步骤
        compensation_steps: 补偿步骤（主步骤失败时执行）
        dry_run: 是否预演模式
        
    Returns:
        执行结果
    """
    import importlib
    
    manager = CompensationManager()
    primary_results = []
    failed = False
    
    # 注册补偿动作
    for comp_step in compensation_steps:
        def make_compensation(step):
            def compensation_action(**params):
                module = importlib.import_module(f"capabilities.{step.get('capability')}")
                return module.run(**step.get("params", {}))
            return compensation_action
        
        manager.register(
            name=comp_step.get("name", "unnamed"),
            action=make_compensation(comp_step),
            params=comp_step.get("params", {})
        )
    
    # 执行主要步骤
    for step in primary_steps:
        if dry_run:
            primary_results.append({
                "step": step.get("name", "unnamed"),
                "dry_run": True,
                "skipped": True
            })
            continue
        
        try:
            module = importlib.import_module(f"capabilities.{step.get('capability')}")
            result = module.run(**step.get("params", {}))
            
            primary_results.append({
                "step": step.get("name"),
                "success": result.get("success", False),
                "result": result
            })
            
            if not result.get("success", False):
                failed = True
                break
        
        except Exception as e:
            primary_results.append({
                "step": step.get("name"),
                "success": False,
                "error": str(e)
            })
            failed = True
            break
    
    # 如果失败，执行补偿
    compensation_results = None
    if failed and not dry_run:
        compensation_results = manager.execute_all()
    
    return {
        "success": not failed,
        "dry_run": dry_run,
        "primary_results": primary_results,
        "compensation_executed": failed,
        "compensation_results": compensation_results
    }


def rollback_create_event(event_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """回滚创建的日程事件"""
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": f"预演模式：将删除事件 {event_id}"
        }
    
    from capabilities.delete_calendar_event import delete_calendar_event
    return delete_calendar_event(event_id=event_id, reason="rollback")


def rollback_send_message(invocation_id: int, dry_run: bool = False) -> Dict[str, Any]:
    """回滚发送的消息（记录状态）"""
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": f"预演模式：将标记消息 {invocation_id} 为已回滚"
        }
    
    from platform_adapter.invocation_ledger import InvocationLedger
    ledger = InvocationLedger()
    
    return ledger.confirm_record(
        record_id=invocation_id,
        confirmed_status="confirmed_failed",
        confirm_note="rollback: 主流程失败，回滚此操作"
    )


def rollback_create_note(note_id: str, dry_run: bool = False) -> Dict[str, Any]:
    """回滚创建的备忘录"""
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": f"预演模式：将删除备忘录 {note_id}"
        }
    
    from capabilities.delete_note import delete_note
    return delete_note(note_id=note_id, reason="rollback")
