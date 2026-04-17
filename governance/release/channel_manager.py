"""
Channel Manager - 通道管理器
Phase3 Group6 核心模块
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import os


class Channel(Enum):
    """发布通道"""
    DEV = "dev"
    STAGING = "staging"
    STABLE = "stable"


@dataclass
class ChannelState:
    """通道状态"""
    channel: Channel
    current_baseline_id: Optional[str] = None
    current_version: Optional[str] = None
    promoted_at: Optional[str] = None
    promotion_count: int = 0
    health_status: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "channel": self.channel.value,
            "current_baseline_id": self.current_baseline_id,
            "current_version": self.current_version,
            "promoted_at": self.promoted_at,
            "promotion_count": self.promotion_count,
            "health_status": self.health_status
        }


class ChannelManager:
    """
    通道管理器
    
    职责：
    - 管理发布通道
    - 追踪通道状态
    - 支持通道晋升
    """
    
    def __init__(self, channels_path: str = "reports/release/release_channels.json"):
        self.channels_path = channels_path
        self._channels: Dict[Channel, ChannelState] = {}
        self._ensure_dir()
        self._initialize_channels()
        self._load()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.channels_path), exist_ok=True)
    
    def _initialize_channels(self):
        """初始化通道"""
        for channel in Channel:
            self._channels[channel] = ChannelState(channel=channel)
    
    def _load(self):
        """加载通道状态"""
        if not os.path.exists(self.channels_path):
            return
        
        try:
            with open(self.channels_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for channel_str, state_data in data.get("channels", {}).items():
                channel = Channel(channel_str)
                if channel in self._channels:
                    self._channels[channel] = ChannelState(
                        channel=channel,
                        current_baseline_id=state_data.get("current_baseline_id"),
                        current_version=state_data.get("current_version"),
                        promoted_at=state_data.get("promoted_at"),
                        promotion_count=state_data.get("promotion_count", 0),
                        health_status=state_data.get("health_status", "unknown")
                    )
        except Exception:
            pass
    
    def _save(self):
        """保存通道状态"""
        data = {
            "updated_at": datetime.now().isoformat(),
            "channels": {
                channel.value: state.to_dict()
                for channel, state in self._channels.items()
            }
        }
        
        with open(self.channels_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_channel(self, channel: Channel) -> ChannelState:
        """获取通道状态"""
        return self._channels.get(channel, ChannelState(channel=channel))
    
    def get_current_baseline(self, channel: Channel) -> Optional[str]:
        """获取通道当前基线"""
        state = self._channels.get(channel)
        return state.current_baseline_id if state else None
    
    def promote(
        self,
        from_channel: Channel,
        to_channel: Channel,
        baseline_id: str,
        version: str
    ) -> bool:
        """
        晋升基线
        
        Args:
            from_channel: 源通道
            to_channel: 目标通道
            baseline_id: 基线 ID
            version: 版本
        
        Returns:
            bool
        """
        # 验证晋升顺序
        valid_promotions = [
            (Channel.DEV, Channel.STAGING),
            (Channel.STAGING, Channel.STABLE)
        ]
        
        if (from_channel, to_channel) not in valid_promotions:
            return False
        
        # 更新目标通道
        target_state = self._channels[to_channel]
        target_state.current_baseline_id = baseline_id
        target_state.current_version = version
        target_state.promoted_at = datetime.now().isoformat()
        target_state.promotion_count += 1
        
        self._save()
        return True
    
    def set_baseline(
        self,
        channel: Channel,
        baseline_id: str,
        version: str
    ):
        """设置通道基线"""
        state = self._channels[channel]
        state.current_baseline_id = baseline_id
        state.current_version = version
        state.promoted_at = datetime.now().isoformat()
        self._save()
    
    def update_health(self, channel: Channel, health_status: str):
        """更新通道健康状态"""
        if channel in self._channels:
            self._channels[channel].health_status = health_status
            self._save()
    
    def get_all_channels(self) -> Dict[Channel, ChannelState]:
        """获取所有通道"""
        return dict(self._channels)


# 全局单例
_channel_manager = None


def get_channel_manager() -> ChannelManager:
    """获取通道管理器单例"""
    global _channel_manager
    if _channel_manager is None:
        _channel_manager = ChannelManager()
    return _channel_manager
