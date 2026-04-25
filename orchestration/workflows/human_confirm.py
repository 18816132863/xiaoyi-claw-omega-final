"""工作流人工确认节点"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import uuid


class HumanConfirmState(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


# 简单的状态存储（生产环境应使用数据库）
_pending_confirms = {}


def create_human_confirm_node(
    invocation_id: int,
    reason: str,
    options: Optional[List[str]] = None,
    timeout_seconds: int = 3600,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    创建人工确认节点
    
    Args:
        invocation_id: 需要确认的调用记录ID
        reason: 确认原因
        options: 可选项列表
        timeout_seconds: 超时时间（秒）
        context: 上下文信息
        
    Returns:
        确认节点信息
    """
    from enum import Enum
    
    confirm_id = f"confirm_{uuid.uuid4().hex[:16]}"
    
    confirm_node = {
        "confirm_id": confirm_id,
        "invocation_id": invocation_id,
        "reason": reason,
        "options": options or ["confirmed_success", "confirmed_failed"],
        "state": "pending",
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + __import__("datetime").timedelta(seconds=timeout_seconds)).isoformat(),
        "context": context or {},
        "response": None,
        "responded_at": None
    }
    
    _pending_confirms[confirm_id] = confirm_node
    
    return {
        "success": True,
        "confirm_id": confirm_id,
        "state": "pending",
        "message": f"已创建人工确认节点，等待确认",
        "options": confirm_node["options"],
        "expires_at": confirm_node["expires_at"]
    }


def get_pending_confirms() -> List[Dict[str, Any]]:
    """获取所有待确认节点"""
    now = datetime.now()
    
    # 检查超时
    for confirm_id, node in list(_pending_confirms.items()):
        if node["state"] == "pending":
            expires_at = datetime.fromisoformat(node["expires_at"])
            if now > expires_at:
                node["state"] = "timeout"
    
    return [n for n in _pending_confirms.values() if n["state"] == "pending"]


def respond_to_confirm(
    confirm_id: str,
    response: str,
    note: Optional[str] = None,
) -> Dict[str, Any]:
    """
    响应确认节点
    
    Args:
        confirm_id: 确认节点ID
        response: 响应（approved / rejected 或具体选项）
        note: 备注
        
    Returns:
        响应结果
    """
    if confirm_id not in _pending_confirms:
        return {
            "success": False,
            "error": f"确认节点 {confirm_id} 不存在"
        }
    
    node = _pending_confirms[confirm_id]
    
    if node["state"] != "pending":
        return {
            "success": False,
            "error": f"确认节点已处于 {node['state']} 状态"
        }
    
    # 检查超时
    expires_at = datetime.fromisoformat(node["expires_at"])
    if datetime.now() > expires_at:
        node["state"] = "timeout"
        return {
            "success": False,
            "error": "确认节点已超时"
        }
    
    # 更新状态
    if response in ["approved", "confirmed_success"]:
        node["state"] = "approved"
    elif response in ["rejected", "confirmed_failed"]:
        node["state"] = "rejected"
    else:
        node["state"] = "responded"
    
    node["response"] = response
    node["responded_at"] = datetime.now().isoformat()
    node["note"] = note
    
    # 如果有关联的 invocation，更新其确认状态
    if node.get("invocation_id"):
        from platform_adapter.invocation_ledger import InvocationLedger
        ledger = InvocationLedger()
        ledger.confirm_record(
            record_id=node["invocation_id"],
            confirmed_status=response,
            confirm_note=note
        )
    
    return {
        "success": True,
        "confirm_id": confirm_id,
        "state": node["state"],
        "response": response,
        "message": f"确认已完成: {response}"
    }


def execute_with_human_confirm(
    step: Dict[str, Any],
    confirm_on_uncertain: bool = True,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    执行步骤并在 uncertain 时转人工确认
    
    Args:
        step: 步骤定义
        confirm_on_uncertain: 是否在 uncertain 时转人工
        dry_run: 是否预演模式
        
    Returns:
        执行结果
    """
    import importlib
    
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "message": "预演模式：将执行步骤并在需要时转人工确认"
        }
    
    # 执行步骤
    capability = step.get("capability")
    params = step.get("params", {})
    
    try:
        module = importlib.import_module(f"capabilities.{capability}")
        result = module.run(**params)
        
        # 检查是否需要人工确认
        if confirm_on_uncertain and result.get("normalized_status") == "result_uncertain":
            confirm_node = create_human_confirm_node(
                invocation_id=result.get("invocation_id", 0),
                reason=f"步骤 {step.get('name', capability)} 执行结果不确定，需要人工确认"
            )
            
            return {
                "success": True,
                "step_result": result,
                "needs_confirmation": True,
                "confirm_id": confirm_node["confirm_id"],
                "message": "步骤执行结果不确定，已创建人工确认节点"
            }
        
        return {
            "success": result.get("success", False),
            "step_result": result,
            "needs_confirmation": False
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
