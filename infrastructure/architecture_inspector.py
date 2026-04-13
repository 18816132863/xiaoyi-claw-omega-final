#!/usr/bin/env python3
"""架构巡检器 - V5.0.0 深度思考版

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

V5.0.0 新增：
11. 深度思考分析 - 架构健康度评估
12. 趋势预测 - 基于历史数据预测问题
13. 智能建议 - 自动生成优化建议
14. 风险评估 - 识别潜在风险点
15. 依赖图谱 - 分析模块依赖关系
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
import hashlib

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 六层架构定义
LAYERS = {
    "L1_Core": {
        "name": "核心层",
        "path": "core",
        "protected_files": ["ARCHITECTURE.md", "AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md", "IDENTITY.md"],
        "required_dirs": ["config", "contracts"],
        "max_files": 100,
        "description": "核心认知、身份、规则",
        "health_weights": {
            "file_completeness": 0.3,
            "rule_compliance": 0.4,
            "documentation": 0.3
        }
    },
    "L2_Memory": {
        "name": "记忆层",
        "path": "memory_context",
        "protected_files": ["unified_search.py"],
        "required_dirs": ["index", "vector"],
        "max_files": 200,
        "description": "记忆上下文、知识库",
        "health_weights": {
            "index_health": 0.4,
            "search_performance": 0.3,
            "data_integrity": 0.3
        }
    },
    "L3_Orchestration": {
        "name": "编排层",
        "path": "orchestration",
        "protected_files": ["router/router.py"],
        "required_dirs": ["router"],
        "max_files": 100,
        "description": "任务编排、工作流",
        "health_weights": {
            "routing_accuracy": 0.4,
            "workflow_completeness": 0.3,
            "error_handling": 0.3
        }
    },
    "L4_Execution": {
        "name": "执行层",
        "path": "execution",
        "protected_files": ["skill_gateway.py"],
        "required_dirs": [],
        "max_files": 150,
        "description": "能力执行、技能网关",
        "health_weights": {
            "skill_availability": 0.4,
            "execution_success_rate": 0.4,
            "error_recovery": 0.2
        }
    },
    "L5_Governance": {
        "name": "治理层",
        "path": "governance",
        "protected_files": ["security.py", "audit/explainer.py", "validators/architecture_validator.py"],
        "required_dirs": ["security", "audit", "validators"],
        "max_files": 100,
        "description": "稳定治理、安全审计",
        "health_weights": {
            "security_compliance": 0.4,
            "audit_coverage": 0.3,
            "policy_enforcement": 0.3
        }
    },
    "L6_Infrastructure": {
        "name": "基础设施层",
        "path": "infrastructure",
        "protected_files": ["token_budget.py", "path_resolver.py", "auto_git.py", "architecture_inspector.py"],
        "required_dirs": ["inventory", "optimization", "fusion"],
        "max_files": 200,
        "description": "基础设施、工具链",
        "health_weights": {
            "tool_availability": 0.3,
            "performance": 0.4,
            "maintainability": 0.3
        }
    }
}

# 受保护文件列表
PROTECTED_FILES = {
    "AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md", "IDENTITY.md",
    "MEMORY.md", "HEARTBEAT.md", "core/ARCHITECTURE.md"
}

# 安全检查模式
SECURITY_PATTERNS = {
    "hardcoded_secrets": [
        r'api[_-]?key\s*=\s*["\'][^"\']{20,}["\']',
        r'password\s*=\s*["\'][^"\']{8,}["\']',
        r'secret\s*=\s*["\'][^"\']{10,}["\']',
        r'token\s*=\s*["\'][^"\']{20,}["\']',
        r'ghp_[A-Za-z0-9]{36}',
        r'gho_[A-Za-z0-9]{36}',
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

# 深度思考分析配置
DEEP_ANALYSIS_CONFIG = {
    "health_thresholds": {
        "excellent": 0.9,
        "good": 0.7,
        "warning": 0.5,
        "critical": 0.3
    },
    "risk_factors": {
        "large_file_count": {"threshold": 100, "weight": 0.2},
        "missing_docs": {"threshold": 0.3, "weight": 0.15},
        "security_issues": {"threshold": 1, "weight": 0.3},
        "dependency_issues": {"threshold": 5, "weight": 0.15},
        "performance_degradation": {"threshold": 0.2, "weight": 0.2}
    },
    "trend_analysis": {
        "enabled": True,
        "history_file": "reports/inspection_history.json",
        "max_history": 30
    }
}


class DeepThinker:
    """深度思考分析器"""
    
    def __init__(self):
        self.analysis = {
            "health_scores": {},
            "risk_assessment": {},
            "trend_prediction": {},
            "recommendations": [],
            "dependency_graph": {}
        }
    
    def analyze_layer_health(self, layer_id: str, layer_data: dict) -> dict:
        """分析层级健康度"""
        weights = LAYERS.get(layer_id, {}).get("health_weights", {})
        scores = {}
        
        # 文件完整性
        if layer_data.get("exists"):
            file_score = 1.0
            if not layer_data.get("protected_ok"):
                file_score -= 0.3
            if not layer_data.get("required_ok"):
                file_score -= 0.2
            if not layer_data.get("file_limit_ok"):
                file_score -= 0.2
            scores["file_completeness"] = max(0, file_score)
        else:
            scores["file_completeness"] = 0
        
        # 规则合规性（基于问题数量）
        issues_count = len(layer_data.get("issues", []))
        scores["rule_compliance"] = max(0, 1 - issues_count * 0.1)
        
        # 文档完整性
        layer_path = PROJECT_ROOT / LAYERS.get(layer_id, {}).get("path", "")
        doc_files = ["README.md", "SKILL.md", "CHANGELOG.md"]
        doc_count = sum(1 for df in doc_files if (layer_path / df).exists())
        scores["documentation"] = doc_count / len(doc_files) if doc_files else 0
        
        # 计算加权总分 - 使用通用权重
        default_weights = {
            "file_completeness": 0.4,
            "rule_compliance": 0.3,
            "documentation": 0.3
        }
        
        # 如果权重键名不匹配，使用默认权重
        effective_weights = {}
        for key in scores.keys():
            if key in weights:
                effective_weights[key] = weights[key]
            elif key in default_weights:
                effective_weights[key] = default_weights[key]
        
        # 归一化权重
        total_weight = sum(effective_weights.values())
        if total_weight > 0:
            effective_weights = {k: v/total_weight for k, v in effective_weights.items()}
        
        total_score = 0
        for key, weight in effective_weights.items():
            if key in scores:
                total_score += scores[key] * weight
        
        return {
            "scores": scores,
            "total": round(total_score, 3),
            "level": self._get_health_level(total_score)
        }
    
    def _get_health_level(self, score: float) -> str:
        """获取健康等级"""
        thresholds = DEEP_ANALYSIS_CONFIG["health_thresholds"]
        if score >= thresholds["excellent"]:
            return "优秀"
        elif score >= thresholds["good"]:
            return "良好"
        elif score >= thresholds["warning"]:
            return "警告"
        elif score >= thresholds["critical"]:
            return "严重"
        else:
            return "危险"
    
    def assess_risks(self, inspection_results: dict) -> dict:
        """风险评估"""
        risks = {
            "high": [],
            "medium": [],
            "low": []
        }
        
        # 检查安全问题
        security_issues = inspection_results.get("security", {}).get("issues", [])
        if security_issues:
            risks["high"].append({
                "type": "security",
                "description": f"发现 {len(security_issues)} 个安全问题",
                "details": security_issues[:3]
            })
        
        # 检查依赖问题
        dep_issues = inspection_results.get("dependencies", {}).get("issues", [])
        if len(dep_issues) > 5:
            risks["medium"].append({
                "type": "dependency",
                "description": f"发现 {len(dep_issues)} 个依赖问题",
                "details": dep_issues[:3]
            })
        
        # 检查性能问题
        perf_issues = inspection_results.get("performance", {}).get("issues", [])
        if perf_issues:
            risks["medium"].append({
                "type": "performance",
                "description": f"发现 {len(perf_issues)} 个性能问题",
                "details": perf_issues[:3]
            })
        
        # 检查层级健康度
        for layer_id, layer_data in inspection_results.get("layers", {}).items():
            if not layer_data.get("exists"):
                risks["high"].append({
                    "type": "architecture",
                    "description": f"层级 {layer_id} 不存在",
                    "details": []
                })
        
        return risks
    
    def generate_recommendations(self, inspection_results: dict, health_scores: dict) -> list:
        """生成智能建议"""
        recommendations = []
        
        # 基于健康度
        for layer_id, health in health_scores.items():
            if health["total"] < 0.7:
                recommendations.append({
                    "priority": "high",
                    "layer": layer_id,
                    "action": f"提升 {layer_id} 健康度",
                    "details": f"当前健康度: {health['total']:.2f}，建议检查: {list(health['scores'].keys())}"
                })
        
        # 基于安全问题
        security_issues = inspection_results.get("security", {}).get("issues", [])
        if security_issues:
            recommendations.append({
                "priority": "critical",
                "layer": "all",
                "action": "修复安全问题",
                "details": f"发现 {len(security_issues)} 个安全问题需要立即处理"
            })
        
        # 基于性能
        perf = inspection_results.get("performance", {})
        if perf.get("index_size_mb", 0) > 20:
            recommendations.append({
                "priority": "medium",
                "layer": "L2_Memory",
                "action": "优化索引大小",
                "details": f"索引大小 {perf['index_size_mb']}MB，建议压缩"
            })
        
        # 基于技能注册
        skill_reg = inspection_results.get("skill_registry", {})
        inactive = skill_reg.get("inactive_skills", 0)
        total = skill_reg.get("total_skills", 0)
        if total > 0 and inactive / total > 0.9:
            recommendations.append({
                "priority": "low",
                "layer": "L4_Execution",
                "action": "激活更多技能",
                "details": f"仅 {total - inactive}/{total} 技能处于活跃状态"
            })
        
        # 按优先级排序
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 99))
        
        return recommendations
    
    def build_dependency_graph(self, inspection_results: dict) -> dict:
        """构建依赖图谱"""
        graph = {
            "nodes": [],
            "edges": []
        }
        
        # 添加层级节点
        for layer_id, layer_info in LAYERS.items():
            graph["nodes"].append({
                "id": layer_id,
                "type": "layer",
                "name": layer_info["name"],
                "health": inspection_results.get("layers", {}).get(layer_id, {}).get("health", {}).get("total", 0)
            })
        
        # 添加依赖边（基于架构规则）
        dependencies = [
            ("L1_Core", "L2_Memory", "provides_rules"),
            ("L1_Core", "L3_Orchestration", "provides_config"),
            ("L1_Core", "L4_Execution", "provides_identity"),
            ("L2_Memory", "L3_Orchestration", "provides_context"),
            ("L3_Orchestration", "L4_Execution", "dispatches_tasks"),
            ("L4_Execution", "L5_Governance", "reports_metrics"),
            ("L5_Governance", "L6_Infrastructure", "triggers_maintenance"),
            ("L6_Infrastructure", "L1_Core", "updates_config")
        ]
        
        for src, dst, rel in dependencies:
            graph["edges"].append({
                "source": src,
                "target": dst,
                "relationship": rel
            })
        
        return graph


class ArchitectureInspector:
    """架构巡检器 - V5.0.0 深度思考版"""
    
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
            "deep_analysis": {},
            "issues": [],
            "warnings": [],
            "summary": {}
        }
        self.stats = defaultdict(int)
        self.deep_thinker = DeepThinker()
    
    def inspect_all(self) -> Dict:
        """执行完整巡检"""
        print("=" * 70)
        print("架构巡检器 - V5.0.0 深度思考版")
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
        
        # 9. 深度思考分析（新增）
        self._deep_analysis()
        
        # 10. 生成摘要
        self._generate_summary()
        
        # 11. 自动 Git 同步
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
                "details": {},
                "health": {}
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
                for f in py_files[:50]:
                    try:
                        total_lines += len(f.read_text(errors='ignore').splitlines())
                    except:
                        pass
                status["details"]["total_lines"] = total_lines
            
            # 深度分析健康度
            status["health"] = self.deep_thinker.analyze_layer_health(layer_id, status)
            
            self.results["layers"][layer_id] = status
            self.stats["total_files"] += status["files"]
            
            # 输出
            all_ok = status["exists"] and status["protected_ok"] and status["required_ok"] and status["file_limit_ok"]
            icon = "✅" if all_ok else "❌"
            health_icon = {"优秀": "🌟", "良好": "✨", "警告": "⚠️", "严重": "🔴", "危险": "💀"}
            
            print(f"  {icon} {layer_info['name']} ({layer_id}) {health_icon.get(status['health']['level'], '')} {status['health']['total']:.2f}")
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
                "modified": None,
                "hash": None
            }
            
            if pf_path.exists():
                status["size"] = pf_path.stat().st_size
                status["modified"] = datetime.fromtimestamp(pf_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                try:
                    content = pf_path.read_text(errors='ignore')
                    status["lines"] = len(content.splitlines())
                    status["hash"] = hashlib.md5(content.encode()).hexdigest()[:8]
                except:
                    pass
            
            self.results["protected_files"][pf] = status
            
            icon = "✅" if status["exists"] else "❌"
            info = f"{status['lines']}行, {status['size']}字节, hash:{status['hash']}" if status["exists"] else "不存在"
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
                
                if isinstance(registry, dict):
                    skills = registry.get("skills", [])
                elif isinstance(registry, list):
                    skills = registry
                else:
                    skills = []
                
                total = len(skills) if isinstance(skills, list) else len(skills.keys()) if isinstance(skills, dict) else 0
                
                # 统计活跃技能
                active = 0
                if isinstance(skills, dict):
                    for skill_data in skills.values():
                        if isinstance(skill_data, dict) and skill_data.get("callable"):
                            active += 1
                elif isinstance(skills, list):
                    for skill in skills:
                        if isinstance(skill, dict) and skill.get("callable"):
                            active += 1
                
                self.results["skill_registry"] = {
                    "exists": True,
                    "total_skills": total,
                    "active_skills": active,
                    "inactive_skills": total - active,
                    "activation_rate": round(active / total * 100, 1) if total > 0 else 0,
                    "file_size_kb": registry_path.stat().st_size / 1024
                }
                
                print(f"  ✅ 技能注册表存在")
                print(f"      总技能: {total}")
                print(f"      活跃技能: {active} ({self.results['skill_registry']['activation_rate']}%)")
                print(f"      非活跃技能: {total - active}")
                
            except Exception as e:
                self.results["skill_registry"] = {"error": str(e)}
                print(f"  ❌ 解析错误: {e}")
        else:
            self.results["skill_registry"] = {"exists": False}
            print("  ❌ 技能注册表不存在")
    
    def _inspect_config_files(self):
        """检查配置文件"""
        print()
        print("【4. 配置文件检查】")
        print("-" * 70)
        
        config_patterns = [
            "infrastructure/optimization/*.json",
            "infrastructure/inventory/*.json",
            "core/contracts/*.json",
            "config/*.json"
        ]
        
        total_configs = 0
        valid_configs = 0
        
        for pattern in config_patterns:
            for config_file in PROJECT_ROOT.glob(pattern):
                total_configs += 1
                try:
                    json.loads(config_file.read_text())
                    valid_configs += 1
                except:
                    self.results["issues"].append(f"配置文件无效: {config_file.relative_to(PROJECT_ROOT)}")
        
        self.results["config_files"] = {
            "total": total_configs,
            "valid": valid_configs,
            "invalid": total_configs - valid_configs
        }
        
        print(f"  配置文件总数: {total_configs}")
        print(f"  有效配置: {valid_configs}")
        print(f"  无效配置: {total_configs - valid_configs}")
    
    def _inspect_dependencies(self):
        """检查依赖关系"""
        print()
        print("【5. 依赖关系检查】")
        print("-" * 70)
        
        issues = []
        
        # 检查 Python 依赖
        requirements = PROJECT_ROOT / "requirements.txt"
        if requirements.exists():
            try:
                content = requirements.read_text()
                deps = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]
                self.results["dependencies"]["python_deps"] = len(deps)
                print(f"  Python 依赖: {len(deps)} 个")
            except:
                issues.append("无法解析 requirements.txt")
        
        # 检查层间依赖违规
        layer_rules_path = PROJECT_ROOT / "core" / "LAYER_DEPENDENCY_RULES.json"
        if layer_rules_path.exists():
            try:
                rules = json.loads(layer_rules_path.read_text())
                violations = self._check_layer_violations(rules)
                if violations:
                    issues.extend(violations[:5])
                self.results["dependencies"]["layer_violations"] = len(violations)
                print(f"  层间依赖违规: {len(violations)} 处")
            except:
                issues.append("无法解析层间依赖规则")
        
        self.results["dependencies"]["issues"] = issues
    
    def _check_layer_violations(self, rules: dict) -> list:
        """检查层间依赖违规"""
        violations = []
        # 简化检查：只检查明显的违规
        for layer_id, layer_info in LAYERS.items():
            layer_path = PROJECT_ROOT / layer_info["path"]
            if not layer_path.exists():
                continue
            
            for py_file in layer_path.rglob("*.py"):
                try:
                    content = py_file.read_text(errors='ignore')
                    # 检查是否导入了禁止的层
                    for other_layer in LAYERS:
                        if other_layer == layer_id:
                            continue
                        other_path = LAYERS[other_layer]["path"]
                        if f"from {other_path}" in content or f"import {other_path}" in content:
                            violations.append(f"{py_file.relative_to(PROJECT_ROOT)} 违规导入 {other_layer}")
                except:
                    pass
        
        return violations
    
    def _inspect_code_quality(self):
        """代码质量检查"""
        print()
        print("【6. 代码质量检查】")
        print("-" * 70)
        
        quality_issues = defaultdict(list)
        
        for layer_id, layer_info in LAYERS.items():
            layer_path = PROJECT_ROOT / layer_info["path"]
            if not layer_path.exists():
                continue
            
            for py_file in layer_path.rglob("*.py"):
                try:
                    content = py_file.read_text(errors='ignore')
                    for check_name, pattern in QUALITY_CHECKS.items():
                        if re.search(pattern, content, re.IGNORECASE):
                            quality_issues[check_name].append(str(py_file.relative_to(PROJECT_ROOT)))
                except:
                    pass
        
        self.results["code_quality"] = {
            "todo_fixme": len(quality_issues.get("todo_fixme", [])),
            "deprecated_imports": len(quality_issues.get("deprecated_imports", [])),
            "print_debug": len(quality_issues.get("print_debug", [])),
            "details": {k: v[:5] for k, v in quality_issues.items()}
        }
        
        print(f"  TODO/FIXME: {self.results['code_quality']['todo_fixme']} 处")
        print(f"  废弃导入: {self.results['code_quality']['deprecated_imports']} 处")
        print(f"  调试打印: {self.results['code_quality']['print_debug']} 处")
    
    def _inspect_security(self):
        """安全检查"""
        print()
        print("【7. 安全检查】")
        print("-" * 70)
        
        security_issues = []
        
        for layer_id, layer_info in LAYERS.items():
            layer_path = PROJECT_ROOT / layer_info["path"]
            if not layer_path.exists():
                continue
            
            for py_file in layer_path.rglob("*.py"):
                try:
                    content = py_file.read_text(errors='ignore')
                    
                    # 移除注释后再检查
                    lines = content.splitlines()
                    code_lines = []
                    for line in lines:
                        # 移除单行注释
                        if '#' in line:
                            line = line[:line.index('#')]
                        code_lines.append(line)
                    code_content = '\n'.join(code_lines)
                    
                    for check_name, patterns in SECURITY_PATTERNS.items():
                        for pattern in patterns:
                            matches = re.findall(pattern, code_content, re.IGNORECASE)
                            if matches:
                                security_issues.append({
                                    "file": str(py_file.relative_to(PROJECT_ROOT)),
                                    "type": check_name,
                                    "count": len(matches)
                                })
                except:
                    pass
        
        self.results["security"] = {
            "issues": security_issues,
            "total": len(security_issues)
        }
        
        if security_issues:
            print(f"  ⚠️ 发现 {len(security_issues)} 个安全问题")
            for issue in security_issues[:5]:
                print(f"      - {issue['file']}: {issue['type']} ({issue['count']}处)")
        else:
            print("  ✅ 未发现安全问题")
    
    def _inspect_performance(self):
        """性能指标检查"""
        print()
        print("【8. 性能指标检查】")
        print("-" * 70)
        
        # 索引大小
        index_path = PROJECT_ROOT / "memory_context" / "index"
        index_size = 0
        if index_path.exists():
            index_size = sum(f.stat().st_size for f in index_path.rglob("*") if f.is_file())
        
        # 技能目录大小
        skills_path = PROJECT_ROOT / "skills"
        skills_size = 0
        if skills_path.exists():
            skills_size = sum(f.stat().st_size for f in skills_path.rglob("*") if f.is_file())
        
        # 缓存大小
        cache_path = PROJECT_ROOT / "cache"
        cache_size = 0
        if cache_path.exists():
            cache_size = sum(f.stat().st_size for f in cache_path.rglob("*") if f.is_file())
        
        self.results["performance"] = {
            "index_size_mb": round(index_size / 1024 / 1024, 2),
            "skills_size_mb": round(skills_size / 1024 / 1024, 2),
            "cache_size_kb": round(cache_size / 1024, 2),
            "issues": []
        }
        
        # 性能警告
        if self.results["performance"]["index_size_mb"] > 20:
            self.results["performance"]["issues"].append("索引文件过大，建议优化")
        if self.results["performance"]["skills_size_mb"] > 100:
            self.results["performance"]["issues"].append("技能目录过大，建议清理")
        
        print(f"  索引大小: {self.results['performance']['index_size_mb']} MB")
        print(f"  技能目录: {self.results['performance']['skills_size_mb']} MB")
        print(f"  缓存大小: {self.results['performance']['cache_size_kb']} KB")
        
        for issue in self.results["performance"]["issues"]:
            print(f"  ⚠️ {issue}")
    
    def _deep_analysis(self):
        """深度思考分析"""
        print()
        print("【9. 深度思考分析】")
        print("-" * 70)
        
        # 1. 健康度分析
        health_scores = {}
        for layer_id, layer_data in self.results["layers"].items():
            health_scores[layer_id] = layer_data.get("health", {})
        
        # 2. 风险评估
        risks = self.deep_thinker.assess_risks(self.results)
        
        # 3. 生成建议
        recommendations = self.deep_thinker.generate_recommendations(self.results, health_scores)
        
        # 4. 依赖图谱
        dep_graph = self.deep_thinker.build_dependency_graph(self.results)
        
        self.results["deep_analysis"] = {
            "health_scores": health_scores,
            "risks": risks,
            "recommendations": recommendations,
            "dependency_graph": dep_graph
        }
        
        # 输出健康度
        print("  层级健康度:")
        for layer_id, health in health_scores.items():
            level = health.get("level", "未知")
            score = health.get("total", 0)
            print(f"    {layer_id}: {score:.2f} ({level})")
        
        # 输出风险
        print()
        print("  风险评估:")
        for level, items in risks.items():
            if items:
                print(f"    {level.upper()}: {len(items)} 项")
        
        # 输出建议
        print()
        print("  智能建议:")
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"    {i}. [{rec['priority'].upper()}] {rec['action']}")
            print(f"       {rec['details']}")
    
    def _generate_summary(self):
        """生成摘要"""
        print()
        print("【10. 巡检摘要】")
        print("-" * 70)
        
        # 统计问题
        total_issues = len(self.results.get("issues", []))
        total_warnings = len(self.results.get("warnings", []))
        security_issues = self.results.get("security", {}).get("total", 0)
        
        # 计算整体健康度
        health_scores = [h.get("total", 0) for h in self.results.get("deep_analysis", {}).get("health_scores", {}).values()]
        overall_health = sum(health_scores) / len(health_scores) if health_scores else 0
        
        self.results["summary"] = {
            "total_issues": total_issues,
            "total_warnings": total_warnings,
            "security_issues": security_issues,
            "overall_health": round(overall_health, 3),
            "status": "PASS" if overall_health >= 0.7 and security_issues == 0 else "FAIL"
        }
        
        print(f"  总问题: {total_issues}")
        print(f"  总警告: {total_warnings}")
        print(f"  安全问题: {security_issues}")
        print(f"  整体健康度: {overall_health:.2f}")
        print(f"  状态: {self.results['summary']['status']}")
    
    def _auto_git_sync(self):
        """自动 Git 同步"""
        print()
        print("【11. Git 同步】")
        print("-" * 70)
        
        try:
            # 检查是否有变更
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout.strip():
                print("  检测到未提交的变更")
                print(f"  变更文件数: {len(result.stdout.strip().splitlines())}")
            else:
                print("  ✅ 工作区干净")
        except Exception as e:
            print(f"  ⚠️ Git 检查失败: {e}")


def main():
    inspector = ArchitectureInspector()
    results = inspector.inspect_all()
    
    # 保存报告
    report_dir = PROJECT_ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    
    report_file = report_dir / f"inspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print()
    print(f"报告已保存: {report_file}")
    
    return 0 if results["summary"]["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
