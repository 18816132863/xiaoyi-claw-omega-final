"""执行记忆 - 记录每次执行的经验"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


@dataclass
class ExecutionRecord:
    """执行记录"""
    execution_id: str = field(default_factory=lambda: str(hash(datetime.now())))
    goal: str = ""
    plan: List[Dict[str, Any]] = field(default_factory=list)
    capabilities_used: List[str] = field(default_factory=list)
    skills_used: List[str] = field(default_factory=list)
    successful_steps: List[int] = field(default_factory=list)
    failed_steps: List[int] = field(default_factory=list)
    step_timings: Dict[int, int] = field(default_factory=dict)  # step_index -> ms
    confirmations_needed: List[int] = field(default_factory=list)
    user_satisfied: Optional[bool] = None
    final_result: str = ""  # success, partial, failed
    visual_paths: List[Dict[str, Any]] = field(default_factory=list)
    fallback_occurred: bool = False
    result_uncertain: bool = False
    optimization_hints: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class ExecutionMemory:
    """执行记忆"""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path or "data/execution_memory.jsonl")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: List[ExecutionRecord] = []
        self._load()
    
    def _load(self):
        """加载历史记录"""
        if self.storage_path.exists():
            with open(self.storage_path, "r") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self._cache.append(ExecutionRecord(**data))
    
    def record(self, record: ExecutionRecord):
        """记录执行"""
        self._cache.append(record)
        with open(self.storage_path, "a") as f:
            f.write(json.dumps(record.__dict__, ensure_ascii=False) + "\n")
    
    def find_similar(self, goal: str, limit: int = 5) -> List[ExecutionRecord]:
        """查找相似目标的历史记录"""
        from .pattern_extractor import PatternExtractor
        
        # 提取目标模式
        goal_pattern = PatternExtractor.extract_goal_pattern(goal)
        
        # 按模式匹配 + 关键词重叠评分
        keywords = set(goal.lower().split())
        scored = []
        
        for record in self._cache:
            record_pattern = PatternExtractor.extract_goal_pattern(record.goal)
            record_keywords = set(record.goal.lower().split())
            
            # 模式匹配加分
            pattern_score = 10 if goal_pattern == record_pattern else 0
            
            # 关键词重叠
            overlap = len(keywords & record_keywords)
            
            # 总分
            total_score = pattern_score + overlap
            
            if total_score > 0:
                scored.append((total_score, record))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:limit]]
    
    def get_successful_paths(self, goal_pattern: str) -> List[Dict[str, Any]]:
        """获取成功路径"""
        similar = self.find_similar(goal_pattern)
        return [
            {
                "plan": r.plan,
                "capabilities": r.capabilities_used,
                "skills": r.skills_used,
                "timings": r.step_timings,
            }
            for r in similar
            if r.final_result == "success"
        ]
    
    def get_failed_steps(self, goal_pattern: str) -> List[int]:
        """获取失败步骤"""
        similar = self.find_similar(goal_pattern)
        failed = []
        for r in similar:
            failed.extend(r.failed_steps)
        return list(set(failed))
    
    def get_preference_hints(self, goal_pattern: str) -> Dict[str, Any]:
        """获取偏好提示"""
        similar = self.find_similar(goal_pattern)
        if not similar:
            return {}
        
        # 统计最常用的能力和技能
        cap_counts: Dict[str, int] = {}
        skill_counts: Dict[str, int] = {}
        
        for r in similar:
            if r.final_result == "success":
                for cap in r.capabilities_used:
                    cap_counts[cap] = cap_counts.get(cap, 0) + 1
                for skill in r.skills_used:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        return {
            "preferred_capabilities": sorted(cap_counts.keys(), key=lambda x: cap_counts[x], reverse=True)[:3],
            "preferred_skills": sorted(skill_counts.keys(), key=lambda x: skill_counts[x], reverse=True)[:3],
            "avg_confirmations": sum(len(r.confirmations_needed) for r in similar) / len(similar),
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total = len(self._cache)
        if total == 0:
            return {"total": 0}
        
        success = sum(1 for r in self._cache if r.final_result == "success")
        partial = sum(1 for r in self._cache if r.final_result == "partial")
        failed = sum(1 for r in self._cache if r.final_result == "failed")
        
        return {
            "total": total,
            "success": success,
            "partial": partial,
            "failed": failed,
            "success_rate": success / total,
        }
