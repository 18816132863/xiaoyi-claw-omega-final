"""删除联系人能力"""

from typing import Dict, Any


def delete_contact(
    contact_id: str,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    删除联系人
    
    Args:
        contact_id: 联系人ID
        dry_run: 是否预演模式
        
    Returns:
        删除结果
    """
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "action": "delete_contact",
            "contact_id": contact_id,
            "message": "预演模式：将删除联系人"
        }
    
    # TODO: 调用小艺联系人删除接口
    return {
        "success": True,
        "contact_id": contact_id,
        "deleted": True,
        "message": "联系人已删除"
    }


def run(**kwargs):
    """能力入口"""
    return delete_contact(**kwargs)
