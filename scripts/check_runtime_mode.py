#!/usr/bin/env python3
"""
Check Runtime Mode

Validates runtime mode configuration and reports current status.
"""

import sys
import json
import yaml
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.runtime_modes import (
    RuntimeMode,
    RUNTIME_MODE_CONFIGS,
    get_runtime_mode_config,
    is_side_effect_allowed,
    is_probe_only,
    requires_device,
)


def check_runtime_mode():
    """Check and report runtime mode configuration."""
    print("=" * 60)
    print("RUNTIME MODE CHECK")
    print("=" * 60)
    
    # Load runtime policy
    policy_path = Path(__file__).parent.parent / "config" / "runtime_policy.yaml"
    if policy_path.exists():
        with open(policy_path) as f:
            policy = yaml.safe_load(f)
        default_mode = policy.get("default_mode", "dry_run")
        print(f"\n📋 Default Mode: {default_mode}")
    else:
        default_mode = "dry_run"
        print(f"\n📋 Default Mode: {default_mode} (policy file not found)")
    
    # Report all modes
    print("\n📊 Runtime Modes:")
    print("-" * 60)
    
    for mode in RuntimeMode:
        config = get_runtime_mode_config(mode)
        print(f"\n  {mode.value}:")
        print(f"    allow_side_effects: {config.allow_side_effects}")
        print(f"    require_device: {config.require_device}")
        print(f"    allow_screen_read: {config.allow_screen_read}")
        print(f"    allow_click: {config.allow_click}")
        print(f"    allow_type: {config.allow_type}")
        print(f"    allow_delete: {config.allow_delete}")
        print(f"    allow_send: {config.allow_send}")
        print(f"    allow_call: {config.allow_call}")
        print(f"    enforce_safety_governor: {config.enforce_safety_governor}")
    
    # Test side effect checks
    print("\n🔒 Side Effect Checks (probe_only):")
    print("-" * 60)
    
    probe_mode = RuntimeMode.PROBE_ONLY
    actions = ["click", "type", "delete", "send", "call"]
    
    for action in actions:
        allowed = is_side_effect_allowed(probe_mode, action)
        status = "✅ ALLOWED" if allowed else "❌ BLOCKED"
        print(f"  {action}: {status}")
    
    # Verify probe_only blocks all side effects
    print("\n✅ Verification:")
    print("-" * 60)
    
    all_blocked = all(
        not is_side_effect_allowed(RuntimeMode.PROBE_ONLY, action)
        for action in actions
    )
    
    if all_blocked:
        print("  ✅ probe_only blocks all side effects")
    else:
        print("  ❌ probe_only allows some side effects (ERROR)")
        return 1
    
    if is_probe_only(RuntimeMode.PROBE_ONLY):
        print("  ✅ is_probe_only() correctly identifies probe_only mode")
    else:
        print("  ❌ is_probe_only() failed (ERROR)")
        return 1
    
    if requires_device(RuntimeMode.PROBE_ONLY):
        print("  ✅ probe_only requires device")
    else:
        print("  ❌ probe_only does not require device (ERROR)")
        return 1
    
    if not requires_device(RuntimeMode.DRY_RUN):
        print("  ✅ dry_run does not require device")
    else:
        print("  ❌ dry_run requires device (ERROR)")
        return 1
    
    print("\n" + "=" * 60)
    print("RUNTIME MODE CHECK: PASSED")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(check_runtime_mode())
