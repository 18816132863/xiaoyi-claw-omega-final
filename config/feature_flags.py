"""
Feature Flags - 功能开关
"""

from typing import Dict, Any, Optional
from enum import Enum


class Feature(Enum):
    """功能枚举"""
    DIAGNOSTICS = "diagnostics"
    EXPORT_HISTORY = "export_history"
    REPLAY_RUN = "replay_run"
    SELF_REPAIR = "self_repair"
    BATCH_TASKS = "batch_tasks"
    WORKFLOW_ENGINE = "workflow_engine"
    PLATFORM_SCHEDULING = "platform_scheduling"
    ADVANCED_RETRY = "advanced_retry"
    CHECKPOINT_RECOVERY = "checkpoint_recovery"


class FeatureFlags:
    """功能开关管理"""
    
    def __init__(self):
        self._flags: Dict[str, bool] = {
            # 默认启用的功能
            Feature.DIAGNOSTICS.value: True,
            Feature.EXPORT_HISTORY.value: True,
            Feature.REPLAY_RUN.value: True,
            Feature.SELF_REPAIR.value: True,
            Feature.BATCH_TASKS.value: True,
            Feature.WORKFLOW_ENGINE.value: True,
            
            # 默认禁用的功能（需要特定环境）
            Feature.PLATFORM_SCHEDULING.value: False,
            Feature.ADVANCED_RETRY.value: True,
            Feature.CHECKPOINT_RECOVERY.value: True,
        }
    
    def is_enabled(self, feature: Feature) -> bool:
        """检查功能是否启用"""
        return self._flags.get(feature.value, False)
    
    def enable(self, feature: Feature) -> None:
        """启用功能"""
        self._flags[feature.value] = True
    
    def disable(self, feature: Feature) -> None:
        """禁用功能"""
        self._flags[feature.value] = False
    
    def set(self, feature: Feature, enabled: bool) -> None:
        """设置功能状态"""
        self._flags[feature.value] = enabled
    
    def get_all(self) -> Dict[str, bool]:
        """获取所有功能状态"""
        return dict(self._flags)
    
    def update_from_config(self, config: Dict[str, Any]) -> None:
        """从配置更新"""
        for key, value in config.items():
            if key in self._flags and isinstance(value, bool):
                self._flags[key] = value
    
    def auto_configure(self) -> None:
        """自动配置（根据运行环境）"""
        from platform_adapter.runtime_probe import RuntimeProbe
        env = RuntimeProbe.detect_environment()
        
        # 根据环境自动启用/禁用功能
        if env.get("is_xiaoyi"):
            self.enable(Feature.PLATFORM_SCHEDULING)
        
        if env.get("has_database") and env.get("has_redis"):
            self.enable(Feature.ADVANCED_RETRY)
            self.enable(Feature.CHECKPOINT_RECOVERY)


# 全局实例
_global_flags: Optional[FeatureFlags] = None


def get_feature_flags() -> FeatureFlags:
    """获取全局功能开关"""
    global _global_flags
    if _global_flags is None:
        _global_flags = FeatureFlags()
        _global_flags.auto_configure()
    return _global_flags
