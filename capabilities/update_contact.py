"""更新联系人能力"""

from typing import Optional, Dict, Any


def update_contact(
    contact_id: str,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    company: Optional[str] = None,
    notes: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    更新联系人
    
    Args:
        contact_id: 联系人ID
        name: 新姓名
        phone: 新电话
        email: 新邮箱
        company: 新公司
        notes: 新备注
        dry_run: 是否预演模式
        
    Returns:
        更新结果
    """
    updates = {}
    if name:
        updates["name"] = name
    if phone:
        updates["phone"] = phone
    if email:
        updates["email"] = email
    if company:
        updates["company"] = company
    if notes:
        updates["notes"] = notes
    
    if not updates:
        return {
            "success": False,
            "error": "没有提供要更新的字段"
        }
    
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "action": "update_contact",
            "contact_id": contact_id,
            "updates": updates,
            "message": "预演模式：将更新联系人"
        }
    
    # TODO: 调用小艺联系人更新接口
    return {
        "success": True,
        "contact_id": contact_id,
        "updates": updates,
        "message": "联系人已更新"
    }


def run(**kwargs):
    """能力入口"""
    return update_contact(**kwargs)
