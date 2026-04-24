#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path

from core.events.event_persistence import get_event_persistence
from core.events.event_replay import EventReplay
from infrastructure.monitoring.system_health_report import get_system_health_reporter

ROOT = Path(__file__).resolve().parent.parent
OBS_DIR = ROOT / "reports" / "observability"
OBS_DIR.mkdir(parents=True, exist_ok=True)

def main():
    persistence = get_event_persistence()
    replay = EventReplay(persistence)

    events = persistence.list(limit=10000)

    workflow_events = [e for e in events if e.workflow_instance_id]
    skill_events = [e for e in events if e.event_type in {"skill_selected", "skill_executed", "skill_failed"}]
    policy_events = [e for e in events if e.event_type == "policy_decided"]

    workflow_timeline = {
        "total_events": len(workflow_events),
        "items": [e.to_dict() for e in workflow_events]
    }
    skill_timeline = {
        "total_events": len(skill_events),
        "items": [e.to_dict() for e in skill_events]
    }
    policy_timeline = {
        "total_events": len(policy_events),
        "items": [e.to_dict() for e in policy_events]
    }

    with open(OBS_DIR / "workflow_timeline.json", "w", encoding="utf-8") as f:
        json.dump(workflow_timeline, f, ensure_ascii=False, indent=2)

    with open(OBS_DIR / "skill_timeline.json", "w", encoding="utf-8") as f:
        json.dump(skill_timeline, f, ensure_ascii=False, indent=2)

    with open(OBS_DIR / "policy_timeline.json", "w", encoding="utf-8") as f:
        json.dump(policy_timeline, f, ensure_ascii=False, indent=2)

    reporter = get_system_health_reporter()
    report = reporter.generate_report()
    with open(OBS_DIR / "system_health_report.json", "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)

    print("observability reports generated")

if __name__ == "__main__":
    main()
