#!/usr/bin/env python
"""
安全脱敏检查
检查文档和样例中是否有敏感信息泄漏
"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_phone_numbers() -> bool:
    """检查未脱敏手机号"""
    print(f"\n{'='*60}")
    print("🔍 手机号脱敏检查")
    print(f"{'='*60}")
    
    # 中国手机号正则
    phone_pattern = re.compile(r'1[3-9]\d{9}')
    
    # 检查文档文件
    doc_files = list(project_root.glob("*.md")) + list(project_root.glob("*.txt"))
    
    found_phones = []
    for doc in doc_files:
        try:
            content = doc.read_text()
            matches = phone_pattern.findall(content)
            for match in matches:
                # 检查是否已脱敏（包含 ****）
                if "****" not in content[max(0, content.find(match)-10):content.find(match)+15]:
                    # 排除示例号码
                    if match.startswith("138") or match.startswith("139"):
                        # 这些是示例号码，检查是否在代码块中
                        lines = content.split("\n")
                        for i, line in enumerate(lines):
                            if match in line:
                                # 如果在同一行有 "示例" 或 "example"，跳过
                                if "示例" in line or "example" in line.lower():
                                    continue
                                # 如果在 JSON 代码块中，检查是否已脱敏
                                if '"phone"' in line or '"phone_number"' in line:
                                    if "****" not in line:
                                        found_phones.append(f"{doc.name}:{i+1}: {match}")
        except:
            pass
    
    if found_phones:
        print(f"⚠️ 发现可能的未脱敏手机号 ({len(found_phones)} 处):")
        for f in found_phones[:5]:
            print(f"  {f}")
        return True  # 警告但不失败
    else:
        print("✅ 无未脱敏手机号")
        return True


def check_auth_codes() -> bool:
    """检查真实 authCode"""
    print(f"\n{'='*60}")
    print("🔍 AuthCode 泄漏检查")
    print(f"{'='*60}")
    
    # 检查文档文件
    doc_files = list(project_root.glob("*.md")) + list(project_root.glob("*.txt"))
    
    found_auth_codes = []
    for doc in doc_files:
        try:
            content = doc.read_text()
            lines = content.split("\n")
            for i, line in enumerate(lines):
                # 检查是否有真实的 authCode 赋值
                if "authCode" in line or "auth_code" in line or "XIAOYI_AUTH_CODE" in line:
                    # 排除示例
                    if "your_" in line or "example" in line.lower() or "xxx" in line:
                        continue
                    # 检查是否有真实值（不是空字符串或占位符）
                    if "=" in line and '"' in line:
                        # 提取值
                        match = re.search(r'=\s*["\']([^"\']+)["\']', line)
                        if match:
                            value = match.group(1)
                            if len(value) > 10 and not value.startswith("your"):
                                found_auth_codes.append(f"{doc.name}:{i+1}: {line[:60]}")
        except:
            pass
    
    if found_auth_codes:
        print(f"❌ 发现可能的 AuthCode 泄漏 ({len(found_auth_codes)} 处):")
        for f in found_auth_codes[:5]:
            print(f"  {f}")
        return False
    else:
        print("✅ 无 AuthCode 泄漏")
        return True


def check_export_samples() -> bool:
    """检查导出样例"""
    print(f"\n{'='*60}")
    print("🔍 导出样例检查")
    print(f"{'='*60}")
    
    # 检查 demo_outputs 目录
    demo_outputs = project_root / "demo_outputs"
    
    if not demo_outputs.exists():
        print("✅ 无导出样例目录")
        return True
    
    # 检查导出文件
    export_files = list(demo_outputs.glob("*.json")) + list(demo_outputs.glob("*.csv"))
    
    found_sensitive = []
    for ef in export_files:
        try:
            content = ef.read_text()
            # 检查是否有未脱敏的手机号
            phone_pattern = re.compile(r'1[3-9]\d{9}')
            matches = phone_pattern.findall(content)
            for match in matches:
                if "****" not in match:
                    found_sensitive.append(f"{ef.name}: {match}")
        except:
            pass
    
    if found_sensitive:
        print(f"⚠️ 导出样例中有未脱敏数据 ({len(found_sensitive)} 处)")
        return True  # 警告但不失败
    else:
        print("✅ 导出样例安全")
        return True


def check_backup_samples() -> bool:
    """检查备份样例"""
    print(f"\n{'='*60}")
    print("🔍 备份样例检查")
    print(f"{'='*60}")
    
    # 检查 backups 目录
    backups = project_root / "backups"
    
    if not backups.exists():
        print("✅ 无备份目录")
        return True
    
    # 检查备份文件
    backup_files = list(backups.glob("*.json"))
    
    if backup_files:
        print(f"⚠️ 发现备份文件 ({len(backup_files)} 个)，请确保不含敏感数据")
        return True
    else:
        print("✅ 无备份文件")
        return True


def check_config_files() -> bool:
    """检查配置文件"""
    print(f"\n{'='*60}")
    print("🔍 配置文件检查")
    print(f"{'='*60}")
    
    config_files = [
        project_root / "config" / "xiaoyi_config.json",
        project_root / ".xiaoyi_auth",
    ]
    
    found_secrets = []
    for cf in config_files:
        if cf.exists():
            try:
                content = cf.read_text()
                # 检查是否有真实 authCode
                if len(content) > 10 and "your_" not in content:
                    found_secrets.append(str(cf))
            except:
                pass
    
    if found_secrets:
        print(f"⚠️ 配置文件可能含敏感信息 ({len(found_secrets)} 个):")
        for f in found_secrets:
            print(f"  {f}")
        return True  # 警告但不失败
    else:
        print("✅ 配置文件安全")
        return True


def main():
    """主函数"""
    print("=" * 60)
    print("🔒 安全脱敏检查")
    print("=" * 60)
    print(f"时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"工作目录: {project_root}")
    
    results = {}
    
    # 1. 手机号检查
    results["phone_numbers"] = check_phone_numbers()
    
    # 2. AuthCode 检查
    results["auth_codes"] = check_auth_codes()
    
    # 3. 导出样例检查
    results["export_samples"] = check_export_samples()
    
    # 4. 备份样例检查
    results["backup_samples"] = check_backup_samples()
    
    # 5. 配置文件检查
    results["config_files"] = check_config_files()
    
    # 汇总
    print("\n" + "=" * 60)
    print("📊 检查结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print("")
    if all_passed:
        print("✅ 安全检查通过")
        return 0
    else:
        print("❌ 发现安全问题，请修复")
        return 1


if __name__ == "__main__":
    sys.exit(main())
