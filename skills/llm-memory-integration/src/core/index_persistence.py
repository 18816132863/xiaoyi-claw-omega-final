#!/usr/bin/env python3
"""
索引持久化模块 (v6.0.1)
索引序列化保存、增量更新、版本管理

安全更新：使用 numpy npz 格式替代 pickle，避免反序列化漏洞
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import json
import hashlib
from pathlib import Path
from datetime import datetime

# 安全警告：不再使用 pickle
# pickle.load 可能导致任意代码执行，改用 numpy npz 格式
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)


class IndexPersistence:
    """
    索引持久化管理器
    """
    
    def __init__(
        self,
        index_dir: str = "~/.openclaw/memory-tdai/indices",
        version: str = "4.1.0"
    ):
        """
        初始化持久化管理器
        
        Args:
            index_dir: 索引存储目录
            version: 版本号
        """
        self.index_dir = Path(index_dir).expanduser()
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.version = version
        self.metadata_file = self.index_dir / "metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """加载元数据"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {
            'version': self.version,
            'indices': {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    def _save_metadata(self):
        """保存元数据"""
        self.metadata['updated_at'] = datetime.now().isoformat()
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def _compute_hash(self, data: np.ndarray) -> str:
        """计算数据哈希"""
        return hashlib.sha256(data.tobytes()).hexdigest()[:16]
    
    def save_index(
        self,
        name: str,
        index: Any,
        vectors: np.ndarray,
        config: Optional[Dict] = None
    ) -> str:
        """
        保存索引
        
        Args:
            name: 索引名称
            index: 索引对象（仅保存向量，索引需要重建）
            vectors: 原始向量
            config: 配置信息
        
        Returns:
            str: 索引 ID
        
        安全说明：
            不再保存索引对象本身，只保存向量和配置。
            索引需要在加载后重建，避免 pickle 反序列化漏洞。
        """
        # 生成索引 ID
        index_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 保存向量和配置（使用安全的 npz 格式）
        index_file = self.index_dir / f"{index_id}.npz"
        
        np.savez_compressed(
            index_file,
            vectors=vectors.astype(np.float32),
            config=np.array([json.dumps(config or {})]),
            created_at=np.array([datetime.now().isoformat()])
        )
        
        # 更新元数据
        self.metadata['indices'][index_id] = {
            'name': name,
            'n_vectors': len(vectors),
            'dim': vectors.shape[1] if len(vectors.shape) > 1 else 0,
            'hash': self._compute_hash(vectors),
            'created_at': datetime.now().isoformat(),
            'file': str(index_file.name),
            'config': config or {}
        }
        
        self._save_metadata()
        print(f"✅ 索引已保存: {index_id}")
        
        return index_id
    
    def load_index(self, index_id: str) -> Optional[Dict]:
        """
        加载索引
        
        Args:
            index_id: 索引 ID
        
        Returns:
            Optional[Dict]: 索引数据
        """
        if index_id not in self.metadata['indices']:
            print(f"❌ 索引不存在: {index_id}")
            return None
        
        index_file = self.index_dir / self.metadata['indices'][index_id]['file']
        
        if not index_file.exists():
            print(f"❌ 索引文件不存在: {index_file}")
            return None
        
        # 安全加载：使用 npz 格式，禁用 pickle
        try:
            data = np.load(index_file, allow_pickle=False)
            result = {
                'vectors': data['vectors'],
                'config': json.loads(str(data['config'][0])) if len(data['config']) > 0 else {},
                'created_at': str(data['created_at'][0]) if len(data['created_at']) > 0 else None,
                'note': '索引需要重建，仅保存了向量'
            }
            print(f"✅ 索引已加载: {index_id} (需要重建索引)")
            return result
        except Exception as e:
            print(f"❌ 索引加载失败: {e}")
            return None
    
    def get_latest_index(self, name: str) -> Optional[Dict]:
        """
        获取最新索引
        
        Args:
            name: 索引名称
        
        Returns:
            Optional[Dict]: 索引数据
        """
        # 查找该名称的最新索引
        matching_indices = [
            (index_id, info)
            for index_id, info in self.metadata['indices'].items()
            if info['name'] == name
        ]
        
        if not matching_indices:
            print(f"❌ 未找到索引: {name}")
            return None
        
        # 按时间排序，获取最新的
        matching_indices.sort(key=lambda x: x[1]['created_at'], reverse=True)
        latest_id = matching_indices[0][0]
        
        return self.load_index(latest_id)
    
    def list_indices(self, name: Optional[str] = None) -> List[Dict]:
        """
        列出索引
        
        Args:
            name: 索引名称（可选）
        
        Returns:
            List[Dict]: 索引列表
        """
        indices = []
        for index_id, info in self.metadata['indices'].items():
            if name is None or info['name'] == name:
                indices.append({
                    'id': index_id,
                    **info
                })
        
        return indices
    
    def delete_index(self, index_id: str) -> bool:
        """
        删除索引
        
        Args:
            index_id: 索引 ID
        
        Returns:
            bool: 是否成功
        """
        if index_id not in self.metadata['indices']:
            print(f"❌ 索引不存在: {index_id}")
            return False
        
        # 删除文件
        index_file = self.index_dir / self.metadata['indices'][index_id]['file']
        if index_file.exists():
            index_file.unlink()
        
        # 更新元数据
        del self.metadata['indices'][index_id]
        self._save_metadata()
        
        print(f"✅ 索引已删除: {index_id}")
        return True
    
    def cleanup_old_indices(self, name: str, keep: int = 3):
        """
        清理旧索引
        
        Args:
            name: 索引名称
            keep: 保留数量
        """
        indices = self.list_indices(name)
        
        if len(indices) <= keep:
            return
        
        # 按时间排序
        indices.sort(key=lambda x: x['created_at'], reverse=True)
        
        # 删除旧索引
        for index_info in indices[keep:]:
            self.delete_index(index_info['id'])
        
        print(f"✅ 已清理 {len(indices) - keep} 个旧索引")


class IncrementalIndexUpdater:
    """
    增量索引更新器
    """
    
    def __init__(self, persistence: IndexPersistence):
        """
        初始化增量更新器
        
        Args:
            persistence: 持久化管理器
        """
        self.persistence = persistence
    
    def update_index(
        self,
        name: str,
        new_vectors: np.ndarray,
        index_builder: callable
    ) -> str:
        """
        增量更新索引
        
        Args:
            name: 索引名称
            new_vectors: 新向量
            index_builder: 索引构建函数
        
        Returns:
            str: 新索引 ID
        """
        # 加载现有索引
        existing = self.persistence.get_latest_index(name)
        
        if existing:
            # 合并向量
            existing_vectors = existing['vectors']
            all_vectors = np.vstack([existing_vectors, new_vectors])
            print(f"增量更新: {len(existing_vectors)} + {len(new_vectors)} = {len(all_vectors)}")
        else:
            all_vectors = new_vectors
            print(f"新建索引: {len(all_vectors)} 个向量")
        
        # 构建新索引
        new_index = index_builder(all_vectors)
        
        # 保存
        return self.persistence.save_index(
            name=name,
            index=new_index,
            vectors=all_vectors,
            config={'incremental': True}
        )


if __name__ == "__main__":
    # 测试
    print("=== 索引持久化测试 ===")
    
    persistence = IndexPersistence()
    
    # 创建测试数据
    dim = 4096
    n_vectors = 1000
    vectors = np.random.randn(n_vectors, dim).astype(np.float32)
    
    # 保存索引
    index_id = persistence.save_index(
        name="test_index",
        index={'type': 'test'},
        vectors=vectors,
        config={'algorithm': 'hnsw'}
    )
    
    # 加载索引
    data = persistence.load_index(index_id)
    print(f"加载的向量数: {len(data['vectors'])}")
    
    # 列出索引
    indices = persistence.list_indices()
    print(f"索引数量: {len(indices)}")
    
    # 清理
    persistence.cleanup_old_indices("test_index", keep=1)
