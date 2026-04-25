#!/usr/bin/env python3
"""
创建 Clean Root 工程包
顶层直接是工程目录，排除 .openclaw / .local 等运行时目录
"""

import tarfile
import json
from pathlib import Path
from datetime import datetime


# 要包含的顶层目录
INCLUDE_DIRS = [
    "application",
    "domain",
    "capabilities",
    "device_capability_bus",
    "autonomous_planner",
    "visual_operation_agent",
    "safety_governor",
    "learning_loop",
    "closed_loop_verifier",
    "tests",
    "scripts",
    "docs",
    "infrastructure",
    "governance",
    "core",
    "orchestration",
    "skills",
    "memory_context",
]

# 要包含的顶层文件
INCLUDE_FILES = [
    "MEMORY.md",
    "AGENTS.md",
    "SOUL.md",
    "USER.md",
    "IDENTITY.md",
    "TOOLS.md",
    "HEARTBEAT.md",
    "Makefile",
    "requirements.txt",
    "pyproject.toml",
    "README.md",
    "ROUTE_RISK_POLICY_UNIFICATION_REPORT_V2.txt",
]

# 排除的模式
EXCLUDE_PATTERNS = [
    ".openclaw",
    ".local",
    "logs",
    "bin",
    "lib",
    "site-packages",
    "__pycache__",
    ".pytest_cache",
    "*.pyc",
    "*.log",
    "*.tar.gz",
    "*.zip",
    ".git",
    ".env",
    "node_modules",
    "*.bak",
    "*.json.bak",
]


def should_exclude(path: Path) -> bool:
    """检查路径是否应该被排除"""
    path_str = str(path)
    name = path.name
    
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        elif pattern in path_str.split("/"):
            return True
    
    return False


def create_clean_package():
    """创建 clean root 压缩包"""
    workspace = Path(__file__).parent.parent
    output_dir = workspace / "dist"
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"xiaoyi-claw-omega-clean-{timestamp}.tar.gz"
    
    included_count = 0
    excluded_count = 0
    
    with tarfile.open(output_file, "w:gz") as tar:
        # 添加顶层目录
        for dir_name in INCLUDE_DIRS:
            dir_path = workspace / dir_name
            if dir_path.exists() and dir_path.is_dir():
                # 先添加目录本身
                tar.add(dir_path, arcname=dir_name, recursive=False)
                included_count += 1
                
                # 再递归添加内容
                for item in dir_path.rglob("*"):
                    if not should_exclude(item):
                        arcname = str(item.relative_to(workspace))
                        tar.add(item, arcname=arcname)
                        included_count += 1
                    else:
                        excluded_count += 1
        
        # 添加顶层文件
        for file_name in INCLUDE_FILES:
            file_path = workspace / file_name
            if file_path.exists() and file_path.is_file():
                arcname = file_name
                tar.add(file_path, arcname=arcname)
                included_count += 1
    
    # 生成报告
    report = {
        "package": str(output_file),
        "timestamp": timestamp,
        "included_files": included_count,
        "excluded_files": excluded_count,
        "include_dirs": INCLUDE_DIRS,
        "include_files": INCLUDE_FILES,
        "exclude_patterns": EXCLUDE_PATTERNS,
    }
    
    report_path = output_dir / f"clean_package_report_{timestamp}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Clean 包已创建: {output_file}")
    print(f"   包含文件: {included_count}")
    print(f"   排除文件: {excluded_count}")
    print(f"   报告: {report_path}")
    
    # 验证顶层结构
    print(f"\n📦 验证顶层结构:")
    with tarfile.open(output_file, "r:gz") as tar:
        members = tar.getnames()
        top_level = set()
        for m in members:
            parts = m.split("/")
            if parts[0]:
                top_level.add(parts[0])
        
        for item in sorted(top_level):
            print(f"   - {item}/")
        
        # 检查是否有 .openclaw 或 .local
        if ".openclaw" in top_level or ".local" in top_level:
            print(f"\n❌ 错误: 包中包含 .openclaw 或 .local")
            return None
    
    print(f"\n✅ 顶层结构验证通过 (无 .openclaw / .local)")
    
    return output_file


if __name__ == "__main__":
    create_clean_package()
