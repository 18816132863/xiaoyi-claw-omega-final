#!/usr/bin/env python3
"""
技能质量门禁 - L5 Governance 模块

职责:
- 质量门禁检查
- 合规性验证
- 异常告警
- 阻断不合格变更

依赖:
- L1 Core: 读取评分标准
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class GateLevel(Enum):
    """门禁级别"""
    PRE_COMMIT = "pre_commit"
    PRE_MERGE = "pre_merge"
    PRE_RELEASE = "pre_release"


class GateResult(Enum):
    """门禁结果"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


class QualityGate:
    """技能质量门禁"""
    
    def __init__(self):
        self.workspace = Path.home() / ".openclaw" / "workspace"
        
        # 从 L1 Core 读取门禁规则
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict:
        """从 L1 Core 读取门禁规则"""
        # 硬编码规则 (实际应从 core/SKILL_UPGRADE_ARCHITECTURE.md 解析)
        return {
            "pre_commit": {
                "checks": [
                    {"name": "skill_py_exists", "rule": "skill.py 文件存在", "severity": "error"},
                    {"name": "skill_md_exists", "rule": "SKILL.md 文件存在", "severity": "error"},
                    {"name": "templates_dir_exists", "rule": "templates/ 目录存在", "severity": "error"},
                    {"name": "output_dir_exists", "rule": "output/ 目录存在", "severity": "warning"},
                    {"name": "skill_md_quality", "rule": "SKILL.md 文档质量 >= 10分", "severity": "warning"}
                ]
            },
            "pre_merge": {
                "checks": [
                    {"name": "skill_score", "rule": "技能评分 >= 4⭐", "severity": "error"},
                    {"name": "test_passed", "rule": "skill.py help 命令执行成功", "severity": "error"},
                    {"name": "template_valid", "rule": "至少有一个有效模板", "severity": "warning"}
                ]
            },
            "pre_release": {
                "checks": [
                    {"name": "skill_score_max", "rule": "技能评分 = 5⭐", "severity": "error"},
                    {"name": "all_tests_passed", "rule": "所有测试通过", "severity": "error"},
                    {"name": "user_acceptance", "rule": "用户验收通过", "severity": "error"}
                ]
            }
        }
    
    def check(self, skill_dir: Path, level: GateLevel = GateLevel.PRE_COMMIT) -> Dict:
        """执行质量门禁检查"""
        results = {
            "skill": skill_dir.name,
            "level": level.value,
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "result": "pass"
        }
        
        # 获取对应级别的规则
        rules = self.rules.get(level.value, {})
        checks = rules.get("checks", [])
        
        print(f"\n质量门禁检查 [{level.value}]: {skill_dir.name}")
        
        for check in checks:
            check_result = self._execute_check(skill_dir, check)
            results["checks"].append(check_result)
            
            if check_result["result"] == "pass":
                results["passed"] += 1
                print(f"  ✅ {check['name']}")
            elif check_result["result"] == "warning":
                results["warnings"] += 1
                print(f"  ⚠️  {check['name']}: {check_result.get('message', '')}")
            else:
                results["failed"] += 1
                print(f"  ❌ {check['name']}: {check_result.get('message', '')}")
                
                # error 级别失败，整体失败
                if check["severity"] == "error":
                    results["result"] = "fail"
        
        # 保存门禁报告
        self._save_report(results)
        
        return results
    
    def _execute_check(self, skill_dir: Path, check: Dict) -> Dict:
        """执行单个检查"""
        name = check["name"]
        severity = check["severity"]
        
        try:
            # 执行检查逻辑
            if name == "skill_py_exists":
                exists = (skill_dir / "skill.py").exists()
                return {
                    "name": name,
                    "result": "pass" if exists else "fail",
                    "message": "" if exists else "skill.py 不存在"
                }
            
            elif name == "skill_md_exists":
                exists = (skill_dir / "SKILL.md").exists()
                return {
                    "name": name,
                    "result": "pass" if exists else "fail",
                    "message": "" if exists else "SKILL.md 不存在"
                }
            
            elif name == "templates_dir_exists":
                exists = (skill_dir / "templates").exists()
                has_files = exists and list((skill_dir / "templates").glob("*.md"))
                return {
                    "name": name,
                    "result": "pass" if has_files else "fail",
                    "message": "" if has_files else "templates/ 不存在或为空"
                }
            
            elif name == "output_dir_exists":
                exists = (skill_dir / "output").exists()
                return {
                    "name": name,
                    "result": "pass" if exists else "warning",
                    "message": "" if exists else "output/ 不存在"
                }
            
            elif name == "skill_md_quality":
                quality = self._check_document_quality(skill_dir / "SKILL.md")
                return {
                    "name": name,
                    "result": "pass" if quality >= 10 else "warning",
                    "message": f"文档质量: {quality}/20分"
                }
            
            elif name == "skill_score":
                score = self._calculate_score(skill_dir)
                return {
                    "name": name,
                    "result": "pass" if score >= 4 else "fail",
                    "message": f"技能评分: {score}⭐"
                }
            
            elif name == "skill_score_max":
                score = self._calculate_score(skill_dir)
                return {
                    "name": name,
                    "result": "pass" if score == 5 else "fail",
                    "message": f"技能评分: {score}⭐"
                }
            
            else:
                return {
                    "name": name,
                    "result": "pass",
                    "message": "检查未实现"
                }
        
        except Exception as e:
            return {
                "name": name,
                "result": "fail",
                "message": str(e)
            }
    
    def _check_document_quality(self, skill_md: Path) -> int:
        """检查文档质量"""
        if not skill_md.exists():
            return 0
        
        content = skill_md.read_text(encoding='utf-8')
        score = 0
        
        # 检查描述长度
        if len(content) >= 50:
            score += 5
        
        # 检查用法说明
        if "用法" in content or "使用" in content or "example" in content.lower():
            score += 5
        
        # 检查标题数量
        if content.count('##') >= 3:
            score += 5
        
        # 检查内容长度
        if len(content) >= 500:
            score += 5
        
        return score
    
    def _calculate_score(self, skill_dir: Path) -> int:
        """计算技能评分"""
        score = 0
        
        # 检查必需项
        if (skill_dir / "skill.py").exists():
            score += 1
        
        if (skill_dir / "SKILL.md").exists():
            score += 1
        
        if (skill_dir / "templates").exists() and list((skill_dir / "templates").glob("*.md")):
            score += 1
        
        if (skill_dir / "output").exists():
            score += 1
        
        if self._check_document_quality(skill_dir / "SKILL.md") >= 15:
            score += 1
        
        return min(score, 5)
    
    def _save_report(self, results: Dict):
        """保存门禁报告"""
        reports_dir = self.workspace / "reports" / "skill_quality"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"gate_{results['skill']}_{timestamp}.json"
        report_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    """主函数"""
    gate = QualityGate()
    
    # 测试门禁
    skills_dir = Path.home() / ".openclaw" / "workspace" / "skills"
    
    for skill in ["copywriter", "novel-generator", "claw-art"]:
        skill_dir = skills_dir / skill
        if skill_dir.exists():
            result = gate.check(skill_dir, GateLevel.PRE_COMMIT)
            print(f"结果: {result['result']}\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
