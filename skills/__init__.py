"""
Skills Platform - 技能插件平台
Phase3 Group3
"""

from skills.runtime.skill_package_loader import (
    SkillPackageLoader,
    SkillPackage,
    LoadResult,
    get_skill_package_loader
)
from skills.runtime.skill_dependency_resolver import (
    SkillDependencyResolver,
    ResolutionResult,
    get_skill_dependency_resolver
)
from skills.runtime.skill_version_selector import (
    SkillVersionSelector,
    SelectionCriteria,
    SelectionResult,
    get_skill_version_selector
)
from skills.runtime.skill_health_monitor import (
    SkillHealthMonitor,
    HealthMetrics,
    HealthCheckResult,
    get_skill_health_monitor
)
from skills.lifecycle.upgrade_manager import (
    UpgradeManager,
    UpgradeResult,
    get_upgrade_manager
)
from skills.lifecycle.remove_manager import (
    RemoveManager,
    RemoveResult,
    get_remove_manager
)
from skills.lifecycle.compatibility_manager import (
    CompatibilityManager,
    CompatibilityResult,
    get_compatibility_manager
)

__all__ = [
    # Package Loader
    "SkillPackageLoader",
    "SkillPackage",
    "LoadResult",
    "get_skill_package_loader",

    # Dependency Resolver
    "SkillDependencyResolver",
    "ResolutionResult",
    "get_skill_dependency_resolver",

    # Version Selector
    "SkillVersionSelector",
    "SelectionCriteria",
    "SelectionResult",
    "get_skill_version_selector",

    # Health Monitor
    "SkillHealthMonitor",
    "HealthMetrics",
    "HealthCheckResult",
    "get_skill_health_monitor",

    # Upgrade Manager
    "UpgradeManager",
    "UpgradeResult",
    "get_upgrade_manager",

    # Remove Manager
    "RemoveManager",
    "RemoveResult",
    "get_remove_manager",

    # Compatibility Manager
    "CompatibilityManager",
    "CompatibilityResult",
    "get_compatibility_manager",
]
