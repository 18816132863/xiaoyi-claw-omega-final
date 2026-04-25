from pathlib import Path

def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent
    while current != "/" and not (current / "core" / "ARCHITECTURE.md").exists():
        current = current.parent
    return current if current != "/" else Path(__file__).resolve().parent

#!/usr/bin/env python3
"""
架构集成脚本
V2.7.0 - 2026-04-10

将性能模块集成到六层架构
"""

import os
import json
from pathlib import Path

WORKSPACE = Path(str(get_project_root()))

# 层级配置
LAYER_CONFIG = {
    "L1_core": {
        "path": "core",
        "components": ["fast_bridge", "smart_router"],
        "imports": [
            "from infrastructure.performance import fast_call, Layer, get_router"
        ]
    },
    "L2_memory": {
        "path": "memory_context",
        "components": ["layer_cache", "zero_copy"],
        "imports": [
            "from infrastructure.performance import cache_get, cache_set, share_data, get_shared"
        ]
    },
    "L3_orchestration": {
        "path": "orchestration",
        "components": ["async_queue", "smart_router"],
        "imports": [
            "from infrastructure.performance import async_call, Priority, get_router"
        ]
    },
    "L4_execution": {
        "path": "execution",
        "components": ["unified_optimizer", "performance_monitor"],
        "imports": [
            "from infrastructure.performance import optimize_call, get_monitor"
        ]
    },
    "L5_governance": {
        "path": "governance",
        "components": ["performance_monitor"],
        "imports": [
            "from infrastructure.performance import get_monitor"
        ]
    },
    "L6_infrastructure": {
        "path": "infrastructure",
        "components": ["performance_monitor", "smart_router"],
        "imports": [
            "from infrastructure.performance import get_monitor, get_router"
        ]
    }
}

def create_layer_integration(layer_name: str, config: dict):
    """创建层级集成文件"""
    layer_path = WORKSPACE / config["path"]
    
    if not layer_path.exists():
        print(f"跳过 {layer_name}: 目录不存在")
        return
    
    # 创建集成文件
    integration_file = layer_path / "performance_integration.py"
    
    content = f'''"""
{layer_name} 性能集成
V2.7.0 - 2026-04-10

集成组件: {", ".join(config["components"])}
"""

# 导入性能组件
{chr(10).join(config["imports"])}

# 初始化
def init_performance():
    """初始化性能组件"""
    pass

# 导出
__all__ = [
    {", ".join([f"'{imp.split()[-1]}'" for imp in config["imports"]])}
]
'''
    
    integration_file.write_text(content)
    print(f"✓ 创建 {integration_file}")

def main():
    """主函数"""
    print("="*50)
    print("性能模块架构集成")
    print("="*50 + "\n")
    
    for layer_name, config in LAYER_CONFIG.items():
        create_layer_integration(layer_name, config)
    
    print("\n" + "="*50)
    print("集成完成")
    print("="*50)

if __name__ == "__main__":
    main()
