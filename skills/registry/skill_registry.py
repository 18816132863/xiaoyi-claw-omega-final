from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class SkillCategory(str, Enum):
    UTILITY = "utility"
    CODE = "code"
    DATA = "data"
    FILE = "file"
    OTHER = "other"


class SkillStatus(str, Enum):
    EXPERIMENTAL = "experimental"
    BETA = "beta"
    STABLE = "stable"
    RESTRICTED = "restricted"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


@dataclass
class SkillManifest:
    skill_id: str
    name: str
    version: str
    description: str
    category: SkillCategory = SkillCategory.UTILITY
    status: SkillStatus = SkillStatus.STABLE
    executor_type: str = "skill_md"
    entry_point: str = ""
    timeout_seconds: int = 60
    tags: List[str] = field(default_factory=list)


class SkillRegistry:
    def __init__(self):
        self._skills: Dict[str, SkillManifest] = {}

    def register(self, manifest: SkillManifest) -> SkillManifest:
        self._skills[manifest.skill_id] = manifest
        return manifest

    def get(self, skill_id: str) -> Optional[SkillManifest]:
        return self._skills.get(skill_id)

    def list(self) -> List[SkillManifest]:
        return list(self._skills.values())

    def enable(self, skill_id: str) -> bool:
        manifest = self._skills.get(skill_id)
        if not manifest:
            return False
        if manifest.status in {SkillStatus.DISABLED, SkillStatus.DEPRECATED}:
            manifest.status = SkillStatus.STABLE
        return True

    def disable(self, skill_id: str) -> bool:
        manifest = self._skills.get(skill_id)
        if not manifest:
            return False
        manifest.status = SkillStatus.DISABLED
        return True

    def search(self, query: str) -> List[SkillManifest]:
        q = (query or "").lower().strip()
        if not q:
            return self.list()

        results: List[SkillManifest] = []
        for manifest in self._skills.values():
            haystacks = [
                manifest.skill_id,
                manifest.name,
                manifest.description,
                " ".join(manifest.tags or []),
                manifest.category.value,
            ]
            text = " ".join(haystacks).lower()
            if q in text:
                results.append(manifest)
        return results
