#!/usr/bin/env python3
"""架构巡检器 - V6.0.0 新模块融入版

增强功能：
1. 六层架构完整性检查
2. 受保护文件检查
3. 技能注册表一致性检查
4. 配置文件完整性检查
5. 依赖关系检查
6. 代码质量检查
7. 安全检查
8. 性能指标检查
9. 自动 Git 同步
10. 生成详细报告

V5.0.0 新增:
11. 规则注册表检查 (RULE_REGISTRY.json)
12. 规则引擎检查 (run_rule_engine.py)
13. 变更影响检查 (change_impact.json)
14. 技能安全检查 (skill_security_report.json)
15. 循环防护检查 (loop_guard.py)
16. 门禁报告检查 (gate_report.json)

V6.0.0 新增:
17. 新模块融入检查 (application/, domain/, infrastructure/storage/)
18. 任务系统检查 (task_engine.py, task_service/)
19. 响应服务检查 (response_service/)
20. 数据库迁移检查 (migrations/)
"""

import json
import sys
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 六层架构定义
LAYERS = {
    "L1_Core": {
        "name": "核心层",
        "path": "core",
        "protected_files": ["ARCHITECTURE.md", "AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md", "IDENTITY.md"],
        "required_dirs": ["config", "health"],
        "max_files": 100,
        "description": "核心认知、身份、规则"
    },
    "L2_Memory": {
        "name": "记忆层",
        "path": "memory_context",
        "protected_files": ["unified_search.py"],
        "required_dirs": ["index", "vector"],
        "max_files": 200,
        "description": "记忆上下文、知识库"
    },
    "L3_Orchestration": {
        "name": "编排层",
        "path": "orchestration",
        "protected_files": ["router/router.py"],
        "required_dirs": ["router"],
        "max_files": 100,
        "description": "任务编排、工作流"
    },
    "L4_Execution": {
        "name": "执行层",
        "path": "execution",
        "protected_files": ["skill_gateway.py"],
        "required_dirs": ["ecommerce"],
        "max_files": 150,
        "description": "能力执行、技能网关"
    },
    "L5_Governance": {
        "name": "治理层",
        "path": "governance",
        "protected_files": ["security.py", "audit/explainer.py", "validators/architecture_validator.py"],
        "required_dirs": ["security", "audit", "validators"],
        "max_files": 100,
        "description": "稳定治理、安全审计"
    },
    "L6_Infrastructure": {
        "name": "基础设施层",
        "path": "infrastructure",
        "protected_files": ["token_budget.py", "path_resolver.py", "auto_git.py", "architecture_inspector.py"],
        "required_dirs": ["loader", "cache", "inventory"],
        "max_files": 200,
        "description": "基础设施、工具链"
    }
}

# 受保护文件列表
PROTECTED_FILES = {
    "AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md", "IDENTITY.md",
    "MEMORY.md", "HEARTBEAT.md", "core/ARCHITECTURE.md",
    "core/RULE_REGISTRY.json", "core/LAYER_DEPENDENCY_MATRIX.md",
    "core/LAYER_DEPENDENCY_RULES.json", "core/LAYER_IO_CONTRACTS.md",
    "core/CHANGE_IMPACT_MATRIX.md", "core/SINGLE_SOURCE_OF_TRUTH.md",
    "governance/ARCHITECTURE_GUARDRAILS.md",
    "governance/CHANGE_IMPACT_ENFORCEMENT_POLICY.md"
}

# 安全检查模式
SECURITY_PATTERNS = {
    "hardcoded_secrets": [
        r'api[_-]?key\s*=\s*["\'][^"\']{20,}["\']',
        r'password\s*=\s*["\'][^"\']{8,}["\']',
        r'secret\s*=\s*["\'][^"\']{10,}["\']',
        r'token\s*=\s*["\'][^"\']{20,}["\']',
    ],
    "dangerous_commands": [
        r'rm\s+-rf\s+/',
        r'sudo\s+rm',
        r'drop\s+table',
        r'delete\s+from\s+\*',
    ],
    "shell_injection": [
        r'shell\s*=\s*True',
        r'os\.system\s*\(',
        r'subprocess\.call\s*\([^)]*shell\s*=\s*True',
    ]
}

# 代码质量检查
QUALITY_CHECKS = {
    "todo_fixme": r'(TODO|FIXME|XXX|HACK)',
    "deprecated_imports": r'from\s+distutils|import\s+distutils',
    "print_debug": r'print\s*\(["\']debug',
}


class ArchitectureInspector:
    """架构巡检器 - V5.0.0 规则平台化版"""
    
    def __init__(self):
        self.results = {
            "version": "5.0.0",
            "timestamp": datetime.now().isoformat(),
            "layers": {},
            "protected_files": {},
            "skill_registry": {},
            "config_files": {},
            "dependencies": {},
            "code_quality": {},
            "security": {},
            "performance": {},
            "rule_registry": {},
            "rule_engine": {},
            "change_impact": {},
            "skill_security": {},
            "loop_guard": {},
            "gate_reports": {},
            "issues": [],
            "warnings": [],
            "summary": {}
        }
        self.stats = defaultdict(int)
    
    def inspect_all(self) -> Dict:
        """执行完整巡检"""
        print("=" * 70)
        print("架构巡检器 - V6.0.0 新模块融入版")
        print("=" * 70)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 1. 检查六层架构
        self._inspect_layers()
        
        # 2. 检查受保护文件
        self._inspect_protected_files()
        
        # 3. 检查技能注册表
        self._inspect_skill_registry()
        
        # 4. 检查配置文件
        self._inspect_config_files()
        
        # 5. 检查依赖关系
        self._inspect_dependencies()
        
        # 6. 代码质量检查
        self._inspect_code_quality()
        
        # 7. 安全检查
        self._inspect_security()
        
        # 8. 性能指标
        self._inspect_performance()
        
        # 9. 规则注册表检查 (V5.0.0 新增)
        self._inspect_rule_registry()
        
        # 10. 规则引擎检查 (V5.0.0 新增)
        self._inspect_rule_engine()
        
        # 11. 变更影响检查 (V5.0.0 新增)
        self._inspect_change_impact()
        
        # 12. 技能安全检查 (V5.0.0 新增)
        self._inspect_skill_security()
        
        # 13. 循环防护检查 (V5.0.0 新增)
        self._inspect_loop_guard()
        
        # 14. 门禁报告检查 (V5.0.0 新增)
        self._inspect_gate_reports()
        
        # 15. 新模块融入检查 (V6.0.0 新增)
        self._inspect_new_modules()
        
        # 16. 任务系统检查 (V6.0.0 新增)
        self._inspect_task_system()
        
        # 17. 生成摘要
        self._generate_summary()
        
        # 18. 自动 Git 同步
        self._auto_git_sync()
        
        return self.results
    
    def _inspect_layers(self):
        """检查六层架构"""
        print("【1. 六层架构检查】")
        print("-" * 70)
        
        for layer_id, layer_info in LAYERS.items():
            layer_path = PROJECT_ROOT / layer_info["path"]
            status = {
                "exists": layer_path.exists(),
                "files": 0,
                "dirs": 0,
                "size_mb": 0,
                "protected_ok": True,
                "required_ok": True,
                "file_limit_ok": True,
                "issues": [],
                "details": {}
            }
            
            if layer_path.exists():
                # 统计文件
                py_files = list(layer_path.rglob("*.py"))
                status["files"] = len(py_files)
                status["dirs"] = len([d for d in layer_path.rglob("*") if d.is_dir()])
                
                # 计算大小
                total_size = sum(f.stat().st_size for f in layer_path.rglob("*") if f.is_file())
                status["size_mb"] = round(total_size / 1024 / 1024, 2)
                
                # 检查文件数量限制
                if status["files"] > layer_info.get("max_files", 999):
                    status["file_limit_ok"] = False
                    status["issues"].append(f"文件数超限: {status['files']} > {layer_info['max_files']}")
                
                # 检查受保护文件
                for pf in layer_info.get("protected_files", []):
                    pf_path = layer_path / pf
                    if not pf_path.exists():
                        status["protected_ok"] = False
                        status["issues"].append(f"缺失受保护文件: {pf}")
                
                # 检查必需目录
                for rd in layer_info.get("required_dirs", []):
                    rd_path = layer_path / rd
                    if not rd_path.exists():
                        status["required_ok"] = False
                        status["issues"].append(f"缺失必需目录: {rd}")
                
                # 统计 Python 文件行数
                total_lines = 0
                for f in py_files[:50]:  # 最多检查50个文件
                    try:
                        total_lines += len(f.read_text(errors='ignore').splitlines())
                    except:
                        pass
                status["details"]["total_lines"] = total_lines
            
            self.results["layers"][layer_id] = status
            self.stats["total_files"] += status["files"]
            
            # 输出
            all_ok = status["exists"] and status["protected_ok"] and status["required_ok"] and status["file_limit_ok"]
            icon = "✅" if all_ok else "❌"
            
            print(f"  {icon} {layer_info['name']} ({layer_id})")
            print(f"      路径: {layer_info['path']}")
            print(f"      文件: {status['files']} | 目录: {status['dirs']} | 大小: {status['size_mb']}MB")
            print(f"      说明: {layer_info['description']}")
            
            for issue in status["issues"]:
                print(f"      ⚠️ {issue}")
            
            print()
    
    def _inspect_protected_files(self):
        """检查受保护文件"""
        print("【2. 受保护文件检查】")
        print("-" * 70)
        
        for pf in sorted(PROTECTED_FILES):
            pf_path = PROJECT_ROOT / pf
            status = {
                "exists": pf_path.exists(),
                "size": 0,
                "lines": 0,
                "modified": None
            }
            
            if pf_path.exists():
                status["size"] = pf_path.stat().st_size
                status["modified"] = datetime.fromtimestamp(pf_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                try:
                    status["lines"] = len(pf_path.read_text(errors='ignore').splitlines())
                except:
                    pass
            
            self.results["protected_files"][pf] = status
            
            icon = "✅" if status["exists"] else "❌"
            info = f"{status['lines']}行, {status['size']}字节" if status["exists"] else "不存在"
            print(f"  {icon} {pf} - {info}")
    
    def _inspect_skill_registry(self):
        """检查技能注册表"""
        print()
        print("【3. 技能注册表检查】")
        print("-" * 70)
        
        registry_path = PROJECT_ROOT / "infrastructure" / "inventory" / "skill_registry.json"
        
        if registry_path.exists():
            try:
                registry = json.loads(registry_path.read_text())
                
                # 处理不同格式
                if isinstance(registry, dict):
                    skills = registry.get("skills", [])
                elif isinstance(registry, list):
                    skills = registry
                else:
                    skills = []
                
                status = {
                    "exists": True,
                    "skill_count": len(skills),
                    "categories": {},
                    "layers": {},
                    "issues": []
                }
                
                # 统计分类和层级
                for skill in skills:
                    if isinstance(skill, dict):
                        cat = skill.get("category", "unknown")
                        layer = skill.get("layer", "unknown")
                        status["categories"][cat] = status["categories"].get(cat, 0) + 1
                        status["layers"][layer] = status["layers"].get(layer, 0) + 1
                
                self.results["skill_registry"] = status
                
                print(f"  ✅ 技能总数: {status['skill_count']}")
                print(f"  分类统计:")
                for cat, count in sorted(status["categories"].items(), key=lambda x: -x[1])[:10]:
                    print(f"      • {cat}: {count}")
                
            except Exception as e:
                self.results["skill_registry"] = {"exists": True, "error": str(e)}
                print(f"  ❌ 解析失败: {e}")
        else:
            self.results["skill_registry"] = {"exists": False}
            print("  ❌ 技能注册表不存在")
    
    def _inspect_config_files(self):
        """检查配置文件"""
        print()
        print("【4. 配置文件检查】")
        print("-" * 70)
        
        config_files = [
            "core/CONFIG.json",
            "infrastructure/inventory/load_config.json",
            "infrastructure/inventory/exclude_config.json",
            "skills/llm-memory-integration/config/llm_config.json",
            "skills/llm-memory-integration/config/unified_config.json"
        ]
        
        for cf in config_files:
            cf_path = PROJECT_ROOT / cf
            status = {
                "exists": cf_path.exists(),
                "valid_json": False,
                "size": 0,
                "keys": []
            }
            
            if cf_path.exists():
                status["size"] = cf_path.stat().st_size
                try:
                    data = json.loads(cf_path.read_text())
                    status["valid_json"] = True
                    if isinstance(data, dict):
                        status["keys"] = list(data.keys())[:10]
                except:
                    pass
            
            self.results["config_files"][cf] = status
            
            icon = "✅" if status["exists"] and status["valid_json"] else "❌"
            info = f"{status['size']}字节" if status["exists"] else "不存在"
            print(f"  {icon} {cf} - {info}")
    
    def _inspect_dependencies(self):
        """检查依赖关系"""
        print()
        print("【5. 依赖关系检查】")
        print("-" * 70)
        
        sys.path.insert(0, str(PROJECT_ROOT))
        
        critical_imports = [
            ("memory_context.unified_search", "统一搜索"),
            ("infrastructure.token_budget", "Token 预算"),
            ("infrastructure.path_resolver", "路径解析"),
            ("infrastructure.auto_git", "自动 Git"),
            ("execution.skill_gateway", "技能网关"),
        ]
        
        status = {"imports": {}}
        
        for module, name in critical_imports:
            try:
                __import__(module)
                status["imports"][module] = {"ok": True, "name": name}
                print(f"  ✅ {name} ({module})")
            except Exception as e:
                status["imports"][module] = {"ok": False, "name": name, "error": str(e)}
                print(f"  ❌ {name} ({module}): {e}")
                self.results["issues"].append(f"导入失败: {module}")
        
        self.results["dependencies"] = status
    
    def _inspect_code_quality(self):
        """代码质量检查"""
        print()
        print("【6. 代码质量检查】")
        print("-" * 70)
        
        status = {
            "total_files": 0,
            "total_lines": 0,
            "todos": 0,
            "fixmes": 0,
            "deprecated": 0,
            "issues": []
        }
        
        # 检查关键目录
        check_dirs = ["memory_context", "infrastructure", "execution", "orchestration"]
        
        for dir_name in check_dirs:
            dir_path = PROJECT_ROOT / dir_name
            if not dir_path.exists():
                continue
            
            for py_file in dir_path.rglob("*.py"):
                status["total_files"] += 1
                try:
                    content = py_file.read_text(errors='ignore')
                    lines = content.splitlines()
                    status["total_lines"] += len(lines)
                    
                    # 检查 TODO/FIXME
                    for line in lines:
                        if "TODO" in line.upper():
                            status["todos"] += 1
                        if "FIXME" in line.upper():
                            status["fixmes"] += 1
                        if "distutils" in line:
                            status["deprecated"] += 1
                
                except:
                    pass
        
        self.results["code_quality"] = status
        
        print(f"  文件数: {status['total_files']}")
        print(f"  总行数: {status['total_lines']}")
        print(f"  TODO: {status['todos']}")
        print(f"  FIXME: {status['fixmes']}")
        print(f"  废弃导入: {status['deprecated']}")
    
    def _inspect_security(self):
        """安全检查"""
        print()
        print("【7. 安全检查】")
        print("-" * 70)
        
        status = {
            "hardcoded_secrets": 0,
            "dangerous_commands": 0,
            "shell_injection": 0,
            "issues": []
        }
        
        # 检查关键文件
        check_files = []
        for dir_name in ["memory_context", "infrastructure", "execution"]:
            dir_path = PROJECT_ROOT / dir_name
            if dir_path.exists():
                check_files.extend(dir_path.rglob("*.py"))
        
        for py_file in check_files[:100]:  # 最多检查100个文件
            try:
                content = py_file.read_text(errors='ignore')
                
                for pattern_name, patterns in SECURITY_PATTERNS.items():
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            status[pattern_name] += 1
                            status["issues"].append(f"{py_file.name}: {pattern_name}")
            except:
                pass
        
        self.results["security"] = status
        
        icon_secrets = "✅" if status["hardcoded_secrets"] == 0 else "⚠️"
        icon_danger = "✅" if status["dangerous_commands"] == 0 else "❌"
        icon_shell = "✅" if status["shell_injection"] == 0 else "⚠️"
        
        print(f"  {icon_secrets} 硬编码密钥: {status['hardcoded_secrets']}")
        print(f"  {icon_danger} 危险命令: {status['dangerous_commands']}")
        print(f"  {icon_shell} Shell 注入风险: {status['shell_injection']}")
    
    def _inspect_performance(self):
        """性能指标检查"""
        print()
        print("【8. 性能指标检查】")
        print("-" * 70)
        
        status = {
            "index_size": 0,
            "cache_size": 0,
            "log_size": 0,
            "largest_files": []
        }
        
        # 检查索引大小
        index_dir = PROJECT_ROOT / "memory_context" / "index"
        if index_dir.exists():
            for f in index_dir.glob("*.json"):
                status["index_size"] += f.stat().st_size
        
        # 检查缓存大小
        cache_dir = PROJECT_ROOT / ".cache"
        if cache_dir.exists():
            for f in cache_dir.glob("*"):
                if f.is_file():
                    status["cache_size"] += f.stat().st_size
        
        # 检查日志大小
        reports_dir = PROJECT_ROOT / "reports"
        if reports_dir.exists():
            for f in reports_dir.glob("*.json"):
                status["log_size"] += f.stat().st_size
        
        # 找出最大的文件
        all_files = []
        for f in PROJECT_ROOT.rglob("*.py"):
            if f.is_file() and "site-packages" not in str(f):
                try:
                    all_files.append((str(f.relative_to(PROJECT_ROOT)), f.stat().st_size))
                except:
                    pass
        
        all_files.sort(key=lambda x: -x[1])
        status["largest_files"] = all_files[:5]
        
        self.results["performance"] = status
        
        print(f"  索引大小: {status['index_size'] / 1024:.1f}KB")
        print(f"  缓存大小: {status['cache_size'] / 1024:.1f}KB")
        print(f"  日志大小: {status['log_size'] / 1024:.1f}KB")
        print(f"  最大文件:")
        for path, size in status["largest_files"]:
            print(f"      • {path}: {size / 1024:.1f}KB")
    
    def _inspect_rule_registry(self):
        """检查规则注册表 (V5.0.0 新增)"""
        print()
        print("【9. 规则注册表检查】")
        print("-" * 70)
        
        registry_path = PROJECT_ROOT / "core" / "RULE_REGISTRY.json"
        
        if registry_path.exists():
            try:
                registry = json.loads(registry_path.read_text())
                
                rules = registry.get("rules", {})
                profiles = registry.get("profiles", {})
                
                status = {
                    "exists": True,
                    "version": registry.get("version", "unknown"),
                    "rule_count": len(rules),
                    "profile_count": len(profiles),
                    "rules": list(rules.keys()),
                    "profiles": list(profiles.keys()),
                    "issues": []
                }
                
                # 检查每条规则的 checker 是否存在
                for rule_id, rule in rules.items():
                    checker = rule.get("checker_script", "")
                    if checker:
                        checker_path = PROJECT_ROOT / checker
                        if not checker_path.exists():
                            status["issues"].append(f"规则 {rule_id} 的检查器不存在: {checker}")
                
                self.results["rule_registry"] = status
                
                print(f"  ✅ 版本: {status['version']}")
                print(f"  ✅ 规则数: {status['rule_count']}")
                print(f"  ✅ Profile 数: {status['profile_count']}")
                print(f"  规则列表:")
                for rule_id in status["rules"]:
                    print(f"      • {rule_id}")
                
                for issue in status["issues"]:
                    print(f"  ⚠️ {issue}")
                
            except Exception as e:
                self.results["rule_registry"] = {"exists": True, "error": str(e)}
                print(f"  ❌ 解析失败: {e}")
        else:
            self.results["rule_registry"] = {"exists": False}
            print("  ❌ 规则注册表不存在")
    
    def _inspect_rule_engine(self):
        """检查规则引擎 (V5.0.0 新增)"""
        print()
        print("【10. 规则引擎检查】")
        print("-" * 70)
        
        engine_path = PROJECT_ROOT / "scripts" / "run_rule_engine.py"
        report_path = PROJECT_ROOT / "reports" / "ops" / "rule_engine_report.json"
        
        status = {
            "engine_exists": engine_path.exists(),
            "report_exists": report_path.exists(),
            "last_run": None,
            "passed_rules": 0,
            "failed_rules": 0
        }
        
        if engine_path.exists():
            print(f"  ✅ 规则引擎存在: scripts/run_rule_engine.py")
        else:
            print(f"  ❌ 规则引擎不存在")
        
        if report_path.exists():
            try:
                report = json.loads(report_path.read_text())
                status["last_run"] = report.get("generated_at")
                status["passed_rules"] = len(report.get("passed_rules", []))
                status["failed_rules"] = len(report.get("failed_rules", []))
                
                print(f"  ✅ 最近运行: {status['last_run']}")
                print(f"  ✅ 通过规则: {status['passed_rules']}")
                print(f"  {'✅' if status['failed_rules'] == 0 else '❌'} 失败规则: {status['failed_rules']}")
            except:
                print(f"  ⚠️ 报告解析失败")
        else:
            print(f"  ⚠️ 规则引擎报告不存在")
        
        self.results["rule_engine"] = status
    
    def _inspect_change_impact(self):
        """检查变更影响 (V5.0.0 新增)"""
        print()
        print("【11. 变更影响检查】")
        print("-" * 70)
        
        impact_path = PROJECT_ROOT / "reports" / "ops" / "change_impact.json"
        enforcement_path = PROJECT_ROOT / "reports" / "ops" / "change_impact_enforcement.json"
        
        status = {
            "impact_exists": impact_path.exists(),
            "enforcement_exists": enforcement_path.exists(),
            "changed_files": 0,
            "blocking_commands": 0,
            "enforcement_passed": None
        }
        
        if impact_path.exists():
            try:
                impact = json.loads(impact_path.read_text())
                status["changed_files"] = len(impact.get("changed_files", []))
                status["blocking_commands"] = len(impact.get("blocking_commands_current_profile", []))
                print(f"  ✅ 变更文件数: {status['changed_files']}")
                print(f"  ✅ 阻断命令数: {status['blocking_commands']}")
            except:
                print(f"  ⚠️ 变更影响报告解析失败")
        else:
            print(f"  ⚠️ 变更影响报告不存在")
        
        if enforcement_path.exists():
            try:
                enforcement = json.loads(enforcement_path.read_text())
                status["enforcement_passed"] = enforcement.get("enforcement_passed", False)
                icon = "✅" if status["enforcement_passed"] else "❌"
                print(f"  {icon} 强制门禁: {'通过' if status['enforcement_passed'] else '未通过'}")
            except:
                print(f"  ⚠️ 强制门禁报告解析失败")
        else:
            print(f"  ⚠️ 强制门禁报告不存在")
        
        self.results["change_impact"] = status
    
    def _inspect_skill_security(self):
        """检查技能安全 (V5.0.0 新增)"""
        print()
        print("【12. 技能安全检查】")
        print("-" * 70)
        
        checker_path = PROJECT_ROOT / "scripts" / "check_skill_security.py"
        report_path = PROJECT_ROOT / "reports" / "ops" / "skill_security_report.json"
        
        status = {
            "checker_exists": checker_path.exists(),
            "report_exists": report_path.exists(),
            "scanned": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        if checker_path.exists():
            print(f"  ✅ 技能安全检查器存在: scripts/check_skill_security.py")
        else:
            print(f"  ❌ 技能安全检查器不存在")
        
        if report_path.exists():
            try:
                report = json.loads(report_path.read_text())
                status["scanned"] = report.get("scanned", 0)
                status["critical"] = report.get("critical", 0)
                status["high"] = report.get("high", 0)
                status["medium"] = report.get("medium", 0)
                status["low"] = report.get("low", 0)
                
                print(f"  ✅ 扫描技能数: {status['scanned']}")
                
                icon_crit = "❌" if status["critical"] > 0 else "✅"
                icon_high = "⚠️" if status["high"] > 0 else "✅"
                
                print(f"  {icon_crit} Critical 风险: {status['critical']}")
                print(f"  {icon_high} High 风险: {status['high']}")
                print(f"  ✅ Medium 风险: {status['medium']}")
                print(f"  ✅ Low 风险: {status['low']}")
            except:
                print(f"  ⚠️ 技能安全报告解析失败")
        else:
            print(f"  ⚠️ 技能安全报告不存在")
        
        self.results["skill_security"] = status
    
    def _inspect_loop_guard(self):
        """检查循环防护 (V5.0.0 新增)"""
        print()
        print("【13. 循环防护检查】")
        print("-" * 70)
        
        guard_path = PROJECT_ROOT / "execution" / "loop_guard.py"
        design_path = PROJECT_ROOT / "docs" / "loop_guard_design.md"
        
        status = {
            "guard_exists": guard_path.exists(),
            "design_exists": design_path.exists()
        }
        
        if guard_path.exists():
            print(f"  ✅ 循环防护模块存在: execution/loop_guard.py")
        else:
            print(f"  ❌ 循环防护模块不存在")
        
        if design_path.exists():
            print(f"  ✅ 设计文档存在: docs/loop_guard_design.md")
        else:
            print(f"  ⚠️ 设计文档不存在")
        
        self.results["loop_guard"] = status
    
    def _inspect_gate_reports(self):
        """检查门禁报告 (V5.0.0 新增)"""
        print()
        print("【14. 门禁报告检查】")
        print("-" * 70)
        
        reports = {
            "runtime_integrity": PROJECT_ROOT / "reports" / "runtime_integrity.json",
            "quality_gate": PROJECT_ROOT / "reports" / "quality_gate.json",
            "release_gate": PROJECT_ROOT / "reports" / "release_gate.json",
            "rule_execution_index": PROJECT_ROOT / "reports" / "ops" / "rule_execution_index.json",
            "followup_requirements": PROJECT_ROOT / "reports" / "ops" / "followup_requirements.json"
        }
        
        status = {"reports": {}}
        
        for name, path in reports.items():
            exists = path.exists()
            status["reports"][name] = {"exists": exists}
            
            icon = "✅" if exists else "⚠️"
            print(f"  {icon} {name}: {'存在' if exists else '不存在'}")
        
        self.results["gate_reports"] = status
    
    def _inspect_new_modules(self):
        """V6.0.0: 检查新模块融入"""
        print()
        print("【15. 新模块融入检查】")
        print("-" * 70)
        
        new_modules = {
            "application/task_service": {
                "required_files": ["service.py", "scheduler.py"],
                "layer": "L3 Orchestration"
            },
            "application/response_service": {
                "required_files": ["renderer.py", "evidence_formatter.py"],
                "layer": "L3 Orchestration"
            },
            "domain/tasks": {
                "required_files": ["specs.py", "state_machine.py"],
                "layer": "L4 Execution"
            },
            "infrastructure/storage/repositories": {
                "required_files": ["interfaces.py", "sqlite_repo.py"],
                "layer": "L6 Infrastructure"
            },
            "infrastructure/storage/migrations": {
                "required_files": ["001_task_system.sql"],
                "layer": "L6 Infrastructure"
            }
        }
        
        status = {"modules": {}}
        all_ok = True
        
        for module_path, config in new_modules.items():
            module_dir = PROJECT_ROOT / module_path
            exists = module_dir.exists()
            
            module_status = {
                "exists": exists,
                "layer": config["layer"],
                "files_found": [],
                "files_missing": []
            }
            
            if exists:
                for req_file in config["required_files"]:
                    file_path = module_dir / req_file
                    if file_path.exists():
                        module_status["files_found"].append(req_file)
                    else:
                        module_status["files_missing"].append(req_file)
                
                if module_status["files_missing"]:
                    all_ok = False
                    print(f"  ⚠️ {module_path}: 缺失 {module_status['files_missing']}")
                else:
                    print(f"  ✅ {module_path}: {len(module_status['files_found'])} 文件")
            else:
                all_ok = False
                print(f"  ❌ {module_path}: 目录不存在")
            
            status["modules"][module_path] = module_status
        
        status["all_ok"] = all_ok
        self.results["new_modules"] = status
    
    def _inspect_task_system(self):
        """V6.0.0: 检查任务系统"""
        print()
        print("【16. 任务系统检查】")
        print("-" * 70)
        
        status = {
            "task_engine": False,
            "skill_gateway": False,
            "evidence_check": False
        }
        
        # 检查 task_engine.py
        task_engine_path = PROJECT_ROOT / "orchestration" / "task_engine.py"
        if task_engine_path.exists():
            content = task_engine_path.read_text()
            # V5.0.0 检查：是否有真实总结器和验证器
            has_summarize = "_execute_summarize" in content
            has_verify = "_execute_verify" in content
            # 证据检查：检查 evidences 列表和 verified 字段
            has_evidence_check = "evidences" in content and "verified" in content
            
            status["task_engine"] = True
            status["summarize_method"] = has_summarize
            status["verify_method"] = has_verify
            status["evidence_check"] = has_evidence_check
            
            print(f"  ✅ task_engine.py 存在")
            print(f"  {'✅' if has_summarize else '❌'} 真实总结器: {'已实现' if has_summarize else '未实现'}")
            print(f"  {'✅' if has_verify else '❌'} 真实验证器: {'已实现' if has_verify else '未实现'}")
            print(f"  {'✅' if has_evidence_check else '❌'} 证据检查: {'已实现' if has_evidence_check else '未实现'}")
        else:
            print(f"  ❌ task_engine.py 不存在")
        
        # 检查 skill_gateway.py
        gateway_path = PROJECT_ROOT / "execution" / "skill_gateway.py"
        if gateway_path.exists():
            content = gateway_path.read_text()
            # V6.0.0: 检查统一的 error 结构（包含 code 字段）
            has_error_code = '"code"' in content and '"message"' in content
            
            status["skill_gateway"] = True
            status["error_code_field"] = has_error_code
            
            print(f"  ✅ skill_gateway.py 存在")
            print(f"  {'✅' if has_error_code else '❌'} error 结构: {'已添加' if has_error_code else '未添加'}")
        else:
            print(f"  ❌ skill_gateway.py 不存在")
        
        self.results["task_system"] = status
    
    def _generate_summary(self):
        """生成摘要"""
        print()
        print("=" * 70)
        print("巡检摘要")
        print("=" * 70)
        
        # 统计
        layer_ok = sum(1 for s in self.results["layers"].values() 
                       if s["exists"] and s["protected_ok"] and s["required_ok"])
        layer_total = len(LAYERS)
        
        protected_ok = sum(1 for s in self.results["protected_files"].values() if s["exists"])
        protected_total = len(PROTECTED_FILES)
        
        config_ok = sum(1 for s in self.results["config_files"].values() 
                        if s["exists"] and s["valid_json"])
        config_total = len(self.results["config_files"])
        
        import_ok = sum(1 for s in self.results["dependencies"]["imports"].values() if s["ok"])
        import_total = len(self.results["dependencies"]["imports"])
        
        security_ok = (self.results["security"]["dangerous_commands"] == 0)
        
        # 汇总
        self.results["summary"] = {
            "layers": f"{layer_ok}/{layer_total}",
            "protected_files": f"{protected_ok}/{protected_total}",
            "config_files": f"{config_ok}/{config_total}",
            "imports": f"{import_ok}/{import_total}",
            "security": "通过" if security_ok else "有问题",
            "total_files": self.results["code_quality"]["total_files"],
            "total_lines": self.results["code_quality"]["total_lines"],
            "issues": len(self.results["issues"]),
            "warnings": len(self.results["warnings"]),
            # V5.0.0 新增
            "rule_registry": "存在" if self.results["rule_registry"].get("exists") else "不存在",
            "rule_engine": "存在" if self.results["rule_engine"].get("engine_exists") else "不存在",
            "change_impact": "通过" if self.results["change_impact"].get("enforcement_passed") else "未通过",
            "skill_security": f"Critical:{self.results['skill_security'].get('critical', 0)} High:{self.results['skill_security'].get('high', 0)}",
            "loop_guard": "存在" if self.results["loop_guard"].get("guard_exists") else "不存在"
        }
        
        print(f"  六层架构: {layer_ok}/{layer_total} 通过")
        print(f"  受保护文件: {protected_ok}/{protected_total} 存在")
        print(f"  配置文件: {config_ok}/{config_total} 有效")
        print(f"  关键导入: {import_ok}/{import_total} 成功")
        print(f"  安全检查: {'通过' if security_ok else '有问题'}")
        print(f"  代码统计: {self.results['code_quality']['total_files']} 文件, {self.results['code_quality']['total_lines']} 行")
        print(f"  问题数: {len(self.results['issues'])}")
        print(f"  警告数: {len(self.results['warnings'])}")
        
        # V5.0.0 新增摘要
        print()
        print("【V5.0.0 新增检查】")
        print(f"  规则注册表: {self.results['summary']['rule_registry']}")
        print(f"  规则引擎: {self.results['summary']['rule_engine']}")
        print(f"  变更影响: {self.results['summary']['change_impact']}")
        print(f"  技能安全: {self.results['summary']['skill_security']}")
        print(f"  循环防护: {self.results['summary']['loop_guard']}")
        
        # V6.0.0 新增摘要
        print()
        print("【V6.0.0 新增检查】")
        new_modules = self.results.get("new_modules", {})
        task_system = self.results.get("task_system", {})
        
        modules_ok = new_modules.get("all_ok", False)
        print(f"  {'✅' if modules_ok else '❌'} 新模块融入: {'全部就绪' if modules_ok else '有缺失'}")
        
        task_engine_ok = task_system.get("task_engine", False) and task_system.get("summarize_method", False)
        print(f"  {'✅' if task_engine_ok else '❌'} 任务引擎: {'V5.0.0 已升级' if task_engine_ok else '需升级'}")
        
        evidence_ok = task_system.get("evidence_check", False)
        print(f"  {'✅' if evidence_ok else '❌'} 证据检查: {'已实现' if evidence_ok else '未实现'}")
        
        # 总体状态
        all_ok = (layer_ok == layer_total and 
                  protected_ok == protected_total and 
                  import_ok == import_total and
                  security_ok and
                  self.results["rule_registry"].get("exists", False) and
                  self.results["rule_engine"].get("engine_exists", False))
        
        print()
        if all_ok:
            print("✅ 架构巡检通过")
        else:
            print("❌ 架构巡检发现问题，请检查上述项目")
    
    def _auto_git_sync(self):
        """自动 Git 同步"""
        print()
        print("【自动 Git 同步】")
        print("-" * 70)
        
        try:
            from infrastructure.auto_git import auto_commit_if_changed
            summary = self.results["summary"]
            ok, msg = auto_commit_if_changed(f"架构巡检: {summary['layers']} 通过, {summary['total_files']} 文件")
            print(f"  {'✅' if ok else '❌'} {msg}")
        except Exception as e:
            print(f"  ⚠️ 自动提交失败: {e}")
    
    def save_report(self, path: Path = None):
        """保存报告"""
        path = path or PROJECT_ROOT / "reports" / f"inspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.results, ensure_ascii=False, indent=2))
        print(f"\n报告已保存: {path}")


def main():
    inspector = ArchitectureInspector()
    results = inspector.inspect_all()
    inspector.save_report()
    
    # 返回退出码
    issues = results["summary"]["issues"]
    return 0 if issues == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
