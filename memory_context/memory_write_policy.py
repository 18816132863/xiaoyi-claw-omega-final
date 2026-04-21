#!/usr/bin/env python3
"""记忆写入策略 - V1.0.0

决定什么内容可以写入长期记忆，解决记忆乱写、上下文污染、幻觉变重。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class MemoryType(Enum):
    """记忆类型"""
    USER_PREFERENCE = "user_preference"
    USER_PROFILE = "user_profile"
    LONG_TERM_GOAL = "long_term_goal"
    IMPORTANT_FACT = "important_fact"
    PROJECT_STATE = "project_state"
    TEMPORARY = "temporary"


@dataclass
class WriteDecision:
    """写入决策"""
    should_write: bool
    reason: str
    memory_type: MemoryType
    confidence: float
    deduplicated: bool


class MemoryWritePolicy:
    """记忆写入策略"""
    
    def __init__(self):
        self.min_confidence = 0.7
        self.max_similar_count = 3
        self.existing_memories: List[Dict] = []
    
    def should_write(
        self,
        content: str,
        memory_type: MemoryType,
        confidence: float,
        metadata: Dict[str, Any] = None
    ) -> WriteDecision:
        """
        判断是否应该写入记忆
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型
            confidence: 置信度
            metadata: 元数据
        
        Returns:
            WriteDecision
        """
        # 1. 低置信度不写
        if confidence < self.min_confidence:
            return WriteDecision(
                should_write=False,
                reason=f"置信度过低: {confidence:.2f} < {self.min_confidence}",
                memory_type=memory_type,
                confidence=confidence,
                deduplicated=False
            )
        
        # 2. 重复内容不写
        if self._is_duplicate(content):
            return WriteDecision(
                should_write=False,
                reason="内容重复",
                memory_type=memory_type,
                confidence=confidence,
                deduplicated=True
            )
        
        # 3. 临时报错不写
        if self._is_temporary_error(content):
            return WriteDecision(
                should_write=False,
                reason="临时错误信息",
                memory_type=MemoryType.TEMPORARY,
                confidence=confidence,
                deduplicated=False
            )
        
        # 4. 检查是否为长期有价值内容
        if not self._is_long_term_valuable(content, memory_type):
            return WriteDecision(
                should_write=False,
                reason="非长期有价值内容",
                memory_type=memory_type,
                confidence=confidence,
                deduplicated=False
            )
        
        return WriteDecision(
            should_write=True,
            reason="符合写入条件",
            memory_type=memory_type,
            confidence=confidence,
            deduplicated=False
        )
    
    def _is_duplicate(self, content: str) -> bool:
        """检查是否重复"""
        content_lower = content.lower().strip()
        
        for mem in self.existing_memories:
            existing = mem.get("content", "").lower().strip()
            
            # 完全相同
            if content_lower == existing:
                return True
            
            # 高度相似 (> 80%)
            if self._similarity(content_lower, existing) > 0.8:
                return True
        
        return False
    
    def _similarity(self, text1: str, text2: str) -> float:
        """计算相似度（简单实现）"""
        if not text1 or not text2:
            return 0.0
        
        # Jaccard 相似度
        set1 = set(text1)
        set2 = set(text2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _is_temporary_error(self, content: str) -> bool:
        """检查是否为临时错误"""
        error_keywords = [
            "error:", "exception:", "failed:", "timeout",
            "connection refused", "network error", "临时"
        ]
        
        content_lower = content.lower()
        return any(kw in content_lower for kw in error_keywords)
    
    def _is_long_term_valuable(self, content: str, memory_type: MemoryType) -> bool:
        """检查是否为长期有价值内容"""
        # 用户偏好、档案、目标、重要事实、项目状态 都是长期有价值的
        if memory_type in [
            MemoryType.USER_PREFERENCE,
            MemoryType.USER_PROFILE,
            MemoryType.LONG_TERM_GOAL,
            MemoryType.IMPORTANT_FACT,
            MemoryType.PROJECT_STATE
        ]:
            return True
        
        # 临时类型需要检查内容
        if memory_type == MemoryType.TEMPORARY:
            return False
        
        # 检查内容长度
        if len(content) < 10:
            return False
        
        return True
    
    def load_existing_memories(self, memories: List[Dict]):
        """加载已有记忆"""
        self.existing_memories = memories


# 全局实例
_write_policy: Optional[MemoryWritePolicy] = None

def get_write_policy() -> MemoryWritePolicy:
    """获取全局写入策略"""
    global _write_policy
    if _write_policy is None:
        _write_policy = MemoryWritePolicy()
    return _write_policy

def should_write_memory(content: str, memory_type: str, confidence: float) -> WriteDecision:
    """判断是否应该写入记忆（便捷函数）"""
    policy = get_write_policy()
    mem_type = MemoryType(memory_type) if memory_type in [e.value for e in MemoryType] else MemoryType.TEMPORARY
    return policy.should_write(content, mem_type, confidence)
