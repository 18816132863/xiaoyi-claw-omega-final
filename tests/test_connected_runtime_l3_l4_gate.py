"""
Test Connected Runtime L3/L4 Gate

Verifies that L3/L4 routes cannot execute without confirmation.
"""

import pytest
import sys
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from safety_governor.runtime_gate import RuntimeGate, ConfirmationType


class TestL3L4Gate:
    """Test L3/L4 confirmation gates."""
    
    @pytest.fixture
    def gate(self):
        """Create runtime gate instance."""
        return RuntimeGate()
    
    def test_l0_allows_without_confirmation(self, gate):
        """L0 should allow execution without confirmation."""
        result = gate.check(
            route_id="route.query_note",
            risk_level="L0",
            policy="auto_execute",
            runtime_mode="connected_runtime",
            probe_only=False,
        )
        
        assert result.allowed is True
        assert result.confirmation_type == ConfirmationType.NONE
        assert result.blocked_reason is None
    
    def test_l1_allows_without_confirmation(self, gate):
        """L1 should allow execution without confirmation."""
        result = gate.check(
            route_id="route.search_notes",
            risk_level="L1",
            policy="auto_execute",
            runtime_mode="connected_runtime",
            probe_only=False,
        )
        
        assert result.allowed is True
        assert result.confirmation_type == ConfirmationType.NONE
    
    def test_l2_allows_with_optional_confirmation(self, gate):
        """L2 should allow execution with optional confirmation."""
        result = gate.check(
            route_id="route.create_alarm",
            risk_level="L2",
            policy="rate_limited",
            runtime_mode="connected_runtime",
            probe_only=False,
        )
        
        assert result.allowed is True
        assert result.confirmation_type == ConfirmationType.OPTIONAL
    
    def test_l3_blocks_without_confirmation(self, gate):
        """L3 should block execution without confirmation."""
        result = gate.check(
            route_id="route.send_message",
            risk_level="L3",
            policy="confirm_once",
            runtime_mode="connected_runtime",
            probe_only=False,
        )
        
        assert result.allowed is False
        assert result.confirmation_type == ConfirmationType.CONFIRM_ONCE
        assert "L3 requires confirm_once" in result.blocked_reason
    
    def test_l4_blocks_without_strong_confirm(self, gate):
        """L4 should block execution without strong confirmation."""
        result = gate.check(
            route_id="route.xiaoyi_gui_agent",
            risk_level="L4",
            policy="strong_confirm",
            runtime_mode="connected_runtime",
            probe_only=False,
        )
        
        assert result.allowed is False
        assert result.confirmation_type == ConfirmationType.STRONG_CONFIRM
        assert "L4 requires strong_confirm" in result.blocked_reason
        assert result.requires_preview is True
        assert result.requires_stepwise is True
    
    def test_blocked_always_blocked(self, gate):
        """BLOCKED routes should always be blocked."""
        result = gate.check(
            route_id="route.blocked_action",
            risk_level="BLOCKED",
            policy="blocked",
            runtime_mode="connected_runtime",
            probe_only=False,
        )
        
        assert result.allowed is False
        assert result.blocked_reason == "Route is BLOCKED"
    
    def test_probe_only_blocks_l3(self, gate):
        """Probe only should block L3 routes."""
        result = gate.check(
            route_id="route.send_message",
            risk_level="L3",
            policy="confirm_once",
            runtime_mode="probe_only",
            probe_only=True,
        )
        
        assert result.allowed is False
        assert "probe_only blocks side effects" in result.blocked_reason
    
    def test_probe_only_blocks_l4(self, gate):
        """Probe only should block L4 routes."""
        result = gate.check(
            route_id="route.xiaoyi_gui_agent",
            risk_level="L4",
            policy="strong_confirm",
            runtime_mode="probe_only",
            probe_only=True,
        )
        
        assert result.allowed is False
        assert "probe_only blocks side effects" in result.blocked_reason
    
    def test_l4_requires_preview(self, gate):
        """L4 should require preview."""
        result = gate.check(
            route_id="route.xiaoyi_gui_agent",
            risk_level="L4",
            policy="strong_confirm",
            runtime_mode="connected_runtime",
            probe_only=False,
        )
        
        assert result.requires_preview is True
    
    def test_l4_requires_stepwise(self, gate):
        """L4 should require stepwise execution."""
        result = gate.check(
            route_id="route.xiaoyi_gui_agent",
            risk_level="L4",
            policy="strong_confirm",
            runtime_mode="connected_runtime",
            probe_only=False,
        )
        
        assert result.requires_stepwise is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
