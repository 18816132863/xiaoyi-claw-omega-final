"""
Policy Snapshot Store - 策略快照存储
保存策略版本快照，支持审计和回溯
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import hashlib


@dataclass
class PolicySnapshot:
    """策略快照"""
    snapshot_id: str
    profile: str
    risk_policy_version: str
    budget_policy_version: str
    permission_policy_version: str
    degradation_policy_version: str
    created_at: str
    checksum: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "profile": self.profile,
            "risk_policy_version": self.risk_policy_version,
            "budget_policy_version": self.budget_policy_version,
            "permission_policy_version": self.permission_policy_version,
            "degradation_policy_version": self.degradation_policy_version,
            "created_at": self.created_at,
            "checksum": self.checksum
        }


class PolicySnapshotStore:
    """
    策略快照存储
    
    保存策略版本快照：
    - snapshot_id: 快照唯一标识
    - profile: 配置文件名
    - risk_policy_version: 风险策略版本
    - budget_policy_version: 预算策略版本
    - permission_policy_version: 权限策略版本
    - degradation_policy_version: 降级策略版本
    - created_at: 创建时间
    """
    
    def __init__(self):
        self._snapshots: Dict[str, PolicySnapshot] = {}
        self._profile_snapshots: Dict[str, List[str]] = {}
        self._current_versions = {
            "risk_policy": "1.0.0",
            "budget_policy": "1.0.0",
            "permission_policy": "1.0.0",
            "degradation_policy": "1.0.0"
        }
    
    def create(self, profile: str) -> PolicySnapshot:
        """
        创建策略快照
        
        Args:
            profile: 配置文件名
            
        Returns:
            策略快照
        """
        timestamp = datetime.now().isoformat()
        
        # 生成快照 ID
        snapshot_id = self._generate_snapshot_id(profile, timestamp)
        
        # 计算校验和
        checksum = self._calculate_checksum(profile)
        
        snapshot = PolicySnapshot(
            snapshot_id=snapshot_id,
            profile=profile,
            risk_policy_version=self._current_versions["risk_policy"],
            budget_policy_version=self._current_versions["budget_policy"],
            permission_policy_version=self._current_versions["permission_policy"],
            degradation_policy_version=self._current_versions["degradation_policy"],
            created_at=timestamp,
            checksum=checksum
        )
        
        # 存储
        self._snapshots[snapshot_id] = snapshot
        
        if profile not in self._profile_snapshots:
            self._profile_snapshots[profile] = []
        self._profile_snapshots[profile].append(snapshot_id)
        
        return snapshot
    
    def get_or_create(self, profile: str) -> Dict[str, Any]:
        """
        获取或创建快照
        
        Args:
            profile: 配置文件名
            
        Returns:
            快照字典
        """
        # 检查是否有最新快照
        if profile in self._profile_snapshots and self._profile_snapshots[profile]:
            latest_id = self._profile_snapshots[profile][-1]
            latest_snapshot = self._snapshots.get(latest_id)
            
            # 检查版本是否一致
            if latest_snapshot and self._is_version_match(latest_snapshot):
                return latest_snapshot.to_dict()
        
        # 创建新快照
        snapshot = self.create(profile)
        return snapshot.to_dict()
    
    def get(self, snapshot_id: str) -> Optional[PolicySnapshot]:
        """
        获取快照
        
        Args:
            snapshot_id: 快照 ID
            
        Returns:
            策略快照，不存在返回 None
        """
        return self._snapshots.get(snapshot_id)
    
    def get_by_profile(self, profile: str) -> List[PolicySnapshot]:
        """
        按配置文件获取快照列表
        
        Args:
            profile: 配置文件名
            
        Returns:
            快照列表
        """
        if profile not in self._profile_snapshots:
            return []
        
        return [
            self._snapshots[sid]
            for sid in self._profile_snapshots[profile]
            if sid in self._snapshots
        ]
    
    def get_latest(self, profile: str) -> Optional[PolicySnapshot]:
        """
        获取最新快照
        
        Args:
            profile: 配置文件名
            
        Returns:
            最新快照，不存在返回 None
        """
        if profile not in self._profile_snapshots or not self._profile_snapshots[profile]:
            return None
        
        latest_id = self._profile_snapshots[profile][-1]
        return self._snapshots.get(latest_id)
    
    def refresh(self, profile: str) -> PolicySnapshot:
        """
        刷新快照（强制创建新快照）
        
        Args:
            profile: 配置文件名
            
        Returns:
            新快照
        """
        return self.create(profile)
    
    def update_version(self, policy_type: str, version: str) -> bool:
        """
        更新策略版本
        
        Args:
            policy_type: 策略类型
            version: 版本号
            
        Returns:
            是否更新成功
        """
        if policy_type not in self._current_versions:
            return False
        
        self._current_versions[policy_type] = version
        return True
    
    def get_current_versions(self) -> Dict[str, str]:
        """
        获取当前策略版本
        
        Returns:
            当前版本字典
        """
        return dict(self._current_versions)
    
    def list_all(self) -> List[Dict[str, Any]]:
        """
        列出所有快照
        
        Returns:
            快照字典列表
        """
        return [snapshot.to_dict() for snapshot in self._snapshots.values()]
    
    def delete(self, snapshot_id: str) -> bool:
        """
        删除快照
        
        Args:
            snapshot_id: 快照 ID
            
        Returns:
            是否删除成功
        """
        if snapshot_id not in self._snapshots:
            return False
        
        snapshot = self._snapshots[snapshot_id]
        profile = snapshot.profile
        
        del self._snapshots[snapshot_id]
        
        if profile in self._profile_snapshots:
            self._profile_snapshots[profile] = [
                sid for sid in self._profile_snapshots[profile]
                if sid != snapshot_id
            ]
        
        return True
    
    def _generate_snapshot_id(self, profile: str, timestamp: str) -> str:
        """
        生成快照 ID
        
        Args:
            profile: 配置文件名
            timestamp: 时间戳
            
        Returns:
            快照 ID
        """
        data = f"{profile}:{timestamp}:{datetime.now().microsecond}"
        return f"snap_{hashlib.md5(data.encode()).hexdigest()[:12]}"
    
    def _calculate_checksum(self, profile: str) -> str:
        """
        计算校验和
        
        Args:
            profile: 配置文件名
            
        Returns:
            校验和
        """
        data = json.dumps({
            "profile": profile,
            "versions": self._current_versions
        }, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _is_version_match(self, snapshot: PolicySnapshot) -> bool:
        """
        检查版本是否匹配
        
        Args:
            snapshot: 快照
            
        Returns:
            是否匹配
        """
        return (
            snapshot.risk_policy_version == self._current_versions["risk_policy"] and
            snapshot.budget_policy_version == self._current_versions["budget_policy"] and
            snapshot.permission_policy_version == self._current_versions["permission_policy"] and
            snapshot.degradation_policy_version == self._current_versions["degradation_policy"]
        )


# 全局单例
_policy_snapshot_store = None

def get_policy_snapshot_store() -> PolicySnapshotStore:
    """获取策略快照存储单例"""
    global _policy_snapshot_store
    if _policy_snapshot_store is None:
        _policy_snapshot_store = PolicySnapshotStore()
    return _policy_snapshot_store
