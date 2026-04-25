#!/usr/bin/env python3
"""
多模型路由模块 (v5.0)
任务路由、成本优化、模型选择
"""

import numpy as np
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import time


class TaskType(Enum):
    """任务类型"""
    SEARCH = "search"
    EMBED = "embed"
    CHAT = "chat"
    SUMMARIZE = "summarize"
    TRANSLATE = "translate"
    CODE = "code"


class ModelCapability(Enum):
    """模型能力"""
    FAST = "fast"
    BALANCED = "balanced"
    ACCURATE = "accurate"
    CHEAP = "cheap"


class Model:
    """
    模型定义
    """
    
    def __init__(
        self,
        model_id: str,
        name: str,
        capabilities: List[ModelCapability],
        cost_per_1k_tokens: float = 0.0,
        max_tokens: int = 4096,
        latency_ms: float = 100.0
    ):
        """
        初始化模型
        
        Args:
            model_id: 模型 ID
            name: 模型名称
            capabilities: 能力列表
            cost_per_1k_tokens: 每 1k token 成本
            max_tokens: 最大 token 数
            latency_ms: 平均延迟
        """
        self.model_id = model_id
        self.name = name
        self.capabilities = capabilities
        self.cost_per_1k_tokens = cost_per_1k_tokens
        self.max_tokens = max_tokens
        self.latency_ms = latency_ms
        
        # 统计
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0


class ModelRouter:
    """
    多模型路由器
    """
    
    def __init__(
        self,
        strategy: str = "cost_optimized",
        default_capability: ModelCapability = ModelCapability.BALANCED
    ):
        """
        初始化模型路由器
        
        Args:
            strategy: 路由策略
            default_capability: 默认能力
        """
        self.strategy = strategy
        self.default_capability = default_capability
        
        # 模型存储
        self.models: Dict[str, Model] = {}
        
        # 任务-模型映射
        self.task_model_map: Dict[TaskType, List[str]] = {}
        
        # 统计
        self.routing_stats = {
            'total_requests': 0,
            'total_cost': 0.0,
            'model_usage': {}
        }
        
        print(f"模型路由器初始化:")
        print(f"  策略: {strategy}")
        print(f"  默认能力: {default_capability.value}")
    
    def register_model(self, model: Model, tasks: Optional[List[TaskType]] = None):
        """
        注册模型
        
        Args:
            model: 模型对象
            tasks: 支持的任务类型
        """
        self.models[model.model_id] = model
        
        # 更新任务映射
        if tasks:
            for task in tasks:
                if task not in self.task_model_map:
                    self.task_model_map[task] = []
                self.task_model_map[task].append(model.model_id)
        
        print(f"模型已注册: {model.name} (成本: ${model.cost_per_1k_tokens}/1k tokens)")
    
    def select_model(
        self,
        task: TaskType,
        capability: Optional[ModelCapability] = None,
        max_cost: Optional[float] = None,
        max_latency: Optional[float] = None
    ) -> Optional[Model]:
        """
        选择模型
        
        Args:
            task: 任务类型
            capability: 能力要求
            max_cost: 最大成本
            max_latency: 最大延迟
        
        Returns:
            Optional[Model]: 选中的模型
        """
        capability = capability or self.default_capability
        
        # 获取候选模型
        candidates = self._get_candidates(task, capability, max_cost, max_latency)
        
        if not candidates:
            print(f"⚠️ 没有符合条件的模型")
            return None
        
        # 根据策略选择
        if self.strategy == "cost_optimized":
            return self._select_cheapest(candidates)
        elif self.strategy == "performance_optimized":
            return self._select_fastest(candidates)
        elif self.strategy == "balanced":
            return self._select_balanced(candidates)
        else:
            return candidates[0]
    
    def _get_candidates(
        self,
        task: TaskType,
        capability: ModelCapability,
        max_cost: Optional[float],
        max_latency: Optional[float]
    ) -> List[Model]:
        """获取候选模型"""
        candidates = []
        
        for model_id in self.task_model_map.get(task, []):
            model = self.models.get(model_id)
            if not model:
                continue
            
            # 检查能力
            if capability not in model.capabilities:
                continue
            
            # 检查成本
            if max_cost and model.cost_per_1k_tokens > max_cost:
                continue
            
            # 检查延迟
            if max_latency and model.latency_ms > max_latency:
                continue
            
            candidates.append(model)
        
        return candidates
    
    def _select_cheapest(self, candidates: List[Model]) -> Model:
        """选择最便宜的"""
        return min(candidates, key=lambda m: m.cost_per_1k_tokens)
    
    def _select_fastest(self, candidates: List[Model]) -> Model:
        """选择最快的"""
        return min(candidates, key=lambda m: m.latency_ms)
    
    def _select_balanced(self, candidates: List[Model]) -> Model:
        """选择平衡的"""
        # 综合考虑成本和延迟
        def score(model: Model) -> float:
            cost_score = 1.0 / (model.cost_per_1k_tokens + 0.001)
            latency_score = 1.0 / (model.latency_ms + 1.0)
            return cost_score * 0.6 + latency_score * 0.4
        
        return max(candidates, key=score)
    
    def route_request(
        self,
        task: TaskType,
        func: Callable,
        *args,
        capability: Optional[ModelCapability] = None,
        **kwargs
    ) -> Any:
        """
        路由请求
        
        Args:
            task: 任务类型
            func: 执行函数
            capability: 能力要求
        
        Returns:
            Any: 执行结果
        """
        # 选择模型
        model = self.select_model(task, capability)
        
        if not model:
            raise Exception(f"没有可用的模型处理任务: {task.value}")
        
        # 记录统计
        model.request_count += 1
        self.routing_stats['total_requests'] += 1
        self.routing_stats['model_usage'][model.model_id] = \
            self.routing_stats['model_usage'].get(model.model_id, 0) + 1
        
        # 执行
        start_time = time.time()
        result = func(model, *args, **kwargs)
        elapsed = time.time() - start_time
        
        # 更新延迟
        model.latency_ms = (model.latency_ms + elapsed * 1000) / 2
        
        return result
    
    def estimate_cost(
        self,
        task: TaskType,
        token_count: int,
        capability: Optional[ModelCapability] = None
    ) -> float:
        """
        估算成本
        
        Args:
            task: 任务类型
            token_count: token 数量
            capability: 能力要求
        
        Returns:
            float: 估算成本
        """
        model = self.select_model(task, capability)
        
        if not model:
            return 0.0
        
        return model.cost_per_1k_tokens * token_count / 1000
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            'routing_stats': self.routing_stats,
            'models': {
                model_id: {
                    'name': model.name,
                    'request_count': model.request_count,
                    'total_cost': model.total_cost,
                    'avg_latency_ms': model.latency_ms
                }
                for model_id, model in self.models.items()
            }
        }


if __name__ == "__main__":
    # 测试
    print("=== 多模型路由测试 ===")
    
    router = ModelRouter(strategy="cost_optimized")
    
    # 注册模型
    router.register_model(
        Model("gpt-4", "GPT-4", [ModelCapability.ACCURATE], cost_per_1k_tokens=0.03, latency_ms=2000),
        [TaskType.CHAT, TaskType.CODE, TaskType.SUMMARIZE]
    )
    
    router.register_model(
        Model("gpt-3.5", "GPT-3.5", [ModelCapability.FAST, ModelCapability.CHEAP], cost_per_1k_tokens=0.002, latency_ms=500),
        [TaskType.CHAT, TaskType.SEARCH, TaskType.TRANSLATE]
    )
    
    router.register_model(
        Model("ada-002", "text-embedding-ada-002", [ModelCapability.CHEAP], cost_per_1k_tokens=0.0001, latency_ms=100),
        [TaskType.EMBED]
    )
    
    # 选择模型
    print("\n选择模型:")
    
    model = router.select_model(TaskType.CHAT, ModelCapability.ACCURATE)
    print(f"  聊天(准确): {model.name if model else 'None'}")
    
    model = router.select_model(TaskType.CHAT, ModelCapability.CHEAP)
    print(f"  聊天(便宜): {model.name if model else 'None'}")
    
    model = router.select_model(TaskType.EMBED)
    print(f"  嵌入: {model.name if model else 'None'}")
    
    # 估算成本
    cost = router.estimate_cost(TaskType.CHAT, 1000)
    print(f"\n估算成本: ${cost:.4f} (1000 tokens)")
    
    # 统计
    stats = router.get_stats()
    print(f"\n统计: {stats['routing_stats']}")
