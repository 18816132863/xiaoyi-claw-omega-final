from pathlib import Path

def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent
    while current != "/" and not (current / "core" / "ARCHITECTURE.md").exists():
        current = current.parent
    return current if current != "/" else Path(__file__).resolve().parent

#!/usr/bin/env python3
"""
架构融合脚本 - V1.0

将架构之外的目录融合到六层架构中：
- autonomy → governance/autonomy
- billing → governance/billing  
- collaboration → orchestration/collaboration
- compliance → governance/compliance
- config → infrastructure/config
- delivery → execution/delivery
- ecosystem → infrastructure/ecosystem
- extension → infrastructure/extension
- guard → governance/guard
- guide → core/guide
- infra → infrastructure/legacy
- openapi → infrastructure/openapi
- ops → infrastructure/ops
- product → orchestration/product
- reliability → governance/reliability
- simulation → execution/simulation
- standards → core/standards
- strategy → orchestration/strategy
- tenant → infrastructure/tenant
"""

import os
import shutil
from pathlib import Path

# 融合映射
CONSOLIDATION_MAP = {
    "autonomy": "governance/autonomy",
    "billing": "governance/billing",
    "collaboration": "orchestration/collaboration",
    "compliance": "governance/compliance",
    "config": "infrastructure/config",
    "delivery": "execution/delivery",
    "ecosystem": "infrastructure/ecosystem",
    "extension": "infrastructure/extension",
    "guard": "governance/guard",
    "guide": "core/guide",
    "infra": "infrastructure/legacy",
    "openapi": "infrastructure/openapi",
    "ops": "infrastructure/ops",
    "product": "orchestration/product",
    "reliability": "governance/reliability",
    "simulation": "execution/simulation",
    "standards": "core/standards",
    "strategy": "orchestration/strategy",
    "tenant": "infrastructure/tenant",
}

def consolidate():
    workspace = Path(str(get_project_root()))
    
    print("╔══════════════════════════════════════════════════╗")
    print("║        架构融合 V1.0                             ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    moved = []
    skipped = []
    
    for src_name, dst_name in CONSOLIDATION_MAP.items():
        src = workspace / src_name
        dst = workspace / dst_name
        
        if not src.exists():
            skipped.append((src_name, "源目录不存在"))
            continue
        
        if dst.exists():
            # 目标已存在，合并内容
            print(f"合并: {src_name} → {dst_name}")
            for item in src.iterdir():
                dst_item = dst / item.name
                if dst_item.exists():
                    if dst_item.is_dir():
                        shutil.rmtree(dst_item)
                    else:
                        dst_item.unlink()
                shutil.move(str(item), str(dst_item))
            shutil.rmtree(src)
            moved.append((src_name, dst_name, "merged"))
        else:
            # 目标不存在，直接移动
            print(f"移动: {src_name} → {dst_name}")
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            moved.append((src_name, dst_name, "moved"))
    
    print()
    print("══════════════════════════════════════════════════")
    print(f"已处理: {len(moved)} 个目录")
    print(f"跳过: {len(skipped)} 个目录")
    print("══════════════════════════════════════════════════")
    
    return moved, skipped

if __name__ == "__main__":
    consolidate()
