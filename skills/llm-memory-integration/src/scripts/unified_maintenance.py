#!/usr/bin/env python3
"""统一维护入口 - 一键执行所有维护任务"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

SCRIPTS_DIR = Path(__file__).parent

def run_script(script_name: str, args: str = "") -> tuple:
    """运行脚本"""
    script_path = SCRIPTS_DIR / script_name
    cmd = ["python3", str(script_path)] + args.split() if args else ["python3", str(script_path)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("=" * 60)
    print(f"向量系统统一维护 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tasks = [
        ("1. 向量覆盖率检查", "vector_coverage_monitor.py", "check"),
        ("2. 智能记忆升级", "smart_memory_upgrade.py", "run"),
        ("3. 用户画像更新", "auto_update_persona.py", "run"),
        ("4. 向量系统优化", "vector_system_optimizer.py", "run"),
    ]
    
    results = []
    
    for name, script, args in tasks:
        print(f"\n{name}...")
        success, stdout, stderr = run_script(script, args)
        
        if success:
            print(f"✅ 完成")
            results.append((name, True, ""))
        else:
            print(f"❌ 失败: {stderr[:100]}")
            results.append((name, False, stderr[:100]))
    
    print("\n" + "=" * 60)
    print("维护结果汇总")
    print("=" * 60)
    
    for name, success, error in results:
        status = "✅ 成功" if success else f"❌ 失败: {error}"
        print(f"{name}: {status}")
    
    success_count = sum(1 for _, s, _ in results if s)
    print(f"\n总计: {success_count}/{len(results)} 成功")

if __name__ == "__main__":
    main()
