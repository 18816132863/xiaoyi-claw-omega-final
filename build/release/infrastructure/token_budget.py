"""Token 预算管理器 - V4.3.2 收尾

接入主搜索上下文装配，超预算时真实限制
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import json

class TokenBudgetManager:
    """Token 预算管理器"""
    
    def __init__(self, max_tokens: int = 9500):
        self.max_tokens = max_tokens
        self.current_usage = 0
        self.layer_usage: Dict[str, int] = {}
        self.budget_config = self._load_budget_config()
    
    def _load_budget_config(self) -> Dict:
        """加载预算配置"""
        config_path = Path("infrastructure/inventory/load_config.json")
        if config_path.exists():
            return json.loads(config_path.read_text())
        return {
            "context_budget": {
                "layers": {
                    "L1": {"max_tokens": 3000},
                    "L2": {"max_tokens": 2000},
                    "L3": {"max_tokens": 1500},
                    "L4": {"max_tokens": 1500},
                    "L5": {"max_tokens": 800},
                    "L6": {"max_tokens": 700},
                }
            }
        }
    
    def estimate_tokens(self, text: str) -> int:
        """估算文本 Token 数"""
        # 中文约 0.5 token/字，英文约 0.25 token/char
        import re
        chinese = len(re.findall(r'[\u4e00-\u9fff]', text))
        other = len(text) - chinese
        return int(chinese / 2 + other / 4)
    
    def can_load(self, layer: str, text: str) -> bool:
        """检查是否可以加载"""
        tokens = self.estimate_tokens(text)
        layer_budget = self.budget_config.get("context_budget", {}).get("layers", {}).get(layer, {})
        layer_max = layer_budget.get("max_tokens", 1500)
        
        # 检查层级预算
        if self.layer_usage.get(layer, 0) + tokens > layer_max:
            return False
        
        # 检查总预算
        if self.current_usage + tokens > self.max_tokens:
            return False
        
        return True
    
    def register_load(self, layer: str, text: str):
        """注册加载"""
        tokens = self.estimate_tokens(text)
        self.current_usage += tokens
        self.layer_usage[layer] = self.layer_usage.get(layer, 0) + tokens
    
    def get_summary(self) -> Dict:
        """获取预算摘要"""
        return {
            "max_tokens": self.max_tokens,
            "current_usage": self.current_usage,
            "remaining": self.max_tokens - self.current_usage,
            "usage_percent": round(self.current_usage / self.max_tokens * 100, 1),
            "layer_usage": self.layer_usage
        }
    
    def reset(self):
        """重置预算"""
        self.current_usage = 0
        self.layer_usage = {}

class LazyLoader:
    """延迟加载器 - V4.3.2 最终修正：硬限制"""
    
    def __init__(self, budget_manager: TokenBudgetManager = None):
        self.budget_manager = budget_manager or TokenBudgetManager()
        self.loaded: Dict[str, Any] = {}
        self.pending: Dict[str, Path] = {}
        self._budget_exceeded = False
    
    def register(self, key: str, path: Path):
        """注册待加载文件"""
        self.pending[key] = path
    
    def load(self, key: str, layer: str = "L4") -> Optional[str]:
        """延迟加载 - 带硬限制
        
        V4.3.2 最终修正：budget_exceeded 只反映总预算状态
        - 单个文件太大超过总预算：跳过该文件，不设置 budget_exceeded
        - 累计使用超过总预算：设置 budget_exceeded = True
        - 层级预算超限：跳过该文件，不设置 budget_exceeded
        """
        # 检查是否已超总预算
        if self._budget_exceeded:
            return None
        
        if key in self.loaded:
            return self.loaded[key]
        
        if key not in self.pending:
            return None
        
        path = self.pending[key]
        if not path.exists():
            return None
        
        try:
            content = path.read_text(encoding='utf-8')
            tokens = self.budget_manager.estimate_tokens(content)
            
            # 检查单个文件是否太大（超过剩余预算）
            remaining = self.budget_manager.max_tokens - self.budget_manager.current_usage
            if tokens > remaining:
                # 文件太大，尝试截断
                max_chars = min(300, int(remaining * 4))  # 估算字符数
                if max_chars < 100:
                    # 剩余预算太小，跳过此文件
                    return None
                content = content[:max_chars]
                tokens = self.budget_manager.estimate_tokens(content)
            
            # 再次检查截断后是否可以加载
            if self.budget_manager.current_usage + tokens > self.budget_manager.max_tokens:
                # 累计超限，设置 budget_exceeded
                self._budget_exceeded = True
                return None
            
            # 检查层级预算
            if not self.budget_manager.can_load(layer, content):
                # 层级预算超限，跳过此文件但不设置 budget_exceeded
                return None
            
            self.budget_manager.register_load(layer, content)
            self.loaded[key] = content
            return content
        except:
            return None
    
    def reset(self):
        """重置状态"""
        self._budget_exceeded = False
        self.loaded.clear()
        self.pending.clear()
    
    def get_status(self) -> Dict:
        """获取加载状态"""
        return {
            "loaded": list(self.loaded.keys()),
            "pending": list(self.pending.keys()),
            "budget_exceeded": self._budget_exceeded,
            "budget": self.budget_manager.get_summary()
        }

# 全局实例
_token_manager: Optional[TokenBudgetManager] = None
_lazy_loader: Optional[LazyLoader] = None

def get_token_manager() -> TokenBudgetManager:
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenBudgetManager()
    return _token_manager

def get_lazy_loader() -> LazyLoader:
    global _lazy_loader
    if _lazy_loader is None:
        _lazy_loader = LazyLoader(get_token_manager())
    return _lazy_loader
