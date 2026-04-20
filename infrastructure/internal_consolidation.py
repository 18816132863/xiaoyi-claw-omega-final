from pathlib import Path

def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent
    while current != "/" and not (current / "core" / "ARCHITECTURE.md").exists():
        current = current.parent
    return current if current != "/" else Path(__file__).resolve().parent

#!/usr/bin/env python3
"""
架构内部融合脚本 - V1.0

融合规则：
1. core/ 内重复概念合并
2. execution/ 内相似功能合并
3. governance/ 内相关模块合并
4. infrastructure/ 内工具类合并
5. orchestration/ 内路由相关合并
"""

import os
import shutil
from pathlib import Path

workspace = Path(str(get_project_root()))

# 内部融合映射
INTERNAL_MERGES = [
    # core/ 融合 - 架构模式合并到 layer_bridge
    ("core/clean_arch", "core/layer_bridge/clean_arch", "架构模式"),
    ("core/ddd", "core/layer_bridge/ddd", "架构模式"),
    ("core/event_driven", "core/layer_bridge/event_driven", "架构模式"),
    ("core/hexagonal", "core/layer_bridge/hexagonal", "架构模式"),
    ("core/microservice", "core/layer_bridge/microservice", "架构模式"),
    ("core/service_mesh", "core/layer_bridge/service_mesh", "架构模式"),
    
    # core/ 融合 - 功能模块合并
    ("core/feedback", "core/state/feedback", "状态管理"),
    ("core/health", "core/state/health", "状态管理"),
    ("core/profile", "core/state/profile", "状态管理"),
    
    # core/ 融合 - 帮助系统合并
    ("core/help", "core/tutorial/help", "教程系统"),
    ("core/onboarding", "core/tutorial/onboarding", "教程系统"),
    
    # core/ 融合 - 查询相关合并
    ("core/search", "core/query/search", "查询系统"),
    
    # execution/ 融合 - 多代理系统合并
    ("execution/multiagent", "execution/collaboration/multiagent", "协作系统"),
    ("execution/domain_agents", "execution/collaboration/domain_agents", "协作系统"),
    
    # execution/ 融合 - 运行时合并
    ("execution/runtime", "execution/commands/runtime", "命令系统"),
    ("execution/autonomy", "execution/commands/autonomy", "命令系统"),
    
    # execution/ 融合 - 搜索合并
    ("execution/search", "execution/text_summary/search", "文本处理"),
    
    # execution/ 融合 - 工作流合并
    ("execution/orchestration", "execution/workflows/orchestration", "工作流"),
    
    # governance/ 融合 - 安全相关合并
    ("governance/safety", "governance/security/safety", "安全系统"),
    
    # governance/ 融合 - 配置合并
    ("governance/config", "governance/security/config", "安全系统"),
    
    # governance/ 融合 - 灾难恢复合并
    ("governance/disaster_recovery", "governance/reliability/disaster_recovery", "可靠性"),
    ("governance/rollback", "governance/reliability/rollback", "可靠性"),
    
    # infrastructure/ 融合 - 监控合并
    ("infrastructure/monitoring", "infrastructure/ops/monitoring", "运维系统"),
    
    # infrastructure/ 融合 - 性能合并
    ("infrastructure/performance", "infrastructure/optimization/performance", "优化系统"),
    
    # infrastructure/ 融合 - 业务合并
    ("infrastructure/business", "infrastructure/portfolio/business", "组合管理"),
    
    # infrastructure/ 融合 - 评估合并
    ("infrastructure/assessment", "infrastructure/portfolio/assessment", "组合管理"),
    
    # orchestration/ 融合 - 路由合并
    ("orchestration/routing", "orchestration/router/routing", "路由系统"),
    
    # orchestration/ 融合 - 调度合并
    ("orchestration/task-scheduler", "orchestration/workflows/scheduler", "工作流"),
]

def merge_dirs(src: Path, dst: Path, category: str):
    """合并目录"""
    if not src.exists():
        return False, "源不存在"
    
    if dst.exists():
        # 目标存在，合并内容
        for item in src.iterdir():
            dst_item = dst / item.name
            if dst_item.exists():
                if dst_item.is_dir():
                    shutil.rmtree(dst_item)
                else:
                    dst_item.unlink()
            shutil.move(str(item), str(dst_item))
        shutil.rmtree(src)
        return True, "merged"
    else:
        # 目标不存在，直接移动
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return True, "moved"

def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║        架构内部融合 V1.0                         ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    moved = []
    skipped = []
    
    for src_name, dst_name, category in INTERNAL_MERGES:
        src = workspace / src_name
        dst = workspace / dst_name
        
        success, status = merge_dirs(src, dst, category)
        
        if success:
            print(f"✓ {src_name} → {dst_name} ({category})")
            moved.append((src_name, dst_name, category, status))
        else:
            skipped.append((src_name, status))
    
    print()
    print("══════════════════════════════════════════════════")
    print(f"已处理: {len(moved)} 个目录")
    print(f"跳过: {len(skipped)} 个目录")
    print("══════════════════════════════════════════════════")
    
    return moved, skipped

if __name__ == "__main__":
    main()
