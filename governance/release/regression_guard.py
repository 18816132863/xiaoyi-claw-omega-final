import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
METRICS_PATH = ROOT / "reports" / "metrics" / "aggregated_metrics.json"

def check_regression() -> dict:
    if not METRICS_PATH.exists():
        return {"passed": False, "reason": "missing_metrics"}

    data = json.load(open(METRICS_PATH, encoding="utf-8"))

    task_success = data.get("task_success_rate", 1.0)
    skill_failure = data.get("skill_failure_rate", 0.0)
    memory_hit = data.get("memory_hit_rate", 1.0)
    rollback_rate = data.get("rollback_rate", 0.0)
    degradation_rate = data.get("degradation_rate", 0.0)

    passed = (
        task_success >= 0.8 and
        skill_failure <= 0.2 and
        memory_hit >= 0.5 and
        rollback_rate <= 0.1 and
        degradation_rate <= 0.2
    )

    return {
        "passed": passed,
        "task_success_rate": task_success,
        "skill_failure_rate": skill_failure,
        "memory_hit_rate": memory_hit,
        "rollback_rate": rollback_rate,
        "degradation_rate": degradation_rate
    }
