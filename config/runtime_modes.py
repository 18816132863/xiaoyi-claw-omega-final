"""
Runtime Mode Definitions

Defines 4 runtime modes for device interaction:
- dry_run: No side effects, for CI/testing
- fake_device: Mock device responses, for E2E testing
- probe_only: Real device connection, read-only probing
- connected_runtime: Real device with controlled execution
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class RuntimeMode(str, Enum):
    """Runtime execution modes."""
    DRY_RUN = "dry_run"
    FAKE_DEVICE = "fake_device"
    PROBE_ONLY = "probe_only"
    CONNECTED_RUNTIME = "connected_runtime"


@dataclass
class RuntimeModeConfig:
    """Configuration for a runtime mode."""
    allow_side_effects: bool
    require_device: bool
    allow_screen_read: bool = False
    allow_click: bool = False
    allow_type: bool = False
    allow_delete: bool = False
    allow_send: bool = False
    allow_call: bool = False
    enforce_safety_governor: bool = False


RUNTIME_MODE_CONFIGS: dict[RuntimeMode, RuntimeModeConfig] = {
    RuntimeMode.DRY_RUN: RuntimeModeConfig(
        allow_side_effects=False,
        require_device=False,
    ),
    RuntimeMode.FAKE_DEVICE: RuntimeModeConfig(
        allow_side_effects=False,
        require_device=False,
        allow_screen_read=True,
    ),
    RuntimeMode.PROBE_ONLY: RuntimeModeConfig(
        allow_side_effects=False,
        require_device=True,
        allow_screen_read=True,
        allow_click=False,
        allow_type=False,
        allow_delete=False,
        allow_send=False,
        allow_call=False,
    ),
    RuntimeMode.CONNECTED_RUNTIME: RuntimeModeConfig(
        allow_side_effects=True,
        require_device=True,
        allow_screen_read=True,
        allow_click=True,
        allow_type=True,
        allow_delete=True,
        allow_send=True,
        allow_call=True,
        enforce_safety_governor=True,
    ),
}


def get_runtime_mode_config(mode: RuntimeMode) -> RuntimeModeConfig:
    """Get configuration for a runtime mode."""
    return RUNTIME_MODE_CONFIGS.get(mode, RUNTIME_MODE_CONFIGS[RuntimeMode.DRY_RUN])


def is_side_effect_allowed(mode: RuntimeMode, action: str) -> bool:
    """Check if a side-effecting action is allowed in the given mode."""
    config = get_runtime_mode_config(mode)
    
    if not config.allow_side_effects:
        return False
    
    action_map = {
        "click": config.allow_click,
        "type": config.allow_type,
        "delete": config.allow_delete,
        "send": config.allow_send,
        "call": config.allow_call,
    }
    
    return action_map.get(action, False)


def is_probe_only(mode: RuntimeMode) -> bool:
    """Check if the mode is probe-only (no side effects)."""
    return mode == RuntimeMode.PROBE_ONLY


def requires_device(mode: RuntimeMode) -> bool:
    """Check if the mode requires a real device."""
    return get_runtime_mode_config(mode).require_device
