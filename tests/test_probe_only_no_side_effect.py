"""
Test Probe Only No Side Effect

Verifies that probe_only mode produces no side effects.
"""

import pytest
import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.runtime_modes import RuntimeMode, is_side_effect_allowed


class TestProbeOnlyNoSideEffect:
    """Test that probe_only mode produces no side effects."""
    
    def test_probe_only_blocks_click(self):
        """Probe only should block click."""
        assert is_side_effect_allowed(RuntimeMode.PROBE_ONLY, "click") is False
    
    def test_probe_only_blocks_type(self):
        """Probe only should block type."""
        assert is_side_effect_allowed(RuntimeMode.PROBE_ONLY, "type") is False
    
    def test_probe_only_blocks_delete(self):
        """Probe only should block delete."""
        assert is_side_effect_allowed(RuntimeMode.PROBE_ONLY, "delete") is False
    
    def test_probe_only_blocks_send(self):
        """Probe only should block send."""
        assert is_side_effect_allowed(RuntimeMode.PROBE_ONLY, "send") is False
    
    def test_probe_only_blocks_call(self):
        """Probe only should block call."""
        assert is_side_effect_allowed(RuntimeMode.PROBE_ONLY, "call") is False
    
    def test_probe_only_config_no_side_effects(self):
        """Probe only config should have all side effects disabled."""
        from config.runtime_modes import get_runtime_mode_config
        
        config = get_runtime_mode_config(RuntimeMode.PROBE_ONLY)
        
        assert config.allow_side_effects is False
        assert config.allow_click is False
        assert config.allow_type is False
        assert config.allow_delete is False
        assert config.allow_send is False
        assert config.allow_call is False
    
    def test_probe_only_allows_screen_read(self):
        """Probe only should allow screen reading."""
        from config.runtime_modes import get_runtime_mode_config
        
        config = get_runtime_mode_config(RuntimeMode.PROBE_ONLY)
        assert config.allow_screen_read is True
    
    def test_unknown_action_blocked(self):
        """Unknown actions should be blocked."""
        assert is_side_effect_allowed(RuntimeMode.PROBE_ONLY, "unknown") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
