"""查询备忘录能力"""

from typing import Optional, Dict, Any
import json


def query_note(
    note_id: Optional[str] = None,
    entity_id: Optional[str] = None,
    title: Optional[str] = None,
) -> Dict[str, Any]:
    """
    查询备忘录
    
    Args:
        note_id: 备忘录ID
        entity_id: 实体ID（用于追踪）
        title: 标题（模糊匹配）
        
    Returns:
        包含备忘录信息的字典
    """
    from platform_adapter import invocation_ledger as ledger_module
    
    pass
    
    # 查询 STORAGE 类型的记录
    records = ledger_module.query_by_capability(capability="STORAGE", limit=100)
    
    # 过滤
    filtered = []
    for r in records:
        request_params = r.get("request_params", {})
        if isinstance(request_params, str):
            try:
                request_params = json.loads(request_params)
            except:
                request_params = {}
        
        # 检查 note_id
        if note_id:
            if request_params.get("note_id") != note_id:
                continue
        
        # 检查 entity_id
        if entity_id:
            if request_params.get("entity_id") != entity_id:
                continue
        
        # 检查标题
        if title:
            note_title = request_params.get("title", "")
            if title.lower() not in note_title.lower():
                continue
        
        filtered.append({
            "invocation_id": r.get("id"),
            "note_id": request_params.get("note_id"),
            "entity_id": request_params.get("entity_id"),
            "title": request_params.get("title"),
            "content": request_params.get("content", "")[:100] + "..." if len(request_params.get("content", "")) > 100 else request_params.get("content", ""),
            "status": r.get("status"),
            "normalized_status": r.get("normalized_status"),
            "created_at": r.get("created_at"),
        })
    
    return {
        "success": True,
        "count": len(filtered),
        "notes": filtered
    }


def run(**kwargs):
    """能力入口"""
    return query_note(**kwargs)
