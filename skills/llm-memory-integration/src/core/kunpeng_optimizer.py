#!/usr/bin/env python3
"""
华为鲲鹏/海思 ARM64 优化模块 (v1.0)
针对鲲鹏 920、HiSilicon 处理器的深度优化

支持的优化技术：
1. NEON/SVE 向量加速
2. 毕昇编译器优化建议
3. KML 数学库集成
4. 鲲鹏特定缓存优化
5. NUMA 亲和性（多路服务器）

参考：
- 华为鲲鹏开发者指南
- Kunpeng 920 Processor Optimization Guide
- BiSheng Compiler Documentation
"""

import os
import platform
import subprocess
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import numpy as np


class KunpengDetector:
    """
    华为鲲鹏处理器检测器
    """
    
    def __init__(self):
        """初始化鲲鹏检测器"""
        self.info = self._detect_kunpeng()
        
    def _detect_kunpeng(self) -> Dict[str, Any]:
        """
        检测鲲鹏处理器信息
        
        Returns:
            Dict: 处理器信息
        """
        info = {
            'is_kunpeng': False,
            'is_hisilicon': False,
            'is_arm64': False,
            'cpu_model': 'unknown',
            'cpu_vendor': 'unknown',
            'cores': 0,
            'numa_nodes': 1,
            'simd': {
                'neon': False,
                'sve': False,
                'sve2': False,
                'fp16': False,
                'dotprod': False,
                'i8mm': False  # Int8 Matrix Multiply
            },
            'cache': {
                'l1d': 0,
                'l1i': 0,
                'l2': 0,
                'l3': 0
            },
            'kml_available': False,
            'bisheng_available': False,
            'recommended_implementation': 'scalar'
        }
        
        # 检测架构
        info['is_arm64'] = platform.machine() in ['aarch64', 'arm64']
        
        if platform.system() != 'Linux':
            return info
        
        # 读取 /proc/cpuinfo
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                
                # 检测 CPU 型号
                for line in cpuinfo.split('\n'):
                    if 'model name' in line.lower() or 'cpu model' in line.lower():
                        info['cpu_model'] = line.split(':')[1].strip()
                        break
                    elif 'hardware' in line.lower():
                        hw = line.split(':')[1].strip().lower()
                        if 'kunpeng' in hw or 'hisi' in hw or 'huawei' in hw:
                            info['cpu_model'] = line.split(':')[1].strip()
                            break
                
                # 检测厂商
                cpuinfo_lower = cpuinfo.lower()
                if 'kunpeng' in cpuinfo_lower or 'hisi' in cpuinfo_lower:
                    info['is_kunpeng'] = True
                    info['is_hisilicon'] = True
                    info['cpu_vendor'] = 'Huawei Kunpeng'
                elif 'hisilicon' in cpuinfo_lower:
                    info['is_hisilicon'] = True
                    info['cpu_vendor'] = 'HiSilicon'
                elif 'arm' in cpuinfo_lower:
                    info['cpu_vendor'] = 'ARM'
                
                # 检测核心数
                info['cores'] = cpuinfo.count('processor')
                
                # 检测 SIMD 特性
                info['simd']['neon'] = 'neon' in cpuinfo_lower or 'asimd' in cpuinfo_lower
                info['simd']['sve'] = 'sve' in cpuinfo_lower
                info['simd']['sve2'] = 'sve2' in cpuinfo_lower
                info['simd']['fp16'] = 'fp16' in cpuinfo_lower or 'asimdfhm' in cpuinfo_lower
                info['simd']['dotprod'] = 'asimddp' in cpuinfo_lower
                info['simd']['i8mm'] = 'i8mm' in cpuinfo_lower
                
        except Exception as e:
            pass
        
        # 检测 NUMA 节点
        try:
            result = subprocess.run(
                ['lscpu'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'NUMA node(s):' in line:
                        info['numa_nodes'] = int(line.split(':')[1].strip())
        except Exception:
            pass
        
        # 检测缓存大小
        try:
            cache_path = '/sys/devices/system/cpu/cpu0/cache'
            if os.path.exists(cache_path):
                for idx in ['index0', 'index1', 'index2', 'index3']:
                    idx_path = f'{cache_path}/{idx}'
                    if not os.path.exists(idx_path):
                        continue
                    
                    level_file = f'{idx_path}/level'
                    size_file = f'{idx_path}/size'
                    
                    if os.path.exists(level_file) and os.path.exists(size_file):
                        with open(level_file, 'r') as f:
                            level = int(f.read().strip())
                        
                        with open(size_file, 'r') as f:
                            size_str = f.read().strip()
                            size_kb = self._parse_cache_size(size_str)
                        
                        if level == 1:
                            type_file = f'{idx_path}/type'
                            if os.path.exists(type_file):
                                with open(type_file, 'r') as f:
                                    cache_type = f.read().strip()
                                if cache_type == 'Data':
                                    info['cache']['l1d'] = size_kb
                                elif cache_type == 'Instruction':
                                    info['cache']['l1i'] = size_kb
                        elif level == 2:
                            info['cache']['l2'] = size_kb
                        elif level == 3:
                            info['cache']['l3'] = size_kb
        except Exception:
            pass
        
        # 检测 KML 数学库
        try:
            result = subprocess.run(
                ['ldconfig', '-p'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info['kml_available'] = 'libkml' in result.stdout.lower() or 'libkm' in result.stdout.lower()
        except Exception:
            pass
        
        # 检测毕昇编译器
        try:
            result = subprocess.run(
                ['which', 'clang'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                clang_path = result.stdout.strip()
                # 检查是否是毕昇编译器
                result2 = subprocess.run(
                    [clang_path, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result2.returncode == 0:
                    info['bisheng_available'] = 'bisheng' in result2.stdout.lower() or 'kunpeng' in result2.stdout.lower()
        except Exception:
            pass
        
        # 确定推荐实现
        info['recommended_implementation'] = self._get_recommended_implementation(info)
        
        return info
    
    def _parse_cache_size(self, size_str: str) -> int:
        """解析缓存大小"""
        size_str = size_str.upper()
        if 'K' in size_str:
            return int(size_str.replace('K', ''))
        elif 'M' in size_str:
            return int(size_str.replace('M', '')) * 1024
        return 0
    
    def _get_recommended_implementation(self, info: Dict) -> str:
        """获取推荐实现"""
        if info['simd']['sve2']:
            return 'sve2'
        elif info['simd']['sve']:
            return 'sve'
        elif info['simd']['neon']:
            if info['simd']['dotprod'] and info['simd']['i8mm']:
                return 'neon_i8mm'
            elif info['simd']['dotprod']:
                return 'neon_dotprod'
            return 'neon'
        return 'scalar'
    
    def is_kunpeng(self) -> bool:
        """是否是鲲鹏处理器"""
        return self.info['is_kunpeng']
    
    def is_arm64(self) -> bool:
        """是否是 ARM64 架构"""
        return self.info['is_arm64']
    
    def get_info(self) -> Dict[str, Any]:
        """获取处理器信息"""
        return self.info
    
    def print_info(self):
        """打印处理器信息"""
        print("=== 华为鲲鹏/海思处理器检测 ===")
        print(f"架构: {'ARM64' if self.info['is_arm64'] else '其他'}")
        print(f"处理器: {self.info['cpu_model']}")
        print(f"厂商: {self.info['cpu_vendor']}")
        print(f"核心数: {self.info['cores']}")
        print(f"NUMA 节点: {self.info['numa_nodes']}")
        
        print(f"\nSIMD 特性:")
        simd = self.info['simd']
        print(f"  NEON: {'✅' if simd['neon'] else '❌'}")
        print(f"  SVE: {'✅' if simd['sve'] else '❌'}")
        print(f"  SVE2: {'✅' if simd['sve2'] else '❌'}")
        print(f"  FP16: {'✅' if simd['fp16'] else '❌'}")
        print(f"  DOTPROD: {'✅' if simd['dotprod'] else '❌'}")
        print(f"  I8MM: {'✅' if simd['i8mm'] else '❌'}")
        
        print(f"\n缓存:")
        cache = self.info['cache']
        print(f"  L1D: {cache['l1d']} KB")
        print(f"  L1I: {cache['l1i']} KB")
        print(f"  L2: {cache['l2']} KB")
        print(f"  L3: {cache['l3']} KB")
        
        print(f"\n优化环境:")
        print(f"  KML 数学库: {'✅' if self.info['kml_available'] else '❌'}")
        print(f"  毕昇编译器: {'✅' if self.info['bisheng_available'] else '❌'}")
        print(f"  推荐实现: {self.info['recommended_implementation']}")
        print("==============================")


class KunpengOptimizer:
    """
    鲲鹏处理器优化器
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化优化器"""
        self.config = config or {}
        self.detector = KunpengDetector()
        self.info = self.detector.info
        
        if self.detector.is_kunpeng() or self.detector.is_arm64():
            print(f"✅ 鲲鹏优化器初始化: {self.info['cpu_model']}")
        else:
            print("⚠️ 非 ARM64 架构，鲲鹏优化不可用")
    
    def get_compiler_flags(self) -> List[str]:
        """
        获取编译器优化选项
        
        Returns:
            List[str]: 编译选项列表
        """
        flags = ['-O3']
        
        if not self.info['is_arm64']:
            return flags
        
        # 架构特定选项
        flags.append('-mcpu=native')
        
        # SIMD 选项
        if self.info['simd']['sve']:
            flags.append('-msve')
        if self.info['simd']['sve2']:
            flags.append('-msve2')
        
        # KML 数学库
        if self.info['kml_available']:
            flags.extend(['-fveclib=MATHLIB', '-lkm'])
        
        return flags
    
    def get_environment_vars(self) -> Dict[str, str]:
        """
        获取环境变量配置
        
        Returns:
            Dict[str, str]: 环境变量
        """
        env = {}
        
        if not self.info['is_arm64']:
            return env
        
        # OpenMP 线程数
        env['OMP_NUM_THREADS'] = str(self.info['cores'])
        
        # KML 配置
        if self.info['kml_available']:
            env['KML_THREAD_NUM'] = str(self.info['cores'])
        
        # 内存对齐
        env['OMP_PLACES'] = 'cores'
        env['OMP_PROC_BIND'] = 'close'
        
        return env
    
    def get_numa_binding_command(self, node: int = 0) -> str:
        """
        获取 NUMA 绑定命令
        
        Args:
            node: NUMA 节点 ID
        
        Returns:
            str: 绑定命令
        """
        if self.info['numa_nodes'] <= 1:
            return ""
        
        return f"numactl --cpunodebind={node} --membind={node}"
    
    def get_optimization_config(self) -> Dict[str, Any]:
        """
        获取优化配置
        
        Returns:
            Dict: 优化配置
        """
        return {
            'is_kunpeng': self.info['is_kunpeng'],
            'is_arm64': self.info['is_arm64'],
            'recommended_implementation': self.info['recommended_implementation'],
            'compiler_flags': self.get_compiler_flags(),
            'environment_vars': self.get_environment_vars(),
            'numa_binding': self.get_numa_binding_command(),
            'optimizations': {
                'neon': self.info['simd']['neon'],
                'sve': self.info['simd']['sve'],
                'sve2': self.info['simd']['sve2'],
                'dotprod': self.info['simd']['dotprod'],
                'i8mm': self.info['simd']['i8mm'],
                'kml': self.info['kml_available'],
                'bisheng': self.info['bisheng_available']
            }
        }
    
    def generate_startup_script(self, script_path: str = "scripts/search.py") -> str:
        """
        生成优化启动脚本
        
        Args:
            script_path: 脚本路径
        
        Returns:
            str: 启动脚本内容
        """
        env_vars = self.get_environment_vars()
        numa_cmd = self.get_numa_binding_command()
        
        script = f"""#!/bin/bash
# 鲲鹏处理器优化启动脚本
# 处理器: {self.info['cpu_model']}
# 推荐实现: {self.info['recommended_implementation']}

# 环境变量
"""
        
        for key, value in env_vars.items():
            script += f"export {key}={value}\n"
        
        script += f"""
# NUMA 绑定（多路服务器）
NUMA_CMD="{numa_cmd}"

# 启动服务
echo "启动向量搜索服务（鲲鹏优化）..."
$NUMA_CMD python3 {script_path} "$@"
"""
        return script
    
    def get_installation_guide(self) -> str:
        """
        获取安装指南
        
        Returns:
            str: 安装指南
        """
        if not self.info['is_arm64']:
            return "# 非 ARM64 架构，无需鲲鹏特定优化"
        
        guide = """# 鲲鹏处理器优化安装指南

## 1. 安装 KML 数学库（推荐）

# 华为鲲鹏软件源
sudo yum install -y kml

# 或从华为开发者社区下载
# https://www.hiascend.com/software/kunpeng

## 2. 安装毕昇编译器（可选）

# 下载毕昇编译器
wget https://mirrors.huawei.com/kunpeng/archive/bisheng/compiler/latest/bisheng-compiler-latest.tar.gz
tar -xzf bisheng-compiler-latest.tar.gz
cd bisheng-compiler-*
sudo ./install.sh

## 3. 编译优化选项

# 使用毕昇编译器
clang -O3 -mcpu=native -fveclib=MATHLIB -lkm your_code.c

# 使用 GCC
gcc -O3 -mcpu=native -march=armv8-a your_code.c

## 4. NUMA 绑定（多路服务器）

# 查看 NUMA 拓扑
numactl --hardware

# 绑定到节点 0
numactl --cpunodebind=0 --membind=0 python3 your_script.py

## 5. 大页内存

# 配置 2MB 大页
echo 1024 | sudo tee /proc/sys/vm/nr_hugepages

# 永久配置
echo "vm.nr_hugepages=1024" | sudo tee -a /etc/sysctl.conf
"""
        return guide


def get_kunpeng_optimizer(config: Optional[Dict] = None) -> KunpengOptimizer:
    """
    获取鲲鹏优化器实例
    
    Args:
        config: 配置选项
    
    Returns:
        KunpengOptimizer: 优化器实例
    """
    return KunpengOptimizer(config)


def check_kunpeng_status() -> Dict[str, Any]:
    """
    检查鲲鹏状态
    
    Returns:
        Dict: 鲲鹏状态信息
    """
    detector = KunpengDetector()
    optimizer = KunpengOptimizer()
    
    return {
        'detection': detector.get_info(),
        'optimization': optimizer.get_optimization_config()
    }


# NEON/SVE 优化的向量操作（如果可用）
try:
    from numba import jit, prange
    NUMBA_AVAILABLE = True
    
    @jit(nopython=True, parallel=True, fastmath=True)
    def neon_dot_product(a: np.ndarray, b: np.ndarray) -> float:
        """NEON 优化的点积"""
        result = 0.0
        for i in prange(len(a)):
            result += a[i] * b[i]
        return result
    
    @jit(nopython=True, parallel=True, fastmath=True)
    def neon_batch_dot_products(query: np.ndarray, vectors: np.ndarray) -> np.ndarray:
        """NEON 优化的批量点积"""
        n = vectors.shape[0]
        result = np.zeros(n, dtype=np.float32)
        for i in prange(n):
            for j in range(len(query)):
                result[i] += query[j] * vectors[i, j]
        return result

except ImportError:
    NUMBA_AVAILABLE = False
    neon_dot_product = None
    neon_batch_dot_products = None


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("华为鲲鹏/海思 ARM64 优化模块测试")
    print("=" * 60)
    print()
    
    # 检测处理器
    detector = KunpengDetector()
    detector.print_info()
    
    # 创建优化器
    print()
    optimizer = KunpengOptimizer()
    
    # 获取优化配置
    print("\n=== 优化配置 ===")
    config = optimizer.get_optimization_config()
    print(f"编译选项: {config['compiler_flags']}")
    print(f"环境变量: {config['environment_vars']}")
    print(f"NUMA 绑定: {config['numa_binding'] or '单节点，无需绑定'}")
    
    # 生成启动脚本
    print("\n=== 启动脚本 ===")
    script = optimizer.generate_startup_script()
    print(script[:500] + "..." if len(script) > 500 else script)
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
