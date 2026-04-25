#!/usr/bin/env python3
"""
复杂任务优化引擎 V2
目标：复杂任务 < 50ms
"""

import asyncio
from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import hashlib
import time

class TaskPriority(Enum):
    CRITICAL = 0   # < 10ms
    HIGH = 1       # < 30ms
    NORMAL = 2     # < 50ms
    LOW = 3        # < 100ms

@dataclass
class Skill:
    name: str
    dependencies: List[str] = field(default_factory=list)
    timeout_ms: int = 100
    priority: TaskPriority = TaskPriority.NORMAL
    cached: bool = False

@dataclass
class Task:
    id: str
    skills: List[Skill]
    context: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL

@dataclass
class PartialResult:
    skill: Optional[str] = None
    status: str = "pending"
    data: Any = None
    progress: int = 0
    latency_ms: float = 0
    is_complete: bool = False

# ============ 技能预热器 ============

class SkillPreheater:
    """技能预热 - 预测并预加载可能需要的技能"""
    
    def __init__(self):
        self.history = defaultdict(int)  # 技能使用频率
        self.transitions = defaultdict(lambda: defaultdict(int))  # 技能转移概率
        self.cache = {}  # 预热的技能配置
        self.pool = {}   # 预初始化的技能实例
    
    def record_usage(self, skill_name: str, prev_skill: Optional[str] = None):
        """记录技能使用"""
        self.history[skill_name] += 1
        if prev_skill:
            self.transitions[prev_skill][skill_name] += 1
    
    def predict_next(self, current_skill: str, top_k: int = 3) -> List[str]:
        """预测下一个可能使用的技能"""
        if current_skill not in self.transitions:
            # 返回最常用的技能
            return sorted(self.history.keys(), key=lambda x: self.history[x], reverse=True)[:top_k]
        
        transitions = self.transitions[current_skill]
        return sorted(transitions.keys(), key=lambda x: transitions[x], reverse=True)[:top_k]
    
    def preheat(self, skill_names: List[str]):
        """预热技能"""
        for name in skill_names:
            if name not in self.cache:
                # 模拟预加载配置
                self.cache[name] = {"loaded": True, "timestamp": time.time()}
    
    def get_preheated(self, skill_name: str) -> Optional[Dict]:
        """获取预热的技能"""
        return self.cache.get(skill_name)

# ============ 流水线执行器 ============

class PipelineExecutor:
    """流水线执行 - 并行+流式返回"""
    
    def __init__(self, preheater: SkillPreheater):
        self.preheater = preheater
        self.result_cache = {}
        self.intermediate_cache = {}
    
    async def execute(self, task: Task) -> AsyncIterator[PartialResult]:
        """流式执行任务"""
        start_time = time.perf_counter()
        
        # 阶段1：立即返回确认 (< 1ms)
        yield PartialResult(
            status="accepted",
            progress=0,
            latency_ms=(time.perf_counter() - start_time) * 1000
        )
        
        # 阶段2：分析依赖，分组执行
        groups = self._group_by_dependency(task.skills)
        
        total_skills = len(task.skills)
        completed = 0
        
        # 阶段3：按依赖层级并行执行
        for group in groups:
            # 并行执行该层所有技能
            tasks = [self._execute_skill(s, task.context) for s in group]
            
            for coro in asyncio.as_completed(tasks):
                result = await coro
                completed += 1
                
                # 流式返回部分结果
                yield PartialResult(
                    skill=result.skill,
                    data=result.data,
                    progress=int(completed / total_skills * 100),
                    latency_ms=(time.perf_counter() - start_time) * 1000
                )
                
                # 预测并预热下一个技能
                next_skills = self.preheater.predict_next(result.skill)
                self.preheater.preheat(next_skills)
        
        # 阶段4：最终完成
        yield PartialResult(
            status="complete",
            progress=100,
            is_complete=True,
            latency_ms=(time.perf_counter() - start_time) * 1000
        )
    
    def _group_by_dependency(self, skills: List[Skill]) -> List[List[Skill]]:
        """按依赖关系分组"""
        # 拓扑排序
        in_degree = {s.name: 0 for s in skills}
        skill_map = {s.name: s for s in skills}
        
        for s in skills:
            for dep in s.dependencies:
                if dep in in_degree:
                    in_degree[s.name] += 1
        
        groups = []
        remaining = set(in_degree.keys())
        
        while remaining:
            # 找出当前无依赖的技能
            group = [skill_map[name] for name in remaining if in_degree[name] == 0]
            
            if not group:
                # 循环依赖，强制执行
                group = [skill_map[name] for name in list(remaining)[:1]]
            
            groups.append(group)
            
            # 更新依赖
            for s in group:
                remaining.remove(s.name)
                for other in skills:
                    if s.name in other.dependencies:
                        in_degree[other.name] -= 1
        
        return groups
    
    async def _execute_skill(self, skill: Skill, context: Dict) -> PartialResult:
        """执行单个技能"""
        start = time.perf_counter()
        
        # 检查缓存
        cache_key = self._make_cache_key(skill.name, context)
        if cache_key in self.result_cache:
            return PartialResult(
                skill=skill.name,
                data=self.result_cache[cache_key],
                latency_ms=(time.perf_counter() - start) * 1000
            )
        
        # 检查预热
        preheated = self.preheater.get_preheated(skill.name)
        
        # 模拟执行
        await asyncio.sleep(0.005)  # 5ms 模拟执行
        
        result = {"skill": skill.name, "output": f"result_of_{skill.name}"}
        
        # 缓存结果
        self.result_cache[cache_key] = result
        
        return PartialResult(
            skill=skill.name,
            data=result,
            latency_ms=(time.perf_counter() - start) * 1000
        )
    
    def _make_cache_key(self, skill_name: str, context: Dict) -> str:
        """生成缓存键"""
        context_hash = hashlib.md5(str(context).encode()).hexdigest()[:8]
        return f"{skill_name}:{context_hash}"

# ============ 智能缓存 ============

class IntelligentCache:
    """智能缓存 - 语义相似任务复用"""
    
    def __init__(self, size: int = 10000):
        self.cache = {}
        self.size = size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any):
        if len(self.cache) >= self.size:
            # LRU 淘汰
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        self.cache[key] = value
    
    def get_similar(self, context: Dict, threshold: float = 0.9) -> Optional[Any]:
        """查找语义相似的结果"""
        # 简化实现：基于哈希相似度
        context_str = str(sorted(context.items()))
        context_hash = hashlib.md5(context_str.encode()).hexdigest()
        
        for key, value in self.cache.items():
            if key.endswith(context_hash[:4]):
                return value
        
        return None
    
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0

# ============ 复杂任务引擎 ============

class ComplexTaskEngine:
    """复杂任务优化引擎"""
    
    def __init__(self):
        self.preheater = SkillPreheater()
        self.executor = PipelineExecutor(self.preheater)
        self.cache = IntelligentCache()
    
    async def execute(self, task: Task) -> AsyncIterator[PartialResult]:
        """执行复杂任务"""
        async for result in self.executor.execute(task):
            yield result
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "cache_hit_rate": f"{self.cache.hit_rate() * 100:.1f}%",
            "preheated_skills": len(self.preheater.cache),
            "cached_results": len(self.executor.result_cache),
        }

# ============ 测试 ============

async def test_complex_task():
    """测试复杂任务执行"""
    engine = ComplexTaskEngine()
    
    # 创建测试任务
    skills = [
        Skill("intent_analysis", [], 50, TaskPriority.CRITICAL),
        Skill("web_search", ["intent_analysis"], 100, TaskPriority.HIGH),
        Skill("memory_search", ["intent_analysis"], 100, TaskPriority.HIGH),
        Skill("result_aggregation", ["web_search", "memory_search"], 50, TaskPriority.NORMAL),
    ]
    
    task = Task(
        id="test-001",
        skills=skills,
        context={"query": "今天天气怎么样"},
        priority=TaskPriority.HIGH
    )
    
    print("=" * 50)
    print("复杂任务优化引擎 V2 测试")
    print("=" * 50)
    
    total_latency = 0
    async for result in engine.execute(task):
        print(f"\n进度: {result.progress}%")
        if result.skill:
            print(f"技能: {result.skill}")
        print(f"延迟: {result.latency_ms:.2f}ms")
        if result.is_complete:
            total_latency = result.latency_ms
    
    print("\n" + "=" * 50)
    print(f"总延迟: {total_latency:.2f}ms")
    print(f"统计: {engine.get_stats()}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_complex_task())
