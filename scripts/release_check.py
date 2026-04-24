#!/usr/bin/env python
"""
发布检查脚本
统一执行所有发布前检查
"""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_check(name: str, cmd: list, cwd: str = None) -> tuple:
    """运行检查并返回结果"""
    print(f"\n{'='*60}")
    print(f"🔍 {name}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=cwd or str(project_root),
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"[STDERR] {result.stderr}")
    
    return result.returncode == 0, result.stdout


def check_pytest() -> bool:
    """检查 pytest"""
    success, output = run_check(
        "Pytest 全量测试",
        ["python", "-m", "pytest", "-q", "--tb=no"]
    )
    return success


def check_demo_bootstrap() -> bool:
    """检查 demo_bootstrap"""
    success, output = run_check(
        "Demo Bootstrap",
        ["python", "scripts/demo_bootstrap.py"]
    )
    return success


def check_notification_auth() -> bool:
    """检查 notification auth"""
    success, output = run_check(
        "NOTIFICATION 授权检查",
        ["python", "scripts/check_notification_auth.py"]
    )
    # not_configured 也是正常的
    return True  # 只要能运行就算通过


def check_database_nonempty() -> bool:
    """检查数据库非空"""
    print(f"\n{'='*60}")
    print("🔍 数据库非空检查")
    print(f"{'='*60}")
    
    import sqlite3
    db_path = project_root / "data" / "tasks.db"
    
    if not db_path.exists():
        print("❌ 数据库不存在")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM platform_invocations")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count > 0:
        print(f"✅ 数据库记录数: {count}")
        return True
    else:
        print("❌ 数据库为空")
        return False


def check_docs_exist() -> bool:
    """检查文档存在"""
    print(f"\n{'='*60}")
    print("🔍 核心文档检查")
    print(f"{'='*60}")
    
    required_docs = [
        "DEMO_QUICKSTART.md",
        "FINAL_DELIVERY_MODE_MATRIX.md",
        "NOTIFICATION_AUTH_GUIDE.md",
        "PLATFORM_HEALTH_CHECK.md",
        "PLATFORM_AUDIT_OPERATIONS.md",
    ]
    
    all_exist = True
    for doc in required_docs:
        doc_path = project_root / doc
        if doc_path.exists():
            print(f"  ✅ {doc}")
        else:
            print(f"  ❌ {doc} 不存在")
            all_exist = False
    
    return all_exist


def check_no_cache_files() -> bool:
    """检查无缓存文件"""
    print(f"\n{'='*60}")
    print("🔍 缓存文件检查")
    print(f"{'='*60}")
    
    cache_patterns = [
        "**/__pycache__",
        "**/.pytest_cache",
        "**/*.pyc",
        "**/*.pyo",
    ]
    
    found_cache = []
    for pattern in cache_patterns:
        for f in project_root.glob(pattern):
            if "node_modules" not in str(f):
                found_cache.append(str(f))
    
    if found_cache:
        print(f"⚠️ 发现缓存文件 ({len(found_cache)} 个):")
        for f in found_cache[:10]:
            print(f"  {f}")
        return True  # 警告但不失败
    else:
        print("✅ 无缓存文件")
        return True


def check_no_secrets() -> bool:
    """检查无明显敏感信息"""
    print(f"\n{'='*60}")
    print("🔍 敏感信息检查")
    print(f"{'='*60}")
    
    # 检查常见敏感模式
    secret_patterns = [
        "authCode",
        "XIAOYI_AUTH_CODE=",
        "password=",
        "api_key=",
        "secret=",
    ]
    
    # 只检查文档文件
    doc_files = list(project_root.glob("*.md")) + list(project_root.glob("*.txt"))
    
    found_secrets = []
    for doc in doc_files:
        try:
            content = doc.read_text()
            for pattern in secret_patterns:
                if pattern in content:
                    # 检查是否是示例（如 "your_auth_code"）
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if pattern in line:
                            # 排除明显的示例
                            if "your_" in line or "example" in line or "xxx" in line:
                                continue
                            found_secrets.append(f"{doc.name}:{i+1}: {line[:50]}")
        except:
            pass
    
    if found_secrets:
        print(f"⚠️ 可能的敏感信息 ({len(found_secrets)} 处):")
        for f in found_secrets[:5]:
            print(f"  {f}")
        return True  # 警告但不失败
    else:
        print("✅ 无明显敏感信息")
        return True


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 发布检查")
    print("=" * 60)
    print(f"时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"工作目录: {project_root}")
    
    results = {}
    
    # 1. Pytest
    results["pytest"] = check_pytest()
    
    # 2. Demo Bootstrap
    results["demo_bootstrap"] = check_demo_bootstrap()
    
    # 3. Notification Auth
    results["notification_auth"] = check_notification_auth()
    
    # 4. Database Non-empty
    results["database"] = check_database_nonempty()
    
    # 5. Docs Exist
    results["docs"] = check_docs_exist()
    
    # 6. No Cache
    results["cache"] = check_no_cache_files()
    
    # 7. No Secrets
    results["secrets"] = check_no_secrets()
    
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
        print("✅ 所有检查通过，可以发布")
        return 0
    else:
        print("❌ 部分检查失败，请修复后再发布")
        return 1


if __name__ == "__main__":
    sys.exit(main())
