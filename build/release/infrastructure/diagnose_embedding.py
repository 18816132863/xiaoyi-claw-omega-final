#!/usr/bin/env python3
"""
Embedding 诊断脚本 - V3.0

输出：
1. 项目根
2. 配置文件路径
3. config_loaded
4. api_key 来源
5. base_url / model
6. mode
7. reason
8. exception_type / exception_message
"""

import os
import sys
import json
from pathlib import Path


def find_project_root() -> Path:
    """查找项目根目录"""
    # 1. 环境变量
    for var in ['OPENCLAW_PROJECT_ROOT', 'OPENCLAW_WORKSPACE']:
        val = os.environ.get(var)
        if val:
            path = Path(val)
            if (path / 'core' / 'ARCHITECTURE.md').exists():
                return path
    
    # 2. 当前目录向上查找
    current = Path.cwd()
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    
    # 3. 回退到当前目录
    return Path.cwd()


def diagnose():
    print("╔══════════════════════════════════════════════════╗")
    print("║        Embedding 诊断 V3.0                       ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    # 1. 项目根
    print("【1】项目根")
    project_root = find_project_root()
    print(f"  project_root: {project_root}")
    print(f"  core/ARCHITECTURE.md 存在: {(project_root / 'core' / 'ARCHITECTURE.md').exists()}")
    print()
    
    # 2. 配置文件路径
    print("【2】配置文件路径")
    config_path = project_root / "skills" / "llm-memory-integration" / "config" / "llm_config.json"
    print(f"  config_path: {config_path}")
    print(f"  存在: {config_path.exists()}")
    print()
    
    # 3. 添加项目根到 sys.path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # 4. QwenEmbeddingEngine 检查
    print("【3】QwenEmbeddingEngine 状态")
    try:
        from memory_context.unified_search import QwenEmbeddingEngine
        
        engine = QwenEmbeddingEngine()
        config_info = engine.get_config_info()
        
        print(f"  config_loaded: {config_info['config_loaded']}")
        print(f"  api_key_source: {config_info['api_key_source']}")
        print(f"  provider: {config_info['provider']}")
        print(f"  base_url: {config_info['base_url']}")
        print(f"  model: {config_info['model']}")
        print(f"  api_key: {config_info['api_key']}")
        print(f"  dimensions: {config_info['dimensions']}")
        print()
        
        # 5. 连接测试
        print("【4】连接测试")
        connection_ok = engine.test_connection()
        config_info = engine.get_config_info()  # 刷新状态
        
        print(f"  connection_ok: {config_info['connection_ok']}")
        print(f"  mode: {config_info['mode']}")
        print(f"  reason: {config_info['reason']}")
        print(f"  exception_type: {config_info['exception_type']}")
        print(f"  exception_message: {config_info['exception_message']}")
        print()
        
        # 6. 实际编码测试
        print("【5】实际编码测试")
        if config_info['mode'] == "embedding":
            try:
                vec = engine.encode("这是一个测试文本")
                print(f"  向量长度: {len(vec)}")
                print(f"  前5个值: {vec[:5]}")
                print(f"  ✅ 真实 embedding 已接通")
            except Exception as e:
                print(f"  ❌ 编码失败: {type(e).__name__}: {e}")
        else:
            print(f"  ❌ 跳过（mode = {config_info['mode']}）")
            print(f"  原因: {config_info['reason']}")
            if config_info['exception_type']:
                print(f"  异常类型: {config_info['exception_type']}")
            if config_info['exception_message']:
                print(f"  异常信息: {config_info['exception_message']}")
        print()
        
        # 7. UnifiedSearch 检查
        print("【6】UnifiedSearch 检查")
        try:
            from memory_context.unified_search import UnifiedSearch
            
            search = UnifiedSearch(project_root)
            print(f"  get_vector_mode(): {search.get_vector_mode()}")
            
            result = search.search("docx", limit=3)
            vector_mode = result.get('vector_mode')
            print(f"  search('docx').vector_mode: {vector_mode}")
            
            if vector_mode == 'embedding':
                print(f"  ✅ search() 返回正确")
            else:
                print(f"  ❌ search() 返回错误")
        except Exception as e:
            print(f"  ❌ 错误: {type(e).__name__}: {e}")
            
    except Exception as e:
        print(f"  ❌ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("══════════════════════════════════════════════════")


if __name__ == "__main__":
    diagnose()
