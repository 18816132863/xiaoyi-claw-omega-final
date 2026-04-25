"""懒加载器 - V1.0.0"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from infrastructure.path_resolver import get_project_root
from functools import lru_cache
import time

class LazyLoader:
    """分层懒加载器"""
    
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path or get_project_root())
        self.config = self._load_config()
        self.cache = {}
        self.load_stats = {"hits": 0, "misses": 0}
    
    def _load_config(self) -> Dict:
        """加载分层配置"""
        config_path = self.workspace / "infrastructure/optimization/LAYERED_LOADING.json"
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {"layers": {}}
    
    def load_layer(self, layer_name: str) -> Dict[str, Any]:
        """加载指定层"""
        start = time.time()
        
        # 检查缓存
        if layer_name in self.cache:
            self.load_stats["hits"] += 1
            return self.cache[layer_name]
        
        self.load_stats["misses"] += 1
        
        layer_config = self.config.get("layers", {}).get(layer_name, {})
        result = {}
        
        # 加载文件
        for file_path in layer_config.get("files", []):
            full_path = self.workspace / file_path
            if full_path.exists():
                result[file_path] = self._load_file(full_path)
        
        # 加载目录
        for dir_path in layer_config.get("directories", []):
            full_dir = self.workspace / dir_path.rstrip("/")
            if full_dir.exists():
                result[dir_path] = self._load_directory(full_dir)
        
        # 缓存结果
        load_mode = layer_config.get("load_mode", "lazy")
        if load_mode in ["immediate", "on_demand"]:
            self.cache[layer_name] = result
        
        elapsed = (time.time() - start) * 1000
        return {"data": result, "load_time_ms": elapsed}
    
    def _load_file(self, path: Path) -> str:
        """加载单个文件"""
        try:
            return path.read_text(encoding="utf-8")
        except:
            return ""
    
    def _load_directory(self, path: Path, max_files: int = 50) -> Dict[str, str]:
        """加载目录内容"""
        result = {}
        count = 0
        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".md", ".py", ".json"]:
                if count >= max_files:
                    break
                result[str(file_path.relative_to(path))] = self._load_file(file_path)
                count += 1
        return result
    
    def get_stats(self) -> Dict:
        """获取加载统计"""
        return {
            "cache_size": len(self.cache),
            "hits": self.load_stats["hits"],
            "misses": self.load_stats["misses"],
            "hit_rate": self.load_stats["hits"] / max(1, self.load_stats["hits"] + self.load_stats["misses"])
        }

# 全局实例
_loader = None

def get_loader() -> LazyLoader:
    global _loader
    if _loader is None:
        _loader = LazyLoader()
    return _loader
