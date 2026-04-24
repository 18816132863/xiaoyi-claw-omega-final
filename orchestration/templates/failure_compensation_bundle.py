"""故障补偿模板"""

from typing import Dict, Any, List, Optional
from datetime import datetime


def failure_compensation_bundle(
    primary_action: Dict[str, Any],
    fallback_actions: List[Dict[str, Any]],
    compensation_actions: List[Dict[str, Any]],
    notify_on_failure: bool = True,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    故障补偿模板：主路径失败 -> fallback -> 审计补偿 -> 输出最终状态
    
    Args:
        primary_action: 主要动作
        fallback_actions: 降级动作列表
        compensation_actions: 补偿动作列表
        notify_on_failure: 失败时是否通知
        dry_run: 是否预演模式
        
    Returns:
        执行结果
    """
    from orchestration.workflows.compensation import execute_with_compensation
    from orchestration.workflows.preview import preview_workflow
    
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": "预演模式：故障补偿模板",
            "primary_action": primary_action,
            "fallback_actions": fallback_actions,
            "compensation_actions": compensation_actions
        }
    
    import importlib
    
    execution_log = []
    final_status = "unknown"
    
    # 1. 执行主要动作
    try:
        capability = primary_action.get("capability")
        params = primary_action.get("params", {})
        module = importlib.import_module(f"capabilities.{capability}")
        primary_result = module.run(**params)
        
        execution_log.append({
            "stage": "primary",
            "action": primary_action.get("name", capability),
            "success": primary_result.get("success", False),
            "result": primary_result
        })
        
        if primary_result.get("success"):
            final_status = "success"
            return {
                "success": True,
                "bundle_type": "failure_compensation",
                "final_status": final_status,
                "execution_log": execution_log,
                "used_fallback": False,
                "used_compensation": False
            }
    
    except Exception as e:
        execution_log.append({
            "stage": "primary",
            "action": primary_action.get("name", "unknown"),
            "success": False,
            "error": str(e)
        })
    
    # 2. 主动作失败，执行 fallback
    fallback_success = False
    for fallback in fallback_actions:
        try:
            capability = fallback.get("capability")
            params = fallback.get("params", {})
            module = importlib.import_module(f"capabilities.{capability}")
            fallback_result = module.run(**params)
            
            execution_log.append({
                "stage": "fallback",
                "action": fallback.get("name", capability),
                "success": fallback_result.get("success", False),
                "result": fallback_result
            })
            
            if fallback_result.get("success"):
                fallback_success = True
                break
        
        except Exception as e:
            execution_log.append({
                "stage": "fallback",
                "action": fallback.get("name", "unknown"),
                "success": False,
                "error": str(e)
            })
    
    # 3. 如果 fallback 也失败，执行补偿
    compensation_results = []
    if not fallback_success:
        for comp in compensation_actions:
            try:
                capability = comp.get("capability")
                params = comp.get("params", {})
                module = importlib.import_module(f"capabilities.{capability}")
                comp_result = module.run(**params)
                
                compensation_results.append({
                    "action": comp.get("name", capability),
                    "success": comp_result.get("success", False),
                    "result": comp_result
                })
            
            except Exception as e:
                compensation_results.append({
                    "action": comp.get("name", "unknown"),
                    "success": False,
                    "error": str(e)
                })
        
        final_status = "compensated"
    else:
        final_status = "fallback_success"
    
    # 4. 失败通知
    if notify_on_failure and final_status != "success":
        try:
            from capabilities.send_notification import send_notification
            send_notification(
                title="故障补偿通知",
                content=f"主动作失败，已执行 {'fallback' if fallback_success else '补偿'} 动作"
            )
        except:
            pass
    
    return {
        "success": fallback_success or len([c for c in compensation_results if c.get("success")]) > 0,
        "bundle_type": "failure_compensation",
        "final_status": final_status,
        "execution_log": execution_log,
        "used_fallback": fallback_success,
        "used_compensation": not fallback_success,
        "compensation_results": compensation_results if compensation_results else None,
        "summary": {
            "primary_success": False,
            "fallback_success": fallback_success,
            "compensation_executed": not fallback_success
        }
    }


def run(**kwargs):
    """模板入口"""
    return failure_compensation_bundle(**kwargs)
