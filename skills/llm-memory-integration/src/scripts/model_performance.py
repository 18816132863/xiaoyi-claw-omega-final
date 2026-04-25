#!/usr/bin/env python3
"""
模型性能监控脚本
监控 LLM 和 Embedding 调用性能
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# 路径配置
WORKSPACE = Path.home() / ".openclaw" / "workspace"
PERF_LOG = WORKSPACE / "memory" / "model_performance.json"
CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"

class ModelPerformanceMonitor:
    """模型性能监控器"""
    
    def __init__(self):
        self.config = self._load_config()
        self.metrics = []
    
    def _load_config(self):
        """加载配置"""
        if CONFIG_PATH.exists():
            return json.loads(CONFIG_PATH.read_text())
        return {}
    
    def get_embedding_config(self):
        """获取 Embedding 配置"""
        plugin = self.config.get("plugins", {}).get("entries", {}).get("memory-tencentdb", {})
        return plugin.get("config", {}).get("embedding", {})
    
    def test_embedding_latency(self):
        """测试 Embedding 延迟"""
        emb_config = self.get_embedding_config()
        if not emb_config.get("apiKey"):
            return None
        
        start = time.time()
        try:
            response = requests.post(
                f"{emb_config.get('baseUrl', 'https://ai.gitee.com/v1')}/embeddings",
                headers={
                    "Authorization": f"Bearer {emb_config['apiKey']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": emb_config.get("model", "Qwen3-Embedding-8B"),
                    "input": "测试文本",
                    "dimensions": emb_config.get("dimensions", 4096)
                },
                timeout=30
            )
            latency = (time.time() - start) * 1000  # ms
            
            return {
                "success": response.status_code == 200,
                "latency_ms": round(latency, 2),
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "success": False,
                "latency_ms": (time.time() - start) * 1000,
                "error": str(e)
            }
    
    def save_metrics(self, metric):
        """保存指标"""
        PERF_LOG.parent.mkdir(parents=True, exist_ok=True)
        
        if PERF_LOG.exists():
            metrics = json.loads(PERF_LOG.read_text())
        else:
            metrics = []
        
        metrics.append(metric)
        
        # 保留最近1000条
        if len(metrics) > 1000:
            metrics = metrics[-1000:]
        
        PERF_LOG.write_text(json.dumps(metrics, indent=2))
    
    def run_monitor(self):
        """运行监控"""
        print("测试 Embedding 性能...")
        result = self.test_embedding_latency()
        
        if result:
            metric = {
                "timestamp": datetime.now().isoformat(),
                "type": "embedding",
                **result
            }
            self.save_metrics(metric)
            return metric
        return None
    
    def print_report(self):
        """打印性能报告"""
        print("=" * 60)
        print("   模型性能报告")
        print("=" * 60)
        print(f"检查时间: {datetime.now().isoformat()}")
        print()
        
        # 测试 Embedding
        result = self.test_embedding_latency()
        if result:
            status = "✅" if result["success"] else "❌"
            print(f"{status} Embedding API")
            print(f"   - 延迟: {result.get('latency_ms', 0):.2f}ms")
            if not result["success"]:
                print(f"   - 错误: {result.get('error', 'unknown')}")
        else:
            print("⚠️ Embedding 配置缺失")
        
        # 历史统计
        if PERF_LOG.exists():
            metrics = json.loads(PERF_LOG.read_text())
            if metrics:
                latencies = [m["latency_ms"] for m in metrics if m.get("success")]
                if latencies:
                    print()
                    print(f"历史统计 (最近{len(latencies)}次成功调用):")
                    print(f"   - 平均延迟: {sum(latencies)/len(latencies):.2f}ms")
                    print(f"   - 最小延迟: {min(latencies):.2f}ms")
                    print(f"   - 最大延迟: {max(latencies):.2f}ms")

def main():
    monitor = ModelPerformanceMonitor()
    monitor.run_monitor()
    monitor.print_report()

if __name__ == "__main__":
    main()
