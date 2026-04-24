#!/usr/bin/env python
"""
演示环境初始化脚本
一键初始化数据库、检查授权、预热演示数据
"""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(cmd: list, description: str) -> tuple:
    """运行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"📌 {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )
    
    print(result.stdout)
    
    if result.stderr:
        print(f"[STDERR] {result.stderr}")
    
    return result.returncode, result.stdout


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 演示环境初始化")
    print("=" * 60)
    print(f"时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"工作目录: {project_root}")
    
    # 1. 初始化数据库并预热演示数据
    print("\n" + "=" * 60)
    print("步骤 1/4: 初始化数据库并预热演示数据")
    print("=" * 60)
    
    run_command(
        ["python", "scripts/seed_platform_invocations.py", "--preset", "demo_standard", "--reset-before-seed"],
        "预热标准演示数据集"
    )
    
    # 2. 检查 NOTIFICATION 授权状态
    print("\n" + "=" * 60)
    print("步骤 2/4: 检查 NOTIFICATION 授权状态")
    print("=" * 60)
    
    returncode, output = run_command(
        ["python", "scripts/check_notification_auth.py"],
        "检查授权状态"
    )
    
    auth_status = "unknown"
    if "configured" in output and "not_configured" not in output:
        auth_status = "configured"
    elif "not_configured" in output:
        auth_status = "not_configured"
    elif "invalid" in output:
        auth_status = "invalid"
    
    # 3. 显示统计信息
    print("\n" + "=" * 60)
    print("步骤 3/4: 显示统计信息")
    print("=" * 60)
    
    run_command(
        ["python", "scripts/invocation_audit_cli.py", "stats"],
        "审计统计"
    )
    
    # 4. 运行健康巡检
    print("\n" + "=" * 60)
    print("步骤 4/4: 运行健康巡检")
    print("=" * 60)
    
    run_command(
        ["python", "scripts/platform_health_check.py"],
        "健康巡检"
    )
    
    # 输出下一步命令
    print("\n" + "=" * 60)
    print("✅ 演示环境初始化完成!")
    print("=" * 60)
    print("\n📋 下一步可执行命令:")
    print("")
    print("  # 查看统计")
    print("  python scripts/invocation_audit_cli.py stats")
    print("")
    print("  # 查看健康状态")
    print("  python scripts/platform_health_check.py")
    print("")
    print("  # 导出日报")
    print("  python scripts/export_daily_platform_report.py --format json")
    print("")
    print("  # 导出周报")
    print("  python scripts/export_weekly_platform_report.py --format json")
    print("")
    print("  # 一键运行所有演示")
    print("  bash scripts/demo_run_all.sh")
    print("")
    print(f"🔐 NOTIFICATION 授权状态: {auth_status}")
    if auth_status != "configured":
        print("   💡 提示: 配置 authCode 后可解锁 NOTIFICATION 能力")
    print("")


if __name__ == "__main__":
    main()
