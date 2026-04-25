"""
Skill Router (Runtime)
技能路由器 - 运行时版本

选择和执行技能
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import threading
from pathlib import Path

from skills.registry.skill_registry import SkillRegistry, get_skill_registry


def _get_project_root() -> Path:
    """动态获取项目根目录"""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "core").exists() and (parent / "infrastructure").exists():
            return parent
    return current.parents[4]


@dataclass
class SkillExecutionContext:
    """技能执行上下文"""
    profile: str = "default"
    constraints: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillExecutionResult:
    """技能执行结果"""
    success: bool
    skill_id: str
    output: Dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    error: Optional[str] = None


class SkillRouter:
    """技能路由器"""
    
    def __init__(self, registry: Optional[SkillRegistry] = None):
        self.registry = registry or get_skill_registry()
        self._metrics: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        
        # 自动加载 metrics
        self._auto_load_metrics()
    
    def _auto_load_metrics(self):
        """自动加载 metrics 文件"""
        try:
            project_root = _get_project_root()
            metrics_path = project_root / "reports" / "metrics" / "skill_metrics.json"
            if metrics_path.exists():
                import json
                with open(metrics_path, 'r', encoding='utf-8') as f:
                    self._metrics = json.load(f)
        except Exception:
            pass
    
    def _check_metrics_reload(self) -> bool:
        """检查并重新加载 metrics"""
        try:
            self._auto_load_metrics()
            return True
        except Exception:
            return False
    
    def select_skill(self, task_type: str, context: Optional[SkillExecutionContext] = None) -> Optional[str]:
        """选择技能"""
        # 简单实现：按名称匹配
        skill = self.registry.get_by_name(task_type)
        if skill:
            return skill.skill_id
        
        # 按标签搜索
        skills = self.registry.list_by_tag(task_type)
        if skills:
            return skills[0].skill_id
        
        # 搜索
        results = self.registry.search(task_type)
        if results:
            return results[0].skill_id
        
        return None
    
    def execute(self, skill_id: str, input_data: Dict[str, Any],
                context: Optional[SkillExecutionContext] = None) -> SkillExecutionResult:
        """执行技能"""
        import time
        
        skill = self.registry.get(skill_id)
        if not skill:
            return SkillExecutionResult(
                success=False,
                skill_id=skill_id,
                error=f"Skill not found: {skill_id}"
            )
        
        start_time = time.perf_counter()
        
        try:
            # 这里应该实际执行技能
            # 目前返回模拟结果
            output = {"result": f"Executed {skill.name}"}
            
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            
            return SkillExecutionResult(
                success=True,
                skill_id=skill_id,
                output=output,
                duration_ms=duration_ms
            )
        except Exception as e:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            return SkillExecutionResult(
                success=False,
                skill_id=skill_id,
                error=str(e),
                duration_ms=duration_ms
            )
    
    def load_metrics(self, metrics_path: str):
        """加载技能指标"""
        import json
        import os
        
        if os.path.exists(metrics_path):
            try:
                with open(metrics_path, 'r', encoding='utf-8') as f:
                    self._metrics = json.load(f)
            except Exception:
                pass
    
    def get_metrics(self, skill_id: str) -> Dict[str, Any]:
        """获取技能指标"""
        return self._metrics.get(skill_id, {})


# 单例实例
_router: Optional[SkillRouter] = None
_router_lock = threading.Lock()


def get_skill_router() -> SkillRouter:
    """获取技能路由器单例"""
    global _router
    if _router is None:
        with _router_lock:
            if _router is None:
                _router = SkillRouter()
    return _router
