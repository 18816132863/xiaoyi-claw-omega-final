"""Conflict Resolver - 上下文冲突解决"""

from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Conflict:
    """冲突记录"""
    source_a: str
    source_b: str
    conflict_type: str  # contradiction, overlap, outdated
    description: str
    resolution: str
    winner: str


class ConflictResolver:
    """
    上下文冲突解决器
    
    处理：
    - 内容矛盾
    - 内容重叠
    - 过时信息
    """
    
    def __init__(self):
        self.resolution_strategies = {
            "contradiction": self._resolve_contradiction,
            "overlap": self._resolve_overlap,
            "outdated": self._resolve_outdated
        }
        
        self.importance_order = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
    
    def resolve(
        self,
        sources: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        解决冲突
        
        Args:
            sources: 源列表
        
        Returns:
            Tuple of (resolved_sources, conflicts)
        """
        conflicts = []
        resolved = []
        seen = set()
        
        for i, source_a in enumerate(sources):
            source_id_a = source_a.get("source_id", str(i))
            
            if source_id_a in seen:
                continue
            
            # 检查与后续源的冲突
            for j, source_b in enumerate(sources[i+1:], i+1):
                source_id_b = source_b.get("source_id", str(j))
                
                conflict = self._detect_conflict(source_a, source_b)
                if conflict:
                    conflicts.append({
                        "source_a": conflict.source_a,
                        "source_b": conflict.source_b,
                        "conflict_type": conflict.conflict_type,
                        "description": conflict.description,
                        "resolution": conflict.resolution,
                        "winner": conflict.winner
                    })
                    
                    # 标记失败者
                    if conflict.winner == source_id_a:
                        seen.add(source_id_b)
                    else:
                        seen.add(source_id_a)
                        break
            
            if source_id_a not in seen:
                resolved.append(source_a)
        
        return resolved, conflicts
    
    def _detect_conflict(
        self,
        source_a: Dict[str, Any],
        source_b: Dict[str, Any]
    ) -> Optional[Conflict]:
        """检测冲突"""
        # 检查内容矛盾
        if self._is_contradiction(source_a, source_b):
            return self._resolve_contradiction(source_a, source_b)
        
        # 检查内容重叠
        if self._is_overlap(source_a, source_b):
            return self._resolve_overlap(source_a, source_b)
        
        # 检查过时信息
        if self._is_outdated(source_a, source_b):
            return self._resolve_outdated(source_a, source_b)
        
        return None
    
    def _is_contradiction(
        self,
        source_a: Dict[str, Any],
        source_b: Dict[str, Any]
    ) -> bool:
        """检查是否矛盾"""
        # 简单实现：检查是否有明确的否定词
        content_a = source_a.get("content", "").lower()
        content_b = source_b.get("content", "").lower()
        
        # TODO: 实现更复杂的矛盾检测
        return False
    
    def _is_overlap(
        self,
        source_a: Dict[str, Any],
        source_b: Dict[str, Any]
    ) -> bool:
        """检查是否重叠"""
        content_a = set(source_a.get("content", "").lower().split())
        content_b = set(source_b.get("content", "").lower().split())
        
        if not content_a or not content_b:
            return False
        
        # 计算重叠比例
        intersection = content_a & content_b
        min_size = min(len(content_a), len(content_b))
        
        return len(intersection) / min_size > 0.8 if min_size > 0 else False
    
    def _is_outdated(
        self,
        source_a: Dict[str, Any],
        source_b: Dict[str, Any]
    ) -> bool:
        """检查是否过时"""
        time_a = source_a.get("created_at")
        time_b = source_b.get("created_at")
        
        if not time_a or not time_b:
            return False
        
        # 如果同类型且时间差距大
        if source_a.get("type") == source_b.get("type"):
            try:
                if isinstance(time_a, str):
                    dt_a = datetime.fromisoformat(time_a)
                else:
                    dt_a = time_a
                
                if isinstance(time_b, str):
                    dt_b = datetime.fromisoformat(time_b)
                else:
                    dt_b = time_b
                
                # 如果差距超过 30 天
                from datetime import timedelta
                return abs((dt_a - dt_b).days) > 30
            except:
                pass
        
        return False
    
    def _resolve_contradiction(
        self,
        source_a: Dict[str, Any],
        source_b: Dict[str, Any]
    ) -> Conflict:
        """解决矛盾"""
        # 按重要性选择
        imp_a = self.importance_order.get(
            source_a.get("importance", "medium"), 2
        )
        imp_b = self.importance_order.get(
            source_b.get("importance", "medium"), 2
        )
        
        if imp_a >= imp_b:
            winner = source_a.get("source_id", "a")
        else:
            winner = source_b.get("source_id", "b")
        
        return Conflict(
            source_a=source_a.get("source_id", "a"),
            source_b=source_b.get("source_id", "b"),
            conflict_type="contradiction",
            description="内容矛盾",
            resolution="选择重要性更高的源",
            winner=winner
        )
    
    def _resolve_overlap(
        self,
        source_a: Dict[str, Any],
        source_b: Dict[str, Any]
    ) -> Conflict:
        """解决重叠"""
        # 按相关性选择
        rel_a = source_a.get("relevance", 0.5)
        rel_b = source_b.get("relevance", 0.5)
        
        winner = source_a.get("source_id", "a") if rel_a >= rel_b else source_b.get("source_id", "b")
        
        return Conflict(
            source_a=source_a.get("source_id", "a"),
            source_b=source_b.get("source_id", "b"),
            conflict_type="overlap",
            description="内容重叠",
            resolution="选择相关性更高的源",
            winner=winner
        )
    
    def _resolve_outdated(
        self,
        source_a: Dict[str, Any],
        source_b: Dict[str, Any]
    ) -> Conflict:
        """解决过时"""
        # 选择更新的
        time_a = source_a.get("created_at")
        time_b = source_b.get("created_at")
        
        winner = source_b.get("source_id", "b")  # 假设 b 更新
        
        if time_a and time_b:
            try:
                if isinstance(time_a, str):
                    dt_a = datetime.fromisoformat(time_a)
                else:
                    dt_a = time_a
                
                if isinstance(time_b, str):
                    dt_b = datetime.fromisoformat(time_b)
                else:
                    dt_b = time_b
                
                winner = source_a.get("source_id", "a") if dt_a >= dt_b else source_b.get("source_id", "b")
            except:
                pass
        
        return Conflict(
            source_a=source_a.get("source_id", "a"),
            source_b=source_b.get("source_id", "b"),
            conflict_type="outdated",
            description="信息过时",
            resolution="选择更新的源",
            winner=winner
        )
