"""Profile state contract - execution profile management."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum


class ProfileType(Enum):
    """Execution profile types."""
    DEFAULT = "default"
    DEVELOPER = "developer"
    OPERATOR = "operator"
    AUDITOR = "auditor"
    ADMIN = "admin"
    RESTRICTED = "restricted"


@dataclass
class ProfileCapabilities:
    """Capabilities granted by a profile."""
    can_read: bool = True
    can_write: bool = True
    can_execute: bool = True
    can_network: bool = True
    can_admin: bool = False
    max_token_budget: int = 8000
    max_execution_time_seconds: int = 300
    allowed_skill_categories: List[str] = field(default_factory=lambda: ["*"])
    denied_skills: List[str] = field(default_factory=list)
    requires_approval_for: List[str] = field(default_factory=list)


@dataclass
class ProfileState:
    """
    Profile state contract.
    
    Represents an execution profile configuration.
    """
    profile_id: str
    profile_type: ProfileType = ProfileType.DEFAULT
    capabilities: ProfileCapabilities = field(default_factory=ProfileCapabilities)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "profile_id": self.profile_id,
            "profile_type": self.profile_type.value,
            "capabilities": {
                "can_read": self.capabilities.can_read,
                "can_write": self.capabilities.can_write,
                "can_execute": self.capabilities.can_execute,
                "can_network": self.capabilities.can_network,
                "can_admin": self.capabilities.can_admin,
                "max_token_budget": self.capabilities.max_token_budget,
                "max_execution_time_seconds": self.capabilities.max_execution_time_seconds,
                "allowed_skill_categories": self.capabilities.allowed_skill_categories,
                "denied_skills": self.capabilities.denied_skills,
                "requires_approval_for": self.capabilities.requires_approval_for
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProfileState":
        caps_data = data.get("capabilities", {})
        capabilities = ProfileCapabilities(
            can_read=caps_data.get("can_read", True),
            can_write=caps_data.get("can_write", True),
            can_execute=caps_data.get("can_execute", True),
            can_network=caps_data.get("can_network", True),
            can_admin=caps_data.get("can_admin", False),
            max_token_budget=caps_data.get("max_token_budget", 8000),
            max_execution_time_seconds=caps_data.get("max_execution_time_seconds", 300),
            allowed_skill_categories=caps_data.get("allowed_skill_categories", ["*"]),
            denied_skills=caps_data.get("denied_skills", []),
            requires_approval_for=caps_data.get("requires_approval_for", [])
        )
        return cls(
            profile_id=data["profile_id"],
            profile_type=ProfileType(data.get("profile_type", "default")),
            capabilities=capabilities,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(),
            metadata=data.get("metadata", {})
        )


# Pre-defined profiles
DEFAULT_PROFILES = {
    "default": ProfileState(
        profile_id="default",
        profile_type=ProfileType.DEFAULT,
        capabilities=ProfileCapabilities()
    ),
    "developer": ProfileState(
        profile_id="developer",
        profile_type=ProfileType.DEVELOPER,
        capabilities=ProfileCapabilities(
            can_write=True,
            can_execute=True,
            max_token_budget=16000,
            allowed_skill_categories=["code", "git", "docker", "utility", "search"]
        )
    ),
    "operator": ProfileState(
        profile_id="operator",
        profile_type=ProfileType.OPERATOR,
        capabilities=ProfileCapabilities(
            can_write=False,
            can_execute=True,
            max_token_budget=8000,
            allowed_skill_categories=["search", "document", "data"]
        )
    ),
    "auditor": ProfileState(
        profile_id="auditor",
        profile_type=ProfileType.AUDITOR,
        capabilities=ProfileCapabilities(
            can_read=True,
            can_write=False,
            can_execute=False,
            max_token_budget=4000,
            allowed_skill_categories=["search", "document"]
        )
    ),
    "admin": ProfileState(
        profile_id="admin",
        profile_type=ProfileType.ADMIN,
        capabilities=ProfileCapabilities(
            can_admin=True,
            max_token_budget=32000,
            allowed_skill_categories=["*"]
        )
    ),
    "restricted": ProfileState(
        profile_id="restricted",
        profile_type=ProfileType.RESTRICTED,
        capabilities=ProfileCapabilities(
            can_read=True,
            can_write=False,
            can_execute=False,
            can_network=False,
            max_token_budget=2000,
            allowed_skill_categories=["utility"]
        )
    )
}


class ProfileStateContract:
    """
    Contract for profile state management.
    
    All profile operations must go through this contract.
    """
    
    def __init__(self):
        self._profiles: Dict[str, ProfileState] = {}
        self._load_default_profiles()
    
    def _load_default_profiles(self):
        """Load default profiles."""
        for profile_id, profile in DEFAULT_PROFILES.items():
            self._profiles[profile_id] = profile
    
    def get_profile(self, profile_id: str) -> Optional[ProfileState]:
        """Get profile by ID."""
        return self._profiles.get(profile_id)
    
    def get_default_profile(self) -> ProfileState:
        """Get the default profile."""
        return self._profiles["default"]
    
    def create_profile(
        self,
        profile_id: str,
        profile_type: ProfileType,
        capabilities: ProfileCapabilities = None
    ) -> ProfileState:
        """Create a new profile."""
        profile = ProfileState(
            profile_id=profile_id,
            profile_type=profile_type,
            capabilities=capabilities or ProfileCapabilities()
        )
        self._profiles[profile_id] = profile
        return profile
    
    def update_profile(self, profile_id: str, **kwargs) -> Optional[ProfileState]:
        """Update profile."""
        profile = self._profiles.get(profile_id)
        if not profile:
            return None
        
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.updated_at = datetime.now()
        return profile
    
    def check_capability(self, profile_id: str, capability: str) -> bool:
        """Check if profile has a capability."""
        profile = self._profiles.get(profile_id)
        if not profile:
            return False
        
        return getattr(profile.capabilities, capability, False)
    
    def is_skill_allowed(self, profile_id: str, skill_category: str, skill_id: str) -> bool:
        """Check if skill is allowed for profile."""
        profile = self._profiles.get(profile_id)
        if not profile:
            return False
        
        # Check denied list
        if skill_id in profile.capabilities.denied_skills:
            return False
        
        # Check allowed categories
        allowed = profile.capabilities.allowed_skill_categories
        if "*" in allowed:
            return True
        
        return skill_category in allowed
    
    def list_profiles(self) -> List[ProfileState]:
        """List all profiles."""
        return list(self._profiles.values())


# Global accessor
_profile_state_contract: Optional[ProfileStateContract] = None


def get_profile_state_contract() -> ProfileStateContract:
    """Get the profile state contract instance."""
    global _profile_state_contract
    if _profile_state_contract is None:
        _profile_state_contract = ProfileStateContract()
    return _profile_state_contract
