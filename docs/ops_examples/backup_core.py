#!/usr/bin/env python3
"""
OpenClaw 核心备份脚本 - V1.0

只包含核心运行文件：
- 六层架构核心文件
- 技能 SKILL.md（不含实现）
- 配置文件
"""

import os
import sys
import tarfile
from pathlib import Path
from datetime import datetime
from infrastructure.path_resolver import get_project_root

workspace = Path(str(get_project_root()))

# 核心文件白名单
CORE_FILES = {
    # L1 Core
    "AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md", "IDENTITY.md", 
    "MEMORY.md", "HEARTBEAT.md", "SECURITY.md", "README.md",
    # L2 Memory Context
    "memory_context/unified_search.py",
    # L3 Orchestration
    "orchestration/task_engine.py",
    "orchestration/router/skill_router.py",
    # L4 Execution
    "execution/skill_gateway.py",
    "execution/skill_adapter_gateway.py",
    # L5 Governance
    "governance/security.py",
    "governance/audit.py",
    # L6 Infrastructure
    "infrastructure/path_resolver.py",
    "infrastructure/token_budget.py",
    "infrastructure/inventory/skill_registry.json",
}

# 核心目录（只包含特定文件类型）
CORE_DIRS = {
    "core": [".md", ".json", ".py"],
    "infrastructure/shared": [".py"],
    "infrastructure/loader": [".py"],
}

# 技能只保留 SKILL.md
SKILL_PATTERN = "skills/*/SKILL.md"


def create_core_backup(output_dir: Path = None, version: str = "v4.3.3") -> Path:
    """创建核心备份"""
    output_dir = output_dir or Path("$HOME")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"openclaw_{version}_core_{timestamp}.tar.gz"
    
    print("╔══════════════════════════════════════════════════╗")
    print("║        OpenClaw 核心备份 V1.0                    ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"版本: {version}")
    print(f"输出: {output_file}")
    print()
    
    print("包含内容:")
    print("  ✓ 六层架构核心文件")
    print("  ✓ 技能 SKILL.md（165个）")
    print("  ✓ 配置文件")
    print()
    
    file_count = 0
    
    with tarfile.open(output_file, "w:gz") as tar:
        # 1. 核心文件
        for f in CORE_FILES:
            path = workspace / f
            if path.exists():
                tar.add(path, arcname=f)
                file_count += 1
        
        # 2. 核心目录
        for dir_name, exts in CORE_DIRS.items():
            dir_path = workspace / dir_name
            if dir_path.exists():
                for f in dir_path.rglob("*"):
                    if f.is_file() and f.suffix in exts:
                        rel = f.relative_to(workspace)
                        tar.add(f, arcname=str(rel))
                        file_count += 1
        
        # 3. 技能 SKILL.md
        for skill_md in workspace.glob(SKILL_PATTERN):
            rel = skill_md.relative_to(workspace)
            tar.add(skill_md, arcname=str(rel))
            file_count += 1
        
        # 4. 技能配置
        for config in workspace.glob("skills/*/config/*.json"):
            rel = config.relative_to(workspace)
            tar.add(config, arcname=str(rel))
            file_count += 1
        
        # 5. llm-memory-integration 完整保留（核心依赖）
        lmi_path = workspace / "skills/llm-memory-integration"
        if lmi_path.exists():
            for f in lmi_path.rglob("*"):
                if f.is_file() and not f.suffix in {".pyc", ".pack"}:
                    if "__pycache__" not in str(f):
                        rel = f.relative_to(workspace)
                        tar.add(f, arcname=str(rel))
                        file_count += 1
    
    print("══════════════════════════════════════════════════")
    print("备份完成")
    print("══════════════════════════════════════════════════")
    print()
    print(f"文件: {output_file}")
    print(f"大小: {output_file.stat().st_size / 1024:.1f} KB")
    print(f"文件数: {file_count}")
    
    return output_file


if __name__ == "__main__":
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("$HOME")
    create_core_backup(output_dir)
