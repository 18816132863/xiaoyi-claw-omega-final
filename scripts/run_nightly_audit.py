#!/usr/bin/env python3
"""
夜间巡检脚本 - V1.0.0

功能：
1. 运行 nightly 门禁
2. 与上次结果比较
3. 检测强回归/弱回归
4. 生成审计报告
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def load_latest_report(report_type: str) -> Optional[Dict]:
    """加载最新报告"""
    root = get_project_root()
    if report_type == "runtime":
        path = root / "reports/runtime_integrity.json"
    elif report_type == "quality":
        path = root / "reports/quality_gate.json"
    elif report_type == "release":
        path = root / "reports/release_gate.json"
    else:
        return None
    
    if not path.exists():
        return None
    try:
        return json.load(open(path, encoding='utf-8'))
    except:
        return None


def load_previous_report(report_type: str, profile: str = None) -> Optional[Dict]:
    """加载上一次报告"""
    root = get_project_root()
    history_dir = root / f"reports/history/{report_type}"
    
    if not history_dir.exists():
        return None
    
    files = sorted(history_dir.glob("*.json"), reverse=True)
    
    if not files:
        return None
    
    if len(files) > 1:
        for f in files[1:]:
            if profile:
                if profile in f.name:
                    return json.load(open(f, encoding='utf-8'))
            else:
                return json.load(open(f, encoding='utf-8'))
    
    return None


def compare_runtime_reports(current: Dict, previous: Dict) -> Dict:
    """比较两次 runtime 报告"""
    if not previous:
        return {"first_run": True, "changes": [], "regressions": []}
    
    changes = []
    regressions = []
    
    # 1. P0/P1/P2 变化
    for key in ["p0_count", "p1_count", "p2_count"]:
        curr_val = current.get(key, 0)
        prev_val = previous.get(key, 0)
        if curr_val != prev_val:
            change = {"field": key, "from": prev_val, "to": curr_val}
            changes.append(change)
            if key == "p0_count" and curr_val > prev_val:
                regressions.append({"type": "strong", "change": change})
            elif curr_val > prev_val:
                regressions.append({"type": "weak", "change": change})
    
    # 2. 状态变化
    for key in ["local_status", "integration_status", "external_status"]:
        curr_val = current.get(key, "unknown")
        prev_val = previous.get(key, "unknown")
        if curr_val != prev_val:
            change = {"field": key, "from": prev_val, "to": curr_val}
            changes.append(change)
            if prev_val == "pass" and curr_val in ["fail", "error"]:
                regressions.append({"type": "strong", "change": change})
            elif prev_val in ["fail", "error"] and curr_val == "pass":
                change["improvement"] = True
    
    # 3. 技能状态变化
    curr_skills = {r["skill"]: r["status"] for r in current.get("local_results", []) + 
                   current.get("integration_results", []) + current.get("external_results", [])}
    prev_skills = {r["skill"]: r["status"] for r in previous.get("local_results", []) + 
                   previous.get("integration_results", []) + previous.get("external_results", [])}
    
    for skill, status in curr_skills.items():
        prev_status = prev_skills.get(skill)
        if prev_status and prev_status != status:
            change = {"field": f"skill.{skill}", "from": prev_status, "to": status}
            changes.append(change)
            if prev_status == "pass" and status in ["fail", "error"]:
                regressions.append({"type": "strong", "change": change})
    
    # 4. overall_passed 变化
    if current.get("overall_passed") != previous.get("overall_passed"):
        change = {
            "field": "overall_passed", 
            "from": previous.get("overall_passed"), 
            "to": current.get("overall_passed")
        }
        changes.append(change)
        if previous.get("overall_passed") and not current.get("overall_passed"):
            regressions.append({"type": "strong", "change": change})
    
    return {"first_run": False, "changes": changes, "regressions": regressions}


def compare_quality_reports(current: Dict, previous: Dict) -> Dict:
    """比较两次 quality 报告"""
    if not previous:
        return {"first_run": True, "changes": [], "regressions": []}
    
    changes = []
    regressions = []
    
    # 检查各项状态变化
    curr_checks = current.get("checks", {})
    prev_checks = previous.get("checks", {})
    
    for name, curr_check in curr_checks.items():
        prev_check = prev_checks.get(name, {})
        curr_status = curr_check.get("status", "unknown")
        prev_status = prev_check.get("status", "unknown")
        
        if curr_status != prev_status:
            change = {"field": f"check.{name}", "from": prev_status, "to": curr_status}
            changes.append(change)
            # pass -> fail 是强回归
            if prev_status == "pass" and curr_status != "pass":
                regressions.append({"type": "strong", "change": change})
    
    # overall_passed 变化
    if current.get("overall_passed") != previous.get("overall_passed"):
        change = {
            "field": "overall_passed",
            "from": previous.get("overall_passed"),
            "to": current.get("overall_passed")
        }
        changes.append(change)
        if previous.get("overall_passed") and not current.get("overall_passed"):
            regressions.append({"type": "strong", "change": change})
    
    return {"first_run": False, "changes": changes, "regressions": regressions}


def compare_release_reports(current: Dict, previous: Dict) -> Dict:
    """比较两次 release 报告"""
    if not previous:
        return {"first_run": True, "changes": [], "regressions": []}
    
    changes = []
    regressions = []
    
    # can_release 变化
    if current.get("can_release") != previous.get("can_release"):
        change = {
            "field": "can_release",
            "from": previous.get("can_release"),
            "to": current.get("can_release")
        }
        changes.append(change)
        # true -> false 是强回归
        if previous.get("can_release") and not current.get("can_release"):
            regressions.append({"type": "strong", "change": change})
    
    # blocked_reasons 变化
    curr_blocked = current.get("blocked_reasons", [])
    prev_blocked = previous.get("blocked_reasons", [])
    if len(curr_blocked) != len(prev_blocked):
        change = {
            "field": "blocked_reasons_count",
            "from": len(prev_blocked),
            "to": len(curr_blocked)
        }
        changes.append(change)
        if len(curr_blocked) > len(prev_blocked):
            regressions.append({"type": "weak", "change": change})
    
    # skipped_external 变化
    curr_skipped = [s["skill"] for s in current.get("skipped_external", [])]
    prev_skipped = [s["skill"] for s in previous.get("skipped_external", [])]
    if set(curr_skipped) != set(prev_skipped):
        change = {
            "field": "skipped_external",
            "from": prev_skipped,
            "to": curr_skipped
        }
        changes.append(change)
        regressions.append({"type": "weak", "change": change})
    
    return {"first_run": False, "changes": changes, "regressions": regressions}


def check_skill_registry_changes() -> Dict:
    """检查技能注册表变化"""
    root = get_project_root()
    registry_path = root / "infrastructure/inventory/skill_registry.json"
    
    if not registry_path.exists():
        return {"status": "error", "message": "skill_registry.json 不存在"}
    
    try:
        data = json.load(open(registry_path, encoding='utf-8'))
        skills = data.get("skills", {})
        
        total = len(skills)
        callable_count = sum(1 for s in skills.values() if isinstance(s, dict) and s.get("callable"))
        registered_count = sum(1 for s in skills.values() if isinstance(s, dict) and s.get("registered"))
        
        # 检查缺失元数据的技能
        missing_metadata = []
        for name, info in skills.items():
            if isinstance(info, dict) and info.get("callable"):
                if not info.get("test_mode"):
                    missing_metadata.append(f"{name}: 缺 test_mode")
                if info.get("test_mode") in ["local", "integration"] and not info.get("testable"):
                    missing_metadata.append(f"{name}: 缺 testable")
        
        return {
            "status": "pass",
            "total_skills": total,
            "callable_skills": callable_count,
            "registered_skills": registered_count,
            "missing_metadata": missing_metadata[:5]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_p2_trend(current: Dict, previous: Dict) -> Dict:
    """检查 P2 趋势"""
    if not previous:
        return {"status": "info", "message": "首次运行，无历史数据"}
    
    curr_p2 = current.get("p2_count", 0)
    prev_p2 = previous.get("p2_count", 0)
    
    if curr_p2 > prev_p2:
        return {
            "status": "warning",
            "message": f"P2 增加: {prev_p2} → {curr_p2}",
            "trend": "increasing"
        }
    elif curr_p2 < prev_p2:
        return {
            "status": "improvement",
            "message": f"P2 减少: {prev_p2} → {curr_p2}",
            "trend": "decreasing"
        }
    else:
        return {
            "status": "stable",
            "message": f"P2 稳定: {curr_p2}",
            "trend": "stable"
        }


def generate_audit_report(runtime_current: Dict, runtime_prev: Dict, 
                          quality_current: Dict, quality_prev: Dict,
                          release_current: Dict, release_prev: Dict) -> Dict:
    """生成完整审计报告"""
    # 比较三类报告
    runtime_comp = compare_runtime_reports(runtime_current, runtime_prev)
    quality_comp = compare_quality_reports(quality_current, quality_prev)
    release_comp = compare_release_reports(release_current, release_prev)
    
    # 合并回归
    strong_regressions = []
    weak_regressions = []
    all_changes = []
    
    for r in runtime_comp.get("regressions", []):
        r["source"] = "runtime"
        strong_regressions.append(r) if r.get("type") == "strong" else weak_regressions.append(r)
    
    for r in quality_comp.get("regressions", []):
        r["source"] = "quality"
        strong_regressions.append(r) if r.get("type") == "strong" else weak_regressions.append(r)
    
    for r in release_comp.get("regressions", []):
        r["source"] = "release"
        strong_regressions.append(r) if r.get("type") == "strong" else weak_regressions.append(r)
    
    all_changes.extend(runtime_comp.get("changes", []))
    all_changes.extend(quality_comp.get("changes", []))
    all_changes.extend(release_comp.get("changes", []))
    
    # 检查技能注册表
    registry_check = check_skill_registry_changes()
    
    # P2 趋势
    p2_trend = check_p2_trend(runtime_current, runtime_prev) if runtime_current else {"status": "info"}
    
    audit = {
        "audit_at": datetime.now().isoformat(),
        "profile": "nightly",
        "overall_passed": runtime_current.get("overall_passed", False) if runtime_current else False,
        "has_regression": len(strong_regressions) > 0,
        "strong_regressions": strong_regressions,
        "weak_regressions": weak_regressions,
        "changes": all_changes,
        "runtime_summary": {
            "p0_count": runtime_current.get("p0_count", 0) if runtime_current else 0,
            "p1_count": runtime_current.get("p1_count", 0) if runtime_current else 0,
            "p2_count": runtime_current.get("p2_count", 0) if runtime_current else 0,
            "local_status": runtime_current.get("local_status") if runtime_current else "unknown",
            "integration_status": runtime_current.get("integration_status") if runtime_current else "unknown",
            "external_status": runtime_current.get("external_status") if runtime_current else "unknown",
            "skipped_count": len(runtime_current.get("skipped_skills", [])) if runtime_current else 0
        },
        "quality_summary": {
            "passed": quality_current.get("overall_passed", False) if quality_current else False,
            "checks": quality_current.get("checks", {}) if quality_current else {}
        },
        "release_summary": {
            "can_release": release_current.get("can_release", False) if release_current else False,
            "blocked_count": len(release_current.get("blocked_reasons", [])) if release_current else 0
        },
        "registry_check": registry_check,
        "p2_trend": p2_trend,
        "summary": {
            "p0_count": runtime_current.get("p0_count", 0) if runtime_current else 0,
            "p1_count": runtime_current.get("p1_count", 0) if runtime_current else 0,
            "p2_count": runtime_current.get("p2_count", 0) if runtime_current else 0,
            "local_status": runtime_current.get("local_status") if runtime_current else "unknown",
            "integration_status": runtime_current.get("integration_status") if runtime_current else "unknown",
            "external_status": runtime_current.get("external_status") if runtime_current else "unknown",
            "skipped_count": len(runtime_current.get("skipped_skills", [])) if runtime_current else 0,
            "total_skills": registry_check.get("total_skills", 0),
            "callable_skills": registry_check.get("callable_skills", 0),
            "quality_gate_passed": quality_current.get("overall_passed", False) if quality_current else False,
            "can_release": release_current.get("can_release", False) if release_current else False,
            "blocked_reason_count": len(release_current.get("blocked_reasons", [])) if release_current else 0
        },
        "recommendations": []
    }
    
    # 生成建议
    if strong_regressions:
        audit["recommendations"].append("🚨 存在强回归，建议立即修复后再发布")
    if weak_regressions:
        audit["recommendations"].append(f"⚠️ 存在 {len(weak_regressions)} 个弱回归，建议在下次迭代中处理")
    if audit["summary"]["p2_count"] > 20:
        audit["recommendations"].append(f"📋 P2 历史遗留较多 ({audit['summary']['p2_count']} 处)，建议逐步清理")
    if registry_check.get("missing_metadata"):
        audit["recommendations"].append(f"📊 {len(registry_check['missing_metadata'])} 个技能缺失元数据")
    if p2_trend.get("trend") == "increasing":
        audit["recommendations"].append("📈 P2 呈上升趋势，需关注代码质量")
    
    return audit


def generate_summary_md(audit: Dict) -> str:
    """生成 Markdown 摘要"""
    lines = [
        f"# 夜间巡检报告",
        f"",
        f"**时间**: {audit['audit_at']}",
        f"**Profile**: {audit['profile']}",
        f"**结果**: {'✅ 通过' if audit['overall_passed'] else '❌ 失败'}",
        f"",
        f"## 状态摘要",
        f"",
        f"| 指标 | 值 |",
        f"|------|-----|",
        f"| P0 硬编码 | {audit['summary']['p0_count']} |",
        f"| P1 工具链 | {audit['summary']['p1_count']} |",
        f"| P2 历史遗留 | {audit['summary']['p2_count']} |",
        f"| Local 状态 | {audit['summary']['local_status']} |",
        f"| Integration 状态 | {audit['summary']['integration_status']} |",
        f"| External 状态 | {audit['summary']['external_status']} |",
        f"| Skipped 技能 | {audit['summary']['skipped_count']} |",
        f"| 技能总数 | {audit['summary']['total_skills']} |",
        f"| 可执行技能 | {audit['summary']['callable_skills']} |",
        f"",
    ]
    
    # P2 趋势
    p2_trend = audit.get("p2_trend", {})
    if p2_trend.get("status") != "info":
        trend_icon = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}.get(p2_trend.get("trend"), "➡️")
        lines.append(f"**P2 趋势**: {trend_icon} {p2_trend.get('message', '')}")
        lines.append("")
    
    if audit['strong_regressions']:
        lines.append("## 🚨 强回归")
        lines.append("")
        for r in audit['strong_regressions']:
            c = r['change']
            lines.append(f"- **{c['field']}**: {c['from']} → {c['to']}")
        lines.append("")
    
    if audit['weak_regressions']:
        lines.append("## ⚠️ 弱回归")
        lines.append("")
        for r in audit['weak_regressions']:
            c = r['change']
            lines.append(f"- {c['field']}: {c['from']} → {c['to']}")
        lines.append("")
    
    # 技能注册表检查
    registry = audit.get("registry_check", {})
    if registry.get("missing_metadata"):
        lines.append("## 📊 元数据缺失")
        lines.append("")
        for m in registry["missing_metadata"][:5]:
            lines.append(f"- {m}")
        lines.append("")
    
    if audit['recommendations']:
        lines.append("## 建议")
        lines.append("")
        for rec in audit['recommendations']:
            lines.append(f"- {rec}")
        lines.append("")
    
    return "\n".join(lines)


def update_trend(audit: Dict):
    """更新趋势文件"""
    root = get_project_root()
    trend_file = root / "reports/trends/gate_trend.json"
    trend_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 加载现有趋势
    trends = []
    if trend_file.exists():
        try:
            trends = json.load(open(trend_file, encoding='utf-8'))
        except:
            pass
    
    # 添加新记录
    trends.append({
        "date": audit["audit_at"],
        "profile": audit["profile"],
        "p0_count": audit["summary"]["p0_count"],
        "p1_count": audit["summary"]["p1_count"],
        "p2_count": audit["summary"]["p2_count"],
        "local_status": audit["summary"]["local_status"],
        "integration_status": audit["summary"]["integration_status"],
        "external_status": audit["summary"]["external_status"],
        "overall_passed": audit["overall_passed"],
        "has_regression": audit["has_regression"],
        "strong_regression_count": len(audit["strong_regressions"]),
        "weak_regression_count": len(audit["weak_regressions"]),
        "quality_gate_passed": audit["summary"]["quality_gate_passed"],
        "can_release": audit["summary"]["can_release"],
        "blocked_reason_count": audit["summary"]["blocked_reason_count"],
        "skill_total": audit["summary"]["total_skills"],
        "callable_total": audit["summary"]["callable_skills"],
        "skipped_external_count": audit["summary"]["skipped_count"]
    })
    
    # 只保留最近 30 条
    trends = trends[-30:]
    
    with open(trend_file, 'w', encoding='utf-8') as f:
        json.dump(trends, f, ensure_ascii=False, indent=2)


def run_nightly_audit():
    """运行夜间巡检"""
    root = get_project_root()
    
    print("╔══════════════════════════════════════════════════╗")
    print("║              夜间巡检 V2.0.0                    ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    # 1. 运行 nightly 门禁
    print("【1】运行 Nightly 门禁...")
    import subprocess
    result = subprocess.run([
        sys.executable,
        str(root / "scripts/run_release_gate.py"),
        "nightly"
    ], cwd=root)
    
    # 2. 加载三类报告
    print()
    print("【2】加载并比较历史报告...")
    
    runtime_current = load_latest_report("runtime")
    runtime_prev = load_previous_report("runtime", "nightly")
    
    quality_current = load_latest_report("quality")
    quality_prev = load_previous_report("quality")
    
    release_current = load_latest_report("release")
    release_prev = load_previous_report("release")
    
    if not runtime_current:
        print("  ❌ 无法加载 runtime 报告")
        return 1
    
    # 3. 生成完整审计报告
    audit = generate_audit_report(
        runtime_current, runtime_prev,
        quality_current, quality_prev,
        release_current, release_prev
    )
    
    # 4. 保存审计报告
    audit_file = root / "reports/nightly_audit.json"
    audit_file.parent.mkdir(parents=True, exist_ok=True)
    with open(audit_file, 'w', encoding='utf-8') as f:
        json.dump(audit, f, ensure_ascii=False, indent=2)
    
    # 5. 生成 Markdown 摘要
    summary_md = generate_summary_md(audit)
    summary_file = root / "reports/nightly_summary.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_md)
    
    # 6. 更新趋势
    update_trend(audit)
    
    # 7. 输出结果
    print()
    print("【3】审计结果")
    if audit["has_regression"]:
        print("  ❌ 检测到强回归")
        for r in audit["strong_regressions"]:
            c = r["change"]
            print(f"     - [{r['source']}] {c['field']}: {c['from']} → {c['to']}")
    else:
        print("  ✅ 无强回归")
    
    if audit["weak_regressions"]:
        print(f"  ⚠️  {len(audit['weak_regressions'])} 个弱回归")
    
    # 输出三块摘要
    print()
    print("【4】门禁摘要")
    print(f"  Runtime: {'✅' if audit['runtime_summary']['local_status'] == 'pass' else '❌'}")
    print(f"  Quality: {'✅' if audit['quality_summary']['passed'] else '❌'}")
    print(f"  Release: {'✅' if audit['release_summary']['can_release'] else '❌'}")
    
    print()
    print("══════════════════════════════════════════════════")
    print(f"报告已保存:")
    print(f"  - {audit_file}")
    print(f"  - {summary_file}")
    print("══════════════════════════════════════════════════")
    
    return 1 if audit["has_regression"] else 0


if __name__ == "__main__":
    sys.exit(run_nightly_audit())
