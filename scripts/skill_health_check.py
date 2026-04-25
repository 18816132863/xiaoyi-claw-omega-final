#!/usr/bin/env python3
"""
技能健康检查脚本 - V1.0.0

检查技能的完整性和配置正确性。
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class HealthIssue:
    skill: str
    severity: str  # critical, warning, info
    category: str
    message: str


def check_skill_md(skill_name: str, skill_path: Path) -> List[HealthIssue]:
    """检查 SKILL.md 文件"""
    issues = []
    skill_md = skill_path / "SKILL.md"
    
    if not skill_md.exists():
        issues.append(HealthIssue(skill_name, "critical", "missing_file", "缺少 SKILL.md"))
        return issues
    
    content = skill_md.read_text(encoding='utf-8', errors='ignore')
    
    # 检查必要字段
    if 'name:' not in content:
        issues.append(HealthIssue(skill_name, "warning", "missing_field", "SKILL.md 缺少 name 字段"))
    if 'description:' not in content:
        issues.append(HealthIssue(skill_name, "warning", "missing_field", "SKILL.md 缺少 description 字段"))
    
    return issues


def check_skill_py(skill_name: str, skill_path: Path, registry_info: Dict) -> List[HealthIssue]:
    """检查 skill.py 文件"""
    issues = []
    skill_py = skill_path / "skill.py"
    executor_type = registry_info.get('executor_type', 'skill_md')
    
    if executor_type == 'skill_md':
        # skill_md 类型不需要 skill.py
        return issues
    
    if not skill_py.exists():
        issues.append(HealthIssue(skill_name, "critical", "missing_file", "缺少 skill.py"))
        return issues
    
    content = skill_py.read_text(encoding='utf-8', errors='ignore')
    
    # 检查 run 函数
    if 'def run(' not in content:
        issues.append(HealthIssue(skill_name, "critical", "missing_function", "skill.py 缺少 run 函数"))
    
    return issues


def check_registry_config(skill_name: str, registry_info: Dict) -> List[HealthIssue]:
    """检查注册表配置"""
    issues = []
    
    required_fields = ['name', 'category', 'risk_level', 'timeout', 'layer']
    for field in required_fields:
        if field not in registry_info:
            issues.append(HealthIssue(skill_name, "warning", "missing_config", f"注册表缺少 {field} 字段"))
    
    # 检查分类
    if registry_info.get('category') == 'other':
        issues.append(HealthIssue(skill_name, "info", "uncategorized", "技能未分类"))
    
    # 检查测试配置
    if not registry_info.get('testable'):
        issues.append(HealthIssue(skill_name, "info", "no_test", "未配置测试"))
    
    return issues


def check_requirements(skill_name: str, skill_path: Path, registry_info: Dict) -> List[HealthIssue]:
    """检查依赖配置"""
    issues = []
    
    deps = registry_info.get('dependencies', [])
    req_file = skill_path / "requirements.txt"
    
    if deps and not req_file.exists():
        issues.append(HealthIssue(skill_name, "warning", "missing_requirements", 
                                  f"注册表有依赖但缺少 requirements.txt"))
    
    return issues


def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║          技能健康检查 V1.0.0                    ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    # 加载注册表
    registry_path = Path("infrastructure/inventory/skill_registry.json")
    if not registry_path.exists():
        print("错误: 技能注册表不存在")
        return 1
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    skills_dir = Path("skills")
    all_issues: List[HealthIssue] = []
    
    # 检查每个技能
    skills_data = registry.get('skills', {})
    
    # 兼容两种格式：数组格式和对象格式
    if isinstance(skills_data, list):
        # 数组格式
        for skill_info in skills_data:
            skill_name = skill_info.get('skill_id', 'unknown')
            if not isinstance(skill_info, dict):
                continue
            
            skill_path = skills_dir / skill_name
            
            # 检查目录存在
            if not skill_path.exists():
                all_issues.append(HealthIssue(skill_name, "critical", "missing_dir", "技能目录不存在"))
                continue
            
            # 运行各项检查
            all_issues.extend(check_skill_md(skill_name, skill_path))
            all_issues.extend(check_skill_py(skill_name, skill_path, skill_info))
            all_issues.extend(check_registry_config(skill_name, skill_info))
            all_issues.extend(check_requirements(skill_name, skill_path, skill_info))
    else:
        # 对象格式
        for skill_name, skill_info in skills_data.items():
            if not isinstance(skill_info, dict):
                continue
            
            skill_path = skills_dir / skill_name
            
            # 检查目录存在
            if not skill_path.exists():
                all_issues.append(HealthIssue(skill_name, "critical", "missing_dir", "技能目录不存在"))
                continue
            
            # 运行各项检查
            all_issues.extend(check_skill_md(skill_name, skill_path))
            all_issues.extend(check_skill_py(skill_name, skill_path, skill_info))
            all_issues.extend(check_registry_config(skill_name, skill_info))
            all_issues.extend(check_requirements(skill_name, skill_path, skill_info))
    
    # 统计
    critical = [i for i in all_issues if i.severity == 'critical']
    warning = [i for i in all_issues if i.severity == 'warning']
    info = [i for i in all_issues if i.severity == 'info']
    
    skills_data = registry.get('skills', {})
    total_skills = len(skills_data) if isinstance(skills_data, list) else len(skills_data)
    
    print(f"【检查结果】")
    print(f"  总技能数: {total_skills}")
    print(f"  总问题数: {len(all_issues)}")
    print()
    
    print(f"【严重程度分布】")
    print(f"  🔴 严重: {len(critical)}")
    print(f"  🟡 警告: {len(warning)}")
    print(f"  🔵 信息: {len(info)}")
    print()
    
    # 显示严重问题
    if critical:
        print("【严重问题】")
        for issue in critical[:20]:
            print(f"  🔴 {issue.skill}: {issue.message}")
        if len(critical) > 20:
            print(f"  ... 还有 {len(critical) - 20} 个")
        print()
    
    # 显示警告
    if warning:
        print("【警告问题】")
        for issue in warning[:10]:
            print(f"  🟡 {issue.skill}: {issue.message}")
        if len(warning) > 10:
            print(f"  ... 还有 {len(warning) - 10} 个")
        print()
    
    # 按类别统计
    print("【问题类别分布】")
    from collections import Counter
    categories = Counter(i.category for i in all_issues)
    for cat, count in categories.most_common():
        print(f"  {cat}: {count}")
    
    # 返回码
    return 1 if critical else 0


if __name__ == "__main__":
    sys.exit(main())
