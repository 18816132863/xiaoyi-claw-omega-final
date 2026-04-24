#!/usr/bin/env python3
"""
状态恢复模块 - V1.0.0

管理系统状态的保存和恢复。
"""

import json
import shutil
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum


class RecoveryPointType(Enum):
    """恢复点类型"""
    MANUAL = "manual"        # 手动创建
    AUTOMATIC = "automatic"  # 自动创建
    PRE_CHANGE = "pre_change"  # 变更前
    SCHEDULED = "scheduled"  # 定时创建


@dataclass
class RecoveryPoint:
    """恢复点"""
    id: str
    name: str
    type: RecoveryPointType
    timestamp: datetime
    description: str
    files: Dict[str, str]  # 文件路径 -> 哈希
    metadata: Dict[str, Any] = field(default_factory=dict)
    verified: bool = False


class StateRecovery:
    """状态恢复管理器"""
    
    def __init__(self, recovery_dir: str = "archive/recovery"):
        self.recovery_dir = Path(recovery_dir)
        self.recovery_dir.mkdir(parents=True, exist_ok=True)
        self.points_file = self.recovery_dir / "recovery_points.json"
        self.recovery_points: Dict[str, RecoveryPoint] = {}
        self._load_recovery_points()
    
    def _load_recovery_points(self):
        """加载恢复点"""
        if self.points_file.exists():
            try:
                with open(self.points_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for p in data.get("points", []):
                        point = RecoveryPoint(
                            id=p["id"],
                            name=p["name"],
                            type=RecoveryPointType(p["type"]),
                            timestamp=datetime.fromisoformat(p["timestamp"]),
                            description=p["description"],
                            files=p["files"],
                            metadata=p.get("metadata", {}),
                            verified=p.get("verified", False)
                        )
                        self.recovery_points[point.id] = point
            except:
                pass
    
    def _save_recovery_points(self):
        """保存恢复点"""
        data = {
            "points": [
                {
                    "id": p.id,
                    "name": p.name,
                    "type": p.type.value,
                    "timestamp": p.timestamp.isoformat(),
                    "description": p.description,
                    "files": p.files,
                    "metadata": p.metadata,
                    "verified": p.verified
                }
                for p in self.recovery_points.values()
            ]
        }
        with open(self.points_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def create_recovery_point(self,
                              name: str,
                              files: List[str],
                              description: str = "",
                              point_type: RecoveryPointType = RecoveryPointType.MANUAL) -> RecoveryPoint:
        """
        创建恢复点
        
        Args:
            name: 恢复点名称
            files: 要保存的文件列表
            description: 描述
            point_type: 恢复点类型
        
        Returns:
            创建的恢复点
        """
        point_id = f"rp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        point_dir = self.recovery_dir / point_id
        point_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        file_hashes = {}
        for file_path in files:
            src = Path(file_path)
            if src.exists():
                # 计算哈希
                import hashlib
                content = src.read_bytes()
                file_hash = hashlib.sha256(content).hexdigest()[:16]
                
                # 复制文件
                dst = point_dir / src.name
                shutil.copy2(src, dst)
                
                file_hashes[str(src)] = file_hash
        
        # 创建恢复点
        point = RecoveryPoint(
            id=point_id,
            name=name,
            type=point_type,
            timestamp=datetime.now(),
            description=description,
            files=file_hashes
        )
        
        self.recovery_points[point_id] = point
        self._save_recovery_points()
        
        return point
    
    def restore(self, point_id: str, verify: bool = True) -> Dict[str, bool]:
        """
        恢复到指定恢复点
        
        Args:
            point_id: 恢复点ID
            verify: 是否验证文件完整性
        
        Returns:
            恢复结果 {文件路径: 是否成功}
        """
        point = self.recovery_points.get(point_id)
        if not point:
            return {"error": False, "message": "恢复点不存在"}
        
        point_dir = self.recovery_dir / point_id
        results = {}
        
        for file_path, expected_hash in point.files.items():
            try:
                src = point_dir / Path(file_path).name
                dst = Path(file_path)
                
                if not src.exists():
                    results[file_path] = False
                    continue
                
                # 验证哈希
                if verify:
                    import hashlib
                    content = src.read_bytes()
                    actual_hash = hashlib.sha256(content).hexdigest()[:16]
                    if actual_hash != expected_hash:
                        results[file_path] = False
                        continue
                
                # 恢复文件
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                results[file_path] = True
                
            except Exception as e:
                results[file_path] = False
        
        return results
    
    def list_recovery_points(self, 
                             point_type: RecoveryPointType = None,
                             limit: int = 20) -> List[RecoveryPoint]:
        """列出恢复点"""
        points = list(self.recovery_points.values())
        
        if point_type:
            points = [p for p in points if p.type == point_type]
        
        points.sort(key=lambda p: p.timestamp, reverse=True)
        return points[:limit]
    
    def delete_recovery_point(self, point_id: str) -> bool:
        """删除恢复点"""
        if point_id not in self.recovery_points:
            return False
        
        # 删除文件
        point_dir = self.recovery_dir / point_id
        if point_dir.exists():
            shutil.rmtree(point_dir)
        
        # 删除记录
        del self.recovery_points[point_id]
        self._save_recovery_points()
        
        return True
    
    def verify_recovery_point(self, point_id: str) -> Dict[str, Any]:
        """验证恢复点完整性"""
        point = self.recovery_points.get(point_id)
        if not point:
            return {"valid": False, "error": "恢复点不存在"}
        
        point_dir = self.recovery_dir / point_id
        results = {
            "valid": True,
            "files_checked": 0,
            "files_valid": 0,
            "errors": []
        }
        
        import hashlib
        for file_path, expected_hash in point.files.items():
            results["files_checked"] += 1
            
            src = point_dir / Path(file_path).name
            if not src.exists():
                results["errors"].append(f"文件缺失: {file_path}")
                results["valid"] = False
                continue
            
            content = src.read_bytes()
            actual_hash = hashlib.sha256(content).hexdigest()[:16]
            
            if actual_hash == expected_hash:
                results["files_valid"] += 1
            else:
                results["errors"].append(f"哈希不匹配: {file_path}")
                results["valid"] = False
        
        point.verified = results["valid"]
        self._save_recovery_points()
        
        return results
    
    def auto_create_before_change(self, change_description: str, files: List[str]) -> RecoveryPoint:
        """变更前自动创建恢复点"""
        return self.create_recovery_point(
            name=f"变更前: {change_description[:50]}",
            files=files,
            description=change_description,
            point_type=RecoveryPointType.PRE_CHANGE
        )


# 全局状态恢复器
_state_recovery: Optional[StateRecovery] = None


def get_state_recovery() -> StateRecovery:
    """获取全局状态恢复器"""
    global _state_recovery
    if _state_recovery is None:
        _state_recovery = StateRecovery()
    return _state_recovery
