#!/usr/bin/env python3
"""
融合机制模块 - V2.0.0

职责：
1. 判断文件是否应该融入架构
2. 判断文件应该提取到哪个目录
3. 执行融合操作
4. 生成融合报告
5. 审查现有结构，提出优化建议

V2.0.0 新增：
- 深度审查模式
- 架构影响分析
- 优化建议生成
- 批量处理能力
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


# ============================================================
# 融合规则定义
# ============================================================

# 核心配置文件 - 必须保留在根目录，不可移动
CORE_ROOT_FILES = {
    "AGENTS.md": "工作空间规则 - 系统启动时读取",
    "SOUL.md": "身份定义 - 定义 AI 人格",
    "USER.md": "用户信息 - 用户配置",
    "TOOLS.md": "工具规则 - 工具使用规范",
    "IDENTITY.md": "身份标识 - 身份元数据",
    "MEMORY.md": "长期记忆 - 记忆存储",
    "HEARTBEAT.md": "心跳任务 - 定时任务定义",
    "BOOTSTRAP.md": "启动引导 - 新会话引导",
    "SKILL.md": "技能说明 - 技能元信息",
    "README.md": "项目说明 - 项目入口文档",
}

# 影响架构的文件 - 不可移动
ARCHITECTURE_IMPACT_FILES = {
    "core/ARCHITECTURE.md": "主架构定义",
    "core/RULE_REGISTRY.json": "规则注册表",
    "core/RULE_EXCEPTIONS.json": "规则例外",
    "core/RULE_LIFECYCLE_POLICY.md": "规则生命周期策略",
    "core/RULE_EXCEPTION_POLICY.md": "规则例外策略",
    "core/FUSION_POLICY.md": "融合策略",
    "core/LAYER_DEPENDENCY_RULES.json": "层间依赖规则",
    "core/LAYER_DEPENDENCY_MATRIX.md": "层间依赖矩阵",
    "core/LAYER_IO_CONTRACTS.md": "层间 IO 契约",
    "core/CHANGE_IMPACT_MATRIX.md": "变更影响矩阵",
    "core/SINGLE_SOURCE_OF_TRUTH.md": "唯一真源清单",
    "infrastructure/inventory/skill_registry.json": "技能注册表",
}

# 对架构有利的文件 - 应该融入
ARCHITECTURE_BENEFICIAL_FILES = {
    # 规则相关
    "core/contracts/*.schema.json": "Schema 契约",
    "scripts/check_*.py": "检查脚本",
    "scripts/run_*.py": "运行脚本",
    "scripts/render_*.py": "渲染脚本",
    "governance/*.py": "治理模块",
    "governance/guard/*.json": "保护配置",
    "infrastructure/*.py": "基础设施脚本",
    "reports/ops/*.json": "运维报告",
}

# 不应该放入架构的文件 - 应该提取
EXTRACT_PATTERNS = {
    # 临时文件
    "*.tar.gz": "压缩包 - 应清理或归档",
    "*.tgz": "压缩包 - 应清理或归档",
    "*.zip": "压缩包 - 应清理或归档",
    "*.bak": "备份文件 - 应清理",
    "*.tmp": "临时文件 - 应清理",
    
    # 日志文件
    "*.log": "日志文件 - 应移到 logs/",
    
    # 缓存文件
    "__pycache__": "Python 缓存 - 应清理",
    ".pytest_cache": "测试缓存 - 应清理",
    "node_modules": "Node 模块 - 应在 .gitignore",
    ".venv": "Python 虚拟环境 - 应在 .gitignore",
}

# 文件分类规则
FILE_CLASSIFICATION = {
    # 文档类 -> docs/
    "docs": {
        "patterns": ["API_REFERENCE", "CHANGELOG", "CONTRIBUTING", "FILE_INVENTORY", 
                     "FUSION_REPORT", "UPGRADE_SUMMARY", "ARCHITECTURE_SUMMARY",
                     "README", "USAGE", "GUIDE", "TUTORIAL"],
        "extensions": [".md"],
        "description": "文档类文件",
        "priority": 1
    },
    
    # 架构归档 -> docs/archives/
    "docs/archives": {
        "patterns": ["架构图", "架构报告", "FILE_INVENTORY.pdf", "ARCHITECTURE_V"],
        "extensions": [".pdf"],
        "description": "架构文档归档",
        "priority": 2
    },
    
    # 历史记录 -> docs/history/
    "docs/history": {
        "patterns": ["V4.3.", "V4.2.", "V4.1.", "V3.", "UPGRADE_SUMMARY", "MIGRATION"],
        "extensions": [".md"],
        "description": "版本升级历史",
        "priority": 2
    },
    
    # 安全文档 -> governance/docs/
    "governance/docs": {
        "patterns": ["SAFETY", "SECURITY", "安全", "COMPLIANCE", "AUDIT"],
        "extensions": [".md"],
        "description": "安全治理文档",
        "priority": 2
    },
    
    # 日志文件 -> logs/
    "logs": {
        "patterns": [],
        "extensions": [".log"],
        "description": "日志文件",
        "priority": 1
    },
    
    # 归档 -> archive/
    "archive": {
        "patterns": ["deprecated", "old", "backup", "legacy"],
        "extensions": [".bak", ".old"],
        "description": "归档文件",
        "priority": 3
    }
}


class FusionEngine:
    """融合引擎 V2.0.0"""
    
    def __init__(self, root: Path):
        self.root = root
        self.fusion_log = []
        self.skipped_files = []
        self.moved_files = []
        self.extract_suggestions = []
        self.beneficial_suggestions = []
    
    def is_core_file(self, filename: str) -> bool:
        """判断是否为核心配置文件"""
        return filename in CORE_ROOT_FILES
    
    def impacts_architecture(self, filepath: str) -> bool:
        """判断是否影响架构"""
        return filepath in ARCHITECTURE_IMPACT_FILES
    
    def should_extract(self, filepath: Path) -> Tuple[bool, str]:
        """判断是否应该提取（不应该放入架构）"""
        filename = filepath.name
        
        for pattern, reason in EXTRACT_PATTERNS.items():
            if pattern.startswith("*"):
                if filepath.suffix == pattern[1:] or filename.endswith(pattern[1:]):
                    return True, reason
            elif pattern in str(filepath):
                return True, reason
        
        return False, ""
    
    def is_beneficial_to_architecture(self, filepath: Path) -> Tuple[bool, str]:
        """判断是否对架构有利"""
        relative_path = str(filepath.relative_to(self.root)) if filepath.is_relative_to(self.root) else filepath.name
        
        for pattern, description in ARCHITECTURE_BENEFICIAL_FILES.items():
            if "*" in pattern:
                # 通配符匹配
                import fnmatch
                if fnmatch.fnmatch(relative_path, pattern):
                    return True, description
            elif pattern in relative_path:
                return True, description
        
        return False, ""
    
    def classify_file(self, filepath: Path) -> Tuple[str, str, int]:
        """
        分类文件，返回 (目标目录, 分类原因, 优先级)
        """
        filename = filepath.name
        relative_path = str(filepath.relative_to(self.root)) if filepath.is_relative_to(self.root) else filepath.name
        
        # 1. 核心配置文件 - 保留根目录
        if self.is_core_file(filename):
            return "root", f"核心配置文件: {CORE_ROOT_FILES.get(filename, '未知')}", 0
        
        # 2. 影响架构的文件 - 不可移动
        if self.impacts_architecture(relative_path):
            return "keep", "影响架构，不可移动", 0
        
        # 3. 检查是否应该提取
        should_extract, extract_reason = self.should_extract(filepath)
        if should_extract:
            return "extract", extract_reason, 0
        
        # 4. 按规则分类（按优先级排序）
        sorted_classifications = sorted(FILE_CLASSIFICATION.items(), 
                                        key=lambda x: x[1].get("priority", 99))
        
        for target_dir, rules in sorted_classifications:
            # 检查文件名模式
            for pattern in rules.get("patterns", []):
                if pattern in filename:
                    return target_dir, f"匹配模式: {pattern}", rules.get("priority", 99)
            
            # 检查扩展名
            if filepath.suffix in rules.get("extensions", []):
                # 对于 .md 文件，需要更精确的判断
                if filepath.suffix == ".md":
                    # 如果是技能目录下的，保留在技能目录
                    if "skills/" in relative_path:
                        return "skill_docs", "技能文档", 99
                return target_dir, f"扩展名: {filepath.suffix}", rules.get("priority", 99)
        
        # 5. 默认保留原位置
        return "keep", "未匹配任何规则，保留原位置", 99
    
    def should_fuse(self, filepath: Path) -> Tuple[bool, str, str]:
        """
        判断是否应该融合
        返回: (是否融合, 目标目录, 原因)
        """
        target, reason, priority = self.classify_file(filepath)
        
        if target == "root":
            return False, "root", f"核心文件保留: {reason}"
        elif target == "keep":
            return False, "keep", reason
        elif target == "extract":
            return False, "extract", f"应提取: {reason}"
        elif target == "skill_docs":
            return False, "skill_docs", "技能文档保留在技能目录"
        else:
            return True, target, reason
    
    def fuse_file(self, filepath: Path, target_dir: str, dry_run: bool = False) -> Dict:
        """执行文件融合"""
        result = {
            "file": str(filepath),
            "target_dir": target_dir,
            "success": False,
            "action": "none",
            "error": None
        }
        
        try:
            target_path = self.root / target_dir
            target_path.mkdir(parents=True, exist_ok=True)
            
            new_path = target_path / filepath.name
            
            if dry_run:
                result["action"] = "would_move"
                result["success"] = True
            else:
                shutil.move(str(filepath), str(new_path))
                result["action"] = "moved"
                result["success"] = True
                result["new_path"] = str(new_path)
                self.moved_files.append({
                    "from": str(filepath),
                    "to": str(new_path)
                })
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def audit_structure(self) -> Dict:
        """
        审查现有结构
        返回优化建议
        """
        results = {
            "should_extract": [],      # 应该提取的文件
            "beneficial_to_add": [],   # 对架构有利应融入的
            "core_files_ok": [],       # 核心文件状态正常
            "architecture_files_ok": [], # 架构文件状态正常
            "issues": []               # 发现的问题
        }
        
        # 1. 检查根目录文件
        for filepath in self.root.iterdir():
            if not filepath.is_file():
                continue
            
            filename = filepath.name
            
            # 检查核心文件
            if self.is_core_file(filename):
                results["core_files_ok"].append(filename)
                continue
            
            # 检查是否应该提取
            should_extract, extract_reason = self.should_extract(filepath)
            if should_extract:
                results["should_extract"].append({
                    "file": filename,
                    "reason": extract_reason,
                    "suggestion": "清理或移到 archive/"
                })
            
            # 检查是否对架构有利
            is_beneficial, beneficial_reason = self.is_beneficial_to_architecture(filepath)
            if is_beneficial:
                results["beneficial_to_add"].append({
                    "file": filename,
                    "reason": beneficial_reason
                })
        
        # 2. 检查架构关键文件是否存在
        for arch_file in ARCHITECTURE_IMPACT_FILES:
            arch_path = self.root / arch_file
            if arch_path.exists():
                results["architecture_files_ok"].append(arch_file)
            else:
                results["issues"].append({
                    "type": "missing_architecture_file",
                    "file": arch_file,
                    "suggestion": "创建或恢复此文件"
                })
        
        # 3. 检查目录结构
        expected_dirs = ["core", "docs", "governance", "infrastructure", "scripts", 
                        "skills", "execution", "orchestration", "reports", "memory"]
        for dir_name in expected_dirs:
            dir_path = self.root / dir_name
            if not dir_path.exists():
                results["issues"].append({
                    "type": "missing_directory",
                    "directory": dir_name,
                    "suggestion": f"创建 {dir_name}/ 目录"
                })
        
        return results
    
    def scan_and_fuse(self, directory: Path = None, dry_run: bool = False) -> Dict:
        """扫描目录并执行融合"""
        if directory is None:
            directory = self.root
        
        results = {
            "scanned": 0,
            "fused": 0,
            "skipped": 0,
            "extracted": 0,
            "errors": 0,
            "details": []
        }
        
        for filepath in directory.iterdir():
            if not filepath.is_file():
                continue
            
            if filepath.name.startswith('.'):
                continue
            
            results["scanned"] += 1
            
            should_fuse, target_dir, reason = self.should_fuse(filepath)
            
            detail = {
                "file": filepath.name,
                "should_fuse": should_fuse,
                "target": target_dir,
                "reason": reason
            }
            
            if target_dir == "extract":
                results["extracted"] += 1
                self.extract_suggestions.append({
                    "file": filepath.name,
                    "reason": reason
                })
            elif should_fuse:
                fuse_result = self.fuse_file(filepath, target_dir, dry_run)
                detail["result"] = fuse_result
                
                if fuse_result["success"]:
                    results["fused"] += 1
                else:
                    results["errors"] += 1
            else:
                results["skipped"] += 1
                self.skipped_files.append(filepath.name)
            
            results["details"].append(detail)
        
        return results
    
    def generate_report(self, results: Dict, audit_results: Dict = None) -> str:
        """生成融合报告"""
        report = []
        report.append("# 融合报告")
        report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 融合统计
        report.append(f"\n## 融合统计\n")
        report.append(f"- 扫描文件: {results['scanned']}")
        report.append(f"- 已融合: {results['fused']}")
        report.append(f"- 已跳过: {results['skipped']}")
        report.append(f"- 应提取: {results.get('extracted', 0)}")
        report.append(f"- 错误: {results['errors']}")
        
        # 已移动文件
        if self.moved_files:
            report.append(f"\n## 已移动文件\n")
            for item in self.moved_files:
                report.append(f"- `{item['from']}` -> `{item['to']}`")
        
        # 应提取的文件
        if self.extract_suggestions:
            report.append(f"\n## 应提取的文件\n")
            for item in self.extract_suggestions:
                report.append(f"- `{item['file']}`: {item['reason']}")
        
        # 跳过的文件
        if self.skipped_files:
            report.append(f"\n## 跳过的文件\n")
            for f in self.skipped_files[:20]:  # 限制显示数量
                report.append(f"- {f}")
            if len(self.skipped_files) > 20:
                report.append(f"- ... 还有 {len(self.skipped_files) - 20} 个文件")
        
        # 审查结果
        if audit_results:
            report.append(f"\n## 结构审查\n")
            
            if audit_results.get("should_extract"):
                report.append(f"\n### 应提取的文件\n")
                for item in audit_results["should_extract"]:
                    report.append(f"- `{item['file']}`: {item['reason']}")
                    report.append(f"  - 建议: {item['suggestion']}")
            
            if audit_results.get("issues"):
                report.append(f"\n### 发现的问题\n")
                for issue in audit_results["issues"]:
                    report.append(f"- [{issue['type']}] {issue.get('file', issue.get('directory', ''))}")
                    report.append(f"  - 建议: {issue['suggestion']}")
            
            report.append(f"\n### 状态正常的文件\n")
            report.append(f"- 核心文件: {len(audit_results.get('core_files_ok', []))} 个")
            report.append(f"- 架构文件: {len(audit_results.get('architecture_files_ok', []))} 个")
        
        return "\n".join(report)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="融合机制模块 V2.0.0")
    parser.add_argument("--scan", action="store_true", help="扫描并显示融合建议")
    parser.add_argument("--audit", action="store_true", help="审查现有结构")
    parser.add_argument("--execute", action="store_true", help="执行融合操作")
    parser.add_argument("--dry-run", action="store_true", help="模拟执行，不实际移动文件")
    parser.add_argument("--report", type=str, help="保存报告到指定文件")
    args = parser.parse_args()
    
    root = get_project_root()
    engine = FusionEngine(root)
    
    print("╔══════════════════════════════════════════════════╗")
    print("║          融合机制模块 V2.0.0                   ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"工作目录: {root}")
    print()
    
    audit_results = None
    
    if args.audit:
        print("【结构审查模式】")
        print()
        audit_results = engine.audit_structure()
        
        print("=== 应提取的文件 ===")
        for item in audit_results["should_extract"]:
            print(f"  - {item['file']}: {item['reason']}")
        
        print()
        print("=== 发现的问题 ===")
        for issue in audit_results["issues"]:
            print(f"  - [{issue['type']}] {issue.get('file', issue.get('directory', ''))}")
            print(f"    建议: {issue['suggestion']}")
        
        print()
        print(f"=== 状态正常 ===")
        print(f"  核心文件: {len(audit_results['core_files_ok'])} 个")
        print(f"  架构文件: {len(audit_results['architecture_files_ok'])} 个")
        print()
    
    if args.scan or args.dry_run or args.execute:
        dry_run = not args.execute
        print(f"模式: {'模拟执行' if dry_run else '实际执行'}")
        print()
        
        results = engine.scan_and_fuse(dry_run=dry_run)
        
        print(engine.generate_report(results, audit_results))
        
        if args.report:
            report_path = Path(args.report)
            report_path.write_text(engine.generate_report(results, audit_results), encoding='utf-8')
            print(f"\n报告已保存: {report_path}")
    elif not args.audit:
        parser.print_help()


if __name__ == "__main__":
    main()
