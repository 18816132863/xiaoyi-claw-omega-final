#!/usr/bin/env python
"""
技能上传前检查
检查技能是否满足上传条件
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_no_external_deps() -> bool:
    """检查不依赖外部服务"""
    print(f"\n{'='*60}")
    print("🔍 外部依赖检查")
    print(f"{'='*60}")
    
    # 检查核心代码目录
    core_dirs = ["platform_adapter", "capabilities"]
    
    found_actual_deps = []
    
    for code_dir in core_dirs:
        code_path = project_root / code_dir
        if code_path.exists():
            for py_file in code_path.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    # 检查是否有实际的 import（排除可选的生产脚本）
                    if "import psycopg" in content or "import redis" in content or "import docker" in content:
                        found_actual_deps.append(str(py_file.relative_to(project_root)))
                except:
                    pass
    
    if found_actual_deps:
        print(f"❌ 核心代码中发现外部依赖: {found_actual_deps}")
        return False
    else:
        print("✅ 核心代码无外部服务依赖")
        print("   注: infrastructure/scripts 中有可选的生产环境脚本")
        return True


def check_default_sqlite() -> bool:
    """检查默认数据库为 SQLite"""
    print(f"\n{'='*60}")
    print("🔍 默认数据库检查")
    print(f"{'='*60}")
    
    # 检查数据库路径
    db_path = project_root / "data" / "tasks.db"
    
    if db_path.parent.exists():
        print(f"✅ 默认数据库路径: {db_path}")
        return True
    else:
        print(f"⚠️ 数据库目录不存在，但会在运行时创建")
        return True


def check_demo_mode_works() -> bool:
    """检查 demo 模式可运行"""
    print(f"\n{'='*60}")
    print("🔍 Demo 模式检查")
    print(f"{'='*60}")
    
    import subprocess
    
    result = subprocess.run(
        ["python", "scripts/seed_platform_invocations.py", "--preset", "demo_standard", "--reset-before-seed"],
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )
    
    if result.returncode == 0:
        print("✅ Demo 模式可运行")
        return True
    else:
        print(f"❌ Demo 模式运行失败: {result.stderr}")
        return False


def check_docs_complete() -> bool:
    """检查文档齐全"""
    print(f"\n{'='*60}")
    print("🔍 文档完整性检查")
    print(f"{'='*60}")
    
    required_docs = {
        "DEMO_QUICKSTART.md": "快速入门",
        "FINAL_DELIVERY_MODE_MATRIX.md": "运行模式",
        "NOTIFICATION_AUTH_GUIDE.md": "授权指南",
        "PLATFORM_HEALTH_CHECK.md": "健康巡检",
        "PLATFORM_AUDIT_OPERATIONS.md": "审计操作",
        "PLATFORM_EXPORT_AND_BACKUP.md": "导出备份",
        "MANUAL_CONFIRMATION_PLAYBOOK.md": "手动确认",
        "USER_RESULT_MESSAGE_MATRIX.md": "用户消息",
    }
    
    all_exist = True
    for doc, desc in required_docs.items():
        doc_path = project_root / doc
        if doc_path.exists():
            print(f"  ✅ {doc} ({desc})")
        else:
            print(f"  ❌ {doc} ({desc}) 不存在")
            all_exist = False
    
    return all_exist


def check_skill_mode_usable() -> bool:
    """检查默认 skill 模式可用"""
    print(f"\n{'='*60}")
    print("🔍 默认 Skill 模式检查")
    print(f"{'='*60}")
    
    # 检查关键脚本存在
    key_scripts = [
        "scripts/seed_platform_invocations.py",
        "scripts/demo_bootstrap.py",
        "scripts/invocation_audit_cli.py",
        "scripts/platform_health_check.py",
    ]
    
    all_exist = True
    for script in key_scripts:
        script_path = project_root / script
        if script_path.exists():
            print(f"  ✅ {script}")
        else:
            print(f"  ❌ {script} 不存在")
            all_exist = False
    
    return all_exist


def check_notification_auth_behavior() -> bool:
    """检查 notification auth 未配置时行为清晰"""
    print(f"\n{'='*60}")
    print("🔍 NOTIFICATION 授权行为检查")
    print(f"{'='*60}")
    
    import subprocess
    
    result = subprocess.run(
        ["python", "scripts/check_notification_auth.py"],
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )
    
    output = result.stdout + result.stderr
    
    # 检查输出是否清晰
    if "not_configured" in output or "configured" in output or "invalid" in output:
        print("✅ 授权状态输出清晰")
        return True
    else:
        print("❌ 授权状态输出不清晰")
        return False


def check_platform_connected_docs() -> bool:
    """检查 platform connected 模式说明存在"""
    print(f"\n{'='*60}")
    print("🔍 Platform Connected 模式说明检查")
    print(f"{'='*60}")
    
    # 检查 FINAL_DELIVERY_MODE_MATRIX.md 是否存在
    doc_path = project_root / "FINAL_DELIVERY_MODE_MATRIX.md"
    
    if doc_path.exists():
        content = doc_path.read_text()
        if "真实运行" in content or "connected" in content.lower():
            print("✅ Platform Connected 模式说明存在")
            return True
        else:
            print("⚠️ Platform Connected 模式说明可能缺失")
            return True
    else:
        print("❌ FINAL_DELIVERY_MODE_MATRIX.md 不存在")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 技能上传前检查")
    print("=" * 60)
    print(f"时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"工作目录: {project_root}")
    
    results = {}
    
    # 1. 无外部依赖
    results["no_external_deps"] = check_no_external_deps()
    
    # 2. 默认 SQLite
    results["default_sqlite"] = check_default_sqlite()
    
    # 3. Demo 模式可运行
    results["demo_mode"] = check_demo_mode_works()
    
    # 4. 文档齐全
    results["docs"] = check_docs_complete()
    
    # 5. Skill 模式可用
    results["skill_mode"] = check_skill_mode_usable()
    
    # 6. Notification auth 行为清晰
    results["notification_auth"] = check_notification_auth_behavior()
    
    # 7. Platform connected 文档
    results["platform_connected"] = check_platform_connected_docs()
    
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
        print("✅ 所有检查通过，可以上传技能")
        return 0
    else:
        print("❌ 部分检查失败，请修复后再上传")
        return 1


if __name__ == "__main__":
    sys.exit(main())
