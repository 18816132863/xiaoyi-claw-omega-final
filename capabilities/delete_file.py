"""删除文件能力"""

from typing import Dict, Any


def delete_file(
    file_id: str,
    permanent: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    删除文件
    
    Args:
        file_id: 文件ID
        permanent: 是否永久删除（否则移到回收站）
        dry_run: 是否预演模式
        
    Returns:
        删除结果
    """
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "action": "delete_file",
            "file_id": file_id,
            "permanent": permanent,
            "message": "预演模式：将删除文件" + ("（永久）" if permanent else "（移到回收站）")
        }
    
    # TODO: 调用小艺文件删除接口
    return {
        "success": True,
        "file_id": file_id,
        "permanent": permanent,
        "deleted": True,
        "message": "文件已删除" + ("（永久）" if permanent else "（已移到回收站）")
    }


def delete_files_batch(
    file_ids: list,
    permanent: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    批量删除文件
    
    Args:
        file_ids: 文件ID列表
        permanent: 是否永久删除
        dry_run: 是否预演模式
        
    Returns:
        删除结果
    """
    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "action": "delete_files_batch",
            "count": len(file_ids),
            "message": f"预演模式：将删除 {len(file_ids)} 个文件"
        }
    
    if len(file_ids) > 20:
        return {
            "success": False,
            "error": f"批次大小超过限制: {len(file_ids)} > 20"
        }
    
    deleted = []
    failed = []
    
    for file_id in file_ids:
        result = delete_file(file_id, permanent=permanent, dry_run=False)
        if result.get("success"):
            deleted.append(file_id)
        else:
            failed.append(file_id)
    
    return {
        "success": len(failed) == 0,
        "deleted_count": len(deleted),
        "failed_count": len(failed),
        "deleted": deleted,
        "failed": failed
    }


def run(**kwargs):
    """能力入口"""
    if "file_ids" in kwargs:
        return delete_files_batch(**kwargs)
    else:
        return delete_file(**kwargs)
