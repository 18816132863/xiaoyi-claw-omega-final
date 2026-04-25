"""
Safety Governor Runtime Gate

Enforces safety policies for connected runtime execution.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ConfirmationType(str, Enum):
    """Types of confirmation required."""
    NONE = "none"
    OPTIONAL = "optional"
    CONFIRM_ONCE = "confirm_once"
    STRONG_CONFIRM = "strong_confirm"


@dataclass
class RuntimeGateResult:
    """Result of runtime gate check."""
    allowed: bool
    risk_level: str
    policy: str
    confirmation_type: ConfirmationType
    confirmation_id: Optional[str]
    blocked_reason: Optional[str]
    requires_preview: bool
    requires_stepwise: bool


class RuntimeGate:
    """Safety gate for connected runtime execution."""
    
    RISK_POLICIES = {
        "L0": {
            "auto_execute": True,
            "confirmation_type": ConfirmationType.NONE,
            "requires_preview": False,
            "requires_stepwise": False,
        },
        "L1": {
            "auto_execute": True,
            "confirmation_type": ConfirmationType.NONE,
            "requires_preview": False,
            "requires_stepwise": False,
        },
        "L2": {
            "auto_execute": True,
            "confirmation_type": ConfirmationType.OPTIONAL,
            "requires_preview": False,
            "requires_stepwise": False,
        },
        "L3": {
            "auto_execute": False,
            "confirmation_type": ConfirmationType.CONFIRM_ONCE,
            "requires_preview": False,
            "requires_stepwise": False,
        },
        "L4": {
            "auto_execute": False,
            "confirmation_type": ConfirmationType.STRONG_CONFIRM,
            "requires_preview": True,
            "requires_stepwise": True,
        },
        "BLOCKED": {
            "auto_execute": False,
            "confirmation_type": ConfirmationType.NONE,
            "requires_preview": False,
            "requires_stepwise": False,
            "blocked": True,
        },
    }
    
    def __init__(self):
        self.confirmation_sessions = {}
    
    def check(
        self,
        route_id: str,
        risk_level: str,
        policy: str,
        runtime_mode: str,
        probe_only: bool = False,
        confirmation_id: Optional[str] = None,
    ) -> RuntimeGateResult:
        """Check if execution is allowed."""
        
        # Get risk policy
        risk_policy = self.RISK_POLICIES.get(risk_level, self.RISK_POLICIES["L0"])
        
        # BLOCKED always blocked
        if risk_level == "BLOCKED" or risk_policy.get("blocked"):
            return RuntimeGateResult(
                allowed=False,
                risk_level=risk_level,
                policy=policy,
                confirmation_type=ConfirmationType.NONE,
                confirmation_id=None,
                blocked_reason="Route is BLOCKED",
                requires_preview=False,
                requires_stepwise=False,
            )
        
        # probe_only blocks all side effects
        if probe_only:
            return RuntimeGateResult(
                allowed=False,
                risk_level=risk_level,
                policy=policy,
                confirmation_type=risk_policy["confirmation_type"],
                confirmation_id=None,
                blocked_reason="probe_only blocks side effects",
                requires_preview=False,
                requires_stepwise=False,
            )
        
        # Check confirmation requirements
        confirmation_type = risk_policy["confirmation_type"]
        
        if confirmation_type == ConfirmationType.NONE:
            # No confirmation required
            return RuntimeGateResult(
                allowed=True,
                risk_level=risk_level,
                policy=policy,
                confirmation_type=confirmation_type,
                confirmation_id=None,
                blocked_reason=None,
                requires_preview=risk_policy["requires_preview"],
                requires_stepwise=risk_policy["requires_stepwise"],
            )
        
        if confirmation_type == ConfirmationType.OPTIONAL:
            # Optional confirmation
            return RuntimeGateResult(
                allowed=True,
                risk_level=risk_level,
                policy=policy,
                confirmation_type=confirmation_type,
                confirmation_id=confirmation_id,
                blocked_reason=None,
                requires_preview=risk_policy["requires_preview"],
                requires_stepwise=risk_policy["requires_stepwise"],
            )
        
        if confirmation_type in (ConfirmationType.CONFIRM_ONCE, ConfirmationType.STRONG_CONFIRM):
            # Requires confirmation
            if confirmation_id and self._validate_confirmation(confirmation_id, route_id):
                return RuntimeGateResult(
                    allowed=True,
                    risk_level=risk_level,
                    policy=policy,
                    confirmation_type=confirmation_type,
                    confirmation_id=confirmation_id,
                    blocked_reason=None,
                    requires_preview=risk_policy["requires_preview"],
                    requires_stepwise=risk_policy["requires_stepwise"],
                )
            else:
                return RuntimeGateResult(
                    allowed=False,
                    risk_level=risk_level,
                    policy=policy,
                    confirmation_type=confirmation_type,
                    confirmation_id=None,
                    blocked_reason=f"{risk_level} requires {confirmation_type.value}",
                    requires_preview=risk_policy["requires_preview"],
                    requires_stepwise=risk_policy["requires_stepwise"],
                )
        
        # Default: blocked
        return RuntimeGateResult(
            allowed=False,
            risk_level=risk_level,
            policy=policy,
            confirmation_type=confirmation_type,
            confirmation_id=None,
            blocked_reason="Unknown policy",
            requires_preview=False,
            requires_stepwise=False,
        )
    
    def _validate_confirmation(self, confirmation_id: str, route_id: str) -> bool:
        """Validate a confirmation session."""
        # In real implementation, would check database
        # For now, return False to indicate confirmation required
        return False
    
    def create_confirmation_session(self, route_id: str, confirmation_type: ConfirmationType) -> str:
        """Create a new confirmation session."""
        import uuid
        session_id = f"confirm_{uuid.uuid4().hex[:12]}"
        self.confirmation_sessions[session_id] = {
            "route_id": route_id,
            "confirmation_type": confirmation_type,
            "confirmed": False,
        }
        return session_id
