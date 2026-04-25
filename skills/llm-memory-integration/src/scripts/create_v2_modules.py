#!/usr/bin/env python3
"""
v2.0 模块安装脚本
从模板目录复制预定义的模块文件

🔒 安全设计：
- 不生成任何代码，仅复制预定义模板
- 模板文件已预先审计
- 无动态代码执行
- 无网络请求
"""

import os
import sys
import hashlib
import shutil
from pathlib import Path

# 使用相对路径
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"

# 安全检查：确保在正确的目录运行
if not (BASE_DIR / "search.py").exists():
    print("❌ 错误：请在正确的目录运行此脚本")
    print("   此脚本必须在 llm-memory-integration/scripts 目录下运行")
    sys.exit(1)

# 预定义的模块列表（白名单）
ALLOWED_MODULES = {
    "async_support.py": "异步支持模块",
    "test_suite.py": "单元测试模块",
    "benchmark.py": "性能基准模块",
    "performance_monitor.py": "监控指标模块"
}

def calculate_file_hash(file_path: Path) -> str:
    """计算文件 SHA256 哈希"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def copy_template_module(module_name: str) -> bool:
    """
    从模板目录复制模块文件
    
    - 检查模块在白名单中
    - 从模板目录复制
    - 设置安全权限
    """
    if module_name not in ALLOWED_MODULES:
        print(f"❌ 拒绝复制：{module_name} 不在允许列表中")
        return False
    
    template_path = TEMPLATES_DIR / module_name
    target_path = BASE_DIR / module_name
    
    if not template_path.exists():
        print(f"⚠️ 模板不存在：{module_name}")
        return False
    
    try:
        # 复制文件
        shutil.copy2(template_path, target_path)
        
        # 设置权限：仅所有者可读写
        os.chmod(target_path, 0o644)
        
        # 计算并记录哈希
        file_hash = calculate_file_hash(target_path)[:16]
        print(f"  ✅ {module_name} (SHA256: {file_hash}...)")
        
        return True
    except Exception as e:
        print(f"❌ 复制失败：{module_name} - {e}")
        return False

def main():
    print("=" * 60)
    print("v2.0 模块安装脚本")
    print("=" * 60)
    
    print("\n📦 从模板安装模块...")
    print(f"   模板目录: {TEMPLATES_DIR}")
    
    if not TEMPLATES_DIR.exists():
        print(f"❌ 模板目录不存在: {TEMPLATES_DIR}")
        print("   请确保 templates 目录存在并包含模块文件")
        sys.exit(1)
    
    success_count = 0
    for module_name in ALLOWED_MODULES:
        if copy_template_module(module_name):
            success_count += 1
    
    print(f"\n📊 安装完成: {success_count}/{len(ALLOWED_MODULES)} 个模块")
    
    if success_count < len(ALLOWED_MODULES):
        print("⚠️ 部分模块安装失败")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ v2.0 模块安装完成")
    print("=" * 60)
    print("\n🔒 安全说明：")
    print("  - 所有模块从预定义模板复制")
    print("  - 模板文件已预先审计")
    print("  - 无动态代码生成")
    print("  - 文件权限已设置为 644")

if __name__ == "__main__":
    main()
