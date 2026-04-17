#!/usr/bin/env python3
"""
文档同步引擎 - V2.0.0

职责：
1. 检测代码变更是否需要同步到文档
2. 自动生成文档更新建议
3. 执行文档同步
4. 检测架构文档是否需要更新
5. 检测新增模块是否需要注册

V2.0.0 新增：
- 架构文档自动更新
- 模块注册检测
- 能力矩阵自动更新
- 多文档联动同步
"""

import os
import sys
import re
import json
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


@dataclass
class SyncSuggestion:
    """同步建议"""
    sync_type: str  # new_method, new_module, new_capability, architecture_update
    source_file: str
    target_doc: str
    section: str
    content: str
    priority: str  # high, medium, low
    auto_sync: bool  # 是否可以自动同步


class DocSyncEngine:
    """文档同步引擎 V2.0"""
    
    def __init__(self, root: Path):
        self.root = root
        self.sync_suggestions: List[SyncSuggestion] = []
        self.synced_items: List[Dict] = []
        self.errors: List[str] = []
        
        # 架构文档路径
        self.architecture_doc = root / "core" / "ARCHITECTURE.md"
        self.memory_doc = root / "MEMORY.md"
        self.agents_doc = root / "AGENTS.md"
        
        # 层级目录映射
        self.layer_dirs = {
            "L1": ["core/"],
            "L2": ["memory_context/"],
            "L3": ["orchestration/"],
            "L4": ["execution/", "skills/"],
            "L5": ["governance/"],
            "L6": ["infrastructure/"]
        }
        
        # 排除的文件模式（噪音文件）
        self.exclude_patterns = [
            "memory_context/traces/",
            "memory_context/long_term/",
            "orchestration/state/checkpoints/",
            "orchestration/state/rollback/",
            "reports/workflow/events/",
            "reports/workflow/instances/",
            "reports/workflow/recovery/",
            "reports/audit/decision_",
            "__pycache__/",
            ".pyc",
            "node_modules/",
            ".jsonl",
        ]
        
        # 能力关键词映射
        self.capability_keywords = {
            "recovery": "恢复能力",
            "review": "审查能力",
            "rules": "规则管控",
            "risk": "风险管控",
            "abuse": "滥用防护",
            "automation": "自动化",
            "cognition": "认知能力",
            "memory": "记忆能力",
            "workflow": "工作流",
            "skill": "技能管理"
        }
    
    def get_git_changed_files(self) -> List[str]:
        """获取 git 变更文件"""
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1'],
                cwd=str(self.root),
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        except Exception:
            pass
        return []
    
    def get_all_new_files(self) -> List[str]:
        """获取所有新增文件（相对于 git）"""
        import subprocess
        files = []
        try:
            # 获取新增的文件
            result = subprocess.run(
                ['git', 'diff', '--name-only', '--diff-filter=A', 'HEAD~1'],
                cwd=str(self.root),
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                files.extend([f.strip() for f in result.stdout.strip().split('\n') if f.strip()])
        except Exception:
            pass
        return files
    
    # ==================== 检测器 ====================
    
    def detect_new_module(self, filepath: Path) -> Optional[SyncSuggestion]:
        """检测新增模块"""
        relative_path = str(filepath.relative_to(self.root)) if filepath.is_relative_to(self.root) else filepath.name
        
        # 检查是否是层级目录下的新 Python 模块
        for layer, dirs in self.layer_dirs.items():
            for dir_prefix in dirs:
                if relative_path.startswith(dir_prefix) and filepath.suffix == '.py':
                    # 检查是否是新目录
                    parent_dir = filepath.parent
                    if parent_dir.exists():
                        py_files = list(parent_dir.glob("*.py"))
                        if len(py_files) <= 3:  # 新目录，文件少
                            module_name = parent_dir.name
                            return SyncSuggestion(
                                sync_type="new_module",
                                source_file=relative_path,
                                target_doc="core/ARCHITECTURE.md",
                                section=f"{layer} Governance" if "governance" in relative_path else f"{layer} 扩展",
                                content=f"- **{module_name}/**: 新增模块",
                                priority="high",
                                auto_sync=True
                            )
        return None
    
    def detect_new_capability(self, filepath: Path) -> Optional[SyncSuggestion]:
        """检测新增能力"""
        relative_path = str(filepath.relative_to(self.root)) if filepath.is_relative_to(self.root) else filepath.name
        filename = filepath.name.lower()
        
        # 只检测 Python 文件
        if filepath.suffix != '.py':
            return None
        
        # 检查文件名中的能力关键词
        for keyword, capability in self.capability_keywords.items():
            if keyword in filename or keyword in relative_path.lower():
                # 检查架构文档是否已包含此能力
                if self.architecture_doc.exists():
                    content = self.architecture_doc.read_text(encoding='utf-8')
                    # 检查能力矩阵中是否已有此能力
                    if f"| {capability} |" not in content:
                        return SyncSuggestion(
                            sync_type="new_capability",
                            source_file=relative_path,
                            target_doc="core/ARCHITECTURE.md",
                            section="能力矩阵",
                            content=f"| {capability} | 1 | 100% |",
                            priority="high",
                            auto_sync=True
                        )
        return None
    
    def detect_architecture_update_needed(self, filepath: Path) -> Optional[SyncSuggestion]:
        """检测是否需要更新架构文档"""
        relative_path = str(filepath.relative_to(self.root)) if filepath.is_relative_to(self.root) else filepath.name
        
        # 只检测 Python 文件
        if filepath.suffix != '.py':
            return None
        
        # 核心模块变更需要更新架构
        core_patterns = [
            "governance/risk/",
            "governance/recovery/",
            "governance/review/",
            "governance/rules/",
            "orchestration/workflow/",
            "skills/runtime/",
            "memory_context/",
            "core/events/",
            "infrastructure/automation/"
        ]
        
        for pattern in core_patterns:
            if pattern in relative_path:
                # 检查架构文档是否提到此模块
                if self.architecture_doc.exists():
                    content = self.architecture_doc.read_text(encoding='utf-8')
                    module_name = filepath.stem
                    # 排除 __init__
                    if module_name == "__init__":
                        # 检查目录名
                        module_name = filepath.parent.name
                    if module_name not in content:
                        return SyncSuggestion(
                            sync_type="architecture_update",
                            source_file=relative_path,
                            target_doc="core/ARCHITECTURE.md",
                            section="治理层扩展" if "governance" in relative_path else "架构扩展",
                            content=f"- **{module_name}**: 新增功能模块",
                            priority="high",
                            auto_sync=True
                        )
        return None
    
    def detect_new_public_method(self, filepath: Path) -> List[SyncSuggestion]:
        """检测新增公共方法"""
        suggestions = []
        try:
            content = filepath.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            # 获取旧版本的方法
            import subprocess
            old_methods = set()
            try:
                result = subprocess.run(
                    ['git', 'show', f'HEAD~1:{filepath.relative_to(self.root)}'],
                    cwd=str(self.root),
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    old_tree = ast.parse(result.stdout)
                    for node in ast.walk(old_tree):
                        if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                            old_methods.add(node.name)
            except Exception:
                pass
            
            # 找新增方法
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('_') or node.name.startswith('test_'):
                        continue
                    if node.name not in old_methods:
                        relative_path = str(filepath.relative_to(self.root)) if filepath.is_relative_to(self.root) else filepath.name
                        suggestions.append(SyncSuggestion(
                            sync_type="new_method",
                            source_file=relative_path,
                            target_doc="MEMORY.md",
                            section="最近变更",
                            content=f"- **{node.name}**: 新增方法 ({relative_path})",
                            priority="low",
                            auto_sync=False
                        ))
        except Exception as e:
            self.errors.append(f"解析 {filepath} 失败: {e}")
        
        return suggestions
    
    def detect_new_makefile_target(self, filepath: Path) -> List[SyncSuggestion]:
        """检测新增 Makefile 目标"""
        suggestions = []
        try:
            content = filepath.read_text(encoding='utf-8')
            
            # 获取旧版本的目标
            import subprocess
            old_targets = set()
            try:
                result = subprocess.run(
                    ['git', 'show', f'HEAD~1:{filepath.relative_to(self.root)}'],
                    cwd=str(self.root),
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        match = re.match(r'^([a-zA-Z][a-zA-Z0-9_-]*):', line)
                        if match:
                            old_targets.add(match.group(1))
            except Exception:
                pass
            
            # 找新增目标
            for line in content.split('\n'):
                match = re.match(r'^([a-zA-Z][a-zA-Z0-9_-]*):', line)
                if match:
                    target = match.group(1)
                    if target not in old_targets and target not in ['PHONY', 'SHELL', 'MAKE']:
                        suggestions.append(SyncSuggestion(
                            sync_type="new_target",
                            source_file="Makefile",
                            target_doc="MEMORY.md",
                            section="最近变更",
                            content=f"- **{target}**: 新增 Makefile 目标",
                            priority="medium",
                            auto_sync=False
                        ))
        except Exception as e:
            self.errors.append(f"解析 Makefile 失败: {e}")
        
        return suggestions
    
    def detect_new_file_type(self, filepath: Path) -> Optional[SyncSuggestion]:
        """检测新增文件类型（如新的报告目录、新的配置文件等）"""
        relative_path = str(filepath.relative_to(self.root)) if filepath.is_relative_to(self.root) else filepath.name
        
        # 检测新的报告目录
        if relative_path.startswith("reports/") and "/" in relative_path[8:]:
            parts = relative_path.split("/")
            if len(parts) >= 3:
                new_dir = parts[1]
                # 检查是否是新目录
                if self.architecture_doc.exists():
                    content = self.architecture_doc.read_text(encoding='utf-8')
                    if f"reports/{new_dir}/" not in content and new_dir not in ["ops", "audit", "metrics", "workflow", "release", "observability", "benchmarks", "bundles"]:
                        return SyncSuggestion(
                            sync_type="new_report_type",
                            source_file=relative_path,
                            target_doc="core/ARCHITECTURE.md",
                            section="报告体系",
                            content=f"- `reports/{new_dir}/`: 新增报告目录",
                            priority="medium",
                            auto_sync=True
                        )
        
        # 检测新的 live 目录
        if relative_path.startswith("reports/live_"):
            return SyncSuggestion(
                sync_type="new_live_system",
                source_file=relative_path,
                target_doc="core/ARCHITECTURE.md",
                section="运营体系",
                content=f"- 新增运营体系文件: {relative_path}",
                priority="high",
                auto_sync=True
            )
        
        return None
    
    # ==================== 扫描 ====================
    
    def scan_changes(self, files: List[str] = None) -> List[SyncSuggestion]:
        """扫描变更文件"""
        if files is None:
            files = self.get_git_changed_files()
        
        # 也检查新增文件
        new_files = self.get_all_new_files()
        all_files = list(set(files + new_files))
        
        # 过滤噪音文件
        filtered_files = []
        for file_path in all_files:
            excluded = False
            for pattern in self.exclude_patterns:
                if pattern in file_path:
                    excluded = True
                    break
            if not excluded:
                filtered_files.append(file_path)
        
        for file_path in filtered_files:
            filepath = self.root / file_path
            if not filepath.exists():
                continue
            
            # 检测新模块
            suggestion = self.detect_new_module(filepath)
            if suggestion:
                self.sync_suggestions.append(suggestion)
            
            # 检测新能力
            suggestion = self.detect_new_capability(filepath)
            if suggestion:
                self.sync_suggestions.append(suggestion)
            
            # 检测架构更新需求
            suggestion = self.detect_architecture_update_needed(filepath)
            if suggestion:
                self.sync_suggestions.append(suggestion)
            
            # 检测新文件类型
            suggestion = self.detect_new_file_type(filepath)
            if suggestion:
                self.sync_suggestions.append(suggestion)
            
            # 检测新方法
            if filepath.suffix == '.py':
                suggestions = self.detect_new_public_method(filepath)
                self.sync_suggestions.extend(suggestions)
            
            # 检测 Makefile 目标
            if filepath.name == 'Makefile':
                suggestions = self.detect_new_makefile_target(filepath)
                self.sync_suggestions.extend(suggestions)
        
        # 去重
        seen = set()
        unique_suggestions = []
        for s in self.sync_suggestions:
            key = (s.sync_type, s.source_file, s.section)
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(s)
        
        self.sync_suggestions = unique_suggestions
        return self.sync_suggestions
    
    # ==================== 同步执行 ====================
    
    def sync_to_doc(self, suggestion: SyncSuggestion) -> bool:
        """同步到文档"""
        try:
            doc_path = self.root / suggestion.target_doc
            if not doc_path.exists():
                return False
            
            doc_content = doc_path.read_text(encoding='utf-8')
            
            # 查找章节
            section_pattern = re.compile(
                rf'^##+\s+{re.escape(suggestion.section)}',
                re.MULTILINE
            )
            match = section_pattern.search(doc_content)
            
            if match:
                # 在章节后插入内容
                insert_pos = match.end()
                # 找到下一个章节
                next_section = re.search(r'\n##', doc_content[insert_pos:])
                if next_section:
                    insert_pos += next_section.start()
                
                new_content = doc_content[:insert_pos] + "\n" + suggestion.content + doc_content[insert_pos:]
                doc_path.write_text(new_content, encoding='utf-8')
                return True
            else:
                # 在文件末尾追加
                new_content = doc_content + f"\n\n## {suggestion.section}\n{suggestion.content}"
                doc_path.write_text(new_content, encoding='utf-8')
                return True
        except Exception as e:
            self.errors.append(f"同步到 {suggestion.target_doc} 失败: {e}")
            return False
    
    def execute_sync(self, dry_run: bool = False) -> Dict:
        """执行同步"""
        results = {
            "suggestions": len(self.sync_suggestions),
            "synced": 0,
            "skipped": 0,
            "auto_synced": 0,
            "manual_required": 0,
            "errors": len(self.errors),
            "details": []
        }
        
        if not self.sync_suggestions:
            return results
        
        for suggestion in self.sync_suggestions:
            detail = {
                "type": suggestion.sync_type,
                "source": suggestion.source_file,
                "target": suggestion.target_doc,
                "section": suggestion.section,
                "content": suggestion.content,
                "priority": suggestion.priority,
                "auto_sync": suggestion.auto_sync
            }
            
            if dry_run:
                detail["action"] = "would_sync"
                results["details"].append(detail)
            else:
                # 高优先级且可自动同步的，自动执行
                if suggestion.priority == "high" and suggestion.auto_sync:
                    success = self.sync_to_doc(suggestion)
                    if success:
                        results["synced"] += 1
                        results["auto_synced"] += 1
                        detail["action"] = "auto_synced"
                        self.synced_items.append({
                            "source": suggestion.source_file,
                            "target": suggestion.target_doc,
                            "content": suggestion.content
                        })
                    else:
                        results["skipped"] += 1
                        detail["action"] = "sync_failed"
                else:
                    # 需要手动确认
                    results["manual_required"] += 1
                    detail["action"] = "manual_required"
                
                results["details"].append(detail)
        
        return results
    
    # ==================== 报告 ====================
    
    def generate_report(self, results: Dict) -> str:
        """生成报告"""
        lines = []
        lines.append("╔══════════════════════════════════════════════════╗")
        lines.append("║          文档同步引擎 V2.0.0                   ║")
        lines.append("╚══════════════════════════════════════════════════╝")
        lines.append("")
        lines.append(f"工作目录: {self.root}")
        lines.append("")
        lines.append("【同步统计】")
        lines.append(f"  发现建议: {results['suggestions']}")
        lines.append(f"  已同步: {results['synced']}")
        lines.append(f"  自动同步: {results.get('auto_synced', 0)}")
        lines.append(f"  需手动确认: {results.get('manual_required', 0)}")
        lines.append(f"  已跳过: {results['skipped']}")
        lines.append(f"  错误: {results['errors']}")
        lines.append("")
        
        if self.sync_suggestions:
            lines.append("【同步建议】")
            for s in self.sync_suggestions:
                lines.append(f"  [{s.priority}] {s.sync_type}: {s.source_file}")
                lines.append(f"    → {s.target_doc} > {s.section}")
                lines.append(f"    内容: {s.content[:50]}...")
            lines.append("")
        
        if results.get('details'):
            lines.append("【同步详情】")
            for d in results['details']:
                lines.append(f"  {d['action']}: {d['source']} → {d['target']}")
            lines.append("")
        
        if self.errors:
            lines.append("【错误】")
            for e in self.errors:
                lines.append(f"  ❌ {e}")
            lines.append("")
        
        return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="文档同步引擎 V2.0.0")
    parser.add_argument("--scan", action="store_true", help="扫描变更并显示同步建议")
    parser.add_argument("--execute", action="store_true", help="执行文档同步")
    parser.add_argument("--dry-run", action="store_true", help="模拟执行")
    parser.add_argument("--files", nargs="+", help="指定要分析的文件")
    args = parser.parse_args()
    
    root = get_project_root()
    engine = DocSyncEngine(root)
    
    # 扫描变更
    files = args.files if args.files else None
    suggestions = engine.scan_changes(files)
    
    # 执行同步
    dry_run = not args.execute
    results = engine.execute_sync(dry_run=dry_run)
    
    print(engine.generate_report(results))
    
    return 0 if results['errors'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
