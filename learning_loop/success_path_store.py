"""成功路径存储"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


@dataclass
class SuccessPath:
    """成功路径"""
    path_id: str
    goal_pattern: str
    plan: List[Dict[str, Any]]
    capabilities: List[str]
    skills: List[str]
    visual_paths: List[Dict[str, Any]]
    success_count: int = 1
    last_success_at: str = field(default_factory=lambda: datetime.now().isoformat())
    avg_time_ms: int = 0


class SuccessPathStore:
    """成功路径存储"""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = Path(storage_path or "data/success_paths.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._paths: Dict[str, SuccessPath] = {}
        self._load()
    
    def _load(self):
        """加载路径"""
        if self.storage_path.exists():
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                for path_data in data.get("paths", []):
                    path = SuccessPath(**path_data)
                    self._paths[path.path_id] = path
    
    def _save(self):
        """保存路径"""
        with open(self.storage_path, "w") as f:
            json.dump({
                "paths": [p.__dict__ for p in self._paths.values()],
            }, f, ensure_ascii=False, indent=2)
    
    def record_success(
        self,
        goal_pattern: str,
        plan: List[Dict[str, Any]],
        capabilities: List[str],
        skills: List[str],
        visual_paths: List[Dict[str, Any]],
        elapsed_ms: int,
    ):
        """记录成功路径"""
        # 查找是否已有相同模式
        for path in self._paths.values():
            if path.goal_pattern == goal_pattern and path.plan == plan:
                path.success_count += 1
                path.last_success_at = datetime.now().isoformat()
                path.avg_time_ms = (path.avg_time_ms * (path.success_count - 1) + elapsed_ms) // path.success_count
                self._save()
                return
        
        # 新路径
        import hashlib
        path_id = hashlib.md5(f"{goal_pattern}:{json.dumps(plan)}".encode()).hexdigest()[:12]
        path = SuccessPath(
            path_id=path_id,
            goal_pattern=goal_pattern,
            plan=plan,
            capabilities=capabilities,
            skills=skills,
            visual_paths=visual_paths,
            avg_time_ms=elapsed_ms,
        )
        self._paths[path_id] = path
        self._save()
    
    def find_best_path(self, goal_pattern: str) -> Optional[SuccessPath]:
        """查找最佳路径"""
        candidates = [
            p for p in self._paths.values()
            if p.goal_pattern == goal_pattern
        ]
        
        if not candidates:
            return None
        
        # 按成功次数和时间排序
        candidates.sort(key=lambda x: (x.success_count, -x.avg_time_ms), reverse=True)
        return candidates[0]
    
    def get_all_patterns(self) -> List[str]:
        """获取所有模式"""
        return list(set(p.goal_pattern for p in self._paths.values()))
