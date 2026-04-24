#!/usr/bin/env python3
"""
rewriter - V4.3.2 融合版

融合自:
- core/query/rewriter.py
- memory_context/search/rewriter.py

此模块为统一实现，其他位置通过兼容层引用
"""

from typing import List, Dict, Any, Optional
import re

class QueryRewriter:
    """查询重写器"""
    
    def __init__(self):
        self._rules = [
            (r"\b(找|查|搜|寻找)\b", "搜索"),
            (r"\b(怎么|如何)\b", "方法"),
            (r"\b(什么|啥)\b", "定义"),
        ]
    
    def rewrite(self, query: str) -> str:
        """重写查询"""
        result = query
        for pattern, replacement in self._rules:
            result = re.sub(pattern, replacement, result)
        return result.strip()
    
    def expand(self, query: str) -> List[str]:
        """扩展查询"""
        expansions = [query]
        
        # 同义词扩展
        synonyms = {
            "搜索": ["查找", "寻找", "检索"],
            "创建": ["新建", "添加", "生成"],
            "删除": ["移除", "清除", "去掉"],
        }
        
        for word, syns in synonyms.items():
            if word in query:
                for syn in syns:
                    expansions.append(query.replace(word, syn))
        
        return expansions

# 全局实例
_rewriter: Optional[QueryRewriter] = None

def get_rewriter() -> QueryRewriter:
    global _rewriter
    if _rewriter is None:
        _rewriter = QueryRewriter()
    return _rewriter
