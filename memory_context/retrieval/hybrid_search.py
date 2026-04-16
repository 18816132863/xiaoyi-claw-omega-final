"""Hybrid Search - 混合检索引擎"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import time


@dataclass
class SearchResult:
    """单条检索结果"""
    id: str
    content: str
    score: float
    source_type: str
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "score": self.score,
            "source_type": self.source_type,
            "metadata": self.metadata or {}
        }


class HybridSearch:
    """
    混合检索引擎
    
    结合多种检索策略：
    - 向量检索（语义相似）
    - 关键词检索（精确匹配）
    - 规则检索（结构化过滤）
    """
    
    def __init__(
        self,
        vector_engine=None,
        keyword_engine=None,
        weights: Dict[str, float] = None
    ):
        self.vector_engine = vector_engine
        self.keyword_engine = keyword_engine
        self.weights = weights or {
            "vector": 0.6,
            "keyword": 0.4
        }
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        执行混合检索
        
        1. 分别执行向量检索和关键词检索
        2. 合并结果
        3. 加权排序
        4. 返回 Top-N
        """
        start_time = time.time()
        
        vector_results = []
        keyword_results = []
        
        # 向量检索
        if self.vector_engine:
            try:
                vector_results = self.vector_engine.search(query, max_results * 2)
            except Exception as e:
                print(f"Warning: Vector search failed: {e}")
        
        # 关键词检索
        if self.keyword_engine:
            try:
                keyword_results = self.keyword_engine.search(query, max_results * 2)
            except Exception as e:
                print(f"Warning: Keyword search failed: {e}")
        
        # 合并结果
        merged = self._merge_results(vector_results, keyword_results)
        
        # 排序并返回 Top-N
        sorted_results = sorted(
            merged,
            key=lambda x: x.get("hybrid_score", 0),
            reverse=True
        )
        
        return sorted_results[:max_results]
    
    def _merge_results(
        self,
        vector_results: List[Dict],
        keyword_results: List[Dict]
    ) -> List[Dict[str, Any]]:
        """合并检索结果"""
        merged = {}
        
        # 处理向量检索结果
        for result in vector_results:
            result_id = result.get("id", str(len(merged)))
            score = result.get("score", 0)
            
            merged[result_id] = {
                "id": result_id,
                "content": result.get("content", ""),
                "vector_score": score,
                "keyword_score": 0,
                "hybrid_score": score * self.weights["vector"],
                "source_type": result.get("source_type", "vector"),
                "metadata": result.get("metadata", {})
            }
        
        # 处理关键词检索结果
        for result in keyword_results:
            result_id = result.get("id", str(len(merged)))
            score = result.get("score", 0)
            
            if result_id in merged:
                # 已存在，合并分数
                merged[result_id]["keyword_score"] = score
                merged[result_id]["hybrid_score"] += score * self.weights["keyword"]
            else:
                # 新结果
                merged[result_id] = {
                    "id": result_id,
                    "content": result.get("content", ""),
                    "vector_score": 0,
                    "keyword_score": score,
                    "hybrid_score": score * self.weights["keyword"],
                    "source_type": result.get("source_type", "keyword"),
                    "metadata": result.get("metadata", {})
                }
        
        return list(merged.values())
    
    def set_weights(self, vector: float, keyword: float):
        """设置权重"""
        total = vector + keyword
        self.weights = {
            "vector": vector / total,
            "keyword": keyword / total
        }


class SimpleKeywordEngine:
    """简单关键词检索引擎"""
    
    def __init__(self):
        self._documents: Dict[str, Dict] = {}
    
    def index(self, doc_id: str, content: str, metadata: Dict = None):
        """索引文档"""
        self._documents[doc_id] = {
            "id": doc_id,
            "content": content,
            "metadata": metadata or {}
        }
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """关键词搜索"""
        query_terms = set(query.lower().split())
        results = []
        
        for doc_id, doc in self._documents.items():
            content_terms = set(doc["content"].lower().split())
            
            # 计算交集比例作为分数
            intersection = query_terms & content_terms
            if intersection:
                score = len(intersection) / len(query_terms)
                results.append({
                    "id": doc_id,
                    "content": doc["content"],
                    "score": score,
                    "source_type": "keyword",
                    "metadata": doc["metadata"]
                })
        
        # 排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]
    
    def clear(self):
        """清空索引"""
        self._documents.clear()
