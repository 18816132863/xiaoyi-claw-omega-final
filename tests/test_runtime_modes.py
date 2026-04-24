"""测试运行模式"""
import pytest
from config.runtime_modes import RuntimeModes, RuntimeMode


def test_get_current_mode():
    """测试获取当前模式"""
    mode = RuntimeModes.get_current_mode()
    assert mode in [RuntimeMode.SKILL_DEFAULT, RuntimeMode.PLATFORM_ENHANCED, RuntimeMode.SELF_HOSTED_ENHANCED]


def test_get_capabilities():
    """测试获取模式能力"""
    caps = RuntimeModes.get_capabilities(RuntimeMode.SKILL_DEFAULT)
    assert caps is not None
    assert caps.mode == RuntimeMode.SKILL_DEFAULT
    assert caps.features.get("sqlite_storage") == True


def test_is_feature_available():
    """测试功能可用性检查"""
    # 默认模式应该有 sqlite_storage
    assert RuntimeModes.is_feature_available("sqlite_storage", RuntimeMode.SKILL_DEFAULT) == True
    
    # 默认模式不应该有 platform_scheduling
    assert RuntimeModes.is_feature_available("platform_scheduling", RuntimeMode.SKILL_DEFAULT) == False


def test_mode_definitions():
    """测试模式定义完整性"""
    for mode in RuntimeMode:
        caps = RuntimeModes.get_capabilities(mode)
        assert caps is not None
        assert caps.description is not None
        assert isinstance(caps.features, dict)
