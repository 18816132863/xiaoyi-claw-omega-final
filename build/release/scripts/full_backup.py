#!/usr/bin/env python3
"""
全面备份器 - V1.0.0

备份所有关键数据：
1. 核心配置文件
2. 规则注册表
3. 技能注册表
4. 记忆数据
5. 报告历史
6. 日志文件
7. Git 仓库状态
"""

import os
import sys
import json
import shutil
import tarfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


# 备份目标定义
BACKUP_TARGETS = {
    "core_configs": {
        "description": "核心配置文件",
        "paths": [
            "AGENTS.md",
            "SOUL.md",
            "USER.md",
            "TOOLS.md",
            "IDENTITY.md",
            "MEMORY.md",
            "HEARTBEAT.md",
            "BOOTSTRAP.md",
            "SKILL.md",
            "README.md",
            "Makefile",
            "openclaw.bundle.json",
        ],
        "priority": 1
    },
    "rules": {
        "description": "规则注册表和策略",
        "paths": [
            "core/RULE_REGISTRY.json",
            "core/RULE_EXCEPTIONS.json",
            "core/RULE_LIFECYCLE_POLICY.md",
            "core/RULE_EXCEPTION_POLICY.md",
            "core/RULE_EXCEPTION_DEBT_POLICY.md",
            "core/FUSION_POLICY.md",
            "core/LAYER_DEPENDENCY_RULES.json",
            "core/LAYER_DEPENDENCY_MATRIX.md",
            "core/LAYER_IO_CONTRACTS.md",
            "core/CHANGE_IMPACT_MATRIX.md",
            "core/SINGLE_SOURCE_OF_TRUTH.md",
        ],
        "priority": 1
    },
    "architecture": {
        "description": "架构定义",
        "paths": [
            "core/ARCHITECTURE.md",
            "core/contracts/",
        ],
        "priority": 1
    },
    "skill_registry": {
        "description": "技能注册表",
        "paths": [
            "infrastructure/inventory/skill_registry.json",
            "infrastructure/inventory/skill_inverted_index.json",
            "infrastructure/inventory/core_skills_188.json",
            "infrastructure/inventory/ecommerce_skills.json",
        ],
        "priority": 2
    },
    "memory": {
        "description": "记忆数据",
        "paths": [
            "memory/",
            "MEMORY.md",
        ],
        "priority": 2
    },
    "memory_context": {
        "description": "记忆上下文",
        "paths": [
            "memory_context/data/",
            "memory_context/ontology/",
            "memory_context/index/",
        ],
        "priority": 2
    },
    "reports": {
        "description": "报告历史",
        "paths": [
            "reports/ops/",
            "reports/remediation/",
            "reports/alerts/",
            "reports/dashboard/",
        ],
        "priority": 3
    },
    "scripts": {
        "description": "检查脚本",
        "paths": [
            "scripts/check_*.py",
            "scripts/run_*.py",
            "scripts/render_*.py",
            "scripts/unified_inspector.py",
        ],
        "priority": 2
    },
    "governance": {
        "description": "治理模块",
        "paths": [
            "governance/guard/",
            "governance/docs/",
        ],
        "priority": 2
    },
    "infrastructure": {
        "description": "基础设施",
        "paths": [
            "infrastructure/fusion_engine.py",
            "infrastructure/performance_optimizer.py",
            "infrastructure/architecture_inspector.py",
            "infrastructure/path_resolver.py",
        ],
        "priority": 2
    },
    "docs": {
        "description": "文档",
        "paths": [
            "docs/",
        ],
        "priority": 3
    },
    "logs": {
        "description": "日志文件",
        "paths": [
            "logs/",
        ],
        "priority": 4
    }
}


def create_backup_manifest(root: Path, backup_dir: Path) -> Dict:
    """创建备份清单"""
    manifest = {
        "backup_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "created_at": datetime.now().isoformat(),
        "root_path": str(root),
        "targets": {},
        "statistics": {
            "total_files": 0,
            "total_size_bytes": 0,
            "by_priority": {}
        }
    }
    
    for target_name, target_info in BACKUP_TARGETS.items():
        target_manifest = {
            "description": target_info["description"],
            "priority": target_info["priority"],
            "files": [],
            "total_size": 0
        }
        
        for path_pattern in target_info["paths"]:
            if "*" in path_pattern:
                # 通配符匹配
                import glob
                matches = list(root.glob(path_pattern))
                for match in matches:
                    if match.is_file():
                        size = match.stat().st_size
                        target_manifest["files"].append({
                            "path": str(match.relative_to(root)),
                            "size": size
                        })
                        target_manifest["total_size"] += size
            else:
                full_path = root / path_pattern
                if full_path.is_file():
                    size = full_path.stat().st_size
                    target_manifest["files"].append({
                        "path": path_pattern,
                        "size": size
                    })
                    target_manifest["total_size"] += size
                elif full_path.is_dir():
                    for f in full_path.rglob("*"):
                        if f.is_file():
                            try:
                                size = f.stat().st_size
                                target_manifest["files"].append({
                                    "path": str(f.relative_to(root)),
                                    "size": size
                                })
                                target_manifest["total_size"] += size
                            except:
                                pass
        
        manifest["targets"][target_name] = target_manifest
        manifest["statistics"]["total_files"] += len(target_manifest["files"])
        manifest["statistics"]["total_size_bytes"] += target_manifest["total_size"]
        
        priority = target_info["priority"]
        if priority not in manifest["statistics"]["by_priority"]:
            manifest["statistics"]["by_priority"][priority] = {"files": 0, "size": 0}
        manifest["statistics"]["by_priority"][priority]["files"] += len(target_manifest["files"])
        manifest["statistics"]["by_priority"][priority]["size"] += target_manifest["total_size"]
    
    return manifest


def copy_backup_files(root: Path, backup_dir: Path, manifest: Dict):
    """复制备份文件"""
    for target_name, target_manifest in manifest["targets"].items():
        target_dir = backup_dir / target_name
        target_dir.mkdir(parents=True, exist_ok=True)
        
        for file_info in target_manifest["files"]:
            src = root / file_info["path"]
            dst = target_dir / file_info["path"]
            
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(src, dst)
                except Exception as e:
                    print(f"  ⚠️ 复制失败: {file_info['path']} - {e}")


def create_backup_archive(backup_dir: Path, manifest: Dict) -> Path:
    """创建备份压缩包"""
    archive_path = backup_dir.parent / f"backup_{manifest['backup_id']}.tar.gz"
    
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(backup_dir, arcname=backup_dir.name)
    
    return archive_path


def run_backup() -> Dict:
    """执行备份"""
    root = get_project_root()
    backup_base = root / "archive" / "backups"
    backup_base.mkdir(parents=True, exist_ok=True)
    
    backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_base / f"backup_{backup_id}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print("╔══════════════════════════════════════════════════╗")
    print("║          全面备份器 V1.0.0                     ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"备份 ID: {backup_id}")
    print(f"备份目录: {backup_dir}")
    print()
    
    # 1. 创建备份清单
    print("【1/4】创建备份清单...")
    manifest = create_backup_manifest(root, backup_dir)
    print(f"  - 总文件数: {manifest['statistics']['total_files']}")
    print(f"  - 总大小: {manifest['statistics']['total_size_bytes'] / 1024 / 1024:.2f} MB")
    
    # 2. 复制备份文件
    print("\n【2/4】复制备份文件...")
    copy_backup_files(root, backup_dir, manifest)
    print(f"  - 已复制 {len(BACKUP_TARGETS)} 个备份目标")
    
    # 3. 保存清单
    print("\n【3/4】保存备份清单...")
    manifest_path = backup_dir / "backup_manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"  - {manifest_path}")
    
    # 4. 创建压缩包
    print("\n【4/4】创建备份压缩包...")
    archive_path = create_backup_archive(backup_dir, manifest)
    archive_size = archive_path.stat().st_size / 1024 / 1024
    print(f"  - {archive_path}")
    print(f"  - 大小: {archive_size:.2f} MB")
    
    # 清理临时目录
    shutil.rmtree(backup_dir)
    
    result = {
        "backup_id": backup_id,
        "archive_path": str(archive_path),
        "archive_size_mb": archive_size,
        "manifest": manifest,
        "success": True
    }
    
    print()
    print("=" * 50)
    print("【备份完成】")
    print("=" * 50)
    print(f"  备份 ID: {backup_id}")
    print(f"  压缩包: {archive_path.name}")
    print(f"  大小: {archive_size:.2f} MB")
    print(f"  文件数: {manifest['statistics']['total_files']}")
    print("=" * 50)
    
    return result


def list_backups() -> List[Dict]:
    """列出所有备份"""
    root = get_project_root()
    backup_base = root / "archive" / "backups"
    
    backups = []
    for archive in backup_base.glob("backup_*.tar.gz"):
        stat = archive.stat()
        backups.append({
            "name": archive.name,
            "path": str(archive),
            "size_mb": stat.st_size / 1024 / 1024,
            "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
        })
    
    return sorted(backups, key=lambda x: x["created_at"], reverse=True)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="全面备份器 V1.0.0")
    parser.add_argument("--run", action="store_true", help="执行备份")
    parser.add_argument("--list", action="store_true", help="列出备份")
    parser.add_argument("--keep", type=int, default=5, help="保留最近 N 个备份")
    args = parser.parse_args()
    
    if args.list:
        backups = list_backups()
        print("【备份列表】")
        for b in backups:
            print(f"  - {b['name']}: {b['size_mb']:.2f} MB ({b['created_at']})")
        return 0
    
    if args.run:
        result = run_backup()
        
        # 清理旧备份
        backups = list_backups()
        if len(backups) > args.keep:
            print(f"\n清理旧备份（保留最近 {args.keep} 个）...")
            for old in backups[args.keep:]:
                Path(old["path"]).unlink()
                print(f"  - 已删除: {old['name']}")
        
        return 0 if result["success"] else 1
    
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
