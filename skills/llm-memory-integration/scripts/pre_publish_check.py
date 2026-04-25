#!/usr/bin/env python3
"""
发布前安全检查脚本
在每次发布到 ClawHub 前运行，确保技能符合安全标准
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# 颜色输出
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_check(name, status, message=""):
    status_str = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if status else f"{Colors.RED}❌ FAIL{Colors.RESET}"
    print(f"  {name}: {status_str}")
    if message:
        print(f"    {message}")

def print_warning(message):
    print(f"  {Colors.YELLOW}⚠️  WARNING: {message}{Colors.RESET}")

def check_meta_json():
    """检查 _meta.json 文件"""
    print_header("检查 _meta.json")
    
    meta_path = Path(__file__).parent.parent / "_meta.json"
    if not meta_path.exists():
        print_check("_meta.json 存在", False, "文件不存在")
        return False
    
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    
    checks = []
    
    # 检查必需字段
    required_fields = ['name', 'version', 'description', 'license', 'author']
    for field in required_fields:
        if field in meta:
            print_check(f"字段 '{field}'", True, str(meta[field])[:50])
            checks.append(True)
        else:
            print_check(f"字段 '{field}'", False, "缺失")
            checks.append(False)
    
    # 检查安全相关字段
    security_fields = {
        'requiredBinaries': ['python3', 'sqlite3'],
        'requiredEnvVars': ['EMBEDDING_API_KEY'],
        'primaryCredential': 'EMBEDDING_API_KEY',
        'credentialType': 'api_key'
    }
    
    for field, expected in security_fields.items():
        if field in meta:
            if isinstance(expected, list):
                if meta[field] == expected:
                    print_check(f"安全字段 '{field}'", True, str(meta[field]))
                    checks.append(True)
                else:
                    print_check(f"安全字段 '{field}'", False, f"期望: {expected}, 实际: {meta[field]}")
                    checks.append(False)
            else:
                if meta[field] == expected:
                    print_check(f"安全字段 '{field}'", True, str(meta[field]))
                    checks.append(True)
                else:
                    print_check(f"安全字段 '{field}'", False, f"期望: {expected}, 实际: {meta[field]}")
                    checks.append(False)
        else:
            print_check(f"安全字段 '{field}'", False, "缺失")
            checks.append(False)
    
    return all(checks)

def check_install_json():
    """检查 install.json 文件"""
    print_header("检查 install.json")
    
    install_path = Path(__file__).parent.parent / "install.json"
    if not install_path.exists():
        print_check("install.json 存在", False, "文件不存在")
        return False
    
    with open(install_path, 'r', encoding='utf-8') as f:
        install = json.load(f)
    
    checks = []
    
    # 检查必需字段
    required_fields = ['version', 'requirements', 'high_risk_capabilities']
    for field in required_fields:
        if field in install:
            print_check(f"字段 '{field}'", True, "存在")
            checks.append(True)
        else:
            print_check(f"字段 '{field}'", False, "缺失")
            checks.append(False)
    
    # 检查高风险能力声明
    if 'high_risk_capabilities' in install:
        hrc = install['high_risk_capabilities']
        
        # 检查原生扩展声明
        if 'native_extensions' in hrc:
            ne = hrc['native_extensions']
            if 'risk_level' in ne and ne['risk_level'] == 'HIGH':
                print_check("原生扩展风险等级", True, "HIGH")
                checks.append(True)
            else:
                print_check("原生扩展风险等级", False, "未设置为 HIGH")
                checks.append(False)
            
            if 'audit_required' in ne and ne['audit_required'] == True:
                print_check("原生扩展审计要求", True, "已启用")
                checks.append(True)
            else:
                print_check("原生扩展审计要求", False, "未启用")
                checks.append(False)
        else:
            print_check("原生扩展声明", False, "缺失")
            checks.append(False)
    
    return all(checks)

def check_skill_md():
    """检查 SKILL.md 文件"""
    print_header("检查 SKILL.md")
    
    skill_path = Path(__file__).parent.parent / "SKILL.md"
    if not skill_path.exists():
        print_check("SKILL.md 存在", False, "文件不存在")
        return False
    
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = []
    
    # 检查必需章节
    required_sections = [
        'high_risk_capabilities_note',
        'dist_directory_note',
        '⚠️ 重要提示',
        '默认配置信息'
    ]
    
    for section in required_sections:
        if section in content:
            print_check(f"章节 '{section}'", True, "存在")
            checks.append(True)
        else:
            print_check(f"章节 '{section}'", False, "缺失")
            checks.append(False)
    
    # 检查版本号
    if 'version:' in content:
        version_line = [line for line in content.split('\n') if 'version:' in line][0]
        version = version_line.split(':')[1].strip()
        print_check("版本号", True, version)
        checks.append(True)
    else:
        print_check("版本号", False, "缺失")
        checks.append(False)
    
    return all(checks)

def check_syntax():
    """检查所有 Python 文件的语法"""
    print_header("检查 Python 语法")
    
    base_path = Path(__file__).parent.parent
    checks = []
    
    # 查找所有 Python 文件
    py_files = list(base_path.rglob("*.py"))
    error_count = 0
    
    for py_file in py_files:
        if 'node_modules' in str(py_file) or '.git' in str(py_file):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, str(py_file), 'exec')
        except SyntaxError as e:
            print_check(f"{py_file.relative_to(base_path)}", False, f"行 {e.lineno}: {e.msg}")
            checks.append(False)
            error_count += 1
    
    if error_count == 0:
        print_check("所有 Python 文件语法正确", True, f"共检查 {len(py_files)} 个文件")
        checks.append(True)
    else:
        print_warning(f"发现 {error_count} 个语法错误")
    
    return all(checks)

def check_no_secrets():
    """检查是否有硬编码的密钥"""
    print_header("检查敏感信息")
    
    base_path = Path(__file__).parent.parent
    checks = []
    
    # 检查的文件模式
    patterns = ['*.py', '*.json', '*.md']
    
    # 敏感信息模式
    secret_patterns = [
        'api_key = "sk-',
        'api_key="sk-',
        'password = "',
        'secret = "',
        'token = "',
    ]
    
    found_secrets = False
    
    for pattern in patterns:
        for file_path in base_path.rglob(pattern.replace('*', '')):
            if 'node_modules' in str(file_path) or '.git' in str(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for secret_pattern in secret_patterns:
                        if secret_pattern in content:
                            print_warning(f"在 {file_path} 中发现可能的敏感信息: {secret_pattern}")
                            found_secrets = True
            except:
                pass
    
    print_check("无硬编码密钥", not found_secrets)
    checks.append(not found_secrets)
    
    return all(checks)

def check_git_status():
    """检查 Git 状态"""
    print_header("检查 Git 状态")
    
    base_path = Path(__file__).parent.parent
    
    try:
        # 检查是否有未提交的更改
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=base_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            if result.stdout.strip():
                print_warning("有未提交的更改")
                print(result.stdout)
                return False
            else:
                print_check("工作目录干净", True)
                return True
        else:
            print_check("Git 状态检查", False, result.stderr)
            return False
    except Exception as e:
        print_check("Git 状态检查", False, str(e))
        return False

def check_security_files():
    """检查安全相关文件"""
    print_header("检查安全文件")
    
    base_path = Path(__file__).parent.parent
    checks = []
    
    # 检查 SECURITY.md
    security_md = base_path / "SECURITY.md"
    print_check("SECURITY.md", security_md.exists())
    checks.append(security_md.exists())
    
    # 检查 safe_extension_loader.py
    safe_loader = base_path / "src" / "scripts" / "safe_extension_loader.py"
    print_check("safe_extension_loader.py", safe_loader.exists())
    checks.append(safe_loader.exists())
    
    # 检查 security_audit.py
    security_audit = base_path / "src" / "scripts" / "security_audit.py"
    print_check("security_audit.py", security_audit.exists())
    checks.append(security_audit.exists())
    
    return all(checks)

def main():
    """主函数"""
    print(f"\n{Colors.BOLD}🔒 LLM Memory Integration 发布前安全检查{Colors.RESET}\n")
    
    all_checks = []
    
    # 运行所有检查
    all_checks.append(check_meta_json())
    all_checks.append(check_install_json())
    all_checks.append(check_skill_md())
    all_checks.append(check_security_files())
    all_checks.append(check_syntax())  # 新增语法检查
    all_checks.append(check_no_secrets())
    all_checks.append(check_git_status())
    
    # 总结
    print_header("检查总结")
    
    total = len(all_checks)
    passed = sum(all_checks)
    failed = total - passed
    
    print(f"  总计: {total} 项检查")
    print(f"  {Colors.GREEN}通过: {passed}{Colors.RESET}")
    print(f"  {Colors.RED}失败: {failed}{Colors.RESET}")
    
    if all(all_checks):
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ 所有检查通过，可以发布！{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ 存在未通过的检查，请修复后再发布！{Colors.RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
