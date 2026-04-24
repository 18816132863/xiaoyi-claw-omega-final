#!/usr/bin/env python3
"""
发布管理器 - V1.1.0

管理发布流程，确保门禁通过后才能发布
V1.1.0 新增：发布证据包打包
"""

import os
import json
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def load_report(report_path: str) -> Optional[Dict]:
    """加载报告"""
    path = get_project_root() / report_path
    if not path.exists():
        return None
    try:
        return json.load(open(path, encoding='utf-8'))
    except:
        return None


def get_recent_history(history_type: str, count: int = 5) -> List[Dict]:
    """获取最近的历史记录"""
    root = get_project_root()
    history_dir = root / f"reports/history/{history_type}"
    
    if not history_dir.exists():
        return []
    
    files = sorted(history_dir.glob("*.json"), reverse=True)[:count]
    
    results = []
    for f in files:
        try:
            data = json.load(open(f, encoding='utf-8'))
            data["file"] = f.name
            results.append(data)
        except:
            pass
    
    return results


def check_release_gate(report_path: str = None) -> Dict:
    """检查发布门禁"""
    root = get_project_root()
    timestamp = datetime.now()
    
    # 加载报告
    runtime_report = load_report("reports/runtime_integrity.json")
    quality_report = load_report("reports/quality_gate.json")
    
    # 从 runtime_report 提取字段
    p0_count = 0
    local_status = "skipped"
    integration_status = "skipped"
    external_status = "skipped"
    
    if runtime_report:
        p0_count = runtime_report.get("p0_count", 0)
        local_status = runtime_report.get("local_status", "skipped")
        integration_status = runtime_report.get("integration_status", "skipped")
        external_status = runtime_report.get("external_status", "skipped")
    
    # 判断是否可以发布
    runtime_ok = runtime_report and runtime_report.get("overall_passed")
    quality_ok = quality_report and quality_report.get("overall_passed")
    can_release = runtime_ok and quality_ok
    
    result = {
        # gate_report contract 必需字段
        "profile": "release",
        "overall_passed": can_release,
        "p0_count": p0_count,
        "local_status": local_status,
        "integration_status": integration_status,
        "external_status": external_status,
        "verified_at": timestamp.isoformat(),
        # release 专属字段
        "can_release": can_release,
        "runtime_gate": None,
        "quality_gate": None,
        "blocked_reasons": [],
        "skipped_external": [],
        "quality_checks_summary": {},
        "recent_nightly_status": [],
        "last_blocked": None,
        "checked_at": timestamp.isoformat()
    }
    
    # 检查运行时门禁
    if not runtime_report:
        result["blocked_reasons"].append("缺少 runtime_integrity.json，请先运行 --profile release")
    else:
        result["runtime_gate"] = {
            "profile": runtime_report.get("profile"),
            "passed": runtime_report.get("overall_passed"),
            "verified_at": runtime_report.get("verified_at"),
            "p0_count": runtime_report.get("p0_count"),
            "local_status": runtime_report.get("local_status"),
            "integration_status": runtime_report.get("integration_status"),
            "external_status": runtime_report.get("external_status")
        }
        
        # 提取 skipped external
        for skill in runtime_report.get("skipped_skills", []):
            result["skipped_external"].append({
                "skill": skill.get("skill"),
                "reason": skill.get("message", "")
            })
        
        if not runtime_report.get("overall_passed"):
            result["blocked_reasons"].append(f"运行时门禁未通过: {runtime_report.get('failure_reasons', [])}")
    
    # 检查质量门禁
    if not quality_report:
        result["blocked_reasons"].append("缺少 quality_gate.json，请先运行 quality_gate.py")
    else:
        checks_summary = {}
        for name, check in quality_report.get("checks", {}).items():
            checks_summary[name] = check.get("status")
        
        result["quality_gate"] = {
            "passed": quality_report.get("overall_passed"),
            "verified_at": quality_report.get("verified_at")
        }
        result["quality_checks_summary"] = checks_summary
        
        if not quality_report.get("overall_passed"):
            failed_checks = [k for k, v in checks_summary.items() if v != "pass"]
            result["blocked_reasons"].append(f"质量门禁未通过: {failed_checks}")
    
    # 获取最近 nightly 历史
    nightly_history = get_recent_history("runtime", 5)
    for h in nightly_history:
        if h.get("profile") == "nightly":
            result["recent_nightly_status"].append({
                "date": h.get("verified_at"),
                "passed": h.get("overall_passed"),
                "p0_count": h.get("p0_count"),
                "local_status": h.get("local_status")
            })
    
    # 查找最近一次 blocked
    for h in nightly_history:
        if not h.get("overall_passed"):
            result["last_blocked"] = {
                "date": h.get("verified_at"),
                "reasons": h.get("failure_reasons", [])
            }
            break
    
    # 保存 latest
    if report_path:
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    # 保存历史快照
    history_dir = root / "reports/history/release"
    history_dir.mkdir(parents=True, exist_ok=True)
    history_file = history_dir / f"{timestamp.strftime('%Y%m%d_%H%M%S')}_gate_check.json"
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return result


def create_release(version: str, notes: str = "") -> Dict:
    """创建发布"""
    gate = check_release_gate()
    
    if not gate["can_release"]:
        return {
            "success": False,
            "message": "门禁未通过，无法发布",
            "blocked_reasons": gate["blocked_reasons"]
        }
    
    # 创建发布记录
    release = {
        "version": version,
        "released_at": datetime.now().isoformat(),
        "notes": notes,
        "runtime_gate": gate["runtime_gate"],
        "quality_gate": gate["quality_gate"]
    }
    
    # 保存发布记录
    root = get_project_root()
    releases_path = root / "reports/releases.json"
    
    releases = []
    if releases_path.exists():
        try:
            releases = json.load(open(releases_path, encoding='utf-8'))
        except:
            pass
    
    releases.append(release)
    
    with open(releases_path, 'w', encoding='utf-8') as f:
        json.dump(releases, f, ensure_ascii=False, indent=2)
    
    return {
        "success": True,
        "message": f"发布 {version} 成功",
        "release": release
    }


def print_gate_status(gate: Dict):
    """打印门禁状态"""
    print("╔══════════════════════════════════════════════════╗")
    print("║              发布门禁检查                       ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    # 运行时门禁
    rt = gate.get("runtime_gate")
    if rt:
        status = "✅" if rt.get("passed") else "❌"
        print(f"  {status} 运行时门禁 ({rt.get('profile', 'unknown')}): {rt.get('verified_at', '')}")
    else:
        print("  ⚠️  运行时门禁: 未运行")
    
    # 质量门禁
    qt = gate.get("quality_gate")
    if qt:
        status = "✅" if qt.get("passed") else "❌"
        print(f"  {status} 质量门禁: {qt.get('verified_at', '')}")
    else:
        print("  ⚠️  质量门禁: 未运行")
    
    print()
    print("══════════════════════════════════════════════════")
    if gate["can_release"]:
        print("✅ 可以发布")
    else:
        print("❌ 门禁未通过，禁止发布")
        for reason in gate.get("blocked_reasons", []):
            print(f"   - {reason}")
    print("══════════════════════════════════════════════════")


def build_release_evidence_bundle() -> Dict:
    """构建发布证据包"""
    root = get_project_root()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bundle_dir = root / "reports/bundles"
    bundle_dir.mkdir(parents=True, exist_ok=True)
    
    bundle_path = bundle_dir / f"release_evidence_{timestamp}.zip"
    
    # 证据文件列表
    evidence_files = [
        "reports/runtime_integrity.json",
        "reports/quality_gate.json",
        "reports/release_gate.json",
        "reports/ops/rule_engine_report.json",
        "reports/ops/rule_execution_index.json",
        "reports/ops/rule_registry_snapshot.json",
        "reports/ops/rule_exception_status.json",
        "reports/ops/rule_exception_debt.json",
        "reports/ops/rule_exception_history.json",
        "reports/ops/control_plane_state.json",
        "reports/ops/control_plane_audit.json",
        "reports/ops/exception_approval_queue.json",
    ]
    
    included = []
    missing = []
    
    with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in evidence_files:
            full_path = root / file_path
            if full_path.exists():
                zf.write(full_path, file_path)
                included.append(file_path)
            else:
                missing.append(file_path)
        
        # 添加清单
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "bundle_path": str(bundle_path),
            "included": included,
            "missing": missing,
            "total_files": len(included)
        }
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    
    return {
        "status": "success",
        "bundle_path": str(bundle_path),
        "included_count": len(included),
        "missing_count": len(missing),
        "included": included,
        "missing": missing
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="发布管理器")
    parser.add_argument("--check", action="store_true", help="检查门禁状态")
    parser.add_argument("--report-json", help="JSON 报告输出路径")
    parser.add_argument("--release", type=str, help="创建发布 (版本号)")
    parser.add_argument("--notes", type=str, default="", help="发布说明")
    parser.add_argument("--bundle", action="store_true", help="构建发布证据包")
    args = parser.parse_args()
    
    if args.bundle:
        result = build_release_evidence_bundle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        import sys
        sys.exit(0 if result["status"] == "success" else 1)
    
    if args.release:
        result = create_release(args.release, args.notes)
        if result["success"]:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['message']}")
            for reason in result.get("blocked_reasons", []):
                print(f"   - {reason}")
        import sys
        sys.exit(0 if result["success"] else 1)
    
    gate = check_release_gate(args.report_json)
    print_gate_status(gate)
    
    import sys
    sys.exit(0 if gate["can_release"] else 1)
