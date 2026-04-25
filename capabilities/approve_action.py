"""审批动作能力"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


# 简单的审批存储（生产环境应使用数据库）
_pending_approvals = {}
_approved_actions = {}


def request_approval(
    action_type: str,
    action_params: Dict[str, Any],
    reason: str,
    approver: Optional[str] = None,
    timeout_hours: int = 24,
) -> Dict[str, Any]:
    """
    请求审批
    
    Args:
        action_type: 操作类型
        action_params: 操作参数
        reason: 审批原因
        approver: 审批人
        timeout_hours: 超时时间（小时）
        
    Returns:
        审批请求结果
    """
    approval_id = f"approval_{uuid.uuid4().hex[:16]}"
    
    approval_request = {
        "approval_id": approval_id,
        "action_type": action_type,
        "action_params": action_params,
        "reason": reason,
        "approver": approver,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + __import__("datetime").timedelta(hours=timeout_hours)).isoformat(),
        "approved_at": None,
        "approved_by": None,
        "rejected_at": None,
        "rejected_by": None,
        "rejection_reason": None
    }
    
    _pending_approvals[approval_id] = approval_request
    
    return {
        "success": True,
        "approval_id": approval_id,
        "status": "pending",
        "message": f"已提交审批请求，等待审批",
        "expires_at": approval_request["expires_at"]
    }


def approve_action(
    approval_id: str,
    approved_by: str,
    note: Optional[str] = None,
) -> Dict[str, Any]:
    """
    批准操作
    
    Args:
        approval_id: 审批ID
        approved_by: 审批人
        note: 备注
        
    Returns:
        批准结果
    """
    if approval_id not in _pending_approvals:
        return {
            "success": False,
            "error": f"审批请求 {approval_id} 不存在"
        }
    
    approval = _pending_approvals[approval_id]
    
    if approval["status"] != "pending":
        return {
            "success": False,
            "error": f"审批请求已处于 {approval['status']} 状态"
        }
    
    # 检查超时
    expires_at = datetime.fromisoformat(approval["expires_at"])
    if datetime.now() > expires_at:
        approval["status"] = "expired"
        return {
            "success": False,
            "error": "审批请求已过期"
        }
    
    # 批准
    approval["status"] = "approved"
    approval["approved_at"] = datetime.now().isoformat()
    approval["approved_by"] = approved_by
    approval["approval_note"] = note
    
    # 移动到已批准列表
    _approved_actions[approval_id] = approval
    del _pending_approvals[approval_id]
    
    return {
        "success": True,
        "approval_id": approval_id,
        "status": "approved",
        "approved_by": approved_by,
        "message": "操作已批准，可以执行"
    }


def reject_action(
    approval_id: str,
    rejected_by: str,
    reason: str,
) -> Dict[str, Any]:
    """
    拒绝操作
    
    Args:
        approval_id: 审批ID
        rejected_by: 拒绝人
        reason: 拒绝原因
        
    Returns:
        拒绝结果
    """
    if approval_id not in _pending_approvals:
        return {
            "success": False,
            "error": f"审批请求 {approval_id} 不存在"
        }
    
    approval = _pending_approvals[approval_id]
    
    if approval["status"] != "pending":
        return {
            "success": False,
            "error": f"审批请求已处于 {approval['status']} 状态"
        }
    
    # 拒绝
    approval["status"] = "rejected"
    approval["rejected_at"] = datetime.now().isoformat()
    approval["rejected_by"] = rejected_by
    approval["rejection_reason"] = reason
    
    del _pending_approvals[approval_id]
    
    return {
        "success": True,
        "approval_id": approval_id,
        "status": "rejected",
        "rejected_by": rejected_by,
        "reason": reason,
        "message": "操作已拒绝"
    }


def check_approval_status(approval_id: str) -> Dict[str, Any]:
    """
    检查审批状态
    
    Args:
        approval_id: 审批ID
        
    Returns:
        审批状态
    """
    # 检查待审批
    if approval_id in _pending_approvals:
        return {
            "success": True,
            "approval_id": approval_id,
            "status": _pending_approvals[approval_id]["status"],
            "is_approved": False
        }
    
    # 检查已批准
    if approval_id in _approved_actions:
        approval = _approved_actions[approval_id]
        return {
            "success": True,
            "approval_id": approval_id,
            "status": "approved",
            "is_approved": True,
            "approved_at": approval["approved_at"],
            "approved_by": approval["approved_by"]
        }
    
    return {
        "success": False,
        "error": f"审批请求 {approval_id} 不存在"
    }


def get_pending_approvals() -> List[Dict[str, Any]]:
    """获取所有待审批请求"""
    return list(_pending_approvals.values())


def execute_with_approval(
    capability: str,
    params: Dict[str, Any],
    approval_id: str,
) -> Dict[str, Any]:
    """
    在审批通过后执行操作
    
    Args:
        capability: 能力名称
        params: 参数
        approval_id: 审批ID
        
    Returns:
        执行结果
    """
    # 检查审批状态
    status = check_approval_status(approval_id)
    
    if not status.get("success"):
        return status
    
    if not status.get("is_approved"):
        return {
            "success": False,
            "error": "操作未获批准",
            "approval_status": status.get("status")
        }
    
    # 执行操作
    import importlib
    try:
        module = importlib.import_module(f"capabilities.{capability}")
        result = module.run(**params)
        
        return {
            "success": result.get("success", False),
            "approval_id": approval_id,
            "result": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def run(**kwargs):
    """能力入口"""
    action = kwargs.pop("action", "request")
    
    if action == "request":
        return request_approval(**kwargs)
    elif action == "approve":
        return approve_action(**kwargs)
    elif action == "reject":
        return reject_action(**kwargs)
    elif action == "check":
        return check_approval_status(**kwargs)
    elif action == "execute":
        return execute_with_approval(**kwargs)
    else:
        return {"success": False, "error": f"未知操作: {action}"}
