#!/usr/bin/env python3
"""
缓存感知调度 (Cache-Aware Scheduling, CAS) 模块 (v1.0)
Linux 内核 2025年12月引入的 CAS 补丁实现

核心原理：
让调度器感知 L3 缓存布局，优化任务分配，减少缓存失效

性能提升：
- 特定场景下最高提升 44%
- PostgreSQL、AI 推理等内存敏感型任务受益明显

参考：
- Linux kernel patch: sched: Implement cache-aware scheduling
- LWN: https://lwn.net/Articles/...
"""

import os
import subprocess
import platform
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import re


class CacheTopology:
    """
    CPU 缓存拓扑检测
    """
    
    def __init__(self):
        """初始化缓存拓扑检测"""
        self.topology = self._detect_cache_topology()
        
    def _detect_cache_topology(self) -> Dict[str, Any]:
        """
        检测 CPU 缓存拓扑
        
        Returns:
            Dict: 缓存拓扑信息
        """
        topology = {
            'l1_data': {'size_kb': 0, 'per_cpu': True},
            'l1_instruction': {'size_kb': 0, 'per_cpu': True},
            'l2': {'size_kb': 0, 'per_cpu': False, 'shared_cpus': {}},
            'l3': {'size_kb': 0, 'per_cpu': False, 'shared_cpus': {}},
            'numa_nodes': 1,
            'cache_domains': [],
            'cas_supported': False,
            'cas_enabled': False
        }
        
        if platform.system() != 'Linux':
            return topology
        
        # 检测 L1/L2/L3 缓存
        cpu_cache_path = '/sys/devices/system/cpu/cpu0/cache'
        if os.path.exists(cpu_cache_path):
            for cache_level in ['index0', 'index1', 'index2', 'index3']:
                cache_path = f'{cpu_cache_path}/{cache_level}'
                if not os.path.exists(cache_path):
                    continue
                
                try:
                    # 读取缓存级别
                    with open(f'{cache_path}/level', 'r') as f:
                        level = int(f.read().strip())
                    
                    # 读取缓存大小
                    with open(f'{cache_path}/size', 'r') as f:
                        size_str = f.read().strip()
                        size_kb = self._parse_cache_size(size_str)
                    
                    # 读取缓存类型
                    with open(f'{cache_path}/type', 'r') as f:
                        cache_type = f.read().strip()
                    
                    # 读取共享 CPU
                    with open(f'{cache_path}/shared_cpu_list', 'r') as f:
                        shared_cpus = f.read().strip()
                    
                    # 更新拓扑
                    if level == 1:
                        if cache_type == 'Data':
                            topology['l1_data']['size_kb'] = size_kb
                        elif cache_type == 'Instruction':
                            topology['l1_instruction']['size_kb'] = size_kb
                    elif level == 2:
                        topology['l2']['size_kb'] = size_kb
                        topology['l2']['shared_cpus']['0'] = shared_cpus
                    elif level == 3:
                        topology['l3']['size_kb'] = size_kb
                        topology['l3']['shared_cpus']['0'] = shared_cpus
                        
                except Exception as e:
                    pass
        
        # 检测所有 CPU 的缓存共享情况
        cpu_path = '/sys/devices/system/cpu'
        if os.path.exists(cpu_path):
            for cpu_dir in os.listdir(cpu_path):
                if not cpu_dir.startswith('cpu') or not cpu_dir[3:].isdigit():
                    continue
                
                cpu_id = cpu_dir[3:]
                cache_path = f'{cpu_path}/{cpu_dir}/cache'
                
                if not os.path.exists(cache_path):
                    continue
                
                for cache_level in ['index2', 'index3']:  # L2, L3
                    level_path = f'{cache_path}/{cache_level}'
                    if not os.path.exists(level_path):
                        continue
                    
                    try:
                        with open(f'{level_path}/shared_cpu_list', 'r') as f:
                            shared_cpus = f.read().strip()
                        
                        if cache_level == 'index2':
                            topology['l2']['shared_cpus'][cpu_id] = shared_cpus
                        else:
                            topology['l3']['shared_cpus'][cpu_id] = shared_cpus
                    except:
                        pass
        
        # 检测缓存域（L3 共享的 CPU 组）
        topology['cache_domains'] = self._detect_cache_domains(topology)
        
        # 检测 CAS 支持
        topology['cas_supported'] = self._check_cas_support()
        topology['cas_enabled'] = self._check_cas_enabled()
        
        return topology
    
    def _parse_cache_size(self, size_str: str) -> int:
        """
        解析缓存大小字符串
        
        Args:
            size_str: 大小字符串，如 "32K", "1M", "2G"
        
        Returns:
            int: 大小（KB）
        """
        match = re.match(r'(\d+)(K|M|G)?', size_str.upper())
        if not match:
            return 0
        
        value = int(match.group(1))
        unit = match.group(2) or 'K'
        
        if unit == 'K':
            return value
        elif unit == 'M':
            return value * 1024
        elif unit == 'G':
            return value * 1024 * 1024
        return value
    
    def _detect_cache_domains(self, topology: Dict) -> List[List[int]]:
        """
        检测缓存域
        
        Args:
            topology: 缓存拓扑信息
        
        Returns:
            List[List[int]]: 缓存域列表，每个域是共享 L3 的 CPU 列表
        """
        domains = []
        seen_cpus = set()
        
        for cpu_id, shared_cpus in topology['l3']['shared_cpus'].items():
            if cpu_id in seen_cpus:
                continue
            
            # 解析共享 CPU 列表
            cpus = self._parse_cpu_list(shared_cpus)
            domains.append(cpus)
            seen_cpus.update(cpus)
        
        return domains
    
    def _parse_cpu_list(self, cpu_list: str) -> List[int]:
        """
        解析 CPU 列表字符串
        
        Args:
            cpu_list: CPU 列表，如 "0-7" 或 "0,2,4,6"
        
        Returns:
            List[int]: CPU ID 列表
        """
        cpus = []
        for part in cpu_list.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                cpus.extend(range(start, end + 1))
            else:
                try:
                    cpus.append(int(part))
                except ValueError:
                    pass
        return cpus
    
    def _check_cas_support(self) -> bool:
        """
        检查内核是否支持 CAS
        
        Returns:
            bool: 是否支持
        """
        # 检查内核版本（CAS 在 5.19+ 支持）
        try:
            result = subprocess.run(
                ['uname', '-r'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = result.stdout.strip()
                parts = version.split('.')
                if len(parts) >= 2:
                    major = int(parts[0])
                    minor = int(parts[1].split('.')[0])
                    return (major > 5) or (major == 5 and minor >= 19)
        except:
            pass
        
        # 检查内核配置
        config_paths = [
            '/boot/config-' + os.uname().release,
            '/proc/config.gz'
        ]
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    if config_path.endswith('.gz'):
                        result = subprocess.run(
                            ['zgrep', 'CONFIG_SCHED_CACHE_AWARE', config_path],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                    else:
                        result = subprocess.run(
                            ['grep', 'CONFIG_SCHED_CACHE_AWARE', config_path],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                    
                    if 'CONFIG_SCHED_CACHE_AWARE=y' in result.stdout:
                        return True
                except:
                    pass
        
        return False
    
    def _check_cas_enabled(self) -> bool:
        """
        检查 CAS 是否已启用
        
        Returns:
            bool: 是否启用
        """
        # 检查内核参数
        try:
            with open('/proc/cmdline', 'r') as f:
                cmdline = f.read()
                if 'sched_cache_aware=1' in cmdline:
                    return True
        except:
            pass
        
        # 检查 sysctl 参数
        try:
            result = subprocess.run(
                ['sysctl', '-n', 'kernel.sched_cache_aware'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip() == '1':
                return True
        except:
            pass
        
        return False
    
    def get_info(self) -> Dict[str, Any]:
        """
        获取缓存拓扑信息
        
        Returns:
            Dict: 缓存拓扑信息
        """
        return self.topology
    
    def print_topology(self):
        """打印缓存拓扑信息"""
        print("=== CPU 缓存拓扑 ===")
        print(f"L1 数据缓存: {self.topology['l1_data']['size_kb']} KB")
        print(f"L1 指令缓存: {self.topology['l1_instruction']['size_kb']} KB")
        print(f"L2 缓存: {self.topology['l2']['size_kb']} KB")
        print(f"L3 缓存: {self.topology['l3']['size_kb']} KB")
        
        print(f"\n缓存域（L3 共享组）:")
        for i, domain in enumerate(self.topology['cache_domains']):
            print(f"  域 {i}: CPU {domain}")
        
        print(f"\nCAS 支持: {'✅' if self.topology['cas_supported'] else '❌'}")
        print(f"CAS 启用: {'✅' if self.topology['cas_enabled'] else '❌'}")
        print("===================")


class CacheAwareScheduler:
    """
    缓存感知调度器
    优化任务分配以减少缓存失效
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化缓存感知调度器
        
        Args:
            config: 配置选项
        """
        self.config = config or {}
        self.cache_topology = CacheTopology()
        
        # 配置选项
        self.auto_optimize = self.config.get('auto_optimize', False)
        self.prefer_cache_locality = self.config.get('prefer_cache_locality', True)
        
        # 打印拓扑信息
        if self.config.get('verbose', True):
            self.cache_topology.print_topology()
    
    def get_optimal_cpu_for_task(self, task_type: str = 'compute') -> int:
        """
        获取执行特定任务的最优 CPU
        
        Args:
            task_type: 任务类型（compute, memory, io）
        
        Returns:
            int: 最优 CPU ID
        """
        domains = self.cache_topology.topology['cache_domains']
        
        if not domains:
            return 0
        
        # 对于计算密集型任务，选择缓存域的第一个 CPU
        if task_type == 'compute':
            return domains[0][0] if domains[0] else 0
        
        # 对于内存密集型任务，选择缓存域中间的 CPU
        elif task_type == 'memory':
            domain = domains[0] if domains[0] else [0]
            return domain[len(domain) // 2]
        
        # 对于 IO 密集型任务，选择最后一个缓存域的 CPU
        elif task_type == 'io':
            return domains[-1][-1] if domains[-1] else 0
        
        return 0
    
    def get_cache_affinity_mask(self, cpu_id: int) -> List[int]:
        """
        获取指定 CPU 的缓存亲和性掩码
        
        Args:
            cpu_id: CPU ID
        
        Returns:
            List[int]: 同一缓存域的 CPU 列表
        """
        for domain in self.cache_topology.topology['cache_domains']:
            if cpu_id in domain:
                return domain
        return [cpu_id]
    
    def optimize_for_vector_search(self) -> Dict[str, Any]:
        """
        优化向量搜索的缓存配置
        
        Returns:
            Dict: 优化配置
        """
        config = {
            'cas_supported': self.cache_topology.topology['cas_supported'],
            'cas_enabled': self.cache_topology.topology['cas_enabled'],
            'cache_domains': self.cache_topology.topology['cache_domains'],
            'recommendations': [],
            'optimal_cpus': {},
            'binding_commands': []
        }
        
        # 推荐最优 CPU
        config['optimal_cpus'] = {
            'compute': self.get_optimal_cpu_for_task('compute'),
            'memory': self.get_optimal_cpu_for_task('memory'),
            'io': self.get_optimal_cpu_for_task('io')
        }
        
        # 生成绑定命令
        for task_type, cpu_id in config['optimal_cpus'].items():
            affinity = self.get_cache_affinity_mask(cpu_id)
            affinity_str = ','.join(map(str, affinity))
            config['binding_commands'].append({
                'task_type': task_type,
                'cpu': cpu_id,
                'affinity': affinity,
                'command': f"taskset -c {affinity_str} python3 scripts/search.py"
            })
        
        # 检查 CAS 状态
        if not config['cas_supported']:
            config['recommendations'].append(
                "当前内核不支持 CAS，建议升级到 Linux 5.19+"
            )
        elif not config['cas_enabled']:
            config['recommendations'].append(
                "CAS 未启用，建议添加内核参数: sched_cache_aware=1"
            )
        
        # 检查缓存域数量
        if len(config['cache_domains']) > 1:
            config['recommendations'].append(
                f"检测到 {len(config['cache_domains'])} 个缓存域，建议绑定任务到单一缓存域"
            )
        
        return config
    
    def enable_cas(self) -> bool:
        """
        启用缓存感知调度
        
        Returns:
            bool: 是否成功
        """
        if not self.cache_topology.topology['cas_supported']:
            print("❌ 当前内核不支持 CAS")
            return False
        
        try:
            # 尝试通过 sysctl 启用
            result = subprocess.run(
                ['sysctl', '-w', 'kernel.sched_cache_aware=1'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print("✅ CAS 已启用")
                return True
            else:
                print(f"⚠️ 启用失败: {result.stderr}")
                print("   请尝试添加内核参数: sched_cache_aware=1")
                return False
        except Exception as e:
            print(f"❌ 启用异常: {e}")
            return False
    
    def generate_kernel_params(self) -> List[str]:
        """
        生成内核参数建议
        
        Returns:
            List[str]: 内核参数列表
        """
        params = []
        
        if self.cache_topology.topology['cas_supported']:
            params.append("sched_cache_aware=1")
        
        # 根据缓存域生成 isolcpus 建议
        domains = self.cache_topology.topology['cache_domains']
        if len(domains) > 1:
            # 保留最后一个缓存域用于系统任务
            isolated = []
            for domain in domains[:-1]:
                isolated.extend(domain)
            
            if isolated:
                params.append(f"isolcpus={','.join(map(str, isolated))}")
        
        return params
    
    def get_grub_config(self) -> str:
        """
        生成 GRUB 配置建议
        
        Returns:
            str: GRUB 配置
        """
        params = self.generate_kernel_params()
        
        if not params:
            return "# 无需额外配置"
        
        config = f"""# 在 /etc/default/grub 的 GRUB_CMDLINE_LINUX 中添加:
GRUB_CMDLINE_LINUX="... {' '.join(params)}"

# 然后运行:
sudo update-grub
sudo reboot
"""
        return config


def get_cache_aware_scheduler(config: Optional[Dict] = None) -> CacheAwareScheduler:
    """
    获取缓存感知调度器实例
    
    Args:
        config: 配置选项
    
    Returns:
        CacheAwareScheduler: 调度器实例
    """
    return CacheAwareScheduler(config)


def check_cas_status() -> Dict[str, Any]:
    """
    检查 CAS 状态
    
    Returns:
        Dict: CAS 状态信息
    """
    topology = CacheTopology()
    scheduler = CacheAwareScheduler({'verbose': False})
    
    return {
        'topology': topology.get_info(),
        'optimization': scheduler.optimize_for_vector_search(),
        'kernel_params': scheduler.generate_kernel_params(),
        'grub_config': scheduler.get_grub_config()
    }


if __name__ == "__main__":
    # 测试
    print("=== 缓存感知调度器测试 ===\n")
    
    # 创建调度器
    scheduler = CacheAwareScheduler({'verbose': True})
    
    # 获取优化配置
    print("\n=== 向量搜索优化 ===")
    config = scheduler.optimize_for_vector_search()
    print(f"CAS 支持: {'✅' if config['cas_supported'] else '❌'}")
    print(f"CAS 启用: {'✅' if config['cas_enabled'] else '❌'}")
    print(f"缓存域: {config['cache_domains']}")
    print(f"最优 CPU: {config['optimal_cpus']}")
    
    if config['recommendations']:
        print("\n建议:")
        for rec in config['recommendations']:
            print(f"  - {rec}")
    
    # 生成内核参数
    print("\n=== 内核参数建议 ===")
    print(scheduler.get_grub_config())
