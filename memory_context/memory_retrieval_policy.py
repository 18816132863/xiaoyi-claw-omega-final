#!/usr/bin/env python3
"""记忆检索策略 - V1.0.0

决定什么时候取记忆、取哪些记忆、按什么顺序返回，解决旧信息干扰当前任务。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RetrievalConfig:
    """检索配置"""
    min_score: float = 0.5
    max_results: int = 10
    prefer_recent: bool = True
    filter_low_relevance: bool = True


@dataclass
class RetrievedMemory:
    """检索到的记忆"""
    id: str
    content: str
    score: float
    memory_type: str
    updated_at: str
    relevance: float


class MemoryRetrievalPolicy:
    """记忆检索策略"""
    
    def __init__(self):
        self.config = RetrievalConfig()
    
    def retrieve(
        self,
        query: str,
        memories: List[Dict[str, Any]],
        config: RetrievalConfig = None
    ) -> List[RetrievedMemory]:
        """
        检索记忆
        
        Args:
            query: 查询文本
            memories: 记忆列表
            config: 检索配置
        
        Returns:
            List[RetrievedMemory]
        """
        if config is None:
            config = self.config
        
        if not memories:
            return []
        
        # 1. 计算相关性分数
        scored_memories = []
        for mem in memories:
            score = self._calculate_score(query, mem)
            
            # 过滤低相关性
            if config.filter_low_relevance and score < config.min_score:
                continue
            
            scored_memories.append(RetrievedMemory(
                id=mem.get("id", ""),
                content=mem.get("content", ""),
                score=score,
                memory_type=mem.get("memory_type", "unknown"),
                updated_at=mem.get("updated_at", ""),
                relevance=score
            ))
        
        # 2. 排序
        if config.prefer_recent:
            scored_memories.sort(key=lambda m: (m.score, m.updated_at), reverse=True)
        else:
            scored_memories.sort(key=lambda m: m.score, reverse=True)
        
        # 3. 限制返回条数
        return scored_memories[:config.max_results]
    
    def _calculate_score(self, query: str, memory: Dict) -> float:
        """计算相关性分数"""
        content = memory.get("content", "").lower()
        query_lower = query.lower()
        
        # 基础分数：关键词匹配
        query_words = set(query_lower.split())
        content_words = set(content.split())
        
        if not query_words:
            return 0.0
        
        # Jaccard 相似度
        intersection = len(query_words & content_words)
        union = len(query_words | content_words)
        
        jaccard = intersection / union if union > 0 else 0.0
        
        # 时间衰减
        updated_at = memory.get("updated_at", "")
        time_decay = self._calculate_time_decay(updated_at)
        
        # 类型权重
        type_weight = self._get_type_weight(memory.get("memory_type", ""))
        
        # 综合分数
        score = jaccard * 0.5 + time_decay * 0.3 + type_weight * 0.2
        
        return min(score, 1.0)
    
    def _calculate_time_decay(self, updated_at: str) -> float:
        """计算时间衰减"""
        if not updated_at:
            return 0.5
        
        try:
            # 解析时间
            if "T" in updated_at:
                mem_time = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            else:
                mem_time = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")
            
            # 计算天数差
            now = datetime.now()
            days_diff = (now - mem_time.replace(tzinfo=None)).days
            
            # 指数衰减
            decay = 1.0 / (1.0 + days_diff / 30.0)  # 30天半衰期
            
            return decay
        except:
            return 0.5
    
    def _get_type_weight(self, memory_type: str) -> float:
        """获取类型权重"""
        weights = {
            "user_preference": 0.9,
            "user_profile": 0.9,
            "long_term_goal": 0.8,
            "important_fact": 0.8,
            "project_state": 0.7,
            "temporary": 0.3
        }
        
        return weights.get(memory_type, 0.5)
    
    def filter_conflicting(self, memories: List[RetrievedMemory]) -> List[RetrievedMemory]:
        """过滤冲突记忆"""
        # 简单实现：保留高分，去除低分冲突
        seen_content = set()
        filtered = []
        
        for mem in memories:
            content_key = mem.content[:50].lower()  # 取前50字符作为key
            
            if content_key not in seen_content:
                seen_content.add(content_key)
                filtered.append(mem)
        
        return filtered


# 全局实例
_retrieval_policy: Optional[MemoryRetrievalPolicy] = None

def get_retrieval_policy() -> MemoryRetrievalPolicy:
    """获取全局检索策略"""
    global _retrieval_policy
    if _retrieval_policy is None:
        _retrieval_policy = MemoryRetrievalPolicy()
    return _retrieval_policy

def retrieve_memories(query: str, memories: List[Dict], max_results: int = 10) -> List[RetrievedMemory]:
    """检索记忆（便捷函数）"""
    policy = get_retrieval_policy()
    config = RetrievalConfig(max_results=max_results)
    return policy.retrieve(query, memories, config)
