#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信智能机器人 OpenClaw 配置脚本
自动配置 openclaw.json 中的 wecom channel
"""

import json
import os
import sys
from pathlib import Path

def get_openclaw_config_path():
    """获取 openclaw.json 配置文件路径"""
    home = Path.home()
    return home / ".openclaw" / "openclaw.json"

def backup_config(config_path):
    """备份配置文件"""
    backup_path = config_path.with_suffix(".json.backup")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ 配置已备份到: {backup_path}")
    return backup_path

def configure_wecom_channel(bot_id, secret):
    """配置企业微信 channel"""
    config_path = get_openclaw_config_path()
    
    if not config_path.exists():
        print(f"✗ 配置文件不存在: {config_path}")
        print("  请先运行 openclaw init 初始化配置")
        return False
    
    # 备份原配置
    backup_config(config_path)
    
    # 读取配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 确保 channels 存在
    if 'channels' not in config:
        config['channels'] = {}
    
    # 添加/更新 wecom 配置
    config['channels']['wecom'] = {
        'enabled': True,
        'botId': bot_id,
        'secret': secret,
        'dmPolicy': 'pairing'
    }
    
    # 写入配置
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 配置已写入: {config_path}")
    return True

def main():
    print("=" * 50)
    print("企业微信智能机器人 OpenClaw 配置工具")
    print("=" * 50)
    print()
    
    # 获取用户输入
    bot_id = input("请输入 Bot ID: ").strip()
    if not bot_id:
        print("✗ Bot ID 不能为空")
        sys.exit(1)
    
    secret = input("请输入安全密钥: ").strip()
    if not secret:
        print("✗ 安全密钥不能为空")
        sys.exit(1)
    
    print()
    print("配置信息:")
    print(f"  Bot ID: {bot_id}")
    print(f"  密钥: {secret[:8]}...{secret[-4:]}")
    print()
    
    confirm = input("确认配置? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        sys.exit(0)
    
    # 执行配置
    if configure_wecom_channel(bot_id, secret):
        print()
        print("=" * 50)
        print("配置完成！后续步骤:")
        print("1. 运行: openclaw gateway restart")
        print("2. 在企业微信中给机器人发消息获取配对码")
        print("3. 运行: openclaw pairing approve wecom <配对码>")
        print("=" * 50)
    else:
        print("✗ 配置失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
