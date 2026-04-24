"""层级管理器 - V1.0.0"""

from typing import Dict, List, Optional
from pathlib import Path
from infrastructure.path_resolver import get_project_root
import json

class LayerManager:
    """层级管理器"""
    
    LAYERS = {
        "P0_CORE": {"priority": 0, "name": "核心层", "token_budget": 3000},
        "P1_COMMON": {"priority": 1, "name": "常用层", "token_budget": 2000},
        "P2_EXTENDED": {"priority": 2, "name": "扩展层", "token_budget": 1500},
        "P3_ARCHIVE": {"priority": 3, "name": "归档层", "token_budget": 0}
    }
    
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path or get_project_root())
        self.loaded_layers = set()
        self.token_usage = {layer: 0 for layer in self.LAYERS}
    
    def should_load(self, layer: str, current_tokens: int) -> bool:
        """判断是否应该加载该层"""
        if layer not in self.LAYERS:
            return False
        
        layer_info = self.LAYERS[layer]
        budget = layer_info["token_budget"]
        
        # P0 必须加载
        if layer == "P0_CORE":
            return True
        
        # P3 不加载
        if layer == "P3_ARCHIVE":
            return False
        
        # 检查 token 预算
        return current_tokens + budget < 10000
    
    def mark_loaded(self, layer: str, tokens_used: int):
        """标记层已加载"""
        self.loaded_layers.add(layer)
        self.token_usage[layer] = tokens_used
    
    def get_layer_for_file(self, file_path: str) -> str:
        """获取文件所属层级"""
        # P0 核心文件
        p0_files = ["AGENTS.md", "SOUL.md", "TOOLS.md", "USER.md", "IDENTITY.md", "HEARTBEAT.md"]
        if Path(file_path).name in p0_files:
            return "P0_CORE"
        
        # P3 归档文件
        p3_patterns = ["repo/", "reports/", ".pdf", ".log"]
        for pattern in p3_patterns:
            if pattern in file_path:
                return "P3_ARCHIVE"
        
        # P1 常用目录
        p1_dirs = ["orchestration/router/", "execution/skill_gateway", "memory_context/search/"]
        for dir_path in p1_dirs:
            if dir_path in file_path:
                return "P1_COMMON"
        
        # 默认 P2
        return "P2_EXTENDED"
    
    def get_summary(self) -> Dict:
        """获取层级摘要"""
        return {
            "loaded_layers": list(self.loaded_layers),
            "token_usage": self.token_usage,
            "total_tokens": sum(self.token_usage.values())
        }
