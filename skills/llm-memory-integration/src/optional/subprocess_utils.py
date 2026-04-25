"""
可选模块 - subprocess 工具
中风险功能：执行系统命令读取硬件信息

⚠️ 安全警告：
- 此模块包含中风险功能
- 仅用于读取系统信息，不修改系统
- 默认禁用

使用方法：
1. 在 config/optional_features.json 中启用
2. 或通过环境变量 ENABLE_SUBPROCESS=true
"""

import os
import subprocess
from typing import Dict, Any, Optional

# 默认禁用
ENABLED = os.environ.get('ENABLE_SUBPROCESS', 'false').lower() == 'true'

def is_enabled() -> bool:
    """检查是否启用"""
    return ENABLED

def run_command(cmd: list, timeout: int = 5) -> Optional[str]:
    """
    执行系统命令（只读操作）
    
    ⚠️ 中风险操作：需要用户明确启用
    
    Args:
        cmd: 命令列表（不使用 shell=True）
        timeout: 超时时间（秒）
    
    Returns:
        Optional[str]: 命令输出
    """
    if not is_enabled():
        print("⚠️ subprocess 调用未启用")
        print("   设置环境变量 ENABLE_SUBPROCESS=true 以启用")
        return None
    
    # 安全检查：只允许只读命令
    safe_commands = ['lscpu', 'lsblk', 'lsmem', 'numactl', 'cat', 'which']
    if cmd[0] not in safe_commands:
        print(f"❌ 不允许执行命令: {cmd[0]}")
        return None
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            return result.stdout
        else:
            return None
    except subprocess.TimeoutExpired:
        print(f"⚠️ 命令超时: {cmd}")
        return None
    except FileNotFoundError:
        print(f"⚠️ 命令不存在: {cmd[0]}")
        return None
    except Exception as e:
        print(f"❌ 执行命令失败: {e}")
        return None

def get_cpu_info() -> Dict[str, Any]:
    """获取 CPU 信息"""
    if not is_enabled():
        return {}
    
    output = run_command(['lscpu'])
    if output:
        # 解析 lscpu 输出
        info = {}
        for line in output.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()
        return info
    return {}

def get_memory_info() -> Dict[str, Any]:
    """获取内存信息"""
    if not is_enabled():
        return {}
    
    output = run_command(['lsmem'])
    if output:
        # 解析 lsmem 输出
        info = {}
        for line in output.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()
        return info
    return {}

__all__ = ['is_enabled', 'run_command', 'get_cpu_info', 'get_memory_info']
