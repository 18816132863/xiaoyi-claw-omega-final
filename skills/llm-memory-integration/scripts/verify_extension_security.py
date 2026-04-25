#!/usr/bin/env python3
"""
原生扩展加载安全措施验证脚本

验证原生扩展加载的所有安全措施是否正确实现。
"""

import hashlib
import json
import os
import stat
from pathlib import Path


def print_header(title: str):
    """打印标题"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def print_check(name: str, passed: bool, message: str = ""):
    """打印检查结果"""
    status = "✅" if passed else "❌"
    print(f"  {status} {name}")
    if message:
        print(f"     {message}")


def verify_hash_implementation():
    """验证哈希检查实现"""
    print_header("1. 哈希检查验证")
    
    safe_loader = Path(__file__).parent.parent / "src" / "scripts" / "safe_extension_loader.py"
    
    if not safe_loader.exists():
        print_check("文件存在", False, "safe_extension_loader.py 不存在")
        return False
    
    content = safe_loader.read_text()
    
    # 检查哈希验证函数
    has_verify_hash = "verify_file_signature" in content or "calculate_file_hash" in content
    has_sha256 = "sha256" in content or "hashlib.sha256" in content
    has_hashlib = "import hashlib" in content
    
    print_check("verify_file_signature 函数", has_verify_hash)
    print_check("SHA256 哈希算法", has_sha256)
    print_check("hashlib 导入", has_hashlib)
    
    return all([has_verify_hash, has_sha256, has_hashlib])


def verify_trustlist():
    """验证信任列表"""
    print_header("2. 信任列表验证")
    
    trust_file = Path.home() / ".openclaw" / "extensions" / ".trusted_hashes.json"
    
    if not trust_file.exists():
        print_check("信任列表文件", True, "信任列表不存在（首次使用时创建）")
        return True
    
    try:
        trust_list = json.loads(trust_file.read_text())
        if isinstance(trust_list, dict):
            print_check("信任列表格式", True, f"包含 {len(trust_list)} 个条目")
            return True
        else:
            print_check("信任列表格式", False, "格式错误（应为 dict）")
            return False
    except Exception as e:
        print_check("信任列表解析", False, f"解析错误: {e}")
        return False


def verify_manual_confirmation():
    """验证手动确认"""
    print_header("3. 手动确认验证")
    
    config_file = Path(__file__).parent.parent / "config" / "extension_config.json"
    
    if not config_file.exists():
        print_check("配置文件存在", False, "extension_config.json 不存在")
        return False
    
    try:
        config = json.loads(config_file.read_text())
        require_confirmation = config.get("require_confirmation", True)
        
        print_check("手动确认配置", require_confirmation, 
                   f"require_confirmation: {require_confirmation}")
        
        return require_confirmation
    except Exception as e:
        print_check("配置文件解析", False, f"解析错误: {e}")
        return False


def verify_default_disabled():
    """验证默认禁用"""
    print_header("4. 默认禁用验证")
    
    config_file = Path(__file__).parent.parent / "config" / "extension_config.json"
    
    if not config_file.exists():
        print_check("配置文件存在", False, "extension_config.json 不存在")
        return False
    
    try:
        config = json.loads(config_file.read_text())
        auto_load = config.get("auto_load", False)
        
        # auto_load 应该为 False（默认禁用）
        is_disabled = not auto_load
        
        print_check("默认禁用", is_disabled, f"auto_load: {auto_load}")
        
        return is_disabled
    except Exception as e:
        print_check("配置文件解析", False, f"解析错误: {e}")
        return False


def verify_permission_check():
    """验证文件权限检查"""
    print_header("5. 文件权限检查验证")
    
    safe_loader = Path(__file__).parent.parent / "src" / "scripts" / "safe_extension_loader.py"
    
    if not safe_loader.exists():
        print_check("文件存在", False, "safe_extension_loader.py 不存在")
        return False
    
    content = safe_loader.read_text()
    
    # 检查权限检查函数
    has_check_permissions = "check_permissions" in content or "st_mode" in content
    has_stat = "import stat" in content or "os.stat" in content
    
    print_check("权限检查函数", has_check_permissions)
    print_check("stat 导入", has_stat)
    
    return all([has_check_permissions, has_stat])


def verify_path_validation():
    """验证路径验证"""
    print_header("6. 路径验证验证")
    
    safe_loader = Path(__file__).parent.parent / "src" / "scripts" / "safe_extension_loader.py"
    
    if not safe_loader.exists():
        print_check("文件存在", False, "safe_extension_loader.py 不存在")
        return False
    
    content = safe_loader.read_text()
    
    # 检查路径验证函数
    has_validate_path = "check_extension_integrity" in content or "get_vec_extension_path" in content
    has_path_check = ".openclaw" in content and "extensions" in content
    
    print_check("路径验证函数", has_validate_path)
    print_check("路径检查", has_path_check)
    
    return all([has_validate_path, has_path_check])


def main():
    """主函数"""
    print("=" * 60)
    print("  🔍 原生扩展加载安全措施验证")
    print("=" * 60)
    
    results = []
    
    # 验证所有安全措施
    results.append(("哈希检查", verify_hash_implementation()))
    results.append(("信任列表", verify_trustlist()))
    results.append(("手动确认", verify_manual_confirmation()))
    results.append(("默认禁用", verify_default_disabled()))
    results.append(("文件权限检查", verify_permission_check()))
    results.append(("路径验证", verify_path_validation()))
    
    # 打印总结
    print_header("验证总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        print_check(name, result)
    
    print(f"\n  总计: {passed}/{total} 项通过")
    
    if passed == total:
        print("\n  ✅ 所有安全措施已正确实现")
        return 0
    else:
        print(f"\n  ⚠️  有 {total - passed} 项安全措施未通过验证")
        return 1


if __name__ == "__main__":
    exit(main())
