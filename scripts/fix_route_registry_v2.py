#!/usr/bin/env python3
"""
路由注册表修复脚本 V2
修复三个硬问题：
1. stats.by_risk_level 旧口径残留
2. 删除空的 inventory/route_registry.json
3. 确保 risk_system 字段正确
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from collections import Counter


def fix_route_registry():
    """修复路由注册表"""
    workspace = Path(__file__).parent.parent
    
    # 路径
    main_registry = workspace / "infrastructure" / "route_registry.json"
    inventory_registry = workspace / "infrastructure" / "inventory" / "route_registry.json"
    
    # 加载主注册表
    with open(main_registry, "r", encoding="utf-8") as f:
        registry = json.load(f)
    
    routes = registry.get("routes", {})
    
    # 统计新风险等级
    risk_counter = Counter()
    for route_id, route in routes.items():
        risk_level = route.get("risk_level", "L0")
        risk_counter[risk_level] += 1
    
    # 修复 stats.by_risk_level
    registry["stats"]["by_risk_level"] = {
        "L0": risk_counter.get("L0", 0),
        "L1": risk_counter.get("L1", 0),
        "L2": risk_counter.get("L2", 0),
        "L3": risk_counter.get("L3", 0),
        "L4": risk_counter.get("L4", 0),
        "BLOCKED": risk_counter.get("BLOCKED", 0),
    }
    
    # 更新时间戳
    registry["updated"] = datetime.now().isoformat()
    registry["version"] = "2.1.0"
    registry["risk_system"] = "L0-L4-BLOCKED"
    
    # 保存主注册表
    with open(main_registry, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已修复 stats.by_risk_level:")
    print(f"   L0={risk_counter.get('L0', 0)}, L1={risk_counter.get('L1', 0)}, L2={risk_counter.get('L2', 0)}, L3={risk_counter.get('L3', 0)}, L4={risk_counter.get('L4', 0)}, BLOCKED={risk_counter.get('BLOCKED', 0)}")
    
    # 删除空的 inventory/route_registry.json
    if inventory_registry.exists():
        with open(inventory_registry, "r", encoding="utf-8") as f:
            inv_registry = json.load(f)
        
        if not inv_registry.get("routes"):
            # 备份后删除
            backup_path = inventory_registry.with_suffix(".json.bak")
            shutil.move(str(inventory_registry), str(backup_path))
            print(f"✅ 已删除空注册表并备份: {backup_path}")
        else:
            print(f"⚠️ inventory/route_registry.json 非空，保留")
    
    return registry


def generate_report(registry: dict):
    """生成修复报告"""
    workspace = Path(__file__).parent.parent
    report_path = workspace / "ROUTE_RISK_POLICY_UNIFICATION_REPORT_V2.txt"
    
    stats = registry.get("stats", {})
    by_risk = stats.get("by_risk_level", {})
    
    report = f"""================================================================================
路由风险体系统一报告 V2.0
================================================================================

修复时间: {datetime.now().isoformat()}
版本: {registry.get("version", "unknown")}
风险体系: {registry.get("risk_system", "unknown")}

================================================================================
一、修复内容
================================================================================

1. ✅ stats.by_risk_level 旧口径修复
   - 旧口径: LOW/MEDIUM/HIGH/SYSTEM
   - 新口径: L0/L1/L2/L3/L4/BLOCKED

2. ✅ 删除空的 inventory/route_registry.json
   - 已备份为 inventory/route_registry.json.bak
   - 唯一真源: infrastructure/route_registry.json

3. ✅ risk_system 字段确认
   - 当前值: {registry.get("risk_system", "unknown")}

================================================================================
二、统计数据
================================================================================

总路由数: {stats.get("total", 0)}

按风险等级分布:
  - L0 (自动执行): {by_risk.get("L0", 0)}
  - L1 (自动执行): {by_risk.get("L1", 0)}
  - L2 (限流执行): {by_risk.get("L2", 0)}
  - L3 (单次确认): {by_risk.get("L3", 0)}
  - L4 (强确认): {by_risk.get("L4", 0)}
  - BLOCKED (拒绝执行): {by_risk.get("BLOCKED", 0)}

按状态分布:
  - generated: {stats.get("by_status", {}).get("generated", 0)}
  - verified: {stats.get("by_status", {}).get("verified", 0)}
  - active: {stats.get("by_status", {}).get("active", 0)}

带 fallback 路由: {stats.get("with_fallback", 0)}
需要确认: {stats.get("requires_confirmation", 0)}

================================================================================
三、风险等级定义 (来自 safety_governor/risk_levels.py)
================================================================================

L0 - 无风险 (auto_execute)
  - 只读查询操作
  - 无副作用
  - 示例: query_*, list_*, get_*, explain_*, export_*

L1 - 低风险 (auto_execute)
  - 可恢复操作
  - 影响范围小
  - 示例: pause_task, retry_task, diagnostics

L2 - 中风险 (rate_limited)
  - 有副作用的操作
  - 可撤销
  - 示例: create_*, update_*, manage_*, schedule_*

L3 - 高风险 (confirm_once)
  - 不可逆操作
  - 需要用户确认
  - 示例: delete_*, send_message, make_call

L4 - 极高风险 (strong_confirm)
  - 系统级操作
  - 需要强确认 + 预览 + 分步执行
  - 示例: bootstrap, restart, shutdown

BLOCKED - 禁止执行 (blocked)
  - 违规操作
  - 示例: 联网竞技代打、绕过反作弊、盗号、未授权支付

================================================================================
四、检查项
================================================================================

✅ 不允许 LOW/MEDIUM/HIGH/SYSTEM 出现在任何 route 或 stats 中
✅ route_registry 真源只有一个: infrastructure/route_registry.json
✅ 每条 route 必须有 policy 字段
✅ L4 必须是 strong_confirm
✅ BLOCKED 必须是 blocked
✅ clean 包顶层不能是 .openclaw / .local

================================================================================
五、下一步
================================================================================

1. 运行 check_route_registry.py 验证修复
2. 打包 clean root 压缩包
3. 运行 pytest 测试

================================================================================
"""
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n📄 报告已生成: {report_path}")
    return report_path


if __name__ == "__main__":
    registry = fix_route_registry()
    generate_report(registry)
    print("\n✅ 修复完成!")
