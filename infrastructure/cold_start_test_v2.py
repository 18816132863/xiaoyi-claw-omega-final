from pathlib import Path

def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent
    while current != "/" and not (current / "core" / "ARCHITECTURE.md").exists():
        current = current.parent
    return current if current != "/" else Path(__file__).resolve().parent

#!/usr/bin/env python3
"""
冷启动测试脚本 - V2.0

严格验收标准：
1. 首次 build_index(force=False) → mode = loaded
2. vector_mode = embedding（degraded 判失败）

重要：
- 不插入旧 workspace 到 sys.path
- 只使用新解压目录的模块
"""

import os
import sys
import json
import shutil
import tarfile
import tempfile
from pathlib import Path


def clean_env():
    """清理污染环境变量"""
    env_vars = [
        "OPENCLAW_GIT_DIR",
        "OPENCLAW_WORKSPACE",
        "OPENCLAW_PROJECT_ROOT",
    ]
    
    for var in env_vars:
        if var in os.environ:
            print(f"清理环境变量: {var}={os.environ[var]}")
            del os.environ[var]


def test_cold_start(tar_file: Path):
    """冷启动测试"""
    print("╔══════════════════════════════════════════════════╗")
    print("║        冷启动测试 V2.0 (严格验收)                ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    # 1. 清理环境变量
    print("【步骤 1】清理环境变量")
    clean_env()
    print()
    
    # 2. 解压到全新目录
    print("【步骤 2】解压到全新目录")
    test_dir = Path(tempfile.mkdtemp(prefix="cold_start_test_"))
    print(f"测试目录: {test_dir}")
    
    with tarfile.open(tar_file, "r:gz") as tar:
        tar.extractall(test_dir)
    
    extracted_dir = test_dir / ".openclaw" / "workspace"
    print(f"解压目录: {extracted_dir}")
    print()
    
    # 3. 切换工作目录
    print("【步骤 3】切换工作目录")
    original_cwd = os.getcwd()
    os.chdir(extracted_dir)
    print(f"当前目录: {os.getcwd()}")
    print()
    
    # 4. 只插入新解压目录到 sys.path（不插入旧 workspace）
    print("【步骤 4】设置 Python 路径")
    # 清理可能存在的旧路径
    sys.path = [p for p in sys.path if str(get_project_root()) not in p]
    # 只插入新解压目录
    sys.path.insert(0, str(extracted_dir))
    print(f"sys.path[0]: {sys.path[0]}")
    print()
    
    # 5. 检查索引文件
    print("【步骤 5】检查索引文件")
    index_dir = extracted_dir / "memory_context" / "index"
    for f in ["keyword_index.json", "fts_index.json", "vector_index.json", 
              "index_metadata.json", "file_states.json"]:
        path = index_dir / f
        if path.exists():
            size = path.stat().st_size
            print(f"  ✓ {f}: {size} bytes")
        else:
            print(f"  ✗ {f}: 不存在")
    print()
    
    # 6. 执行 build_index(force=False)
    print("【步骤 6】执行 build_index(force=False)")
    passed = True
    
    try:
        # 动态导入（从新解压目录）
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "unified_search", 
            extracted_dir / "memory_context" / "unified_search.py"
        )
        us_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(us_module)
        UnifiedSearch = us_module.UnifiedSearch
        
        search = UnifiedSearch(extracted_dir)
        result = search.build_index(force=False)
        
        print(f"  mode: {result['mode']}")
        print(f"  files_indexed: {result['files_indexed']}")
        print(f"  time_ms: {result['time_ms']}")
        print(f"  incremental: {result['incremental']}")
        print()
        
        # 验收标准 1
        if result['mode'] == 'loaded':
            print("  ✅ 验收通过: mode = loaded")
        else:
            print(f"  ❌ 验收失败: mode = {result['mode']}，期望 loaded")
            passed = False
        print()
        
        # 7. 执行搜索测试
        print("【步骤 7】执行搜索测试")
        test_queries = ["docx", "pdf", "architecture"]
        
        for query in test_queries:
            search_result = search.search(query, limit=5)
            vector_mode = search_result.get("vector_mode", "unknown")
            total = search_result.get("total", 0)
            print(f"  查询: {query}")
            print(f"    vector_mode: {vector_mode}")
            print(f"    结果数: {total}")
        
        print()
        
        # 验收标准 2 - 严格：degraded 判失败
        vector_mode = search.get_vector_mode()
        if vector_mode == "embedding":
            print("  ✅ 验收通过: vector_mode = embedding")
        else:
            print(f"  ❌ 验收失败: vector_mode = {vector_mode}，期望 embedding")
            passed = False
        print()
        
        # 8. 输出 embedding 配置信息
        print("【步骤 8】Embedding 配置信息")
        try:
            embedding_engine = us_module.QwenEmbeddingEngine()
            print(f"  mode: {embedding_engine.get_mode()}")
            print(f"  api_key: {'已配置' if embedding_engine.api_key else '未配置'}")
            print(f"  base_url: {embedding_engine.base_url or '未配置'}")
            print(f"  model: {embedding_engine.model or '未配置'}")
            print(f"  dimensions: {embedding_engine.dimensions}")
        except Exception as e:
            print(f"  获取配置失败: {e}")
        print()
        
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        passed = False
    
    finally:
        # 恢复工作目录
        os.chdir(original_cwd)
        
        # 清理测试目录
        print("【清理】删除测试目录")
        shutil.rmtree(test_dir)
        print()
    
    print("══════════════════════════════════════════════════")
    if passed:
        print("✅ 冷启动测试全部通过")
    else:
        print("❌ 冷启动测试失败")
    print("══════════════════════════════════════════════════")
    
    return passed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python cold_start_test_v2.py <tar_file>")
        sys.exit(1)
    
    tar_file = Path(sys.argv[1])
    if not tar_file.exists():
        print(f"错误: 文件不存在 {tar_file}")
        sys.exit(1)
    
    passed = test_cold_start(tar_file)
    sys.exit(0 if passed else 1)
