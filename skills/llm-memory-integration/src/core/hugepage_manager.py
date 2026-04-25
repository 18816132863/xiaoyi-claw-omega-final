#!/usr/bin/env python3
"""
大页内存管理模块 (v5.2.29)
自动检测大页内存可用性，自动配置或提示用户

⚠️ 安全警告：
本模块包含系统级操作，需要用户明确确认才能执行。
所有操作默认禁用，需要手动启用。
"""

import os
import re
from typing import Dict, Any, Optional
import numpy as np

# 安全确认
try:
    from .security_confirmation import SecurityConfirmation, check_system_modification_allowed
    HAS_SECURITY = True
except ImportError:
    HAS_SECURITY = False


def _check_permission(operation_type: str) -> bool:
    """检查操作权限"""
    if HAS_SECURITY:
        return check_system_modification_allowed(operation_type)
    print(f"⚠️ 操作 '{operation_type}' 需要用户确认")
    return False


class HugePageManager:
    """
    大页内存管理器
    """
    
    def __init__(self):
        """初始化大页内存管理器"""
        self.info = self._detect_hugepages()
        self.enabled = False
        
        print(f"大页内存管理器初始化:")
        print(f"  支持大页: {'✅' if self.info['supported'] else '❌'}")
        print(f"  大页大小: {self.info['page_size_kb']} KB")
        print(f"  已配置: {self.info['total_pages']} 页")
        print(f"  已使用: {self.info['free_pages']} 页可用")
    
    def _detect_hugepages(self) -> Dict[str, Any]:
        """
        检测大页内存配置
        
        Returns:
            Dict: 大页内存信息
        """
        info = {
            'supported': False,
            'page_size_kb': 0,
            'total_pages': 0,
            'free_pages': 0,
            'reserved_pages': 0,
            'can_configure': False
        }
        
        if os.path.exists('/proc/meminfo'):
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                
                # 检测大页大小
                match = re.search(r'Hugepagesize:\s+(\d+)\s+kB', meminfo)
                if match:
                    info['page_size_kb'] = int(match.group(1))
                    info['supported'] = True
                
                # 检测大页数量
                match = re.search(r'HugePages_Total:\s+(\d+)', meminfo)
                if match:
                    info['total_pages'] = int(match.group(1))
                
                # 检测可用大页
                match = re.search(r'HugePages_Free:\s+(\d+)', meminfo)
                if match:
                    info['free_pages'] = int(match.group(1))
                
                # 检测保留大页
                match = re.search(r'HugePages_Rsvd:\s+(\d+)', meminfo)
                if match:
                    info['reserved_pages'] = int(match.group(1))
        
        # 检测是否可以配置（需要 root 权限）
        info['can_configure'] = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
        
        return info
    
    def is_available(self) -> bool:
        """
        检查大页内存是否可用
        
        Returns:
            bool: 是否可用
        """
        return self.info['supported'] and self.info['total_pages'] > 0
    
    def configure(self, n_pages: int = 1024) -> bool:
        """
        配置大页内存
        
        ⚠️ 需要用户确认才能执行
        
        Args:
            n_pages: 大页数量
        
        Returns:
            bool: 是否成功
        """
        if not self.info['supported']:
            print("❌ 系统不支持大页内存")
            return False
        
        if not self.info['can_configure']:
            print("⚠️ 需要 root 权限配置大页内存")
            print(f"   请运行: sudo sysctl -w vm.nr_hugepages={n_pages}")
            return False
        
        # 安全检查
        if not _check_permission('hugepage'):
            print("⚠️ 大页内存配置需要用户确认")
            print("   请在配置中启用: allow_hugepage = True")
            print(f"   或手动执行: sudo sysctl -w vm.nr_hugepages={n_pages}")
            return False
        
        # 配置大页内存
        try:
            import subprocess
            result = subprocess.run(
                ['sysctl', '-w', f'vm.nr_hugepages={n_pages}'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ 大页内存已配置: {n_pages} 页")
                self.enabled = True
                return True
            else:
                print(f"❌ 配置失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 配置异常: {e}")
            return False
    
    def allocate(self, size_mb: int) -> Optional[np.ndarray]:
        """
        使用大页内存分配数组
        
        Args:
            size_mb: 分配大小（MB）
        
        Returns:
            Optional[np.ndarray]: 分配的数组
        """
        if not self.is_available():
            print("❌ 大页内存不可用")
            return None
        
        # 计算需要的页数
        page_size_mb = self.info['page_size_kb'] / 1024
        n_pages_needed = int(np.ceil(size_mb / page_size_mb))
        
        if n_pages_needed > self.info['free_pages']:
            print(f"❌ 大页内存不足: 需要 {n_pages_needed} 页，可用 {self.info['free_pages']} 页")
            return None
        
        # 分配内存
        try:
            # 使用 mmap 分配大页内存
            import mmap
            
            size_bytes = size_mb * 1024 * 1024
            
            # 尝试使用 MAP_HUGETLB（需要 root）
            try:
                mem = mmap.mmap(
                    -1,
                    size_bytes,
                    flags=mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS | 0x40000  # MAP_HUGETLB
                )
                print(f"✅ 大页内存已分配: {size_mb} MB")
                
                # 转换为 numpy 数组
                arr = np.frombuffer(mem, dtype=np.float32)
                return arr
            except:
                # 回退到普通内存
                print("⚠️ 无法使用大页内存，回退到普通内存")
                return np.zeros(size_bytes // 4, dtype=np.float32)
        except Exception as e:
            print(f"❌ 分配失败: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            **self.info,
            'total_memory_mb': self.info['total_pages'] * self.info['page_size_kb'] / 1024,
            'free_memory_mb': self.info['free_pages'] * self.info['page_size_kb'] / 1024,
            'enabled': self.enabled
        }
    
    def print_recommendations(self):
        """打印配置建议"""
        if not self.info['supported']:
            print("❌ 系统不支持大页内存")
            return
        
        if self.info['total_pages'] == 0:
            print("\n📋 大页内存配置建议:")
            print("  1. 检查系统支持:")
            print("     grep -i huge /proc/meminfo")
            print("\n  2. 配置大页内存（需要 root）:")
            print("     sudo sysctl -w vm.nr_hugepages=1024")
            print("\n  3. 永久配置:")
            print("     echo 'vm.nr_hugepages=1024' | sudo tee -a /etc/sysctl.conf")
            print("     sudo sysctl -p")
        else:
            print(f"\n✅ 大页内存已配置:")
            print(f"   总计: {self.info['total_pages']} 页 ({self.info['total_pages'] * self.info['page_size_kb'] / 1024:.0f} MB)")
            print(f"   可用: {self.info['free_pages']} 页 ({self.info['free_pages'] * self.info['page_size_kb'] / 1024:.0f} MB)")


if __name__ == "__main__":
    # 测试
    print("=== 大页内存管理器测试 ===")
    
    manager = HugePageManager()
    
    # 打印统计
    stats = manager.get_stats()
    print(f"\n统计信息:")
    print(f"  支持大页: {stats['supported']}")
    print(f"  大页大小: {stats['page_size_kb']} KB")
    print(f"  总计: {stats['total_memory_mb']:.0f} MB")
    print(f"  可用: {stats['free_memory_mb']:.0f} MB")
    
    # 打印建议
    manager.print_recommendations()
