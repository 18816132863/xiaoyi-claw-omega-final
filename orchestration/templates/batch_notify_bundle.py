"""批量通知模板"""

from typing import Dict, Any, List, Optional
from datetime import datetime


def batch_notify_bundle(
    notifications: List[Dict[str, str]],
    max_batch_size: int = 20,
    require_approval: bool = True,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    批量通知模板：批量发送 + 失败汇总 + uncertain汇总 + 执行报告
    
    Args:
        notifications: 通知列表 [{"title": "...", "content": "..."}, ...]
        max_batch_size: 最大批次大小
        require_approval: 是否需要审批
        dry_run: 是否预演模式
        
    Returns:
        执行结果
    """
    from orchestration.workflows.parallel_steps import execute_parallel_steps
    from orchestration.workflows.preview import preview_workflow
    from config.safety_controls import check_approval_required
    
    # 检查批次大小
    if len(notifications) > max_batch_size:
        return {
            "success": False,
            "error": f"批次大小超过限制: {len(notifications)} > {max_batch_size}",
            "max_batch_size": max_batch_size
        }
    
    # 检查是否需要审批
    if require_approval and not dry_run:
        approval_check = check_approval_required("batch_notification", len(notifications))
        if approval_check.get("approval_required"):
            return {
                "success": False,
                "requires_approval": True,
                "message": "批量通知需要审批，请先获取审批"
            }
    
    # 构建步骤
    steps = []
    for i, notif in enumerate(notifications):
        steps.append({
            "name": f"notification_{i+1}",
            "capability": "send_notification",
            "params": {
                "title": notif.get("title", ""),
                "content": notif.get("content", "")
            }
        })
    
    # 预演模式
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": f"预演模式：将发送 {len(notifications)} 条通知",
            "notifications": notifications
        }
    
    # 并行执行
    result = execute_parallel_steps(steps, max_workers=5, dry_run=False)
    
    # 汇总
    success_list = []
    failed_list = []
    uncertain_list = []
    
    for r in result.get("results", []):
        step_result = r.get("result", {})
        status = step_result.get("normalized_status", "unknown")
        
        item = {
            "index": r.get("step"),
            "title": notifications[int(r.get("step", "notification_0").split("_")[1])].get("title") if r.get("step") else "",
            "status": status
        }
        
        if status == "completed":
            success_list.append(item)
        elif status == "failed":
            failed_list.append(item)
        elif status in ["timeout", "result_uncertain"]:
            uncertain_list.append(item)
    
    # 生成报告
    report = {
        "success": len(failed_list) == 0 and len(uncertain_list) == 0,
        "bundle_type": "batch_notify",
        "dry_run": dry_run,
        "total": len(notifications),
        "success_count": len(success_list),
        "failed_count": len(failed_list),
        "uncertain_count": len(uncertain_list),
        "success_list": success_list,
        "failed_list": failed_list,
        "uncertain_list": uncertain_list,
        "executed_at": datetime.now().isoformat()
    }
    
    return report


def batch_sms_bundle(
    messages: List[Dict[str, str]],
    max_batch_size: int = 20,
    require_approval: bool = True,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    批量短信模板
    
    Args:
        messages: 消息列表 [{"to": "phone", "message": "..."}, ...]
        max_batch_size: 最大批次大小
        require_approval: 是否需要审批
        dry_run: 是否预演模式
        
    Returns:
        执行结果
    """
    from orchestration.workflows.parallel_steps import parallel_send_messages
    from config.safety_controls import check_approval_required
    
    # 检查批次大小
    if len(messages) > max_batch_size:
        return {
            "success": False,
            "error": f"批次大小超过限制: {len(messages)} > {max_batch_size}"
        }
    
    # 检查审批
    if require_approval and not dry_run:
        approval_check = check_approval_required("batch_sms", len(messages))
        if approval_check.get("approval_required"):
            return {
                "success": False,
                "requires_approval": True,
                "message": "批量短信需要审批"
            }
    
    # 预演
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": f"预演模式：将发送 {len(messages)} 条短信"
        }
    
    # 并行发送
    result = parallel_send_messages(
        recipients=[{"to": m["to"], "name": m.get("name", "")} for m in messages],
        message_template="{name}" + " " + next((m["message"] for m in messages if "message" in m), ""),
        dry_run=False
    )
    
    return result


def run(**kwargs):
    """模板入口"""
    return batch_notify_bundle(**kwargs)
