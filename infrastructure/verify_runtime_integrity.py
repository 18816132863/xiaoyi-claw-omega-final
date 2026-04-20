#!/usr/bin/env python3
"""
运行时一致性验收脚本 - V5.0.0

V5.0.0 新增：
- --profile premerge/nightly/release 门禁模式
- --report-json 机器可读报告
- 状态矩阵含真实验收结果
"""

import os
import sys
import json
import re
import time
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict
from datetime import datetime

# 基于 __file__ 定位项目根目录
def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    env_workspace = os.environ.get('OPENCLAW_WORKSPACE')
    if env_workspace and (Path(env_workspace) / 'core' / 'ARCHITECTURE.md').exists():
        return Path(env_workspace)
    return Path(__file__).resolve().parent.parent

try:
    from infrastructure.path_resolver import get_project_root, resolve_path
except ImportError:
    def get_project_root() -> Path:
        return _find_project_root()
    def resolve_path(p: str) -> Path:
        return get_project_root() / p

# 硬编码路径模式
HARDCODED_PATTERNS = [
    r'Path\.home\(\)',
    r'os\.path\.expanduser\(["\']~',
    r'["\']/home/sandbox/\.openclaw',
    r'["\']~',
    r'sys\.path\.insert\(0,\s*["\']/home/sandbox',
]
ALLOWED_EXPANDUSER = [r'vault', r'\.cache', r'\.config', r'\.local', r'/tmp']
P0_DIRS = ['infrastructure/component_validator.py', 'core/dynamic_prompt.py', 'governance/security', 'orchestration/router', 'execution', 'memory_context']
P1_DIRS = ['infrastructure/inventory', 'infrastructure/audit', 'infrastructure/test', 'infrastructure/analysis', 'infrastructure/ops', 'infrastructure/portfolio', 'governance/audit', 'infrastructure/optimization', 'infrastructure/plugin']
P2_DIRS = ['infrastructure/legacy', 'infrastructure/archive', 'infrastructure/backup']


def classify_file(filepath: str) -> str:
    for p0 in P0_DIRS:
        if filepath.startswith(p0):
            return 'P0'
    for p1 in P1_DIRS:
        if filepath.startswith(p1):
            return 'P1'
    for p2 in P2_DIRS:
        if filepath.startswith(p2):
            return 'P2'
    return 'P1' if 'infrastructure/' in filepath else 'P2'


def scan_hardcoded_paths() -> Dict[str, List[Dict]]:
    results = defaultdict(list)
    workspace = get_project_root()
    for py_file in workspace.rglob("*.py"):
        if "__pycache__" in str(py_file) or py_file.name == "verify_runtime_integrity.py":
            continue
        try:
            content = py_file.read_text()
            rel_path = str(py_file.relative_to(workspace))
            for pattern in HARDCODED_PATTERNS:
                if re.findall(pattern, content):
                    is_allowed = any(
                        any(re.search(p, content[max(0,m.start()-100):m.end()+100]) for p in ALLOWED_EXPANDUSER)
                        for m in re.finditer(pattern, content)
                    )
                    if not is_allowed:
                        results[classify_file(rel_path)].append({"file": rel_path, "pattern": pattern})
                        break
        except:
            pass
    return dict(results)


def load_registry() -> Tuple[Optional[Dict], Optional[str]]:
    path = resolve_path("infrastructure/inventory/skill_registry.json")
    if not path.exists():
        return None, "skill_registry.json 不存在"
    try:
        return json.load(open(path, encoding='utf-8')), None
    except Exception as e:
        return None, str(e)


def get_skills_by_test_mode(registry: Dict, test_mode: str) -> List[str]:
    skills = []
    skills_data = registry.get("skills", [])
    
    # 支持数组和字典两种格式
    if isinstance(skills_data, list):
        for s in skills_data:
            if isinstance(s, dict):
                if (s.get("test_mode") == test_mode and 
                    s.get("registered") and s.get("routable") and s.get("callable")):
                    skills.append(s.get("skill_id"))
    else:
        for name, info in skills_data.items():
            if isinstance(info, dict):
                if (info.get("test_mode") == test_mode and 
                    info.get("registered") and info.get("routable") and info.get("callable")):
                    skills.append(name)
    return skills


def get_smoke_test_skills(registry: Dict) -> List[str]:
    skills_data = registry.get("skills", [])
    
    # 支持数组和字典两种格式
    if isinstance(skills_data, list):
        return [s.get("skill_id") for s in skills_data 
                if isinstance(s, dict) and s.get("smoke_test") and s.get("test_mode") == "local"]
    else:
        return [n for n, i in skills_data.items() 
                if isinstance(i, dict) and i.get("smoke_test") and i.get("test_mode") == "local"]


def get_external_env_requirements(registry: Dict, skill_name: str) -> Dict:
    skills_data = registry.get("skills", [])
    
    # 支持数组和字典两种格式
    if isinstance(skills_data, list):
        for s in skills_data:
            if isinstance(s, dict) and s.get("skill_id") == skill_name:
                return {
                    "requires_env": s.get("requires_env", False),
                    "env_keys": s.get("env_keys", []),
                }
        return {"requires_env": False, "env_keys": []}
    else:
        info = skills_data.get(skill_name, {})
        return {
            "requires_env": info.get("requires_env", False),
            "env_keys": info.get("env_keys", []),
        } if isinstance(info, dict) else {"requires_env": False, "env_keys": []}


def check_external_env(skill_name: str, registry: Dict) -> Tuple[bool, List[str]]:
    req = get_external_env_requirements(registry, skill_name)
    missing = [k for k in req.get("env_keys", []) if not os.environ.get(k)]
    return len(missing) == 0, missing


# ========== 测试执行 ==========

def run_local_tests() -> Dict:
    """运行本地测试 - 只测试 docx, pdf, cron"""
    registry, err = load_registry()
    if err:
        return {"status": "error", "message": err, "results": []}
    
    smoke_skills = get_smoke_test_skills(registry)
    fixtures_dir = resolve_path("tests/fixtures/smoke")
    workspace = get_project_root()
    
    # 定义测试参数
    test_params = {
        "pdf": {"file_path": str(fixtures_dir / "blank.pdf")},
        "docx": {"file_path": str(fixtures_dir / "sample.docx")},
        "cron": {"expression": "*/5 * * * *"}
    }
    
    results = []
    for skill_name in smoke_skills:
        try:
            if str(workspace) not in sys.path:
                sys.path.insert(0, str(workspace))
            from execution.skill_gateway import SkillGateway
            gateway = SkillGateway()
            
            params = test_params.get(skill_name, {})
            result = gateway.execute(skill_name, params)
            results.append({
                "skill": skill_name,
                "status": "passed" if getattr(result, 'success', False) else "failed",
                "message": str(getattr(result, 'error', '') or '')[:100]
            })
        except Exception as e:
            results.append({"skill": skill_name, "status": "error", "message": str(e)[:100]})
    
    all_pass = all(r["status"] == "passed" for r in results) if results else True
    return {"status": "passed" if all_pass else "failed", "results": results}


def run_integration_tests() -> Dict:
    """运行集成测试 - 只测试 file-manager"""
    registry, err = load_registry()
    if err:
        return {"status": "error", "message": err, "results": []}
    
    integration_skills = get_skills_by_test_mode(registry, "integration")
    workspace = get_project_root()
    fixtures_dir = resolve_path("tests/fixtures/integration")
    
    # 定义测试参数
    test_params = {
        "file-manager": {
            "source_path": str(fixtures_dir / "file_manager" / "source" / "sample.txt"),
            "target_path": str(fixtures_dir / "file_manager" / "target" / "sample.txt"),
            "operation": "copy"
        }
    }
    
    # 只测试 file-manager
    test_skills = ["file-manager"] if "file-manager" in integration_skills else []
    
    results = []
    for skill_name in test_skills:
        try:
            if str(workspace) not in sys.path:
                sys.path.insert(0, str(workspace))
            from execution.skill_gateway import SkillGateway
            gateway = SkillGateway()
            params = test_params.get(skill_name, {})
            result = gateway.execute(skill_name, params)
            results.append({
                "skill": skill_name,
                "status": "passed" if getattr(result, 'success', False) else "failed",
                "message": str(getattr(result, 'error', '') or '')[:100]
            })
        except Exception as e:
            results.append({"skill": skill_name, "status": "error", "message": str(e)[:100]})
    
    pass_count = sum(1 for r in results if r["status"] == "passed")
    return {
        "status": "passed" if pass_count == len(results) else "failed",
        "results": results,
        "summary": f"{pass_count}/{len(results)} 通过"
    }


def run_external_tests() -> Dict:
    registry, err = load_registry()
    if err:
        return {"status": "error", "message": err, "results": []}
    
    external_skills = get_skills_by_test_mode(registry, "external")
    workspace = get_project_root()
    
    results = []
    for skill_name in external_skills:
        env_ok, missing = check_external_env(skill_name, registry)
        if not env_ok:
            results.append({"skill": skill_name, "status": "skipped", "message": f"缺少: {missing}"})
            continue
        try:
            if str(workspace) not in sys.path:
                sys.path.insert(0, str(workspace))
            from execution.skill_gateway import SkillGateway
            gateway = SkillGateway()
            result = gateway.execute(skill_name, {})
            results.append({
                "skill": skill_name,
                "status": "passed" if getattr(result, 'success', False) else "failed",
                "message": (getattr(result, 'error', '') or '')[:100]
            })
        except Exception as e:
            results.append({"skill": skill_name, "status": "error", "message": str(e)[:100]})
    
    pass_count = sum(1 for r in results if r["status"] == "pass")
    skip_count = sum(1 for r in results if r["status"] == "skipped")
    error_count = sum(1 for r in results if r["status"] == "error")
    
    return {
        "status": "passed" if pass_count == len(results) - skip_count and error_count == 0 else "failed",
        "results": results,
        "summary": f"{pass_count} 通过, {skip_count} 跳过, {error_count} 错误"
    }


# ========== Profile 门禁 ==========

PROFILE_RULES = {
    "premerge": {
        "p0_required": 0,
        "local_required": True,
        "integration_required": False,
        "external_required": False,
    },
    "nightly": {
        "p0_required": 0,
        "local_required": True,
        "integration_required": True,
        "external_required": False,
    },
    "release": {
        "p0_required": 0,
        "local_required": True,
        "integration_required": True,
        "external_required": "no_error",  # 允许 skipped，不允许 error
    },
}


def run_profile(profile: str, report_path: str = None) -> Dict:
    """运行指定 profile 的验收"""
    rules = PROFILE_RULES.get(profile, PROFILE_RULES["premerge"])
    root = get_project_root()
    
    # 扫描
    hardcoded = scan_hardcoded_paths()
    p0_count = len(hardcoded.get("P0", []))
    p1_count = len(hardcoded.get("P1", []))
    p2_count = len(hardcoded.get("P2", []))
    
    # 测试
    local_result = run_local_tests()
    integration_result = run_integration_tests()
    external_result = run_external_tests()
    
    # 判断
    passed = True
    reasons = []
    
    if p0_count > rules["p0_required"]:
        passed = False
        reasons.append(f"P0 硬编码路径: {p0_count} > {rules['p0_required']}")
    
    if rules["local_required"] and local_result["status"] != "passed":
        passed = False
        reasons.append(f"Local 层未通过: {local_result['status']}")
    
    if rules["integration_required"] and integration_result["status"] != "passed":
        passed = False
        reasons.append(f"Integration 层未通过: {integration_result['status']}")
    
    if rules["external_required"]:
        if rules["external_required"] == "no_error":
            error_count = sum(1 for r in external_result.get("results", []) if r["status"] == "error")
            if error_count > 0:
                passed = False
                reasons.append(f"External 层有 {error_count} 个错误")
        elif external_result["status"] != "passed":
            passed = False
            reasons.append(f"External 层未通过: {external_result['status']}")
    
    # 构建报告
    timestamp = datetime.now()
    report = {
        "profile": profile,
        "scope": "all",
        "verified_at": timestamp.isoformat(),
        "overall_passed": passed,
        "failure_reasons": reasons if not passed else [],
        "p0_count": p0_count,
        "p1_count": p1_count,
        "p2_count": p2_count,
        "local_status": local_result["status"],
        "local_results": local_result.get("results", []),
        "integration_status": integration_result["status"],
        "integration_results": integration_result.get("results", []),
        "external_status": external_result["status"],
        "external_results": external_result.get("results", []),
        "skipped_skills": [r for r in external_result.get("results", []) if r["status"] == "skipped"],
    }
    
    # 保存 latest 报告
    if report_path:
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 保存 profile 专属快照
        profile_report_path = str(report_path).replace(".json", f"_{profile}.json")
        with open(profile_report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 保存历史快照
    history_dir = root / "reports/history/runtime"
    history_dir.mkdir(parents=True, exist_ok=True)
    history_file = history_dir / f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{profile}.json"
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report


def print_report(report: Dict):
    """打印报告"""
    print("╔══════════════════════════════════════════════════╗")
    print(f"║  运行时验收 V5.0.0 - Profile: {report['profile']:<17}║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    print(f"【硬编码路径】 P0={report['p0_count']} P1={report['p1_count']} P2={report['p2_count']}")
    print()
    
    print(f"【Local】 {report['local_status']}")
    for r in report.get('local_results', []):
        print(f"  - {r['skill']}: {r['status']}")
    print()
    
    print(f"【Integration】 {report['integration_status']}")
    for r in report.get('integration_results', []):
        print(f"  - {r['skill']}: {r['status']}")
    print()
    
    print(f"【External】 {report['external_status']}")
    for r in report.get('external_results', []):
        print(f"  - {r['skill']}: {r['status']}")
    print()
    
    print("══════════════════════════════════════════════════")
    if report['overall_passed']:
        print(f"✅ {report['profile'].upper()} 门禁通过")
    else:
        print(f"❌ {report['profile'].upper()} 门禁失败")
        for reason in report.get('failure_reasons', []):
            print(f"   - {reason}")
    print("══════════════════════════════════════════════════")


def generate_status_matrix() -> List[Dict]:
    """生成状态矩阵"""
    registry, _ = load_registry()
    if not registry:
        return []
    
    # 运行测试获取状态
    local = run_local_tests()
    integration = run_integration_tests()
    external = run_external_tests()
    
    # 构建状态映射
    local_status = {r["skill"]: r["status"] for r in local.get("results", [])}
    integration_status = {r["skill"]: r["status"] for r in integration.get("results", [])}
    external_status = {r["skill"]: r["status"] for r in external.get("results", [])}
    skipped_reason = {r["skill"]: r.get("message", "") for r in external.get("results", []) if r["status"] == "skipped"}
    
    matrix = []
    for name, info in registry.get("skills", {}).items():
        if not isinstance(info, dict):
            continue
        env_req = get_external_env_requirements(registry, name)
        matrix.append({
            "skill_name": name,
            "registered": info.get("registered", False),
            "routable": info.get("routable", False),
            "callable": info.get("callable", False),
            "test_mode": info.get("test_mode", "none"),
            "smoke_test": info.get("smoke_test", False),
            "requires_env": env_req.get("requires_env", False),
            "env_keys": env_req.get("env_keys", []),
            "local_status": local_status.get(name, "not_tested"),
            "integration_status": integration_status.get(name, "not_tested"),
            "external_status": external_status.get(name, "not_tested"),
            "skipped_reason": skipped_reason.get(name, ""),
            "last_verified_at": datetime.now().isoformat()
        })
    return matrix


def main():
    import argparse
    parser = argparse.ArgumentParser(description="运行时一致性验收 V5.0.0")
    parser.add_argument("--scope", choices=["local", "integration", "external", "all"], default="local")
    parser.add_argument("--profile", choices=["premerge", "nightly", "release"], help="门禁模式")
    parser.add_argument("--report-json", help="JSON 报告输出路径")
    parser.add_argument("--matrix", action="store_true", help="输出状态矩阵")
    args = parser.parse_args()
    
    if args.matrix:
        print(json.dumps(generate_status_matrix(), ensure_ascii=False, indent=2))
        return 0
    
    if args.profile:
        report = run_profile(args.profile, args.report_json)
        print_report(report)
        return 0 if report["overall_passed"] else 1
    
    # 兼容旧 scope 模式
    print("使用 --profile 进行门禁验收")
    return 0


if __name__ == "__main__":
    sys.exit(main())
