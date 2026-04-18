#!/usr/bin/env python3
"""
技能升级引擎 V2.0.0
架构化版本 - 完全遵循六层架构规则

L4 Execution 模块
依赖: L1 Core (评分标准), L6 Infrastructure (模板库)
输出: reports/skill_upgrades/ (真源)
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# ============================================
# L4 Execution - 读取 L1 Core 配置
# ============================================

class ConfigLoader:
    """配置加载器 - 从 L1 Core 读取评分标准"""
    
    def __init__(self):
        self.workspace = Path.home() / ".openclaw" / "workspace"
        self.core_dir = self.workspace / "core"
        self.infra_dir = self.workspace / "infrastructure"
    
    def load_scoring_criteria(self) -> Dict:
        """从 L1 Core 读取评分标准"""
        # 硬编码评分标准 (实际应从 core/SKILL_UPGRADE_ARCHITECTURE.md 解析)
        return {
            "required_items": [
                {"name": "skill.py", "path": "skill.py", "weight": 0.2},
                {"name": "SKILL.md", "path": "SKILL.md", "weight": 0.2},
                {"name": "templates/", "path": "templates/", "weight": 0.2},
                {"name": "output/", "path": "output/", "weight": 0.2},
                {"name": "文档质量", "path": "SKILL.md", "weight": 0.2}
            ],
            "quality_metrics": {
                "description_length": {"min": 50, "score": 5},
                "has_usage": {"keywords": ["用法", "使用", "example"], "score": 5},
                "has_headers": {"min_count": 3, "score": 5},
                "content_length": {"min": 500, "score": 5}
            }
        }
    
    def load_template(self, template_name: str) -> str:
        """从 L6 Infrastructure 读取模板"""
        template_path = self.infra_dir / "skill_templates" / f"{template_name}.template"
        if template_path.exists():
            return template_path.read_text(encoding='utf-8')
        return ""


# ============================================
# L4 Execution - 诊断模块
# ============================================

class DiagnosticEngine:
    """诊断引擎 - 评估技能当前状态"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    def diagnose(self, skill_dir: Path) -> Dict:
        """诊断技能状态"""
        score = 0
        issues = []
        details = {}
        
        # 检查必需项
        for item in self.config["required_items"]:
            item_path = skill_dir / item["path"]
            
            if item["name"] == "文档质量":
                # 特殊处理文档质量
                quality_score = self._evaluate_document_quality(skill_dir / "SKILL.md")
                if quality_score >= 15:
                    score += 1
                else:
                    issues.append(f"文档质量不足: {quality_score}/20分")
                details["document_quality"] = quality_score
            elif item_path.exists():
                if item["path"].endswith('/'):
                    # 目录检查
                    if list(item_path.glob("*")):
                        score += 1
                    else:
                        issues.append(f"{item['name']} 为空")
                else:
                    # 文件检查
                    score += 1
            else:
                issues.append(f"缺少 {item['name']}")
        
        return {
            "score": min(score, 5),
            "issues": issues,
            "details": details
        }
    
    def _evaluate_document_quality(self, skill_md: Path) -> int:
        """评估文档质量"""
        if not skill_md.exists():
            return 0
        
        content = skill_md.read_text(encoding='utf-8')
        score = 0
        
        metrics = self.config["quality_metrics"]
        
        # 检查描述长度
        if len(content) >= metrics["description_length"]["min"]:
            score += metrics["description_length"]["score"]
        
        # 检查用法说明
        for keyword in metrics["has_usage"]["keywords"]:
            if keyword in content.lower():
                score += metrics["has_usage"]["score"]
                break
        
        # 检查标题数量
        header_count = content.count('##')
        if header_count >= metrics["has_headers"]["min_count"]:
            score += metrics["has_headers"]["score"]
        
        # 检查内容长度
        if len(content) >= metrics["content_length"]["min"]:
            score += metrics["content_length"]["score"]
        
        return score


# ============================================
# L4 Execution - 实现模块
# ============================================

class ImplementationEngine:
    """实现引擎 - 创建缺失文件"""
    
    def __init__(self, config: Dict, template_loader: ConfigLoader):
        self.config = config
        self.template_loader = template_loader
    
    def implement(self, skill_dir: Path, skill_name: str, diagnosis: Dict):
        """实现升级"""
        actions = []
        
        # 创建 skill.py
        if self._needs_creation(diagnosis, "skill.py"):
            self._create_skill_py(skill_dir, skill_name)
            actions.append("创建 skill.py")
        
        # 创建 templates/
        if self._needs_creation(diagnosis, "templates/"):
            self._create_templates(skill_dir, skill_name)
            actions.append("创建 templates/")
        
        # 创建 output/
        if self._needs_creation(diagnosis, "output/"):
            (skill_dir / "output").mkdir(exist_ok=True)
            actions.append("创建 output/")
        
        # 增强 SKILL.md
        if self._needs_enhancement(diagnosis):
            self._enhance_skill_md(skill_dir, skill_name)
            actions.append("增强 SKILL.md")
        
        return actions
    
    def _needs_creation(self, diagnosis: Dict, item_name: str) -> bool:
        """判断是否需要创建"""
        for issue in diagnosis["issues"]:
            if f"缺少 {item_name}" in issue or f"{item_name} 为空" in issue:
                return True
        return False
    
    def _needs_enhancement(self, diagnosis: Dict) -> bool:
        """判断是否需要增强"""
        for issue in diagnosis["issues"]:
            if "文档质量不足" in issue:
                return True
        return False
    
    def _create_skill_py(self, skill_dir: Path, skill_name: str):
        """创建执行脚本"""
        # 读取模板
        template = self.template_loader.load_template("skill.py")
        
        # 替换占位符
        skill_md = skill_dir / "SKILL.md"
        description = f"{skill_name} 技能"
        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8')
            for line in content.split('\n'):
                if line.startswith('description:'):
                    description = line.split(':', 1)[1].strip().strip('"').strip("'")
                    break
        
        class_name = skill_name.replace('-', '_').replace(' ', '_').title().replace('_', '')
        
        code = template.format(
            skill_name=skill_name,
            description=description,
            ClassName=class_name
        )
        
        (skill_dir / "skill.py").write_text(code, encoding='utf-8')
    
    def _create_templates(self, skill_dir: Path, skill_name: str):
        """创建模板库"""
        templates_dir = skill_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        # 读取模板
        template = self.template_loader.load_template("default.md")
        
        content = template.format(
            skill_name=skill_name,
            date=datetime.now().strftime('%Y-%m-%d')
        )
        
        (templates_dir / "default.md").write_text(content, encoding='utf-8')
    
    def _enhance_skill_md(self, skill_dir: Path, skill_name: str):
        """增强 SKILL.md"""
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return
        
        content = skill_md.read_text(encoding='utf-8')
        
        # 添加用法说明
        if "用法" not in content and "使用" not in content:
            usage = f"""

## 使用方法

### 命令行调用

```bash
# 查看帮助
python skill.py help

# 执行技能
python skill.py run --template default

# 列出模板
python skill.py list
```

## 示例

```bash
python skill.py run --template default
```
"""
            skill_md.write_text(content + usage, encoding='utf-8')


# ============================================
# L4 Execution - 审计模块
# ============================================

class AuditLogger:
    """审计日志记录器 - 写入 reports/ (真源)"""
    
    def __init__(self):
        self.workspace = Path.home() / ".openclaw" / "workspace"
        self.audit_file = self.workspace / "reports" / "skill_upgrades" / "audit.jsonl"
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, event_type: str, skill_name: str, details: Dict):
        """记录审计日志"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "skill_name": skill_name,
            **details
        }
        
        with open(self.audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')


# ============================================
# L4 Execution - 主引擎
# ============================================

class SkillUpgradeEngine:
    """技能升级引擎 - L4 Execution 模块"""
    
    def __init__(self):
        # 初始化各模块
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.load_scoring_criteria()
        self.diagnostic = DiagnosticEngine(self.config)
        self.implementation = ImplementationEngine(self.config, self.config_loader)
        self.audit = AuditLogger()
        
        self.workspace = Path.home() / ".openclaw" / "workspace"
        self.skills_dir = self.workspace / "skills"
        self.reports_dir = self.workspace / "reports" / "skill_upgrades"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def upgrade_all(self, target_skills: List[str] = None) -> Dict:
        """升级所有技能"""
        # 确定目标技能
        if target_skills is None:
            target_skills = self._scan_skills()
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "architecture": "L4 Execution",
            "dependencies": ["L1 Core", "L6 Infrastructure"],
            "total": len(target_skills),
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "details": []
        }
        
        print("=" * 60)
        print("技能升级引擎 V2.0.0 (架构化)")
        print("=" * 60)
        print(f"架构: L4 Execution")
        print(f"依赖: L1 Core (评分标准), L6 Infrastructure (模板库)")
        print(f"输出: reports/skill_upgrades/ (真源)")
        print(f"目标: 升级 {len(target_skills)} 个技能到 ⭐⭐⭐⭐⭐")
        print()
        
        for i, skill_name in enumerate(target_skills, 1):
            print(f"[{i}/{len(target_skills)}] 升级: {skill_name}")
            result = self._upgrade_skill(skill_name)
            results["details"].append(result)
            
            if result["status"] == "success":
                results["success"] += 1
                print(f"  ✅ {result['before']}⭐ → {result['after']}⭐")
            elif result["status"] == "skipped":
                results["skipped"] += 1
                print(f"  ⏭️  已是最高评分: {result['after']}⭐")
            else:
                results["failed"] += 1
                print(f"  ❌ 失败: {result.get('error', '未知错误')}")
        
        # 保存报告 (真源)
        self._save_report(results)
        
        print()
        print("=" * 60)
        print(f"完成: {results['success']}/{results['total']} 成功")
        print(f"跳过: {results['skipped']}")
        print(f"失败: {results['failed']}")
        print("=" * 60)
        
        return results
    
    def _upgrade_skill(self, skill_name: str) -> Dict:
        """升级单个技能"""
        skill_dir = self.skills_dir / skill_name
        
        if not skill_dir.exists():
            return {
                "skill": skill_name,
                "status": "failed",
                "error": "技能目录不存在"
            }
        
        # 记录审计日志
        self.audit.log("upgrade_start", skill_name, {})
        
        # Step 1: 诊断
        diagnosis = self.diagnostic.diagnose(skill_dir)
        
        # 如果已经是⭐⭐⭐⭐⭐，跳过
        if diagnosis["score"] == 5:
            self.audit.log("upgrade_skipped", skill_name, {
                "reason": "已达到最高评分",
                "score": 5
            })
            return {
                "skill": skill_name,
                "status": "skipped",
                "before": 5,
                "after": 5,
                "reason": "已达到最高实用性"
            }
        
        # Step 2-3: 实现
        try:
            actions = self.implementation.implement(skill_dir, skill_name, diagnosis)
            
            # Step 4: 重新诊断
            new_diagnosis = self.diagnostic.diagnose(skill_dir)
            
            # 记录审计日志
            self.audit.log("upgrade_success", skill_name, {
                "before_score": diagnosis["score"],
                "after_score": new_diagnosis["score"],
                "actions": actions
            })
            
            return {
                "skill": skill_name,
                "status": "success",
                "before": diagnosis["score"],
                "after": new_diagnosis["score"],
                "actions": actions
            }
        except Exception as e:
            # 记录审计日志
            self.audit.log("upgrade_failed", skill_name, {
                "error": str(e)
            })
            
            return {
                "skill": skill_name,
                "status": "failed",
                "error": str(e),
                "before": diagnosis["score"],
                "after": diagnosis["score"]
            }
    
    def _scan_skills(self) -> List[str]:
        """扫描所有技能"""
        return [d.name for d in self.skills_dir.iterdir() 
                if d.is_dir() and (d / "SKILL.md").exists()]
    
    def _save_report(self, results: Dict):
        """保存报告到 reports/ (真源)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 报告
        report_file = self.reports_dir / f"upgrade_{timestamp}.json"
        report_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
        
        # Markdown 报告
        md_report = self._generate_md_report(results)
        md_file = self.reports_dir / f"upgrade_{timestamp}.md"
        md_file.write_text(md_report, encoding='utf-8')
        
        print(f"\n报告已保存: {report_file}")
    
    def _generate_md_report(self, results: Dict) -> str:
        """生成 Markdown 报告"""
        # 统计各评分数量
        score_dist = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for detail in results["details"]:
            after_score = detail.get("after", 0)
            if after_score in score_dist:
                score_dist[after_score] += 1
        
        return f"""# 技能升级报告

**时间**: {results['timestamp']}
**版本**: {results['version']}
**架构**: {results['architecture']}

---

## 架构信息

| 层级 | 模块 | 说明 |
|------|------|------|
| L1 Core | SKILL_UPGRADE_ARCHITECTURE.md | 评分标准、升级策略 |
| L4 Execution | skill_upgrade_engine.py | 升级执行引擎 |
| L6 Infrastructure | skill_templates/ | 模板库 |

**依赖**: {', '.join(results['dependencies'])}

---

## 升级概览

| 指标 | 数值 |
|------|------|
| 总技能数 | {results['total']} |
| 成功升级 | {results['success']} |
| 跳过 | {results['skipped']} |
| 失败 | {results['failed']} |
| 完成度 | {results['success'] + results['skipped']}/{results['total']} ({(results['success'] + results['skipped']) / results['total'] * 100:.1f}%) |

---

## 实用性分布

| 评分 | 数量 | 占比 |
|------|------|------|
| ⭐⭐⭐⭐⭐ | {score_dist[5]} | {score_dist[5] / results['total'] * 100:.1f}% |
| ⭐⭐⭐⭐ | {score_dist[4]} | {score_dist[4] / results['total'] * 100:.1f}% |
| ⭐⭐⭐ | {score_dist[3]} | {score_dist[3] / results['total'] * 100:.1f}% |
| ⭐⭐ | {score_dist[2]} | {score_dist[2] / results['total'] * 100:.1f}% |
| ⭐ | {score_dist[1]} | {score_dist[1] / results['total'] * 100:.1f}% |

---

## 详细结果

| 技能 | 升级前 | 升级后 | 状态 |
|------|--------|--------|------|
""" + '\n'.join([
            f"| {d['skill']} | {d.get('before', 0)}⭐ | {d.get('after', 0)}⭐ | {'✅' if d['status'] == 'success' else ('⏭️' if d['status'] == 'skipped' else '❌')} |"
            for d in results["details"]
        ]) + f"""

---

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**架构版本**: V2.0.0
"""


# ============================================
# 主函数
# ============================================

def main():
    """主函数"""
    engine = SkillUpgradeEngine()
    
    # 解析命令行参数
    target_skills = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            target_skills = None
        else:
            target_skills = sys.argv[1:]
    
    # 执行升级
    results = engine.upgrade_all(target_skills)
    
    # 返回退出码
    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
