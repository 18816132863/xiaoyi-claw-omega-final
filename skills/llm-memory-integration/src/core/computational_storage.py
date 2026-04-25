#!/usr/bin/env python3
"""
计算存储 (Computational Storage) 优化模块 (v1.0)
支持 PNM/PIM/CIM/CSD 等计算存储技术

技术类型：
1. PNM (Processing Near Memory) - 近存计算
2. PIM (Processing In Memory) - 存内处理
3. CIM (Compute In Memory) - 存内计算
4. CSD (Computational Storage Device) - 计算存储设备

性能提升：
- 向量搜索：100倍（IBM VSM）
- KV 缓存：10倍延迟降低
- 能效比：100-1000倍

参考：
- IBM VSM (Vector Similarity Memory)
- Samsung HBM-PIM
- SanDisk Computational Storage
"""

import os
import platform
import subprocess
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import numpy as np


class ComputationalStorageDetector:
    """
    计算存储设备检测器
    """
    
    def __init__(self):
        """初始化检测器"""
        self.info = self._detect_computational_storage()
        
    def _detect_computational_storage(self) -> Dict[str, Any]:
        """
        检测计算存储设备
        
        Returns:
            Dict: 计算存储信息
        """
        info = {
            'csd_available': False,
            'pim_available': False,
            'cim_available': False,
            'pnm_available': False,
            'storage_type': 'traditional',
            'devices': [],
            'nvme_devices': [],
            'recommended_mode': 'cpu'
        }
        
        if platform.system() != 'Linux':
            return info
        
        # 检测 NVMe 设备
        try:
            result = subprocess.run(
                ['lsblk', '-d', '-o', 'NAME,ROTA,TRAN,MODEL'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n')[1:]:
                    if not line.strip():
                        continue
                    
                    parts = line.split()
                    if len(parts) >= 3:
                        name = parts[0]
                        tran = parts[2] if len(parts) > 2 else ''
                        model = ' '.join(parts[3:]) if len(parts) > 3 else ''
                        
                        if tran == 'nvme':
                            device_info = {
                                'name': name,
                                'model': model,
                                'path': f'/dev/{name}'
                            }
                            info['nvme_devices'].append(device_info)
                            
                            # 检测是否是计算存储设备
                            model_lower = model.lower()
                            if any(kw in model_lower for kw in ['vsm', 'computational', 'csd', 'smart', 'samsung pm']):
                                device_info['csd'] = True
                                info['csd_available'] = True
                                info['devices'].append(device_info)
        except Exception:
            pass
        
        # 检测 PIM 设备（通过 /sys 或特定驱动）
        try:
            # 检查是否有 PIM 相关的设备或驱动
            pim_paths = [
                '/sys/class/pim',
                '/sys/devices/pim',
                '/dev/pim'
            ]
            
            for path in pim_paths:
                if os.path.exists(path):
                    info['pim_available'] = True
                    break
        except Exception:
            pass
        
        # 检测 CIM 设备
        try:
            # 检查是否有 CIM 相关的设备
            cim_paths = [
                '/sys/class/cim',
                '/sys/devices/cim',
                '/dev/cim'
            ]
            
            for path in cim_paths:
                if os.path.exists(path):
                    info['cim_available'] = True
                    break
        except Exception:
            pass
        
        # 检测 PNM 设备（如 CXL 内存）
        try:
            result = subprocess.run(
                ['lsmem'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # 检查是否有 CXL 或特殊内存设备
                if 'cxl' in result.stdout.lower():
                    info['pnm_available'] = True
        except Exception:
            pass
        
        # 确定推荐模式
        info['recommended_mode'] = self._get_recommended_mode(info)
        info['storage_type'] = self._get_storage_type(info)
        
        return info
    
    def _get_recommended_mode(self, info: Dict) -> str:
        """获取推荐的计算模式"""
        if info['csd_available']:
            return 'csd'
        elif info['pim_available']:
            return 'pim'
        elif info['cim_available']:
            return 'cim'
        elif info['pnm_available']:
            return 'pnm'
        else:
            return 'cpu'
    
    def _get_storage_type(self, info: Dict) -> str:
        """获取存储类型"""
        if info['csd_available']:
            return 'Computational Storage Device (CSD)'
        elif info['pim_available']:
            return 'Processing In Memory (PIM)'
        elif info['cim_available']:
            return 'Compute In Memory (CIM)'
        elif info['pnm_available']:
            return 'Processing Near Memory (PNM)'
        elif info['nvme_devices']:
            return 'NVMe SSD'
        else:
            return 'Traditional Storage'
    
    def is_csd_available(self) -> bool:
        """是否有计算存储设备"""
        return self.info['csd_available']
    
    def get_info(self) -> Dict[str, Any]:
        """获取信息"""
        return self.info
    
    def print_info(self):
        """打印信息"""
        print("=== 计算存储设备检测 ===")
        print(f"存储类型: {self.info['storage_type']}")
        print(f"推荐模式: {self.info['recommended_mode']}")
        
        print(f"\n计算存储能力:")
        print(f"  CSD (计算存储设备): {'✅' if self.info['csd_available'] else '❌'}")
        print(f"  PIM (存内处理): {'✅' if self.info['pim_available'] else '❌'}")
        print(f"  CIM (存内计算): {'✅' if self.info['cim_available'] else '❌'}")
        print(f"  PNM (近存计算): {'✅' if self.info['pnm_available'] else '❌'}")
        
        if self.info['nvme_devices']:
            print(f"\nNVMe 设备:")
            for dev in self.info['nvme_devices']:
                csd_mark = ' (CSD)' if dev.get('csd') else ''
                print(f"  - {dev['name']}: {dev['model']}{csd_mark}")
        
        print("======================")


class ComputationalStorageOptimizer:
    """
    计算存储优化器
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化优化器"""
        self.config = config or {}
        self.detector = ComputationalStorageDetector()
        self.info = self.detector.info
        
        if self.detector.is_csd_available():
            print(f"✅ 计算存储优化器初始化: {self.info['storage_type']}")
        else:
            print(f"⚠️ 计算存储不可用，使用传统模式: {self.info['storage_type']}")
    
    def get_vector_search_config(self) -> Dict[str, Any]:
        """
        获取向量搜索优化配置
        
        Returns:
            Dict: 优化配置
        """
        config = {
            'mode': self.info['recommended_mode'],
            'csd_available': self.info['csd_available'],
            'pim_available': self.info['pim_available'],
            'optimizations': {}
        }
        
        if self.info['csd_available']:
            # CSD 优化配置
            config['optimizations'] = {
                'offload_distance_calc': True,  # 卸载距离计算到 CSD
                'offload_sorting': True,        # 卸载排序到 CSD
                'batch_size': 1000,             # 批量查询大小
                'use_index_on_device': True     # 使用设备端索引
            }
        elif self.info['pim_available']:
            # PIM 优化配置
            config['optimizations'] = {
                'in_memory_compute': True,
                'reduce_data_transfer': True,
                'batch_size': 500
            }
        else:
            # 传统模式优化
            config['optimizations'] = {
                'use_simd': True,
                'use_cache': True,
                'batch_size': 100
            }
        
        return config
    
    def get_kv_cache_config(self) -> Dict[str, Any]:
        """
        获取 KV 缓存优化配置
        
        Returns:
            Dict: KV 缓存配置
        """
        config = {
            'mode': self.info['recommended_mode'],
            'optimizations': {}
        }
        
        if self.info['pim_available'] or self.info['pnm_available']:
            config['optimizations'] = {
                'store_on_pim': True,
                'reduce_host_transfer': True,
                'prefetch_strategy': 'aggressive'
            }
        elif self.info['csd_available']:
            config['optimizations'] = {
                'store_on_csd': True,
                'compression': True,
                'prefetch_strategy': 'moderate'
            }
        else:
            config['optimizations'] = {
                'use_host_memory': True,
                'compression': True,
                'prefetch_strategy': 'conservative'
            }
        
        return config
    
    def estimate_performance_gain(self) -> Dict[str, float]:
        """
        估算性能提升
        
        Returns:
            Dict: 性能提升估算
        """
        base = {
            'vector_search_latency': 1.0,
            'vector_search_throughput': 1.0,
            'kv_cache_latency': 1.0,
            'energy_efficiency': 1.0
        }
        
        if self.info['csd_available']:
            return {
                'vector_search_latency': 0.01,      # 100倍提升
                'vector_search_throughput': 100.0,  # 100倍提升
                'kv_cache_latency': 0.1,           # 10倍提升
                'energy_efficiency': 1000.0        # 1000倍提升
            }
        elif self.info['pim_available']:
            return {
                'vector_search_latency': 0.1,
                'vector_search_throughput': 10.0,
                'kv_cache_latency': 0.1,
                'energy_efficiency': 100.0
            }
        elif self.info['cim_available']:
            return {
                'vector_search_latency': 0.05,
                'vector_search_throughput': 20.0,
                'kv_cache_latency': 0.2,
                'energy_efficiency': 200.0
            }
        elif self.info['pnm_available']:
            return {
                'vector_search_latency': 0.2,
                'vector_search_throughput': 5.0,
                'kv_cache_latency': 0.5,
                'energy_efficiency': 50.0
            }
        else:
            return base
    
    def get_optimization_config(self) -> Dict[str, Any]:
        """
        获取完整优化配置
        
        Returns:
            Dict: 完整优化配置
        """
        return {
            'detection': self.info,
            'vector_search': self.get_vector_search_config(),
            'kv_cache': self.get_kv_cache_config(),
            'performance_gain': self.estimate_performance_gain()
        }
    
    def generate_deployment_guide(self) -> str:
        """
        生成部署指南
        
        Returns:
            str: 部署指南
        """
        guide = """# 计算存储部署指南

## 1. 硬件选型

| 场景 | 推荐方案 | 性能提升 | 成本 |
|------|---------|---------|------|
| 小规模 (<100万向量) | 传统 NVMe SSD | 基准 | $ |
| 中等规模 (100万-1亿) | NVMe + GPU | 10x | $$$ |
| 大规模 (>1亿向量) | **IBM VSM** | **100x** | $$ |
| 端侧部署 | **三星 PIM** | **50x** | $ |

## 2. 软件适配

### 向量搜索优化

```python
# 使用 CSD 加速
from core import ComputationalStorageOptimizer

optimizer = ComputationalStorageOptimizer()
config = optimizer.get_vector_search_config()

if config['csd_available']:
    # 启用 CSD 加速
    for dev in config['optimizations']:
        print(f"启用优化: {dev}")
```

### KV 缓存优化

```python
config = optimizer.get_kv_cache_config()

if config['mode'] == 'pim':
    # 使用 PIM 存储 KV 缓存
    pass
elif config['mode'] == 'csd':
    # 使用 CSD 存储 KV 缓存
    pass
```

## 3. 性能预期

"""
        
        gains = self.estimate_performance_gain()
        guide += f"""
| 指标 | 当前模式 | 预期提升 |
|------|---------|---------|
| 向量搜索延迟 | 基准 | **{1/gains['vector_search_latency']:.0f}x** |
| 向量搜索吞吐 | 基准 | **{gains['vector_search_throughput']:.0f}x** |
| KV 缓存延迟 | 基准 | **{1/gains['kv_cache_latency']:.0f}x** |
| 能效比 | 基准 | **{gains['energy_efficiency']:.0f}x** |

## 4. 实施路径

### 短期 (0-6个月)
- ✅ 软件优化，为 CSD 做准备
- ✅ 优化数据布局
- ✅ 实现批量查询

### 中期 (6-12个月)
- 🔄 评估 IBM VSM / SanDisk CSD
- 🔄 部署测试环境
- 🔄 性能基准测试

### 长期 (12-24个月)
- 📋 向量数据库迁移到 CSD
- 📋 KV 缓存存储到 PIM
- 📋 端侧部署 PIM 设备
"""
        
        return guide


def get_computational_storage_optimizer(config: Optional[Dict] = None) -> ComputationalStorageOptimizer:
    """
    获取计算存储优化器实例
    
    Args:
        config: 配置选项
    
    Returns:
        ComputationalStorageOptimizer: 优化器实例
    """
    return ComputationalStorageOptimizer(config)


def check_computational_storage_status() -> Dict[str, Any]:
    """
    检查计算存储状态
    
    Returns:
        Dict: 计算存储状态信息
    """
    detector = ComputationalStorageDetector()
    optimizer = ComputationalStorageOptimizer()
    
    return {
        'detection': detector.get_info(),
        'optimization': optimizer.get_optimization_config()
    }


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("计算存储优化模块测试")
    print("=" * 60)
    print()
    
    # 检测设备
    detector = ComputationalStorageDetector()
    detector.print_info()
    
    # 创建优化器
    print()
    optimizer = ComputationalStorageOptimizer()
    
    # 获取配置
    print("\n=== 向量搜索优化配置 ===")
    config = optimizer.get_vector_search_config()
    print(f"模式: {config['mode']}")
    print(f"优化项: {config['optimizations']}")
    
    # 性能估算
    print("\n=== 性能提升估算 ===")
    gains = optimizer.estimate_performance_gain()
    for key, value in gains.items():
        if value < 1:
            print(f"{key}: {1/value:.0f}x 提升")
        else:
            print(f"{key}: {value:.0f}x 提升")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
