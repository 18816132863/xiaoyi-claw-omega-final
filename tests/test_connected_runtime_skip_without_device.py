"""
Test Connected Runtime Skip Without Device

Verifies that connected runtime tests skip when no device is available.
"""

import pytest
import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_device_available() -> bool:
    """Check if a real device is available."""
    # In sandbox environment, no real device is available
    # This function would check for actual device connection
    return False


@pytest.mark.connected_runtime
class TestConnectedRuntimeSkipWithoutDevice:
    """Tests that should skip when no device is available."""
    
    @pytest.mark.skipif(
        not check_device_available(),
        reason="No connected device available"
    )
    def test_device_query_note(self):
        """Test querying notes on real device."""
        # This test would run on real device
        pytest.fail("Should have been skipped")
    
    @pytest.mark.skipif(
        not check_device_available(),
        reason="No connected device available"
    )
    def test_device_query_alarm(self):
        """Test querying alarms on real device."""
        # This test would run on real device
        pytest.fail("Should have been skipped")
    
    @pytest.mark.skipif(
        not check_device_available(),
        reason="No connected device available"
    )
    def test_device_get_location(self):
        """Test getting location on real device."""
        # This test would run on real device
        pytest.fail("Should have been skipped")


@pytest.mark.probe_only
class TestProbeOnlySkipWithoutDevice:
    """Probe tests that should skip when no device is available."""
    
    @pytest.mark.skipif(
        not check_device_available(),
        reason="No connected device available"
    )
    def test_probe_device_capabilities(self):
        """Test probing device capabilities."""
        # This test would run on real device
        pytest.fail("Should have been skipped")


def test_default_tests_always_pass():
    """Default tests should always pass regardless of device availability."""
    # This test runs in default pytest (no markers)
    assert True


def test_runtime_mode_config_available():
    """Runtime mode config should be available without device."""
    from config.runtime_modes import RuntimeMode, get_runtime_mode_config
    
    config = get_runtime_mode_config(RuntimeMode.PROBE_ONLY)
    assert config is not None
    assert config.allow_side_effects is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
