#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path

from governance.release.channel_manager import get_channel_manager, Channel
from governance.release.baseline_registry import get_baseline_registry, BaselineStage
from governance.release.promotion_manager import PromotionManager

ROOT = Path(__file__).resolve().parent.parent
REL_DIR = ROOT / "reports" / "release"
REL_DIR.mkdir(parents=True, exist_ok=True)

def main():
    cm = get_channel_manager()
    br = get_baseline_registry()
    pm = PromotionManager()

    channels = {}
    for channel in Channel:
        state = cm.get_channel(channel)
        channels[channel.value] = {
            "current_baseline_id": state.current_baseline_id,
            "current_version": state.current_version,
            "health_status": state.health_status,
            "promoted_at": state.promoted_at
        }

    baselines = []
    for baseline in br.list_all():
        baselines.append({
            "baseline_id": baseline.baseline_id,
            "version": baseline.version,
            "stage": baseline.stage.value if hasattr(baseline.stage, 'value') else str(baseline.stage),
            "channel": baseline.channel,
            "registered_at": baseline.registered_at
        })

    promotions = []
    for record in pm.get_recent_promotions(limit=100):
        promotions.append({
            "promotion_id": record.promotion_id,
            "from_channel": record.from_channel,
            "to_channel": record.to_channel,
            "baseline_id": record.baseline_id,
            "status": record.status.value if hasattr(record.status, 'value') else str(record.status),
            "started_at": record.started_at
        })

    regression = {
        "last_check": None,
        "regressions_found": 0,
        "details": []
    }

    with open(REL_DIR / "release_channels.json", "w", encoding="utf-8") as f:
        json.dump({"channels": channels}, f, ensure_ascii=False, indent=2)

    with open(REL_DIR / "baseline_registry.json", "w", encoding="utf-8") as f:
        json.dump({"baselines": baselines, "regression_guard": regression}, f, ensure_ascii=False, indent=2)

    with open(REL_DIR / "promotion_history.json", "w", encoding="utf-8") as f:
        json.dump({"promotions": promotions}, f, ensure_ascii=False, indent=2)

    print("release reports generated")

if __name__ == "__main__":
    main()
