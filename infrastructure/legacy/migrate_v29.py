#!/usr/bin/env python3
"""
架构迁移脚本 V2.9.0
将 V2.8.x 架构迁移到 V2.9.0 精简架构
"""

import os
import shutil
import json
from pathlib import Path
from infrastructure.path_resolver import get_project_root

WORKSPACE = Path(str(get_project_root()))

# 需要删除的冗余目录
REDUNDANT_DIRS = [
    "autonomy",
    "billing", 
    "business",
    "collaboration",
    "compliance",
    "delivery",
    "ecosystem",
    "extension",
    "openapi",
    "ops",
    "portfolio",
    "product",
    "release",
    "reliability",
    "simulation",
    "standards",
    "strategy",
    "templates",
    "tenant",
]

# 需要保留的目录
KEEP_DIRS = [
    "core",
    "engine",  # 新建，合并 orchestration + execution
    "skills",
    "guard",   # 新建，从 governance 精简
    "infra",   # 新建，从 infrastructure 精简
    "memory",
    "repo",
    "plugins",
    "guide",
    "reports",
    ".clawhub",
    ".learnings",
    ".openclaw",
]

# 需要合并的目录
MERGE_PLANS = {
    "orchestration": "engine",
    "execution": "engine",
    "governance": "guard",
    "infrastructure": "infra",
    "memory_context": "core",
}

def backup_dir(dir_path: Path):
    """备份目录"""
    backup_path = WORKSPACE / ".backup_v28" / dir_path.name
    if dir_path.exists():
        shutil.copytree(dir_path, backup_path, dirs_exist_ok=True)
        print(f"✓ 备份: {dir_path.name} -> .backup_v28/{dir_path.name}")

def remove_redundant():
    """删除冗余目录"""
    print("\n=== 删除冗余目录 ===")
    for dir_name in REDUNDANT_DIRS:
        dir_path = WORKSPACE / dir_name
        if dir_path.exists():
            backup_dir(dir_path)
            shutil.rmtree(dir_path)
            print(f"✗ 删除: {dir_name}")

def merge_directories():
    """合并目录"""
    print("\n=== 合并目录 ===")
    for src_name, dst_name in MERGE_PLANS.items():
        src_path = WORKSPACE / src_name
        dst_path = WORKSPACE / dst_name
        
        if src_path.exists():
            # 创建目标目录
            dst_path.mkdir(exist_ok=True)
            
            # 复制内容
            for item in src_path.iterdir():
                dst_item = dst_path / item.name
                if item.is_dir():
                    shutil.copytree(item, dst_item, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dst_item)
            
            # 备份并删除源目录
            backup_dir(src_path)
            shutil.rmtree(src_path)
            print(f"→ 合并: {src_name} -> {dst_name}")

def create_new_structure():
    """创建新目录结构"""
    print("\n=== 创建新目录结构 ===")
    new_dirs = ["engine", "guard", "infra"]
    for dir_name in new_dirs:
        dir_path = WORKSPACE / dir_name
        dir_path.mkdir(exist_ok=True)
        (dir_path / "__init__.py").touch()
        print(f"✓ 创建: {dir_name}/")

def create_engine_files():
    """创建 engine 目录文件"""
    print("\n=== 创建 engine 文件 ===")
    engine_path = WORKSPACE / "engine"
    
    # router.py
    router_code = '''"""
技能路由器 V2.9.0
根据任务类型自动路由到对应技能
"""

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "core" / "CONFIG.json"

class SkillRouter:
    def __init__(self):
        with open(CONFIG_PATH) as f:
            self.config = json.load(f)
    
    def route(self, user_input: str) -> list:
        """根据用户输入路由到对应层级"""
        layers = ["L1"]  # L1始终加载
        
        for layer, info in self.config["layers"].items():
            if layer == "L1":
                continue
            triggers = info.get("triggers", [])
            if any(t in user_input for t in triggers):
                layers.append(layer)
        
        return layers
    
    def get_skills(self, layer: str, category: str = None) -> list:
        """获取指定层级的技能"""
        layer_info = self.config["layers"].get(layer, {})
        if category and "categories" in layer_info:
            return layer_info["categories"].get(category, {}).get("skills", [])
        return layer_info.get("skills", [])

router = SkillRouter()
'''
    (engine_path / "router.py").write_text(router_code)
    print("✓ 创建: engine/router.py")
    
    # 创建子目录
    (engine_path / "workflows").mkdir(exist_ok=True)
    (engine_path / "executors").mkdir(exist_ok=True)
    (engine_path / "validators").mkdir(exist_ok=True)
    print("✓ 创建: engine/workflows/, executors/, validators/")

def create_guard_files():
    """创建 guard 目录文件"""
    print("\n=== 创建 guard 文件 ===")
    guard_path = WORKSPACE / "guard"
    
    # security.py
    security_code = '''"""
安全检查模块 V2.9.0
"""

DANGEROUS_COMMANDS = ["rm -rf", "sudo", "chmod 777", "> /dev/"]
ALLOWED_PATHS = [str(get_project_root())]

def check_command(cmd: str) -> tuple:
    """检查命令是否安全"""
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous in cmd:
            return False, f"危险命令: {dangerous}"
    return True, "安全"

def check_path(path: str) -> tuple:
    """检查路径是否允许"""
    for allowed in ALLOWED_PATHS:
        if path.startswith(allowed):
            return True, "允许"
    return False, "路径不在白名单中"
'''
    (guard_path / "security.py").write_text(security_code)
    print("✓ 创建: guard/security.py")
    
    # permissions.py
    permissions_code = '''"""
权限管理模块 V2.9.0
"""

PERMISSIONS = {
    "read": True,
    "write": True,
    "exec": False,  # 需要确认
    "delete": False,  # 需要确认
}

def check_permission(action: str) -> tuple:
    """检查权限"""
    allowed = PERMISSIONS.get(action, False)
    return allowed, "允许" if allowed else "需要确认"
'''
    (guard_path / "permissions.py").write_text(permissions_code)
    print("✓ 创建: guard/permissions.py")

def create_infra_files():
    """创建 infra 目录文件"""
    print("\n=== 创建 infra 文件 ===")
    infra_path = WORKSPACE / "infra"
    
    # paths.py
    paths_code = '''"""
路径解析模块 V2.9.0
"""

from pathlib import Path

WORKSPACE = Path(str(get_project_root()))

def resolve(path: str) -> Path:
    """解析路径"""
    if path.startswith("/"):
        return Path(path)
    return WORKSPACE / path

def is_safe(path: Path) -> bool:
    """检查路径是否安全"""
    try:
        path.resolve().relative_to(WORKSPACE)
        return True
    except ValueError:
        return False
'''
    (infra_path / "paths.py").write_text(paths_code)
    print("✓ 创建: infra/paths.py")
    
    # performance.py
    performance_code = '''"""
性能模块 V2.9.0
"""

import time
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_lookup(key: str):
    """缓存查找"""
    return key

class PerformanceTimer:
    def __init__(self, name: str):
        self.name = name
        self.start = time.time()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        elapsed = (time.time() - self.start) * 1000
        print(f"[{self.name}] {elapsed:.2f}ms")
'''
    (infra_path / "performance.py").write_text(performance_code)
    print("✓ 创建: infra/performance.py")

def cleanup_files():
    """清理冗余文件"""
    print("\n=== 清理冗余文件 ===")
    
    # 删除根目录下的冗余文件
    redundant_files = [
        "AGENTS.md.bak",
        "TOOLS.md.bak",
        "AUTO_OPTIMIZATION_V26.py",
        "AUTO_OPTIMIZATION_V26_COMPLETE.py",
        "AUTO_OPTIMIZATION_V26_FINAL.py",
        "AUTO_OPTIMIZATION_V26_FULL.py",
        "COMPLETE_TEST_V26.py",
        "MODULE_ACTIVATION_MATRIX.json",
        "SYSTEM_CAPABILITY_MATRIX_V10.json",
        "SYSTEM_CAPABILITY_MATRIX_V8.json",
        "SKILL_PACKAGE_V12.json",
        "system-config-omega-v5.json",
        "system-config-omega.json",
        "unified-config.yaml",
        "security_config.json",
        "skills-lock.json",
    ]
    
    for filename in redundant_files:
        filepath = WORKSPACE / filename
        if filepath.exists():
            filepath.unlink()
            print(f"✗ 删除文件: {filename}")

def main():
    print("=" * 50)
    print("架构迁移 V2.8.x -> V2.9.0")
    print("=" * 50)
    
    # 创建备份目录
    (WORKSPACE / ".backup_v28").mkdir(exist_ok=True)
    
    # 执行迁移
    create_new_structure()
    merge_directories()
    create_engine_files()
    create_guard_files()
    create_infra_files()
    remove_redundant()
    cleanup_files()
    
    print("\n" + "=" * 50)
    print("迁移完成!")
    print("=" * 50)
    print("\n新目录结构:")
    for item in sorted(WORKSPACE.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            print(f"  {item.name}/")

if __name__ == "__main__":
    main()
