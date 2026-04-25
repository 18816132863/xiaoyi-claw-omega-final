"""
可选模块初始化
所有高风险功能默认禁用，需要用户明确启用
"""

from .sqlite_extension import is_enabled as is_sqlite_extension_enabled
from .subprocess_utils import is_enabled as is_subprocess_enabled

__all__ = [
    'is_sqlite_extension_enabled',
    'is_subprocess_enabled',
]

# 模块状态
STATUS = {
    'sqlite_extension': {
        'enabled': False,
        'risk': 'high',
        'description': 'SQLite 扩展加载（vec0.so）',
        'requires': 'ENABLE_SQLITE_EXTENSION=true',
    },
    'subprocess_utils': {
        'enabled': False,
        'risk': 'medium',
        'description': 'subprocess 调用（读取系统信息）',
        'requires': 'ENABLE_SUBPROCESS=true',
    },
}

def get_status() -> dict:
    """获取所有可选模块状态"""
    return STATUS

def print_status():
    """打印所有可选模块状态"""
    print("=== 可选模块状态 ===")
    for name, info in STATUS.items():
        status = "✅ 启用" if info['enabled'] else "❌ 禁用"
        print(f"{name}: {status}")
        print(f"  风险: {info['risk']}")
        print(f"  描述: {info['description']}")
        print(f"  启用: {info['requires']}")
        print()
