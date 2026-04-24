"""统一路由器 - V4.3.2 主链改造版

所有路由功能的唯一实现，其他模块引用此文件。
V4.3.2 主链改造：
- 路径全部改走 infrastructure/path_resolver.py
- 路由前置条件必须同时检查 registered、routable、callable，且 status 不是 disabled/broken
- route() 的结果里返回 executor_type、entry_point、timeout
- 命中多个技能时按 callable、依赖满足、风险更低、匹配更多的顺序排序
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from infrastructure.path_resolver import get_project_root, get_infrastructure_dir

class RouteMode(Enum):
    """路由模式"""
    FAST = "fast"
    BALANCED = "balanced"
    FULL = "full"

@dataclass
class RouteResult:
    """路由结果 - V4.3.2: 包含执行所需信息"""
    target: str
    confidence: float
    mode: RouteMode
    matched_keywords: List[str]
    alternatives: List[str]
    # V4.3.2: 状态字段
    is_registered: bool = False
    is_routable: bool = False
    is_callable: bool = False
    status: str = "unknown"
    # V4.3.2: 执行所需字段
    executor_type: str = "skill_md"
    entry_point: str = "SKILL.md"
    timeout: int = 60
    path: str = ""
    error: Optional[str] = None

class UnifiedRouter:
    """统一路由器 - 唯一实现"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, workspace_path: str = None):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        # V4.3.2: 使用 path_resolver
        self.workspace = get_project_root()
        self.index: Dict[str, List[str]] = {}
        self.registry: Dict[str, Dict] = {}
        self._load_index()
        self._load_registry()
        self._initialized = True
    
    def _load_index(self):
        """加载索引"""
        index_path = get_infrastructure_dir() / "inventory" / "skill_inverted_index.json"
        if index_path.exists():
            with open(index_path) as f:
                data = json.load(f)
            self.index = data.get("by_trigger", {})
    
    def _load_registry(self):
        """加载技能注册表"""
        registry_path = get_infrastructure_dir() / "inventory" / "skill_registry.json"
        if registry_path.exists():
            with open(registry_path) as f:
                data = json.load(f)
            self.registry = data.get("skills", {})
    
    def _check_skill_status(self, skill_name: str) -> Dict[str, Any]:
        """检查技能状态 - 必须同时满足所有条件"""
        skill = self.registry.get(skill_name, {})
        return {
            "is_registered": skill.get("registered", False),
            "is_routable": skill.get("routable", False),
            "is_callable": skill.get("callable", False),
            "status": skill.get("status", "unknown"),
            "executor_type": skill.get("executor_type", "skill_md"),
            "entry_point": skill.get("entry_point", "SKILL.md"),
            "timeout": skill.get("timeout", 60),
            "path": skill.get("path", ""),
        }
    
    def _is_executable(self, skill_name: str) -> bool:
        """V4.3.2: 检查技能是否可执行"""
        status = self._check_skill_status(skill_name)
        return (
            status["is_registered"] and
            status["is_routable"] and
            status["is_callable"] and
            status["status"] not in ["disabled", "broken"]
        )
    
    def _score_skill(self, skill_name: str, match_count: int) -> float:
        """V4.3.2: 技能评分 - 用于排序"""
        skill = self.registry.get(skill_name, {})
        score = 0.0
        
        # callable 加分
        if skill.get("callable"):
            score += 100
        
        # 依赖满足加分
        deps = skill.get("dependencies", [])
        if deps:
            satisfied = sum(1 for d in deps if d in self.registry and self.registry[d].get("callable"))
            score += (satisfied / len(deps)) * 50
        
        # 风险低加分
        risk = skill.get("risk_level", "medium")
        if risk == "low":
            score += 30
        elif risk == "medium":
            score += 15
        
        # 匹配数加分
        score += match_count * 10
        
        return score
    
    def route(self, query: str, mode: RouteMode = RouteMode.BALANCED) -> Optional[RouteResult]:
        """路由查询 - V4.3.2: 完整状态校验"""
        query_lower = query.lower()
        matched: Dict[str, List[str]] = {}
        
        # 收集所有匹配
        for trigger, targets in self.index.items():
            if trigger in query_lower:
                for target in targets:
                    if target not in matched:
                        matched[target] = []
                    matched[target].append(trigger)
        
        if not matched:
            return None
        
        # 分离可执行和不可执行的技能
        executable = {}
        non_executable = {}
        
        for skill_name, triggers in matched.items():
            if self._is_executable(skill_name):
                executable[skill_name] = triggers
            else:
                non_executable[skill_name] = triggers
        
        # 如果有可执行的，按评分排序
        if executable:
            sorted_skills = sorted(
                executable.items(),
                key=lambda x: self._score_skill(x[0], len(x[1])),
                reverse=True
            )
            best_name, best_triggers = sorted_skills[0]
            status = self._check_skill_status(best_name)
            
            return RouteResult(
                target=best_name,
                confidence=min(len(best_triggers) / 5.0, 1.0),
                mode=mode,
                matched_keywords=best_triggers,
                alternatives=[k for k, _ in sorted_skills[1:4]],
                is_registered=status["is_registered"],
                is_routable=status["is_routable"],
                is_callable=status["is_callable"],
                status=status["status"],
                executor_type=status["executor_type"],
                entry_point=status["entry_point"],
                timeout=status["timeout"],
                path=status["path"],
                error=None
            )
        
        # 所有匹配的技能都不可执行
        best_name = max(matched.keys(), key=lambda k: len(matched[k]))
        status = self._check_skill_status(best_name)
        
        # 构建错误信息
        errors = []
        if not status["is_registered"]:
            errors.append("未注册")
        if not status["is_routable"]:
            errors.append("不可路由")
        if not status["is_callable"]:
            errors.append("不可调用")
        if status["status"] in ["disabled", "broken"]:
            errors.append(f"状态: {status['status']}")
        
        return RouteResult(
            target=best_name,
            confidence=0.0,
            mode=mode,
            matched_keywords=matched[best_name],
            alternatives=[],
            is_registered=status["is_registered"],
            is_routable=status["is_routable"],
            is_callable=status["is_callable"],
            status=status["status"],
            executor_type=status["executor_type"],
            entry_point=status["entry_point"],
            timeout=status["timeout"],
            path=status["path"],
            error=f"技能 '{best_name}' 不可执行: {', '.join(errors)}"
        )

# 全局访问函数
_router: Optional[UnifiedRouter] = None

def get_router() -> UnifiedRouter:
    global _router
    if _router is None:
        _router = UnifiedRouter()
    return _router

def route(query: str, mode: str = "balanced") -> Optional[RouteResult]:
    """便捷路由函数"""
    mode_map = {
        "fast": RouteMode.FAST,
        "balanced": RouteMode.BALANCED,
        "full": RouteMode.FULL
    }
    return get_router().route(query, mode_map.get(mode, RouteMode.BALANCED))
