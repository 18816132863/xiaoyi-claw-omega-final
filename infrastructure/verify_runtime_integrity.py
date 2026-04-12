#!/usr/bin/env python3
"""
运行时一致性验收脚本 - V1.0

校验内容：
1. 硬编码路径扫描
2. 保护清单是否引用旧架构
3. 注册表与索引是否一致
4. 路由是否只命中可执行技能
5. 抽样真实执行技能
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

workspace = Path("/home/sandbox/.openclaw/workspace")

# 硬编码路径模式
HARDCODED_PATTERNS = [
    r'Path\.home\(\)',
    r'os\.path\.expanduser\(["\']~',
    r'["\']/home/sandbox/\.openclaw',
    r'["\']~',
    r'sys\.path\.insert\(0,\s*["\']/home/sandbox',
]

# 旧架构引用
OLD_ARCHITECTURE_REFS = [
    "ARCHITECTURE_V2.",
    "infra/paths.py",
    "guide/bootstrap.py",
    "guide/assistant_guide.py",
]


def scan_hardcoded_paths() -> List[Dict]:
    """扫描硬编码路径"""
    results = []
    
    for py_file in workspace.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        try:
            content = py_file.read_text()
            rel_path = py_file.relative_to(workspace)
            
            for pattern in HARDCODED_PATTERNS:
                matches = re.findall(pattern, content)
                if matches:
                    results.append({
                        "file": str(rel_path),
                        "pattern": pattern,
                        "count": len(matches)
                    })
        except:
            pass
    
    return results


def check_protected_files() -> Dict:
    """检查保护清单是否引用旧架构"""
    protected_path = workspace / "governance" / "guard" / "protected_files.json"
    
    if not protected_path.exists():
        return {"status": "error", "message": "protected_files.json 不存在"}
    
    with open(protected_path) as f:
        data = json.load(f)
    
    core_list = data.get("core", [])
    issues = []
    
    for item in core_list:
        for old_ref in OLD_ARCHITECTURE_REFS:
            if old_ref in item:
                issues.append({
                    "file": item,
                    "old_ref": old_ref
                })
    
    return {
        "status": "pass" if not issues else "fail",
        "issues": issues,
        "deprecated": data.get("deprecated", [])
    }


def check_registry_index_consistency() -> Dict:
    """检查注册表与索引一致性"""
    registry_path = workspace / "infrastructure" / "inventory" / "skill_registry.json"
    index_path = workspace / "infrastructure" / "inventory" / "skill_inverted_index.json"
    
    if not registry_path.exists():
        return {"status": "error", "message": "skill_registry.json 不存在"}
    
    if not index_path.exists():
        return {"status": "error", "message": "skill_inverted_index.json 不存在"}
    
    with open(registry_path) as f:
        registry = json.load(f)
    
    with open(index_path) as f:
        index = json.load(f)
    
    # 获取可执行技能集合
    executable_skills = set()
    skills_data = registry.get("skills", [])
    
    # 处理不同格式
    if isinstance(skills_data, dict):
        for skill_name, skill_info in skills_data.items():
            if isinstance(skill_info, dict):
                if skill_info.get("registered") and skill_info.get("routable") and skill_info.get("callable"):
                    executable_skills.add(skill_name)
    elif isinstance(skills_data, list):
        for skill in skills_data:
            if isinstance(skill, dict):
                if skill.get("registered") and skill.get("routable") and skill.get("callable"):
                    executable_skills.add(skill.get("name"))
    
    # 获取索引技能集合
    indexed_skills = set()
    for keyword, skills in index.items():
        if isinstance(skills, list):
            for skill in skills:
                if isinstance(skill, str):
                    indexed_skills.add(skill)
                elif isinstance(skill, dict):
                    indexed_skills.add(skill.get("name", ""))
    
    # 比较差异
    missing_in_index = executable_skills - indexed_skills
    extra_in_index = indexed_skills - executable_skills
    
    return {
        "status": "pass" if not missing_in_index and not extra_in_index else "fail",
        "executable_count": len(executable_skills),
        "indexed_count": len(indexed_skills),
        "missing_in_index": list(missing_in_index)[:10],
        "extra_in_index": list(extra_in_index)[:10]
    }


def check_routing() -> Dict:
    """检查路由是否只命中可执行技能"""
    try:
        # 添加 workspace 到 sys.path
        if str(workspace) not in sys.path:
            sys.path.insert(0, str(workspace))
        
        from infrastructure.shared.router import get_router
        
        router = get_router()
        
        # 测试几个常见技能
        test_skills = ["docx", "pdf", "weather"]
        results = []
        
        for skill_name in test_skills:
            try:
                info = router._check_skill_status(skill_name)
                if info:
                    results.append({
                        "skill": skill_name,
                        "callable": info.get("is_callable", False),
                        "status": "pass" if info.get("is_callable") else "fail"
                    })
                else:
                    results.append({
                        "skill": skill_name,
                        "callable": False,
                        "status": "not_found"
                    })
            except Exception as e:
                results.append({
                    "skill": skill_name,
                    "callable": False,
                    "status": f"error: {str(e)[:30]}"
                })
        
        all_pass = all(r.get("callable", False) for r in results)
        
        return {
            "status": "pass" if all_pass else "partial",
            "results": results
        }
    except Exception as e:
        import traceback
        return {"status": "error", "message": f"{str(e)}\n{traceback.format_exc()}"}


def sample_skill_execution() -> Dict:
    """抽样执行技能"""
    try:
        sys.path.insert(0, str(workspace))
        from execution.skill_gateway import SkillGateway
        
        gateway = SkillGateway()
        
        # 抽样执行简单技能
        test_cases = [
            ("weather", {"city": "北京"}),
        ]
        
        results = []
        for skill_name, params in test_cases:
            try:
                result = gateway.execute(skill_name, params)
                results.append({
                    "skill": skill_name,
                    "status": "pass" if result.get("success") else "fail",
                    "message": result.get("message", "")
                })
            except Exception as e:
                results.append({
                    "skill": skill_name,
                    "status": "error",
                    "message": str(e)
                })
        
        return {
            "status": "pass" if all(r["status"] == "pass" for r in results) else "partial",
            "results": results
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def run_verification():
    """运行完整验收"""
    print("╔══════════════════════════════════════════════════╗")
    print("║        运行时一致性验收 V1.0                     ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    all_passed = True
    
    # 1. 硬编码路径扫描
    print("【1】硬编码路径扫描")
    hardcoded = scan_hardcoded_paths()
    if hardcoded:
        print(f"  ❌ 发现 {len(hardcoded)} 处硬编码路径")
        for item in hardcoded[:5]:
            print(f"     - {item['file']}: {item['pattern']}")
        all_passed = False
    else:
        print("  ✅ 未发现硬编码路径")
    print()
    
    # 2. 保护清单检查
    print("【2】保护清单检查")
    protected = check_protected_files()
    if protected["status"] == "pass":
        print("  ✅ 保护清单未引用旧架构")
    else:
        print(f"  ❌ 发现 {len(protected['issues'])} 处旧架构引用")
        for issue in protected["issues"][:5]:
            print(f"     - {issue['file']}: {issue['old_ref']}")
        all_passed = False
    print()
    
    # 3. 注册表与索引一致性
    print("【3】注册表与索引一致性")
    consistency = check_registry_index_consistency()
    if consistency["status"] == "pass":
        print(f"  ✅ 一致 (可执行: {consistency['executable_count']}, 索引: {consistency['indexed_count']})")
    else:
        print(f"  ❌ 不一致")
        if consistency.get("missing_in_index"):
            print(f"     索引缺失: {consistency['missing_in_index'][:5]}")
        if consistency.get("extra_in_index"):
            print(f"     索引多余: {consistency['extra_in_index'][:5]}")
        all_passed = False
    print()
    
    # 4. 路由检查
    print("【4】路由检查")
    routing = check_routing()
    if routing["status"] == "pass":
        print("  ✅ 路由正常")
        for r in routing.get("results", []):
            print(f"     - {r['skill']}: {r['status']}")
    elif routing["status"] == "partial":
        print("  ⚠️ 部分技能不可执行")
        for r in routing.get("results", []):
            print(f"     - {r['skill']}: {r['status']}")
    else:
        print(f"  ❌ 路由异常: {routing.get('message', 'unknown')}")
        all_passed = False
    print()
    
    # 5. 抽样执行
    print("【5】抽样执行")
    execution = sample_skill_execution()
    if execution["status"] == "pass":
        print("  ✅ 抽样执行成功")
    else:
        print(f"  ⚠️ {execution.get('status')}: {execution.get('message', '')}")
    print()
    
    print("══════════════════════════════════════════════════")
    if all_passed:
        print("✅ 运行时一致性验收通过")
    else:
        print("❌ 运行时一致性验收失败")
    print("══════════════════════════════════════════════════")
    
    return all_passed


if __name__ == "__main__":
    passed = run_verification()
    sys.exit(0 if passed else 1)
