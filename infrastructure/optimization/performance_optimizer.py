from pathlib import Path

def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent
    while current != "/" and not (current / "core" / "ARCHITECTURE.md").exists():
        current = current.parent
    return current if current != "/" else Path(__file__).resolve().parent

#!/usr/bin/env python3
"""
六层架构性能优化器
V2.7.0 - 2026-04-10
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime

class PerformanceOptimizer:
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        self.config = self.load_config()
        self.stats = {
            "files_processed": 0,
            "tokens_saved": 0,
            "compression_ratio": 0
        }
    
    def load_config(self):
        config_path = self.workspace / "infrastructure/optimization/TOKEN_OPTIMIZATION.json"
        if config_path.exists():
            return json.loads(config_path.read_text())
        return {"version": "2.7.0", "strategies": {}}
    
    def optimize_layer(self, layer: str, path: Path):
        """优化指定层"""
        results = {
            "layer": layer,
            "files": 0,
            "lines_before": 0,
            "lines_after": 0,
            "tokens_saved": 0
        }
        
        if not path.exists():
            return results
        
        for file in path.rglob("*.md"):
            if file.name in ["AGENTS.md", "SOUL.md", "TOOLS.md", "USER.md", "IDENTITY.md"]:
                continue
            
            content = file.read_text()
            lines_before = len(content.splitlines())
            
            # 应用优化策略
            optimized = self.apply_strategies(content, layer)
            lines_after = len(optimized.splitlines())
            
            if lines_after < lines_before:
                # 保存优化版本
                file.write_text(optimized)
                results["files"] += 1
                results["lines_before"] += lines_before
                results["lines_after"] += lines_after
                results["tokens_saved"] += (lines_before - lines_after) * 4  # 估算 token
        
        return results
    
    def apply_strategies(self, content: str, layer: str) -> str:
        """应用优化策略"""
        lines = content.splitlines()
        max_lines = self.config.get("layerOptimization", {}).get(f"L{layer}", {}).get("maxTokens", 500) // 4
        
        # 策略1: 截断过长文件
        if len(lines) > max_lines * 2:
            # 保留开头和结尾
            head = lines[:max_lines]
            tail = lines[-max_lines//4:]
            lines = head + [f"\n... [已压缩 {len(lines) - len(head) - len(tail)} 行] ...\n"] + tail
        
        # 策略2: 移除空行
        lines = [line for line in lines if line.strip() or line == ""]
        
        # 策略3: 压缩代码块
        in_code_block = False
        result = []
        for line in lines:
            if line.startswith("```"):
                in_code_block = not in_code_block
                result.append(line)
            elif in_code_block and len(result) > 100:
                # 跳过过长代码块
                continue
            else:
                result.append(line)
        
        return "\n".join(result)
    
    def run(self):
        """运行优化"""
        layers = {
            "1_core": self.workspace / "core",
            "2_memory_context": self.workspace / "memory_context",
            "3_orchestration": self.workspace / "orchestration",
            "4_execution": self.workspace / "execution",
            "5_governance": self.workspace / "governance",
            "6_infrastructure": self.workspace / "infrastructure"
        }
        
        results = []
        for layer_name, layer_path in layers.items():
            layer_num = layer_name.split("_")[0]
            result = self.optimize_layer(layer_num, layer_path)
            results.append(result)
            print(f"优化 {layer_name}: {result['files']} 文件, 节省 {result['tokens_saved']} tokens")
        
        return results

if __name__ == "__main__":
    optimizer = PerformanceOptimizer(str(get_project_root()))
    results = optimizer.run()
    print(f"\n总计节省: {sum(r['tokens_saved'] for r in results)} tokens")
