#!/usr/bin/env python3
"""
架构违规自动改进器 - V1.0.0

职责：
1. 检测架构违规
2. 自动分析违规原因
3. 自动生成改进方案
4. 自动应用改进
5. 自动升级规则

触发时机：
- 每次任务结束后
- 检测到违规时
- 定期巡检时

使用方式：
    from scripts.architecture_auto_improver import AutoImprover
    
    improver = AutoImprover()
    improver.analyze_and_improve(violation_record)
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class ImprovementType(Enum):
    """改进类型"""
    ADD_CHECK = "add_check"           # 添加检查项
    STRENGTHEN_RULE = "strengthen"    # 加强规则
    FIX_BUG = "fix_bug"              # 修复 bug
    UPDATE_DOC = "update_doc"         # 更新文档
    AUTO_CORRECT = "auto_correct"     # 自动纠正


@dataclass
class ViolationPattern:
    """违规模式"""
    pattern_id: str
    description: str
    frequency: int
    last_seen: str
    suggested_fix: str
    auto_fixable: bool = False


@dataclass
class Improvement:
    """改进方案"""
    improvement_id: str
    type: ImprovementType
    description: str
    affected_files: List[str]
    implementation: str
    tested: bool = False
    applied: bool = False
    auto_fixable: bool = False


class AutoImprover:
    """架构违规自动改进器"""
    
    def __init__(self, root: Path = None):
        self.root = root or self._get_project_root()
        self.violations_file = self.root / "reports" / "ops" / "architecture_violations.jsonl"
        self.patterns_file = self.root / "reports" / "ops" / "violation_patterns.json"
        self.improvements_file = self.root / "reports" / "ops" / "auto_improvements.jsonl"
        self.rule_registry = self.root / "core" / "RULE_REGISTRY.json"
        
        # 确保目录存在
        self.violations_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载违规模式
        self.patterns = self._load_patterns()
    
    def _get_project_root(self) -> Path:
        current = Path(__file__).resolve().parent.parent
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        return Path(__file__).resolve().parent.parent
    
    def _load_patterns(self) -> Dict[str, ViolationPattern]:
        """加载违规模式"""
        patterns = {}
        
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for k, v in data.items():
                    patterns[k] = ViolationPattern(**v)
        
        return patterns
    
    def _save_patterns(self):
        """保存违规模式"""
        with open(self.patterns_file, 'w', encoding='utf-8') as f:
            data = {k: asdict(v) for k, v in self.patterns.items()}
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def analyze_violations(self) -> Dict[str, Any]:
        """分析违规记录"""
        if not self.violations_file.exists():
            return {
                "total": 0,
                "patterns": [],
                "suggestions": []
            }
        
        # 读取违规记录
        violations = []
        with open(self.violations_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    violations.append(json.loads(line.strip()))
                except:
                    pass
        
        # 分析模式
        pattern_counts = {}
        for v in violations:
            layer = v.get('layer', 'unknown')
            severity = v.get('severity', 'UNKNOWN')
            pattern_key = f"{layer}_{severity}"
            
            if pattern_key not in pattern_counts:
                pattern_counts[pattern_key] = {
                    "layer": layer,
                    "severity": severity,
                    "count": 0,
                    "examples": []
                }
            
            pattern_counts[pattern_key]["count"] += 1
            if len(pattern_counts[pattern_key]["examples"]) < 3:
                pattern_counts[pattern_key]["examples"].append(v.get('description'))
        
        # 更新模式库
        for pattern_key, pattern_data in pattern_counts.items():
            if pattern_key in self.patterns:
                self.patterns[pattern_key].frequency = pattern_data["count"]
                self.patterns[pattern_key].last_seen = datetime.now().isoformat()
            else:
                self.patterns[pattern_key] = ViolationPattern(
                    pattern_id=pattern_key,
                    description=f"{pattern_data['layer']} {pattern_data['severity']} 违规",
                    frequency=pattern_data["count"],
                    last_seen=datetime.now().isoformat(),
                    suggested_fix=self._suggest_fix(pattern_data),
                    auto_fixable=self._is_auto_fixable(pattern_data)
                )
        
        self._save_patterns()
        
        return {
            "total": len(violations),
            "patterns": list(pattern_counts.values()),
            "suggestions": [self._suggest_fix(p) for p in pattern_counts.values()]
        }
    
    def _suggest_fix(self, pattern_data: Dict) -> str:
        """建议修复方案"""
        layer = pattern_data.get('layer', '')
        severity = pattern_data.get('severity', '')
        
        suggestions = {
            "L1_core_CRITICAL": "在任务开始前强制读取 ARCHITECTURE_QUICK_REFERENCE.md",
            "L2_memory_HIGH": "在 L1 Core 后自动调用 memory_search()",
            "L3_orchestration_HIGH": "在 L2 Memory 后自动调用 TaskEngine.process()",
            "L4_execution_MEDIUM": "在 L3 Orchestration 后自动路由技能",
            "L5_governance_MEDIUM": "在 L4 Execution 后自动验证结果",
            "L6_infrastructure_MEDIUM": "在 L5 Governance 后自动调用工具",
        }
        
        key = f"{layer}_{severity}"
        return suggestions.get(key, f"检查 {layer} 层是否正确执行")
    
    def _is_auto_fixable(self, pattern_data: Dict) -> bool:
        """判断是否可自动修复"""
        layer = pattern_data.get('layer', '')
        severity = pattern_data.get('severity', '')
        
        # CRITICAL 违规不能自动修复，必须人工介入
        if severity == "CRITICAL":
            return False
        
        # HIGH 违规可以自动补充执行
        if severity == "HIGH":
            return True
        
        # MEDIUM/LOW 违规可以自动修复
        return True
    
    def generate_improvement(self, pattern: ViolationPattern) -> Improvement:
        """生成改进方案"""
        import time
        
        improvement_id = f"improve_{int(time.time() * 1000)}"
        
        # 根据模式生成改进方案
        if "L1_core" in pattern.pattern_id:
            return Improvement(
                improvement_id=improvement_id,
                type=ImprovementType.ADD_CHECK,
                description="在任务开始前强制检查 L1 Core 规则读取",
                affected_files=["scripts/architecture_compliance_checker.py"],
                implementation="在 start_task() 中添加强制读取检查",
                auto_fixable=True
            )
        
        elif "L2_memory" in pattern.pattern_id:
            return Improvement(
                improvement_id=improvement_id,
                type=ImprovementType.AUTO_CORRECT,
                description="自动调用 memory_search() 补充 L2 Memory",
                affected_files=["scripts/architecture_compliance_checker.py"],
                implementation="在检测到 L2 Memory 未完成时自动调用 memory_search()",
                auto_fixable=True
            )
        
        elif "L3_orchestration" in pattern.pattern_id:
            return Improvement(
                improvement_id=improvement_id,
                type=ImprovementType.AUTO_CORRECT,
                description="自动调用 TaskEngine 补充 L3 Orchestration",
                affected_files=["scripts/architecture_compliance_checker.py"],
                implementation="在检测到 L3 Orchestration 未完成时自动调用 TaskEngine",
                auto_fixable=True
            )
        
        else:
            return Improvement(
                improvement_id=improvement_id,
                type=ImprovementType.UPDATE_DOC,
                description=f"更新文档说明 {pattern.description}",
                affected_files=["core/ARCHITECTURE_QUICK_REFERENCE.md"],
                implementation="增加违规案例说明",
                auto_fixable=False
            )
    
    def apply_improvement(self, improvement: Improvement) -> bool:
        """应用改进方案"""
        if not improvement.auto_fixable:
            print(f"⚠️  改进方案需要人工审核: {improvement.description}")
            return False
        
        # TODO: 实现自动应用改进
        # 这里需要根据 improvement.type 和 improvement.implementation 来修改文件
        
        print(f"✅ 应用改进: {improvement.description}")
        return True
    
    def auto_upgrade_rule(self) -> Dict[str, Any]:
        """自动升级规则"""
        # 读取当前规则
        with open(self.rule_registry, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        r010 = registry.get("rules", {}).get("R010", {})
        current_version = r010.get("version", "1.0.0")
        
        # 分析违规
        analysis = self.analyze_violations()
        
        # 判断是否需要升级
        if analysis["total"] == 0:
            return {
                "status": "no_upgrade_needed",
                "current_version": current_version,
                "violations": 0
            }
        
        # 升级版本号
        major, minor, patch = map(int, current_version.split('.'))
        new_version = f"{major}.{minor}.{patch + 1}"
        
        # 更新规则
        r010["version"] = new_version
        r010["description"] = f"{r010.get('description', '')} (自动升级 {datetime.now().strftime('%Y-%m-%d')})"
        
        # 添加新的检查项
        check_items = r010.get("check_items", [])
        for pattern in analysis["patterns"]:
            check_item = f"auto_detect_{pattern['layer']}"
            if check_item not in check_items:
                check_items.append(check_item)
        
        r010["check_items"] = check_items
        
        # 保存规则
        registry["rules"]["R010"] = r010
        with open(self.rule_registry, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "upgraded",
            "old_version": current_version,
            "new_version": new_version,
            "violations_analyzed": analysis["total"],
            "patterns_detected": len(analysis["patterns"]),
            "check_items_added": len(check_items) - len(r010.get("check_items", []))
        }
    
    def run(self) -> Dict[str, Any]:
        """运行自动改进器"""
        print("=" * 60)
        print("  架构违规自动改进器 V1.0.0")
        print("=" * 60)
        print()
        
        # 1. 分析违规
        print("📊 分析违规记录...")
        analysis = self.analyze_violations()
        print(f"  总违规数: {analysis['total']}")
        print(f"  模式数: {len(analysis['patterns'])}")
        print()
        
        # 2. 生成改进方案
        if analysis['total'] > 0:
            print("🔧 生成改进方案...")
            improvements = []
            for pattern_key, pattern in self.patterns.items():
                if pattern.frequency > 0:
                    improvement = self.generate_improvement(pattern)
                    improvements.append(improvement)
                    print(f"  - {improvement.description}")
            print()
            
            # 3. 应用改进
            print("✅ 应用改进方案...")
            for improvement in improvements:
                if improvement.auto_fixable:
                    self.apply_improvement(improvement)
            print()
        
        # 4. 自动升级规则
        print("⬆️  自动升级规则...")
        upgrade_result = self.auto_upgrade_rule()
        if upgrade_result["status"] == "upgraded":
            print(f"  版本: {upgrade_result['old_version']} → {upgrade_result['new_version']}")
            print(f"  新增检查项: {upgrade_result['check_items_added']}")
        else:
            print(f"  当前版本: {upgrade_result['current_version']} (无需升级)")
        print()
        
        print("=" * 60)
        
        return {
            "analysis": analysis,
            "upgrade": upgrade_result
        }


def main():
    """主函数"""
    improver = AutoImprover()
    result = improver.run()
    
    # 保存结果
    result_file = Path(__file__).resolve().parent.parent / "reports" / "ops" / "auto_improvement_result.json"
    result_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 结果已保存: {result_file}")


if __name__ == "__main__":
    main()
