"""搜索备忘录能力"""

from typing import Optional, Dict, Any
import json


def search_notes(
    keyword: Optional[str] = None,
    title_contains: Optional[str] = None,
    content_contains: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    搜索备忘录
    
    Args:
        keyword: 关键词（同时匹配标题和内容）
        title_contains: 标题包含
        content_contains: 内容包含
        limit: 返回数量限制
        offset: 偏移量
        
    Returns:
        包含搜索结果的字典
    """
    from platform_adapter import invocation_ledger as ledger_module
    
    pass
    
    # 查询 STORAGE 类型的记录
    records = ledger_module.query_by_capability(capability="STORAGE", limit=200)
    
    # 搜索
    results = []
    for r in records:
        request_params = r.get("request_params", {})
        if isinstance(request_params, str):
            try:
                request_params = json.loads(request_params)
            except:
                request_params = {}
        
        note_title = request_params.get("title", "")
        note_content = request_params.get("content", "")
        
        # 关键词匹配
        if keyword:
            keyword_lower = keyword.lower()
            if keyword_lower not in note_title.lower() and keyword_lower not in note_content.lower():
                continue
        
        # 标题匹配
        if title_contains:
            if title_contains.lower() not in note_title.lower():
                continue
        
        # 内容匹配
        if content_contains:
            if content_contains.lower() not in note_content.lower():
                continue
        
        results.append({
            "invocation_id": r.get("id"),
            "note_id": request_params.get("note_id"),
            "title": note_title,
            "content_preview": note_content[:100] + "..." if len(note_content) > 100 else note_content,
            "status": r.get("normalized_status"),
            "created_at": r.get("created_at"),
        })
    
    # 分页
    paginated = results[offset:offset + limit]
    
    return {
        "success": True,
        "count": len(paginated),
        "total": len(results),
        "limit": limit,
        "offset": offset,
        "keyword": keyword,
        "results": paginated
    }


def run(**kwargs):
    """能力入口"""
    return search_notes(**kwargs)
