"""L6 懒加载模块"""

from .lazy_loader import LazyLoader, get_loader
from .layer_manager import LayerManager

__all__ = ['LazyLoader', 'LayerManager', 'get_loader']
