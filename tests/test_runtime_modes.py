"""测试运行模式"""
import pytest
from config.runtime_modes import RuntimeMode, get_runtime_mode_config


def test_runtime_mode_values():
    """测试运行模式值"""
    assert RuntimeMode.DRY_RUN.value == "dry_run"
    assert RuntimeMode.FAKE_DEVICE.value == "fake_device"
    assert RuntimeMode.PROBE_ONLY.value == "probe_only"
    assert RuntimeMode.CONNECTED_RUNTIME.value == "connected_runtime"


def test_get_runtime_mode_config():
    """测试获取模式配置"""
    config = get_runtime_mode_config(RuntimeMode.DRY_RUN)
    assert config is not None
    assert config.allow_side_effects is False
    assert config.require_device is False


def test_probe_only_config():
    """测试 probe_only 模式配置"""
    config = get_runtime_mode_config(RuntimeMode.PROBE_ONLY)
    assert config.allow_side_effects is False
    assert config.require_device is True
    assert config.allow_screen_read is True


def test_connected_runtime_config():
    """测试 connected_runtime 模式配置"""
    config = get_runtime_mode_config(RuntimeMode.CONNECTED_RUNTIME)
    assert config.allow_side_effects is True
    assert config.require_device is True
    assert config.enforce_safety_governor is True


def test_mode_definitions():
    """测试模式定义完整性"""
    for mode in RuntimeMode:
        config = get_runtime_mode_config(mode)
        assert config is not None
        assert hasattr(config, "allow_side_effects")
        assert hasattr(config, "require_device")
