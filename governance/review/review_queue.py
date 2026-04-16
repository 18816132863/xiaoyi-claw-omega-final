"""
Review Queue - 审查队列
高风险任务真实入队，不只是布尔值标记
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import uuid


class ReviewStatus(Enum):
    """审查状态"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    TIMEOUT = "timeout"


class ReviewPriority(Enum):
    """审查优先级"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ReviewItem:
    """审查项"""
    review_id: str
    task_id: str
    profile: str
    reason: str
    status: ReviewStatus
    priority: ReviewPriority
    decision_id: str
    created_at: str
    updated_at: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    review_comment: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "review_id": self.review_id,
            "task_id": self.task_id,
            "profile": self.profile,
            "reason": self.reason,
            "status": self.status.value,
            "priority": self.priority.value,
            "decision_id": self.decision_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at,
            "review_comment": self.review_comment,
            "metadata": self.metadata
        }


class ReviewQueue:
    """
    审查队列
    
    高风险任务真实入队：
    - review_id: 审查唯一标识
    - task_id: 任务 ID
    - profile: 配置文件名
    - reason: 审查原因
    - status: 审查状态 (pending/approved/rejected/escalated/timeout)
    - created_at: 创建时间
    """
    
    def __init__(self):
        self._queue: Dict[str, ReviewItem] = {}
        self._pending: List[str] = []  # 待审查队列
        self._task_index: Dict[str, str] = {}  # task_id -> review_id
        self._decision_index: Dict[str, str] = {}  # decision_id -> review_id
    
    def enqueue(
        self,
        task_id: str,
        profile: str,
        reason: str,
        decision_id: str = "",
        priority: int = 2,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ReviewItem:
        """
        入队审查
        
        Args:
            task_id: 任务 ID
            profile: 配置文件名
            reason: 审查原因
            decision_id: 决策 ID
            priority: 优先级
            metadata: 元数据
            
        Returns:
            审查项
        """
        timestamp = datetime.now().isoformat()
        review_id = f"rev_{uuid.uuid4().hex[:12]}"
        
        # 转换 priority 为枚举
        if isinstance(priority, int):
            priority_enum = ReviewPriority(priority)
        else:
            priority_enum = priority
        
        item = ReviewItem(
            review_id=review_id,
            task_id=task_id,
            profile=profile,
            reason=reason,
            status=ReviewStatus.PENDING,
            priority=priority_enum,
            decision_id=decision_id,
            created_at=timestamp,
            updated_at=timestamp,
            metadata=metadata or {}
        )
        
        # 存储并入队
        self._queue[review_id] = item
        self._pending.append(review_id)
        
        # 更新索引
        self._task_index[task_id] = review_id
        if decision_id:
            self._decision_index[decision_id] = review_id
        
        return item
    
    def dequeue(self, review_id: str) -> Optional[ReviewItem]:
        """
        出队审查项
        
        Args:
            review_id: 审查 ID
            
        Returns:
            审查项，不存在返回 None
        """
        return self._queue.get(review_id)
    
    def approve(
        self,
        review_id: str,
        reviewer: str = "system",
        comment: str = ""
    ) -> bool:
        """
        批准审查
        
        Args:
            review_id: 审查 ID
            reviewer: 审查人
            comment: 审查意见
            
        Returns:
            是否成功
        """
        item = self._queue.get(review_id)
        if not item or item.status != ReviewStatus.PENDING:
            return False
        
        item.status = ReviewStatus.APPROVED
        item.reviewed_by = reviewer
        item.reviewed_at = datetime.now().isoformat()
        item.review_comment = comment
        item.updated_at = datetime.now().isoformat()
        
        # 从待审查队列移除
        if review_id in self._pending:
            self._pending.remove(review_id)
        
        return True
    
    def reject(
        self,
        review_id: str,
        reviewer: str = "system",
        comment: str = ""
    ) -> bool:
        """
        拒绝审查
        
        Args:
            review_id: 审查 ID
            reviewer: 审查人
            comment: 审查意见
            
        Returns:
            是否成功
        """
        item = self._queue.get(review_id)
        if not item or item.status != ReviewStatus.PENDING:
            return False
        
        item.status = ReviewStatus.REJECTED
        item.reviewed_by = reviewer
        item.reviewed_at = datetime.now().isoformat()
        item.review_comment = comment
        item.updated_at = datetime.now().isoformat()
        
        # 从待审查队列移除
        if review_id in self._pending:
            self._pending.remove(review_id)
        
        return True
    
    def escalate(
        self,
        review_id: str,
        reason: str = ""
    ) -> bool:
        """
        升级审查
        
        Args:
            review_id: 审查 ID
            reason: 升级原因
            
        Returns:
            是否成功
        """
        item = self._queue.get(review_id)
        if not item:
            return False
        
        item.status = ReviewStatus.ESCALATED
        item.priority = ReviewPriority.CRITICAL
        item.updated_at = datetime.now().isoformat()
        item.metadata["escalation_reason"] = reason
        
        return True
    
    def get_pending(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取待审查列表
        
        Args:
            limit: 返回数量限制
            
        Returns:
            待审查项列表
        """
        items = [
            self._queue[rid]
            for rid in self._pending
            if rid in self._queue
        ]
        
        # 按优先级排序
        items.sort(key=lambda x: x.priority.value, reverse=True)
        
        return [item.to_dict() for item in items[:limit]]
    
    def get_by_task(self, task_id: str) -> Optional[ReviewItem]:
        """
        按任务 ID 获取审查项
        
        Args:
            task_id: 任务 ID
            
        Returns:
            审查项，不存在返回 None
        """
        review_id = self._task_index.get(task_id)
        if review_id:
            return self._queue.get(review_id)
        return None
    
    def get_by_decision(self, decision_id: str) -> Optional[ReviewItem]:
        """
        按决策 ID 获取审查项
        
        Args:
            decision_id: 决策 ID
            
        Returns:
            审查项，不存在返回 None
        """
        review_id = self._decision_index.get(decision_id)
        if review_id:
            return self._queue.get(review_id)
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息
        """
        total = len(self._queue)
        if total == 0:
            return {
                "total": 0,
                "pending": 0,
                "approved": 0,
                "rejected": 0,
                "escalated": 0
            }
        
        stats = {
            "total": total,
            "pending": 0,
            "approved": 0,
            "rejected": 0,
            "escalated": 0,
            "timeout": 0
        }
        
        for item in self._queue.values():
            status = item.status.value
            if status in stats:
                stats[status] += 1
        
        return stats
    
    def cleanup_old(self, days: int = 30) -> int:
        """
        清理旧记录
        
        Args:
            days: 保留天数
            
        Returns:
            清理数量
        """
        # 简化实现：保留所有记录
        return 0
    
    def export(self, format: str = "json") -> str:
        """
        导出队列
        
        Args:
            format: 导出格式
            
        Returns:
            导出内容
        """
        if format == "json":
            data = [item.to_dict() for item in self._queue.values()]
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported format: {format}")


# 全局单例
_review_queue = None

def get_review_queue() -> ReviewQueue:
    """获取审查队列单例"""
    global _review_queue
    if _review_queue is None:
        _review_queue = ReviewQueue()
    return _review_queue
