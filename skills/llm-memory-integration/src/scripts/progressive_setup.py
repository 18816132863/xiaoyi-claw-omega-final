#!/usr/bin/env python3
"""渐进式启用脚本"""
import json
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"
CONFIG_FILE = CONFIG_DIR / "progressive_config.json"

def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}

def save_config(config):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2))

def enable_stage(stage: str):
    """启用指定阶段"""
    config = load_config()
    if stage in config.get("stages", {}):
        config["stages"][stage]["enabled"] = True
        save_config(config)
        print(f"✅ 已启用 {stage}: {config['stages'][stage]['name']}")
        return True
    print(f"❌ 未找到阶段: {stage}")
    return False

def disable_stage(stage: str):
    """禁用指定阶段"""
    config = load_config()
    if stage in config.get("stages", {}):
        config["stages"][stage]["enabled"] = False
        save_config(config)
        print(f"✅ 已禁用 {stage}: {config['stages'][stage]['name']}")
        return True
    print(f"❌ 未找到阶段: {stage}")
    return False

def show_status():
    """显示当前状态"""
    config = load_config()
    print("=" * 50)
    print("渐进式启用状态")
    print("=" * 50)
    
    for stage_id, stage in config.get("stages", {}).items():
        status = "✅ 启用" if stage.get("enabled") else "❌ 禁用"
        print(f"\n{stage_id}: {stage['name']}")
        print(f"  状态: {status}")
        print(f"  模块: {', '.join(stage['modules'])}")
        print(f"  说明: {stage['description']}")
    
    print("\n" + "=" * 50)
    print("优化配置")
    print("=" * 50)
    
    for opt_name, opt in config.get("optimizations", {}).items():
        print(f"\n{opt_name}:")
        print(f"  {opt.get('description', '')}")
        for k, v in opt.items():
            if k != "description":
                print(f"  {k}: {v}")

def enable_all():
    """启用所有阶段"""
    config = load_config()
    for stage_id in config.get("stages", {}):
        config["stages"][stage_id]["enabled"] = True
    save_config(config)
    print("✅ 已启用所有阶段")

def main():
    import sys
    
    if len(sys.argv) < 2:
        show_status()
        return
    
    cmd = sys.argv[1]
    
    # 输入验证
    if len(cmd) > 50:
        print("❌ 错误: 命令过长")
        return
    
    if not cmd.isalnum():
        print(f"❌ 错误: 无效的命令格式: {cmd}")
        return
    
    if cmd == "enable":
        if len(sys.argv) > 2:
            stage = sys.argv[2]
            # 输入验证
            if len(stage) > 10 or not stage.startswith('P'):
                print("❌ 错误: 无效的阶段名称")
                return
            enable_stage(stage)
        else:
            enable_all()
    elif cmd == "disable":
        if len(sys.argv) > 2:
            stage = sys.argv[2]
            # 输入验证
            if len(stage) > 10 or not stage.startswith('P'):
                print("❌ 错误: 无效的阶段名称")
                return
            disable_stage(stage)
    elif cmd == "status":
        show_status()
    else:
        print(f"未知命令: {cmd}")
        print("用法: progressive_setup.py [enable|disable|status] [stage]")

if __name__ == "__main__":
    main()
