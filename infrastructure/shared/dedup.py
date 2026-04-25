#!/usr/bin/env python3
"""
dedup - V4.3.2 融合版

融合自:
- infrastructure/shared/dedup.py
- execution/search/dedup.py
- memory_context/search/dedup.py

此模块为统一实现，其他位置通过兼容层引用
"""

from typing import List, Any, Dict, Set
import hashlib

def deduplicate(items: List[Any], key_func=None) -> List[Any]:
    """去重列表"""
    seen = set()
    result = []
    
    for item in items:
        key = key_func(item) if key_func else item
        if key not in seen:
            seen.add(key)
            result.append(item)
    
    return result

def deduplicate_dicts(items: List[Dict], key_field: str = "id") -> List[Dict]:
    """去重字典列表"""
    return deduplicate(items, key_func=lambda x: x.get(key_field))

def content_hash(content: str) -> str:
    """计算内容哈希"""
    return hashlib.md5(content.encode()).hexdigest()

def deduplicate_by_content(items: List[str]) -> List[str]:
    """按内容哈希去重"""
    seen_hashes = set()
    result = []
    
    for item in items:
        h = content_hash(item)
        if h not in seen_hashes:
            seen_hashes.add(h)
            result.append(item)
    
    return result
