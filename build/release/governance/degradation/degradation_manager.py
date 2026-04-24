"""Degradation manager - handles system degradation and fallback modes."""

from typing import Dict, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os


class DegradationLevel(Enum):
    NORMAL = "normal"
    DEGRADED = "degraded"
    MINIMAL = "minimal"
    EMERGENCY = "emergency"


class DegradationTrigger(Enum):
    BUDGET_EXCEEDED = "budget_exceeded"
    HIGH_ERROR_RATE = "high_error_rate"
    PERFORMANCE_ISSUE = "performance_issue"
    EXTERNAL_FAILURE = "external_failure"
    MANUAL = "manual"
    SCHEDULED = "scheduled"


@dataclass
class DegradationState:
    """Current degradation state."""
    level: DegradationLevel
    triggers: List[str]
    disabled_features: List[str]
    fallback_modes: Dict[str, str]
    started_at: datetime
    expected_recovery: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class KillSwitch:
    """Kill switch for emergency shutdown."""
    switch_id: str
    target: str  # skill_id, feature, or "all"
    reason: str
    activated_at: datetime
    activated_by: str
    auto_recover_at: Optional[datetime] = None


class DegradationManager:
    """
    Manages system degradation and fallback modes.
    
    Features:
    - Graceful degradation under load/failure
    - Kill switches for emergency shutdown
    - Automatic recovery
    - Fallback mode policies
    """
    
    def __init__(self, state_path: str = "governance/degradation/state.json"):
        self.state_path = state_path
        self._state = DegradationState(
            level=DegradationLevel.NORMAL,
            triggers=[],
            disabled_features=[],
            fallback_modes={},
            started_at=datetime.now()
        )
        self._kill_switches: Dict[str, KillSwitch] = {}
        self._fallback_handlers: Dict[str, Callable] = {}
        self._recovery_handlers: Dict[str, Callable] = {}
        self._load()
    
    def _load(self):
        """Load state from file."""
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, 'r') as f:
                    data = json.load(f)
                    self._state = DegradationState(
                        level=DegradationLevel(data.get("level", "normal")),
                        triggers=data.get("triggers", []),
                        disabled_features=data.get("disabled_features", []),
                        fallback_modes=data.get("fallback_modes", {}),
                        started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else datetime.now(),
                        expected_recovery=datetime.fromisoformat(data["expected_recovery"]) if data.get("expected_recovery") else None,
                        metadata=data.get("metadata", {})
                    )
            except Exception as e:
                print(f"Warning: Failed to load degradation state: {e}")
    
    def _save(self):
        """Save state to file."""
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        data = {
            "level": self._state.level.value,
            "triggers": self._state.triggers,
            "disabled_features": self._state.disabled_features,
            "fallback_modes": self._state.fallback_modes,
            "started_at": self._state.started_at.isoformat(),
            "expected_recovery": self._state.expected_recovery.isoformat() if self._state.expected_recovery else None,
            "metadata": self._state.metadata
        }
        with open(self.state_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def degrade(
        self,
        trigger: DegradationTrigger,
        target_level: DegradationLevel = None,
        reason: str = "",
        disable_features: List[str] = None,
        fallback_modes: Dict[str, str] = None,
        recovery_timeout_minutes: int = None
    ) -> bool:
        """
        Trigger degradation.
        
        Args:
            trigger: What triggered the degradation
            target_level: Target degradation level (auto if None)
            reason: Human-readable reason
            disable_features: Features to disable
            fallback_modes: Fallback modes to activate
            recovery_timeout_minutes: Auto-recovery timeout
        
        Returns:
            True if degradation was applied
        """
        # Determine target level
        if target_level is None:
            target_level = self._calculate_level(trigger)
        
        # Don't downgrade
        level_order = [DegradationLevel.NORMAL, DegradationLevel.DEGRADED, DegradationLevel.MINIMAL, DegradationLevel.EMERGENCY]
        current_idx = level_order.index(self._state.level)
        target_idx = level_order.index(target_level)
        
        if target_idx <= current_idx:
            return False
        
        # Apply degradation
        self._state.level = target_level
        self._state.triggers.append(trigger.value)
        
        if disable_features:
            self._state.disabled_features.extend(disable_features)
        
        if fallback_modes:
            self._state.fallback_modes.update(fallback_modes)
        
        if recovery_timeout_minutes:
            self._state.expected_recovery = datetime.now() + timedelta(minutes=recovery_timeout_minutes)
        
        self._state.metadata["last_reason"] = reason
        self._save()
        
        # Execute fallback handlers
        for feature, mode in (fallback_modes or {}).items():
            handler = self._fallback_handlers.get(feature)
            if handler:
                try:
                    handler(mode)
                except Exception as e:
                    print(f"Warning: Fallback handler failed for {feature}: {e}")
        
        return True
    
    def recover(self, reason: str = "") -> bool:
        """
        Recover from degradation.
        
        Returns:
            True if recovery was successful
        """
        if self._state.level == DegradationLevel.NORMAL:
            return False
        
        # Execute recovery handlers
        for feature in self._state.disabled_features:
            handler = self._recovery_handlers.get(feature)
            if handler:
                try:
                    handler()
                except Exception as e:
                    print(f"Warning: Recovery handler failed for {feature}: {e}")
        
        # Reset state
        self._state = DegradationState(
            level=DegradationLevel.NORMAL,
            triggers=[],
            disabled_features=[],
            fallback_modes={},
            started_at=datetime.now(),
            metadata={"recovery_reason": reason}
        )
        self._save()
        
        return True
    
    def activate_kill_switch(
        self,
        target: str,
        reason: str,
        activated_by: str = "system",
        auto_recover_minutes: int = None
    ) -> str:
        """
        Activate a kill switch.
        
        Args:
            target: What to kill (skill_id, feature, or "all")
            reason: Why the kill switch is activated
            activated_by: Who activated it
            auto_recover_minutes: Auto-recovery timeout
        
        Returns:
            Kill switch ID
        """
        switch_id = f"kill_{target}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        switch = KillSwitch(
            switch_id=switch_id,
            target=target,
            reason=reason,
            activated_at=datetime.now(),
            activated_by=activated_by,
            auto_recover_at=datetime.now() + timedelta(minutes=auto_recover_minutes) if auto_recover_minutes else None
        )
        
        self._kill_switches[switch_id] = switch
        
        # Apply immediately
        if target == "all":
            self.degrade(
                trigger=DegradationTrigger.MANUAL,
                target_level=DegradationLevel.EMERGENCY,
                reason=f"Kill switch activated: {reason}"
            )
        else:
            if target not in self._state.disabled_features:
                self._state.disabled_features.append(target)
                self._save()
        
        return switch_id
    
    def deactivate_kill_switch(self, switch_id: str) -> bool:
        """Deactivate a kill switch."""
        if switch_id not in self._kill_switches:
            return False
        
        switch = self._kill_switches[switch_id]
        target = switch.target
        
        # Remove from disabled features
        if target in self._state.disabled_features:
            self._state.disabled_features.remove(target)
            self._save()
        
        del self._kill_switches[switch_id]
        return True
    
    def is_feature_available(self, feature: str) -> bool:
        """Check if a feature is available."""
        # Check kill switches
        for switch in self._kill_switches.values():
            if switch.target == feature or switch.target == "all":
                return False
        
        # Check disabled features
        if feature in self._state.disabled_features:
            return False
        
        return True
    
    def get_fallback_mode(self, feature: str) -> Optional[str]:
        """Get fallback mode for a feature."""
        return self._state.fallback_modes.get(feature)
    
    def register_fallback_handler(self, feature: str, handler: Callable):
        """Register a fallback handler for a feature."""
        self._fallback_handlers[feature] = handler
    
    def register_recovery_handler(self, feature: str, handler: Callable):
        """Register a recovery handler for a feature."""
        self._recovery_handlers[feature] = handler
    
    def _calculate_level(self, trigger: DegradationTrigger) -> DegradationLevel:
        """Calculate degradation level from trigger."""
        level_map = {
            DegradationTrigger.BUDGET_EXCEEDED: DegradationLevel.DEGRADED,
            DegradationTrigger.HIGH_ERROR_RATE: DegradationLevel.DEGRADED,
            DegradationTrigger.PERFORMANCE_ISSUE: DegradationLevel.DEGRADED,
            DegradationTrigger.EXTERNAL_FAILURE: DegradationLevel.MINIMAL,
            DegradationTrigger.MANUAL: DegradationLevel.EMERGENCY,
            DegradationTrigger.SCHEDULED: DegradationLevel.DEGRADED
        }
        return level_map.get(trigger, DegradationLevel.DEGRADED)
    
    def get_state(self) -> DegradationState:
        """Get current degradation state."""
        return self._state
    
    def get_kill_switches(self, active_only: bool = True) -> List[KillSwitch]:
        """Get kill switches."""
        switches = list(self._kill_switches.values())
        
        if active_only:
            # Filter out auto-recovered
            now = datetime.now()
            switches = [s for s in switches if not s.auto_recover_at or s.auto_recover_at > now]
        
        return switches
    
    def check_auto_recovery(self) -> List[str]:
        """Check and apply auto-recovery."""
        recovered = []
        now = datetime.now()
        
        # Check expected recovery
        if self._state.expected_recovery and now >= self._state.expected_recovery:
            self.recover("Auto-recovery timeout")
            recovered.append("system")
        
        # Check kill switches
        for switch_id, switch in list(self._kill_switches.items()):
            if switch.auto_recover_at and now >= switch.auto_recover_at:
                self.deactivate_kill_switch(switch_id)
                recovered.append(switch.target)
        
        return recovered
