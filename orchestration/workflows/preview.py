"""工作流预演模式"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PreviewResult:
    """预演结果"""
    step_name: str
    capability: str
    params: Dict[str, Any]
    will_execute: bool
    estimated_effects: List[str]
    warnings: List[str]


def preview_workflow(
    steps: List[Dict[str, Any]],
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    预览工作流执行效果
    
    Args:
        steps: 步骤列表
        context: 执行上下文
        
    Returns:
        预览结果
    """
    context = context or {}
    previews = []
    all_effects = []
    all_warnings = []
    
    for step in steps:
        preview = _preview_step(step, context)
        previews.append(preview)
        all_effects.extend(preview.get("estimated_effects", []))
        all_warnings.extend(preview.get("warnings", []))
    
    return {
        "success": True,
        "preview_mode": True,
        "total_steps": len(steps),
        "previews": previews,
        "all_estimated_effects": all_effects,
        "all_warnings": all_warnings,
        "has_warnings": len(all_warnings) > 0,
        "generated_at": datetime.now().isoformat()
    }


def _preview_step(step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """预览单个步骤"""
    capability = step.get("capability", "unknown")
    params = step.get("params", {})
    
    # 定义每个能力的预估效果
    effects_map = {
        "send_message": [
            f"将发送短信到: {params.get('to', '未知号码')}",
            f"消息内容: {params.get('message', '')[:50]}..."
        ],
        "schedule_task": [
            f"将创建日程: {params.get('title', '无标题')}",
            f"开始时间: {params.get('start_time', '未知')}",
            f"结束时间: {params.get('end_time', '未知')}"
        ],
        "create_note": [
            f"将创建备忘录: {params.get('title', '无标题')}",
            f"内容长度: {len(params.get('content', ''))} 字符"
        ],
        "send_notification": [
            f"将推送通知: {params.get('title', '无标题')}",
            f"内容: {params.get('content', '')[:50]}..."
        ],
        "delete_calendar_event": [
            f"将删除日程: {params.get('event_id', '未知')}",
            "此操作不可撤销"
        ],
        "delete_note": [
            f"将删除备忘录: {params.get('note_id', '未知')}",
            "此操作不可撤销"
        ],
        "cancel_notification": [
            f"将取消通知: {params.get('notification_id', '未知')}"
        ]
    }
    
    # 定义警告
    warnings_map = {
        "send_message": ["短信发送会产生费用"] if params.get("to") else ["未指定收件人"],
        "delete_calendar_event": ["删除操作不可撤销"],
        "delete_note": ["删除操作不可撤销"],
        "cancel_notification": ["取消后需要重新发送"]
    }
    
    effects = effects_map.get(capability, [f"将执行能力: {capability}"])
    warnings = warnings_map.get(capability, [])
    
    # 检查参数完整性
    if capability in ["send_message"]:
        if not params.get("to"):
            warnings.append("缺少收件人")
        if not params.get("message"):
            warnings.append("缺少消息内容")
    
    if capability in ["schedule_task"]:
        if not params.get("title"):
            warnings.append("缺少日程标题")
        if not params.get("start_time"):
            warnings.append("缺少开始时间")
    
    return {
        "step_name": step.get("name", capability),
        "capability": capability,
        "params": params,
        "will_execute": True,
        "estimated_effects": effects,
        "warnings": warnings
    }


def dry_run_workflow(
    steps: List[Dict[str, Any]],
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    干运行工作流（不产生实际副作用）
    
    Args:
        steps: 步骤列表
        context: 执行上下文
        
    Returns:
        干运行结果
    """
    context = context or {}
    results = []
    
    for step in steps:
        capability = step.get("capability")
        params = step.get("params", {})
        
        # 模拟执行
        result = {
            "step": step.get("name", capability),
            "capability": capability,
            "dry_run": True,
            "simulated": True,
            "would_execute": True,
            "params": params
        }
        
        # 模拟成功
        result["simulated_result"] = {
            "success": True,
            "dry_run": True,
            "message": f"[DRY RUN] 将执行 {capability}"
        }
        
        results.append(result)
    
    return {
        "success": True,
        "dry_run": True,
        "message": "干运行完成，未产生实际副作用",
        "total_steps": len(steps),
        "results": results
    }


def compare_preview_and_actual(
    preview: Dict[str, Any],
    actual: Dict[str, Any],
) -> Dict[str, Any]:
    """
    比较预览和实际执行结果
    
    Args:
        preview: 预览结果
        actual: 实际执行结果
        
    Returns:
        比较结果
    """
    differences = []
    
    preview_steps = {p["step_name"]: p for p in preview.get("previews", [])}
    actual_steps = {r.get("step"): r for r in actual.get("results", [])}
    
    for step_name, preview_step in preview_steps.items():
        actual_step = actual_steps.get(step_name)
        
        if not actual_step:
            differences.append({
                "step": step_name,
                "type": "missing",
                "message": "步骤未执行"
            })
            continue
        
        if preview_step.get("will_execute") and not actual_step.get("success"):
            differences.append({
                "step": step_name,
                "type": "failure",
                "message": f"步骤执行失败: {actual_step.get('error', '未知错误')}"
            })
    
    return {
        "success": len(differences) == 0,
        "differences": differences,
        "preview_total": len(preview_steps),
        "actual_total": len(actual_steps)
    }
