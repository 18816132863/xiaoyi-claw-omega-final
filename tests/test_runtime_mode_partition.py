"""
Test Runtime Mode Partition

Verifies that runtime modes are properly partitioned and isolated.
"""

import pytest
import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.runtime_modes import (
    RuntimeMode,
    get_runtime_mode_config,
    is_side_effect_allowed,
    is_probe_only,
    requires_device,
)


class TestRuntimeModePartition:
    """Test runtime mode partitioning."""
    
    def test_dry_run_no_side_effects(self):
        """Dry run should not allow side effects."""
        assert not is_side_effect_allowed(RuntimeMode.DRY_RUN, "click")
        assert not is_side_effect_allowed(RuntimeMode.DRY_RUN, "type")
        assert not is_side_effect_allowed(RuntimeMode.DRY_RUN, "delete")
        assert not is_side_effect_allowed(RuntimeMode.DRY_RUN, "send")
        assert not is_side_effect_allowed(RuntimeMode.DRY_RUN, "call")
    
    def test_fake_device_no_side_effects(self):
        """Fake device should not allow side effects."""
        assert not is_side_effect_allowed(RuntimeMode.FAKE_DEVICE, "click")
        assert not is_side_effect_allowed(RuntimeMode.FAKE_DEVICE, "type")
        assert not is_side_effect_allowed(RuntimeMode.FAKE_DEVICE, "delete")
        assert not is_side_effect_allowed(RuntimeMode.FAKE_DEVICE, "send")
        assert not is_side_effect_allowed(RuntimeMode.FAKE_DEVICE, "call")
    
    def test_probe_only_no_side_effects(self):
        """Probe only should not allow side effects."""
        assert not is_side_effect_allowed(RuntimeMode.PROBE_ONLY, "click")
        assert not is_side_effect_allowed(RuntimeMode.PROBE_ONLY, "type")
        assert not is_side_effect_allowed(RuntimeMode.PROBE_ONLY, "delete")
        assert not is_side_effect_allowed(RuntimeMode.PROBE_ONLY, "send")
        assert not is_side_effect_allowed(RuntimeMode.PROBE_ONLY, "call")
    
    def test_connected_runtime_allows_side_effects(self):
        """Connected runtime should allow side effects."""
        config = get_runtime_mode_config(RuntimeMode.CONNECTED_RUNTIME)
        assert config.allow_side_effects is True
        assert config.allow_click is True
        assert config.allow_type is True
        assert config.allow_delete is True
        assert config.allow_send is True
        assert config.allow_call is True
    
    def test_dry_run_does_not_require_device(self):
        """Dry run should not require device."""
        assert not requires_device(RuntimeMode.DRY_RUN)
    
    def test_fake_device_does_not_require_device(self):
        """Fake device should not require device."""
        assert not requires_device(RuntimeMode.FAKE_DEVICE)
    
    def test_probe_only_requires_device(self):
        """Probe only should require device."""
        assert requires_device(RuntimeMode.PROBE_ONLY)
    
    def test_connected_runtime_requires_device(self):
        """Connected runtime should require device."""
        assert requires_device(RuntimeMode.CONNECTED_RUNTIME)
    
    def test_is_probe_only_identifies_probe_only(self):
        """is_probe_only should correctly identify probe_only mode."""
        assert is_probe_only(RuntimeMode.PROBE_ONLY) is True
        assert is_probe_only(RuntimeMode.DRY_RUN) is False
        assert is_probe_only(RuntimeMode.FAKE_DEVICE) is False
        assert is_probe_only(RuntimeMode.CONNECTED_RUNTIME) is False
    
    def test_probe_only_allows_screen_read(self):
        """Probe only should allow screen reading."""
        config = get_runtime_mode_config(RuntimeMode.PROBE_ONLY)
        assert config.allow_screen_read is True
    
    def test_connected_runtime_enforces_safety_governor(self):
        """Connected runtime should enforce safety governor."""
        config = get_runtime_mode_config(RuntimeMode.CONNECTED_RUNTIME)
        assert config.enforce_safety_governor is True


class TestRuntimeModeConfig:
    """Test runtime mode configuration."""
    
    def test_all_modes_have_configs(self):
        """All runtime modes should have configurations."""
        for mode in RuntimeMode:
            config = get_runtime_mode_config(mode)
            assert config is not None
            assert hasattr(config, "allow_side_effects")
            assert hasattr(config, "require_device")
    
    def test_mode_values_are_strings(self):
        """Runtime mode values should be strings."""
        assert RuntimeMode.DRY_RUN.value == "dry_run"
        assert RuntimeMode.FAKE_DEVICE.value == "fake_device"
        assert RuntimeMode.PROBE_ONLY.value == "probe_only"
        assert RuntimeMode.CONNECTED_RUNTIME.value == "connected_runtime"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
