"""Skill lifecycle management."""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import os


class LifecycleState(Enum):
    EXPERIMENTAL = "experimental"
    BETA = "beta"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


@dataclass
class LifecycleEvent:
    """Event in skill lifecycle."""
    skill_id: str
    event_type: str
    from_state: LifecycleState
    to_state: LifecycleState
    reason: str
    timestamp: datetime
    metadata: Dict = None


class LifecycleManager:
    """
    Manages skill lifecycle from experimental to retired.
    
    Lifecycle stages:
    1. experimental - New skill, limited usage
    2. beta - Testing phase, broader usage
    3. stable - Production ready
    4. deprecated - Scheduled for removal
    5. retired - No longer available
    """
    
    def __init__(self, registry=None, history_path: str = "skills/registry/lifecycle_history.json"):
        self.registry = registry
        self.history_path = history_path
        self._history: List[LifecycleEvent] = []
        self._load_history()
    
    def _load_history(self):
        """Load lifecycle history."""
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r') as f:
                    data = json.load(f)
                    for event_data in data.get("events", []):
                        self._history.append(LifecycleEvent(
                            skill_id=event_data["skill_id"],
                            event_type=event_data["event_type"],
                            from_state=LifecycleState(event_data["from_state"]),
                            to_state=LifecycleState(event_data["to_state"]),
                            reason=event_data["reason"],
                            timestamp=datetime.fromisoformat(event_data["timestamp"]),
                            metadata=event_data.get("metadata")
                        ))
            except Exception as e:
                print(f"Warning: Failed to load lifecycle history: {e}")
    
    def _save_history(self):
        """Save lifecycle history."""
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        data = {
            "events": [
                {
                    "skill_id": e.skill_id,
                    "event_type": e.event_type,
                    "from_state": e.from_state.value,
                    "to_state": e.to_state.value,
                    "reason": e.reason,
                    "timestamp": e.timestamp.isoformat(),
                    "metadata": e.metadata
                }
                for e in self._history
            ]
        }
        with open(self.history_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def promote(self, skill_id: str, reason: str = "") -> bool:
        """Promote skill to next lifecycle stage."""
        manifest = self._get_manifest(skill_id)
        if not manifest:
            return False
        
        current = self._get_lifecycle_state(manifest)
        next_state = self._get_next_state(current)
        
        if not next_state:
            return False
        
        return self._transition(skill_id, current, next_state, "promote", reason)
    
    def deprecate(self, skill_id: str, reason: str, deprecation_period_days: int = 90) -> bool:
        """Deprecate a skill."""
        manifest = self._get_manifest(skill_id)
        if not manifest:
            return False
        
        current = self._get_lifecycle_state(manifest)
        
        if current == LifecycleState.DEPRECATED or current == LifecycleState.RETIRED:
            return False
        
        # Set deprecation metadata
        if manifest:
            manifest.metadata["deprecation_date"] = datetime.now().isoformat()
            manifest.metadata["removal_date"] = (datetime.now() + timedelta(days=deprecation_period_days)).isoformat()
            manifest.metadata["deprecation_reason"] = reason
        
        return self._transition(skill_id, current, LifecycleState.DEPRECATED, "deprecate", reason)
    
    def retire(self, skill_id: str, reason: str = "") -> bool:
        """Retire a deprecated skill."""
        manifest = self._get_manifest(skill_id)
        if not manifest:
            return False
        
        current = self._get_lifecycle_state(manifest)
        
        if current != LifecycleState.DEPRECATED:
            return False
        
        return self._transition(skill_id, current, LifecycleState.RETIRED, "retire", reason)
    
    def rollback(self, skill_id: str, reason: str = "") -> bool:
        """Rollback to previous lifecycle state."""
        # Find last event for this skill
        skill_events = [e for e in self._history if e.skill_id == skill_id]
        if not skill_events:
            return False
        
        last_event = skill_events[-1]
        
        return self._transition(
            skill_id,
            last_event.to_state,
            last_event.from_state,
            "rollback",
            reason
        )
    
    def _transition(
        self,
        skill_id: str,
        from_state: LifecycleState,
        to_state: LifecycleState,
        event_type: str,
        reason: str
    ) -> bool:
        """Execute a lifecycle transition."""
        # Update manifest
        manifest = self._get_manifest(skill_id)
        if manifest:
            manifest.metadata["lifecycle_state"] = to_state.value
            manifest.updated_at = datetime.now()
        
        # Record event
        event = LifecycleEvent(
            skill_id=skill_id,
            event_type=event_type,
            from_state=from_state,
            to_state=to_state,
            reason=reason,
            timestamp=datetime.now()
        )
        self._history.append(event)
        self._save_history()
        
        return True
    
    def _get_manifest(self, skill_id: str):
        """Get skill manifest."""
        if not self.registry:
            return None
        return self.registry.get(skill_id)
    
    def _get_lifecycle_state(self, manifest) -> LifecycleState:
        """Get lifecycle state from manifest."""
        state_value = manifest.metadata.get("lifecycle_state", "stable")
        return LifecycleState(state_value)
    
    def _get_next_state(self, current: LifecycleState) -> Optional[LifecycleState]:
        """Get next lifecycle state."""
        transitions = {
            LifecycleState.EXPERIMENTAL: LifecycleState.BETA,
            LifecycleState.BETA: LifecycleState.STABLE,
            LifecycleState.STABLE: None,
            LifecycleState.DEPRECATED: None,
            LifecycleState.RETIRED: None
        }
        return transitions.get(current)
    
    def get_deprecated_skills(self) -> List[str]:
        """Get all deprecated skills."""
        deprecated = []
        if self.registry:
            for manifest in self.registry.list_all():
                state = self._get_lifecycle_state(manifest)
                if state == LifecycleState.DEPRECATED:
                    deprecated.append(manifest.skill_id)
        return deprecated
    
    def get_expiring_skills(self, days: int = 30) -> List[Dict]:
        """Get skills expiring within N days."""
        expiring = []
        if self.registry:
            for manifest in self.registry.list_all():
                state = self._get_lifecycle_state(manifest)
                if state == LifecycleState.DEPRECATED:
                    removal_date = manifest.metadata.get("removal_date")
                    if removal_date:
                        removal = datetime.fromisoformat(removal_date)
                        if removal <= datetime.now() + timedelta(days=days):
                            expiring.append({
                                "skill_id": manifest.skill_id,
                                "removal_date": removal_date,
                                "reason": manifest.metadata.get("deprecation_reason", "")
                            })
        return expiring
    
    def get_history(self, skill_id: str = None) -> List[LifecycleEvent]:
        """Get lifecycle history."""
        if skill_id:
            return [e for e in self._history if e.skill_id == skill_id]
        return self._history
