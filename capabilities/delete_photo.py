"""删除照片能力"""

from typing import Optional, Dict, Any


def delete_photo(
    photo_id: str,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    删除照片
    
    Args:
        photo_id: 照片ID
        dry_run: 是否预演模式
        
    Returns:
        删除结果
    """
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "action": "delete_photo",
            "photo_id": photo_id,
            "message": "预演模式：将删除照片"
        }
    
    # TODO: 调用小艺图库删除接口
    return {
        "success": True,
        "photo_id": photo_id,
        "deleted": True,
        "message": "照片已删除"
    }


def delete_photos_batch(
    photo_ids: list,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    批量删除照片
    
    Args:
        photo_ids: 照片ID列表
        dry_run: 是否预演模式
        
    Returns:
        删除结果
    """
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "action": "delete_photos_batch",
            "count": len(photo_ids),
            "message": f"预演模式：将删除 {len(photo_ids)} 张照片"
        }
    
    # 检查批次大小
    if len(photo_ids) > 20:
        return {
            "success": False,
            "error": f"批次大小超过限制: {len(photo_ids)} > 20"
        }
    
    deleted = []
    failed = []
    
    for photo_id in photo_ids:
        result = delete_photo(photo_id, dry_run=False)
        if result.get("success"):
            deleted.append(photo_id)
        else:
            failed.append(photo_id)
    
    return {
        "success": len(failed) == 0,
        "deleted_count": len(deleted),
        "failed_count": len(failed),
        "deleted": deleted,
        "failed": failed
    }


def run(**kwargs):
    """能力入口"""
    if "photo_ids" in kwargs:
        return delete_photos_batch(**kwargs)
    else:
        return delete_photo(**kwargs)
