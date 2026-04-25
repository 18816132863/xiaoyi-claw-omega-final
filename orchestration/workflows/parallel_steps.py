"""工作流并行步骤"""

from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


def execute_parallel_steps(
    steps: List[Dict[str, Any]],
    max_workers: int = 5,
    fail_fast: bool = False,
    dry_run: bool = False,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    并行执行多个步骤
    
    Args:
        steps: 步骤列表
        max_workers: 最大并行数
        fail_fast: 是否快速失败（任一步骤失败则终止其他）
        dry_run: 是否预演模式
        context: 执行上下文
        
    Returns:
        执行结果
    """
    context = context or {}
    results = []
    errors = []
    cancelled = False
    lock = threading.Lock()
    
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": f"预演模式：将并行执行 {len(steps)} 个步骤",
            "steps": [{"name": s.get("name"), "capability": s.get("capability")} for s in steps]
        }
    
    def execute_step(step: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个步骤"""
        nonlocal cancelled
        
        if cancelled and fail_fast:
            return {
                "step": step.get("name", "unnamed"),
                "skipped": True,
                "reason": "fail_fast_cancelled"
            }
        
        import importlib
        capability = step.get("capability")
        params = step.get("params", {})
        
        try:
            module = importlib.import_module(f"capabilities.{capability}")
            if hasattr(module, "run"):
                result = module.run(**params)
                
                # 检查是否需要取消其他步骤
                if fail_fast and not result.get("success", False):
                    with lock:
                        cancelled = True
                
                return {
                    "step": step.get("name", capability),
                    "success": result.get("success", False),
                    "result": result
                }
            else:
                return {
                    "step": step.get("name", capability),
                    "success": False,
                    "error": f"Capability {capability} has no run function"
                }
        except Exception as e:
            with lock:
                if fail_fast:
                    cancelled = True
            return {
                "step": step.get("name", capability),
                "success": False,
                "error": str(e)
            }
    
    # 并行执行
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(execute_step, step): step for step in steps}
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            if not result.get("success", False):
                errors.append(result)
    
    # 统计
    success_count = sum(1 for r in results if r.get("success", False))
    failure_count = len(results) - success_count
    
    return {
        "success": failure_count == 0,
        "total": len(steps),
        "success_count": success_count,
        "failure_count": failure_count,
        "results": results,
        "errors": errors if errors else None
    }


def parallel_send_messages(
    recipients: List[Dict[str, str]],
    message_template: str,
    max_workers: int = 5,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    并行发送多条消息
    
    Args:
        recipients: 收件人列表 [{"to": "phone", "name": "name"}, ...]
        message_template: 消息模板（支持 {name} 占位符）
        max_workers: 最大并行数
        dry_run: 是否预演模式
        
    Returns:
        发送结果
    """
    steps = []
    for recipient in recipients:
        message = message_template.format(name=recipient.get("name", ""))
        steps.append({
            "name": f"send_to_{recipient.get('to')}",
            "capability": "send_message",
            "params": {
                "to": recipient.get("to"),
                "message": message
            }
        })
    
    return execute_parallel_steps(steps, max_workers=max_workers, dry_run=dry_run)


def parallel_send_notifications(
    notifications: List[Dict[str, str]],
    max_workers: int = 5,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    并行发送多个通知
    
    Args:
        notifications: 通知列表 [{"title": "...", "content": "..."}, ...]
        max_workers: 最大并行数
        dry_run: 是否预演模式
        
    Returns:
        发送结果
    """
    steps = []
    for i, notif in enumerate(notifications):
        steps.append({
            "name": f"notification_{i}",
            "capability": "send_notification",
            "params": {
                "title": notif.get("title"),
                "content": notif.get("content")
            }
        })
    
    return execute_parallel_steps(steps, max_workers=max_workers, dry_run=dry_run)
