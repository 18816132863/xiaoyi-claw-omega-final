"""统一配置加载器 - V4.3.1

运行时只认 config/unified.json，其他配置仅作兼容。
"""

from typing import Dict, Any, Optional
from pathlib import Path
from infrastructure.path_resolver import get_project_root
import json

class UnifiedConfig:
    """统一配置加载器"""
    
    _instance = None
    _config: Dict = {}
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, workspace_path: str = None):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.workspace = Path(workspace_path or get_project_root())
        self.config_path = self.workspace / "config/unified.json"
        self._load()
        self._initialized = True
    
    def _load(self):
        """加载配置"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                self._config = json.load(f)
        else:
            self._config = self._defaults()
    
    def _defaults(self) -> Dict:
        """默认配置"""
        return {
            "version": "4.3.1",
            "search": {"top_k": 10, "mode": "balanced"},
            "cache": {"max_size": 1000, "default_ttl": 300},
            "router": {"mode": "balanced"},
            "token_budget": {"total": 10000}
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置"""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def get_all(self) -> Dict:
        """获取全部配置"""
        return self._config.copy()
    
    def reload(self):
        """重新加载"""
        self._load()

# 全局访问
_config = None

def get_config() -> UnifiedConfig:
    global _config
    if _config is None:
        _config = UnifiedConfig()
    return _config
