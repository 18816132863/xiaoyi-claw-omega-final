#!/usr/bin/env python3
"""
故障转移模块 (v5.0)
自动故障检测、节点切换、数据恢复
"""

import time
import asyncio
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import random


class NodeStatus(Enum):
    """节点状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


class Node:
    """
    节点定义
    """
    
    def __init__(
        self,
        node_id: str,
        endpoint: str,
        weight: float = 1.0
    ):
        """
        初始化节点
        
        Args:
            node_id: 节点 ID
            endpoint: 端点地址
            weight: 权重
        """
        self.node_id = node_id
        self.endpoint = endpoint
        self.weight = weight
        self.status = NodeStatus.HEALTHY
        self.last_check = time.time()
        self.failure_count = 0
        self.success_count = 0
        self.latency = 0.0


class HealthChecker:
    """
    健康检查器
    """
    
    def __init__(
        self,
        check_interval: float = 10.0,
        timeout: float = 5.0,
        failure_threshold: int = 3,
        recovery_threshold: int = 2
    ):
        """
        初始化健康检查器
        
        Args:
            check_interval: 检查间隔
            timeout: 超时时间
            failure_threshold: 失败阈值
            recovery_threshold: 恢复阈值
        """
        self.check_interval = check_interval
        self.timeout = timeout
        self.failure_threshold = failure_threshold
        self.recovery_threshold = recovery_threshold
        
        self.nodes: Dict[str, Node] = {}
        self.check_callbacks: List[Callable] = []
        
        print(f"健康检查器初始化:")
        print(f"  检查间隔: {check_interval}s")
        print(f"  失败阈值: {failure_threshold}")
    
    def register_node(self, node: Node):
        """
        注册节点
        
        Args:
            node: 节点对象
        """
        self.nodes[node.node_id] = node
        print(f"节点已注册: {node.node_id}")
    
    def add_check_callback(self, callback: Callable):
        """
        添加检查回调
        
        Args:
            callback: 回调函数
        """
        self.check_callbacks.append(callback)
    
    async def check_node(self, node: Node) -> bool:
        """
        检查节点健康
        
        Args:
            node: 节点对象
        
        Returns:
            bool: 是否健康
        """
        # 简化实现：模拟健康检查
        # 实际实现应发送 HTTP 请求或 ping
        
        # 模拟延迟
        latency = random.uniform(0.01, 0.1)
        await asyncio.sleep(latency)
        
        # 模拟成功率
        is_healthy = random.random() > 0.1  # 90% 成功率
        
        node.last_check = time.time()
        node.latency = latency
        
        if is_healthy:
            node.success_count += 1
            node.failure_count = 0
            
            if node.status != NodeStatus.HEALTHY:
                if node.success_count >= self.recovery_threshold:
                    node.status = NodeStatus.HEALTHY
                    print(f"✅ 节点恢复: {node.node_id}")
        else:
            node.failure_count += 1
            node.success_count = 0
            
            if node.failure_count >= self.failure_threshold:
                node.status = NodeStatus.UNHEALTHY
                print(f"❌ 节点不健康: {node.node_id}")
        
        return is_healthy
    
    async def check_all(self):
        """检查所有节点"""
        tasks = [self.check_node(node) for node in self.nodes.values()]
        await asyncio.gather(*tasks)
        
        # 触发回调
        for callback in self.check_callbacks:
            callback(self.nodes)
    
    async def start_monitoring(self):
        """开始监控"""
        print("开始健康监控...")
        
        while True:
            await self.check_all()
            await asyncio.sleep(self.check_interval)


class FailoverManager:
    """
    故障转移管理器
    """
    
    def __init__(
        self,
        health_checker: HealthChecker,
        strategy: str = "round_robin"
    ):
        """
        初始化故障转移管理器
        
        Args:
            health_checker: 健康检查器
            strategy: 负载均衡策略
        """
        self.health_checker = health_checker
        self.strategy = strategy
        
        self.current_index = 0
        self.failover_count = 0
        
        print(f"故障转移管理器初始化:")
        print(f"  策略: {strategy}")
    
    def get_healthy_nodes(self) -> List[Node]:
        """
        获取健康节点
        
        Returns:
            List[Node]: 健康节点列表
        """
        return [
            node for node in self.health_checker.nodes.values()
            if node.status == NodeStatus.HEALTHY
        ]
    
    def select_node(self) -> Optional[Node]:
        """
        选择节点
        
        Returns:
            Optional[Node]: 选中的节点
        """
        healthy_nodes = self.get_healthy_nodes()
        
        if not healthy_nodes:
            print("⚠️ 没有健康节点可用")
            return None
        
        if self.strategy == "round_robin":
            return self._round_robin(healthy_nodes)
        elif self.strategy == "weighted":
            return self._weighted(healthy_nodes)
        elif self.strategy == "least_latency":
            return self._least_latency(healthy_nodes)
        else:
            return healthy_nodes[0]
    
    def _round_robin(self, nodes: List[Node]) -> Node:
        """轮询策略"""
        node = nodes[self.current_index % len(nodes)]
        self.current_index += 1
        return node
    
    def _weighted(self, nodes: List[Node]) -> Node:
        """加权策略"""
        total_weight = sum(n.weight for n in nodes)
        r = random.uniform(0, total_weight)
        
        current = 0
        for node in nodes:
            current += node.weight
            if r <= current:
                return node
        
        return nodes[0]
    
    def _least_latency(self, nodes: List[Node]) -> Node:
        """最低延迟策略"""
        return min(nodes, key=lambda n: n.latency)
    
    async def execute_with_failover(
        self,
        func: Callable,
        *args,
        max_retries: int = 3,
        **kwargs
    ) -> Any:
        """
        带故障转移的执行
        
        Args:
            func: 执行函数
            max_retries: 最大重试次数
        
        Returns:
            Any: 执行结果
        """
        for attempt in range(max_retries):
            node = self.select_node()
            
            if not node:
                raise Exception("没有可用节点")
            
            try:
                # 执行函数
                result = await func(node, *args, **kwargs)
                return result
            
            except Exception as e:
                print(f"⚠️ 节点 {node.node_id} 执行失败: {e}")
                
                # 标记节点不健康
                node.status = NodeStatus.DEGRADED
                node.failure_count += 1
                
                self.failover_count += 1
                
                if attempt < max_retries - 1:
                    print(f"  切换到其他节点...")
                    await asyncio.sleep(0.1)
        
        raise Exception(f"所有节点都失败，已重试 {max_retries} 次")
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        nodes = self.health_checker.nodes
        
        return {
            'total_nodes': len(nodes),
            'healthy_nodes': len(self.get_healthy_nodes()),
            'failover_count': self.failover_count,
            'nodes': {
                node_id: {
                    'status': node.status.value,
                    'latency': node.latency,
                    'failure_count': node.failure_count
                }
                for node_id, node in nodes.items()
            }
        }


if __name__ == "__main__":
    # 测试
    async def test():
        print("=== 故障转移测试 ===")
        
        # 创建健康检查器
        checker = HealthChecker(check_interval=5.0)
        
        # 注册节点
        checker.register_node(Node("node1", "http://node1:8080", weight=1.0))
        checker.register_node(Node("node2", "http://node2:8080", weight=1.5))
        checker.register_node(Node("node3", "http://node3:8080", weight=0.8))
        
        # 创建故障转移管理器
        failover = FailoverManager(checker, strategy="round_robin")
        
        # 检查节点
        print("\n检查节点:")
        await checker.check_all()
        
        # 选择节点
        print("\n选择节点:")
        for i in range(5):
            node = failover.select_node()
            if node:
                print(f"  {i+1}. {node.node_id} (延迟: {node.latency:.3f}s)")
        
        # 统计
        stats = failover.get_stats()
        print(f"\n统计:")
        print(f"  总节点: {stats['total_nodes']}")
        print(f"  健康节点: {stats['healthy_nodes']}")
    
    asyncio.run(test())
