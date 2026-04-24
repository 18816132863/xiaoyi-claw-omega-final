from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class CanaryDecision:
    mode: str
    target: str
    percentage: int
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def profile_canary(profile: str, percentage: int = 10) -> CanaryDecision:
    return CanaryDecision(mode="profile", target=profile, percentage=percentage)

def workflow_canary(workflow_id: str, percentage: int = 10) -> CanaryDecision:
    return CanaryDecision(mode="workflow", target=workflow_id, percentage=percentage)

def capability_canary(capability: str, percentage: int = 10) -> CanaryDecision:
    return CanaryDecision(mode="capability", target=capability, percentage=percentage)
